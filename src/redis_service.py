from typing import AsyncGenerator

import redis.asyncio as redis
from loguru import logger
from redis.asyncio import Redis

from src.config import REDIS_HOST, REDIS_PORT

__all__ = [
    "RedisService",
    "get_redis_service"
]


class RedisService:
    _con: Redis
    _REQUESTS_COUNT_EXPIRE_TIME = 10
    _MAX_REQUESTS_COUNT = 250
    """
    Values above are set by API limits. 
    More: https://www.sima-land.ru/api/v3/help/
    """

    async def can_make_request(self) -> bool:
        requests_count = await self._increase_requests_count()
        logger.info(f"Requests count now: {requests_count}")

        if requests_count > self._MAX_REQUESTS_COUNT - 10:
            return False

        if requests_count == 1:
            await self._set_expire_time()
        return True

    async def _increase_requests_count(self) -> int:
        return await self._con.incr("requests_count")

    async def _set_expire_time(self) -> None:
        await self._con.expire("requests_count", self._REQUESTS_COUNT_EXPIRE_TIME)

    async def __aenter__(self) -> "RedisService":
        self._con = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        return self

    async def __aexit__(self, exc_type, *_) -> None:
        if exc_type is not None:
            logger.error("Error while using Redis:\n" + exc_type)

        await self._con.aclose()


async def get_redis_service() -> RedisService:
    async with RedisService() as redis_service:
        return redis_service
