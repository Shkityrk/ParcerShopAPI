import json
from threading import Thread
from datetime import datetime

from loguru import logger

from src.config import THREADS_COUNT, TOTAL_IDS_COUNT
from src.redis_service import get_redis_service, RedisService

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

    async def download_items_in_thread(self) -> None:
        logger.info(f"Started downloading products in {self._threads_count} threads")

        # Getting total_ids_count value
        redis_service = await get_redis_service()
        total_ids_count = await redis_service.get_total_ids_count()
        if not total_ids_count:
            total_ids_count = self._sima_land_api.find_total_ids_count(TOTAL_IDS_COUNT)
            await redis_service.set_total_ids_count(total_ids_count)
            # TODO: need a logic of changing TOTAL_IDS_COUNT in .env file using found value

        threads = []
        counter = 0

        # Spreading threads on first part of ids
        index_limit_first_part = int(total_ids_count * 0.375)
        index_shift_first_part = index_limit_first_part // int(self._threads_count * 0.13)
        for i in range(0, index_limit_first_part, index_shift_first_part):
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    i,
                    i + index_shift_first_part if counter < index_limit_first_part else index_limit_first_part,
                    counter
                )
            )
            )

            logger.info(f"Thread ID: {counter} | Index start: {i} | Index end: {i + index_shift_first_part}")

            counter += 1

        # Spreading threads on second part of ids
        index_start_second_part = index_limit_first_part
        index_limit_second_part = int(total_ids_count * 0.75)
        index_shift_second_part = (index_limit_second_part-index_start_second_part) // (self._threads_count // 3)
        for i in range(index_start_second_part, index_limit_second_part, index_shift_second_part):
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    i,
                    i + index_shift_second_part if counter < index_limit_second_part else index_limit_second_part,
                    counter
                )
            )
            )
            logger.info(f"Thread ID: {counter} | Index start: {i} | Index end: {i + index_shift_second_part}")

            counter += 1

        # Spreading threads on third part of ids
        index_start_third_part = index_limit_second_part
        index_limit_third_part = total_ids_count
        index_shift_third_part = (
                (index_limit_third_part - index_start_third_part)
                //
                (self._threads_count - int(self._threads_count * 0.13) - 1 - (self._threads_count // 3))
        )
        for i in range(index_start_third_part, index_limit_third_part, index_shift_third_part):
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    i,
                    i + index_shift_third_part if counter < index_limit_third_part else index_limit_third_part,
                    counter
                )
            )
            )
            logger.info(f"Thread ID: {counter} | Index start: {i} | Index end: {i + index_shift_third_part}")

            counter += 1

        # Starting all threads
        time_start = datetime.now()
        for thread in threads:
            thread.start()

        # Waiting till all threads are completed
        for thread in threads:
            thread.join()
        time_end = datetime.now()

        # Getting the final list of items
        items = []
        for i in range(self._threads_count):
            items = items + self._sima_land_api.items_from_threads[i]

        logger.info(f"Downloaded info about {len(items)} items. Time taken: {(time_end - time_start)}")

        # Writing items into file
        items_json = {"items": items}
        with open("files/items.json", "w", encoding="UTF-8") as file:
            json.dump(items_json, file)

        logger.info(f"Info about products was written to files/items.json")


def get_items_file_downloader() -> ItemsFileDownloader:
    return ItemsFileDownloader(THREADS_COUNT)
