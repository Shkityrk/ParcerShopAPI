import json

import requests

__all__ = [
    "SimaLandAPI"
]


class SimaLandAPI:
    _products_url: str = "https://www.sima-land.ru/api/v3/item/?per_page=100&id-greater-than="
    _products_count_url: str = "https://www.sima-land.ru/api/v3/item/"
    items_from_threads: list[list[dict]] = []

    def __init__(self, threads_count: int):
        self.items_from_threads = [[] for _ in range(threads_count)]

    def get_products_count(self):
        response_json = requests.get(self._products_count_url, headers={"Accept": "application/json"}).json()
        return response_json["_meta"]["totalCount"]

    def download_products_file(self, start_index: int, end_index: int, thread_id: int):
        items = []
        while start_index <= end_index:
            response_json = requests.get(self._products_url+str(start_index)).json()
            items = items + response_json["items"]

            start_index = response_json["items"][-1]["id"]

        self.items_from_threads[thread_id] = items
