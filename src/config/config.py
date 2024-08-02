from pathlib import Path

from src.config.env import StrEnv, BoolEnv, IntEnv

__all__ = [
    "PROJECT_NAME",
    "DOCS_URL",
    "OPENAPI_URL",
    "LOGGING_PATH",
    "HTTP_HOST",
    "HTTP_PORT",
    "API_TOKEN"
]

PROJECT_NAME: str = StrEnv("PROJECT_NAME")
DOCS_URL: str = StrEnv("DOCS_URL")
OPENAPI_URL: str = StrEnv("OPENAPI_URL")

LOGGING_PATH: Path = Path(StrEnv("LOGGING_PATH"))

HTTP_HOST: str = StrEnv("HTTP_HOST")
HTTP_PORT: int = IntEnv("HTTP_PORT")

API_TOKEN: str = StrEnv("API_TOKEN")
