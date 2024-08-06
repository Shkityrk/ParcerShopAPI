from fastapi import FastAPI

from src.config import PROJECT_NAME, DOCS_URL, OPENAPI_URL
from src.catch_exception_middleware import catch_exception_middleware
from src.get_file_router import get_items_file_router

__all__ = [
    "app"
]


app = FastAPI(
    title=PROJECT_NAME,
    docs_url=DOCS_URL,
    openapi_url=OPENAPI_URL,
)

app.middleware("http")(catch_exception_middleware)
app.include_router(get_items_file_router)
