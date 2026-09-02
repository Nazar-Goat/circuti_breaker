import json
from redis.asyncio import Redis

from src.config import settings


class CacheService:
    def __init__(self):
        self.__redis_cache_db = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )   

    async def get_cached_health(self, service_id: int) -> dict:
        raw_data = await self.__redis_cache_db.get(f"health:{service_id}")
        return json.loads(raw_data) if raw_data else None

    async def set_cached_health(self, service_id: int, result_data: dict) -> None:
        await self.__redis_cache_db.set(
            f"health:{service_id}",
            json.dumps(result_data),
            ex=settings.HEALTH_CHECK_EXPIRATION,
        )

cache_service = CacheService()