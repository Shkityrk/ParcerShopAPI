from datetime import datetime

from src.utils import ProductsFileDownloader, get_products_file_downloader
from apscheduler.schedulers.asyncio import AsyncIOScheduler

__all__ = [
    "start_download_products_job"
]


class DownloadProductsJob:
    _product_file_downloader: ProductsFileDownloader
    _scheduler: AsyncIOScheduler

    def __init__(self):
        self._product_file_downloader = get_products_file_downloader()
        self._scheduler = AsyncIOScheduler()

    def start_job(self):
        self._scheduler.add_job(self._product_file_downloader.download_products_in_thread, 'interval', minutes=60)
        self._scheduler.start()

        for job in self._scheduler.get_jobs():
            job.modify(next_run_time=datetime.now())


async def start_download_products_job():
    download_products_job = DownloadProductsJob()
    download_products_job.start_job()
