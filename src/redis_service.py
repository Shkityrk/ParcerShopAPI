from enum import StrEnum, UNIQUE, verify

import redis.asyncio as redis
from loguru import logger
from redis.asyncio import Redis

from src.config import REDIS_HOST, REDIS_PORT

__all__ = [
    "RedisService",
    "get_redis_service"
]


@verify(UNIQUE)
class RedisKeys(StrEnum):
    REQUESTS_COUNT = "requests_count"
    TOTAL_IDS_COUNT = "total_ids_count"


class RedisService:
    _con: Redis
    _REQUESTS_COUNT_EXPIRE_TIME_SECONDS = 10
    _MAX_REQUESTS_COUNT = 250
    _TOTAL_IDS_COUNT_VALUE_EXPIRE_TIME_SECONDS = 60*60*24  # One day
    """
    Values above are set by API limits. 
    More: https://www.sima-land.ru/api/v3/help/
    """

    async def can_make_request(self) -> bool:
        requests_count = await self._increase_requests_count()

        if requests_count > self._MAX_REQUESTS_COUNT - 10:
            return False

        if requests_count == 1:
            await self._set_expire_time()
        return True

    async def _increase_requests_count(self) -> int:
        return await self._con.incr(RedisKeys.REQUESTS_COUNT)

    async def _set_expire_time(self) -> None:
        await self._con.expire(RedisKeys.REQUESTS_COUNT, self._REQUESTS_COUNT_EXPIRE_TIME_SECONDS)

    async def get_total_ids_count(self) -> int | None:
        total_ids_count = await self._con.get(RedisKeys.TOTAL_IDS_COUNT)
        return total_ids_count if not total_ids_count else int(total_ids_count)

    async def set_total_ids_count(self, total_ids_count: int) -> None:
        await self._con.set(
            RedisKeys.TOTAL_IDS_COUNT,
            total_ids_count,
            ex=self._TOTAL_IDS_COUNT_VALUE_EXPIRE_TIME_SECONDS
        )

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
