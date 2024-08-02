from pathlib import Path

from src.config.env import StrEnv, BoolEnv, IntEnv

__all__ = [
    "API_TOKEN",
    "LOGGING_PATH",

]

API_TOKEN: str = StrEnv(StrEnv("API_TOKEN"))

LOGGING_PATH: Path = Path(StrEnv("LOGGING_PATH"))