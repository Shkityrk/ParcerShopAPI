from threading import Thread
from datetime import datetime

from loguru import logger
from dict2xml import Converter, DataSorter

from src.config import THREADS_COUNT, TOTAL_IDS_COUNT
from src.redis_service import get_redis_service

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

        #  total_ids_count = 1_000_000 (only for testing)
        threads = []
        threads_counter = 0

        # Spreading threads on first part of ids
        index_limit_first_part = int(total_ids_count * 0.375)
        index_shift_first_part = index_limit_first_part // int(self._threads_count * 0.13)
        for index_limit_left in range(0, index_limit_first_part, index_shift_first_part):
            index_limit_right = index_limit_left + index_shift_first_part if threads_counter < index_limit_first_part \
                else index_limit_first_part
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    index_limit_left,
                    index_limit_right,
                    threads_counter
                )
            )
            )

            logger.info(
                f"Thread ID: {threads_counter} | Index start: {index_limit_left} | Index end: {index_limit_right}"
            )

            threads_counter += 1

        # Spreading threads on second part of ids
        index_start_second_part = index_limit_first_part
        index_limit_second_part = int(total_ids_count * 0.75)
        index_shift_second_part = (index_limit_second_part-index_start_second_part) // (self._threads_count // 3)
        for index_limit_left in range(index_start_second_part, index_limit_second_part, index_shift_second_part):
            index_limit_right = index_limit_left + index_shift_second_part if threads_counter < index_limit_second_part \
                else index_limit_second_part
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    index_limit_left,
                    index_limit_right,
                    threads_counter
                )
            )
            )
            logger.info(
                f"Thread ID: {threads_counter} | Index start: {index_limit_left} | Index end: {index_limit_right}"
            )

            threads_counter += 1

        # Spreading threads on third part of ids
        index_start_third_part = index_limit_second_part
        index_limit_third_part = total_ids_count
        index_shift_third_part = (
                (index_limit_third_part - index_start_third_part)
                //
                (self._threads_count - int(self._threads_count * 0.13) - 1 - (self._threads_count // 3))
        )
        for index_limit_left in range(index_start_third_part, index_limit_third_part, index_shift_third_part):
            index_limit_right = index_limit_left + index_shift_third_part if threads_counter < index_limit_third_part \
                else index_limit_third_part
            threads.append(Thread(
                target=self._sima_land_api.download_items_file,
                args=(
                    index_limit_left,
                    index_limit_right,
                    threads_counter
                )
            )
            )
            logger.info(
                f"Thread ID: {threads_counter} | Index start: {index_limit_left} | Index end: {index_limit_left}"
            )

            threads_counter += 1

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

        # Writing items into xml file
        items_json = {"items": {"item": items}}
        with open("files/items.xml", "w") as file:
            file.write(Converter(wrap="response", indent="  ").build(items_json, data_sorter=DataSorter.never()))

        logger.info(f"Info about products was written to files/items.xml.")


def get_items_file_downloader() -> ItemsFileDownloader:
    return ItemsFileDownloader(THREADS_COUNT)
