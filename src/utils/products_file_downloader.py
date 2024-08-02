from threading import Thread

from .sima_land_api import SimaLandAPI
from src.config import THREADS_COUNT, TOTAL_IDS_COUNT

__all__ = [
    "ProductsFileDownloader",
    "get_products_file_downloader"
]


class ProductsFileDownloader:
    _threads_count: int
    _sima_land_api: SimaLandAPI

    def __init__(self, threads_count: int) -> None:
        self._threads_count = threads_count
        self._sima_land_api = SimaLandAPI(threads_count)

    def download_products_in_thread(self) -> None:
        products_count = self._sima_land_api.get_products_count()

        shift = TOTAL_IDS_COUNT // self._threads_count
        threads = []
        counter = 0
        for i in range(0, TOTAL_IDS_COUNT, shift):
            threads.append(Thread(target=self._sima_land_api.download_products_file, args=(i, i+shift, counter)))
            threads[counter].start()

            counter += 1

        for i in range(0, self._threads_count):
            threads[i].join()

        items = []
        for i in range(self._threads_count):
            items = items + self._sima_land_api.items_from_threads

        with open("files/products.txt", "w") as file:
            file.write("\n".join(items).join("\n"))


def get_products_file_downloader() -> ProductsFileDownloader:
    return ProductsFileDownloader(THREADS_COUNT)
