from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.utils import ItemsFileDownloader, get_items_file_downloader

__all__ = [
    "get_items_file_router"
]


get_items_file_router = APIRouter()


@get_items_file_router.get("/items/file")
async def get_items_file() -> FileResponse:
    return FileResponse(path="files/items.xml", filename="items.xml")
