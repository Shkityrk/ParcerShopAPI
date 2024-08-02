from fastapi import APIRouter
from fastapi.responses import FileResponse

__all__ = [
    "get_file_router"
]


get_file_router = APIRouter()


@get_file_router.get("/products/file")
async def get_products_file() -> FileResponse:
    return FileResponse(path="files/file.xml", filename="Список товаров.xml")
