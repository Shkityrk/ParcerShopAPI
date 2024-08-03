from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.utils import ItemsFileDownloader, get_items_file_downloader

__all__ = [
    "get_file_router"
]


get_file_router = APIRouter()


@get_file_router.get("/products/file")
async def get_items_file() -> FileResponse:
    return FileResponse(path="files/items.json", filename="Список товаров.json")
