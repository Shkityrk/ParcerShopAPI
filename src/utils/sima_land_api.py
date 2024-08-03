import json

import requests
from loguru import logger

__all__ = [
    "SimaLandAPI"
]


class SimaLandAPI:
    _items_url: str = "https://www.sima-land.ru/api/v3/item/?per_page=100&id-greater-than="
    items_from_threads: list[list[dict]] = []

    def __init__(self, threads_count: int):
        self.items_from_threads = [[] for _ in range(threads_count+1)]

    def download_items_file(self, start_index: int, end_index: int, thread_id: int):
        items = []
        while start_index <= end_index:
            try:
                response = requests.get(self._items_url + str(start_index))
            except Exception:
                logger.exception(
                    "Occured exception with requests' limit to SimaLand API. Need to decrease amount of threads"
                )
                continue
            if response.status_code == 200:
                if response.json()["items"][0]["id"] > end_index:
                    break

                items = items + response.json()["items"]
                start_index = response.json()["items"][-1]["id"]
                logger.info(f"Downloaded one of the parts in the thread {thread_id}...")
            else:
                logger.error(
                    f"Request failed with status code {response.status_code} (mostly cuz such indexes does not exist)"
                )
                break

        self.items_from_threads[thread_id] = items
