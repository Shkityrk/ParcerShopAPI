from asyncio import sleep, run

import requests
from loguru import logger

from src.redis_service import get_redis_service

__all__ = [
    "SimaLandAPI"
]


class SimaLandAPI:
    _items_url: str = "https://www.sima-land.ru/api/v3/item/?per_page=100&id-greater-than="
    items_from_threads: list[list[dict]] = []

    def __init__(self, threads_count: int):
        self.items_from_threads = [[] for _ in range(threads_count+1)]

    def download_items_file(self, start_index: int, end_index: int, thread_id: int):
        run(self._download_items_file(start_index, end_index, thread_id))

    async def _download_items_file(self, start_index: int, end_index: int, thread_id: int):
        redis_service = await get_redis_service()

        items = []
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

            for item in response_json["items"]:
                if item["id"] > end_index:
                    break
                items.append(item)

            start_index = response_json["items"][-1]["id"]
            logger.info(f"Downloaded one of the parts in the thread {thread_id}...")

        self.items_from_threads[thread_id] = items

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
