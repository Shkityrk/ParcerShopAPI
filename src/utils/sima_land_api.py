from asyncio import sleep, run
from typing import Any

import requests
import xml.etree.ElementTree as ET

from loguru import logger

from src.redis_service import get_redis_service

__all__ = [
    "SimaLandAPI"
]


class SimaLandAPI:
    _items_url: str = "https://www.sima-land.ru/api/v3/item/?per_page=100&id-greater-than="
    amount_of_items: int = 0
    amount_of_exceptions: int = 0

    def __init__(self, threads_count: int):
        self.items_from_threads = [[] for _ in range(threads_count+1)]

    def download_items_file(self, start_index: int, end_index: int, thread_id: int) -> None:
        with open(f"files/items_{thread_id}.xml", "w+") as file:
            file.write("<response><items></items></response>")

        with open(f"files/items_{thread_id}.xml", "r") as file:
            run(self._download_items_file(start_index, end_index, thread_id, file))

    async def _download_items_file(self, start_index: int, end_index: int, thread_id: int, file) -> None:
        redis_service = await get_redis_service()

        while start_index <= end_index:
            if not await redis_service.can_make_request():
                logger.info(f"Faced API limits in thread {thread_id}. Will sleep for 5 seconds.")
                await sleep(5)
                continue

            try:
                response = requests.get(self._items_url + str(start_index))
            except Exception:
                logger.exception(
                    "Occurred exception with requests' limit to SimaLand API. Need to decrease amount of threads"
                )
                continue
            if response.status_code != 200:
                logger.error(
                    f"Request failed with status code {response.status_code} (mostly cuz such indexes does not exist)"
                )
                break

            response_json = response.json()

            try:
                file.seek(0)
                response_xml = ET.parse(file)
                xml_items = response_xml.getroot().find("items")

                for item in response_json["items"]:
                    if item["id"] > end_index:
                        break

                    xml_item = ET.Element("item")
                    self.add_item_to_items(item, xml_item)
                    xml_items.append(xml_item)

                    self.amount_of_items += 1

                response_xml.write(f"files/items_{thread_id}.xml", encoding="utf-8")

            except Exception as e:
                logger.error(e)

            start_index = response_json["items"][-1]["id"]
            logger.info(f"Downloaded one of the parts in the thread {thread_id}...")

    def add_item_to_items(self, item: Any, items: ET.Element) -> None:
        if isinstance(item, str | int):
            items.text = str(item)

        if isinstance(item, dict):
            for key, value in item.items():
                self.add_item_to_items(value, ET.SubElement(items, key))

        if isinstance(item, list):
            for it in item:
                self.add_item_to_items(it, ET.SubElement(items, "item"))

    def find_total_ids_count(self, total_ids_count: int) -> int:
        try:
            response = requests.get(self._items_url + str(total_ids_count))
        except Exception:
            logger.exception(
                "Occurred exception trying to make request to SimaLand API. IDK the reason, really."
            )
            return total_ids_count  # IDK if this is good decision, although I hope this except will never happen

        if response.status_code == 200:
            return self.find_total_ids_count(total_ids_count+100000)
        elif response.status_code == 404:
            return total_ids_count
        else:
            logger.error(f"Got status code {response.status_code} trying to get total_ids_count. It should not be so.")
            return total_ids_count  # Also don't know whether it is correct (the same as in except clause).
