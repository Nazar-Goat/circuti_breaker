import json

import pytest

from unittest.mock import MagicMock, AsyncMock, patch

from src.cache import CacheService


class TestCacheService:

    @pytest.mark.asyncio
    async def test_cache_service_get_not_none(self):
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(
            return_value=json.dumps({
                "service_id": 1,
                "healthy": True,
            })
        )

        with patch(
            "src.cache.Redis",
            return_value=mock_redis,
        ):
            cache_service = CacheService()

        result = await cache_service.get_cached_health(1)

        assert result == {
            "service_id": 1,
            "healthy": True,
        }

        mock_redis.get.assert_awaited_once_with("health:1")

    @pytest.mark.asyncio
    async def test_cache_service_get_none(self):
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch(
            "src.cache.Redis",
            return_value=mock_redis,
        ):
            cache_service = CacheService()

        result = await cache_service.get_cached_health(1)

        assert result is None
        mock_redis.get.assert_awaited_once_with("health:1")

