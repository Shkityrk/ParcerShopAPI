from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.utils import ProductsFileDownloader, get_products_file_downloader

__all__ = [
    "get_file_router"
]


get_file_router = APIRouter()


@get_file_router.get("/products/file")
async def get_products_file() -> FileResponse:
    return FileResponse(path="files/products.txt", filename="Список товаров.txt")
