from datetime import datetime

from src.utils import ItemsFileDownloader, get_items_file_downloader
from apscheduler.schedulers.asyncio import AsyncIOScheduler

__all__ = [
    "start_download_items_job"
]


class DownloadProductsJob:
    _items_file_downloader: ItemsFileDownloader
    _scheduler: AsyncIOScheduler

    def __init__(self):
        self._items_file_downloader = get_items_file_downloader()
        self._scheduler = AsyncIOScheduler()

    def start_job(self):
        self._scheduler.add_job(self._items_file_downloader.download_items_in_thread, 'interval', minutes=60)
        self._scheduler.start()

        for job in self._scheduler.get_jobs():
            job.modify(next_run_time=datetime.now())


async def start_download_items_job():
    download_products_job = DownloadProductsJob()
    download_products_job.start_job()
