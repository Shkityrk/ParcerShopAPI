from threading import Thread
import json

from loguru import logger

from src.config import THREADS_COUNT, TOTAL_IDS_COUNT

from .sima_land_api import SimaLandAPI


__all__ = [
    "ItemsFileDownloader",
    "get_items_file_downloader"
]


class ItemsFileDownloader:
    _threads_count: int
    _sima_land_api: SimaLandAPI

    def __init__(self, threads_count: int) -> None:
        self._threads_count = threads_count
        self._sima_land_api = SimaLandAPI(threads_count)

    def download_items_in_thread(self) -> None:
        logger.info(f"Started downloading products in {self._threads_count} threads")
        threads = []
        counter = 0

        index_limit_first_part = TOTAL_IDS_COUNT * 3 // 5
        shift_first_part = index_limit_first_part // (self._threads_count // 3)
        for i in range(0, index_limit_first_part, shift_first_part):
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    i,
                    i + shift_first_part if counter != index_limit_first_part else index_limit_first_part,
                    counter
                )
            )
            )
            print(i, i + shift_first_part, counter)

            threads[counter].start()
            counter += 1

        index_start_second_part = index_limit_first_part
        index_limit_second_part = TOTAL_IDS_COUNT
        index_shift_second_part = (index_limit_second_part-index_start_second_part) // (self._threads_count * 2 // 3)
        for i in range(index_start_second_part, index_limit_second_part, index_shift_second_part):
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    i,
                    i + index_shift_second_part if counter != index_limit_second_part else index_limit_second_part,
                    counter
                )
            )
            )
            print(i, i + index_shift_second_part, counter)

            threads[counter].start()
            counter += 1

        for i in range(0, self._threads_count):
            threads[i].join()

        items = []
        for i in range(self._threads_count):
            items = items + self._sima_land_api.items_from_threads[i]

        logger.info(f"Downloaded info about {len(items)} items")

        items_json = {"items": items}

        with open("files/items.json", "w", encoding="UTF-8") as file:
            json.dump(items_json, file)

        logger.info(f"Info about products was written to files/items.json")


def get_items_file_downloader() -> ItemsFileDownloader:
    return ItemsFileDownloader(THREADS_COUNT)
