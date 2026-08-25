import time
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException

from src.breakers_record import CircuitBreakerRecord
from src.cache import CacheService
from src.service_router import health_check


class HealthCheckService:
    def __init__(self, breaker_record: CircuitBreakerRecord, cache_service: CacheService):
        self._breaker_record = breaker_record
        self._cache_service = cache_service

    async def check_service_health(
            self,
            service_id: int,
            health_check_url: str,
            failure_threshold: int,
            reset_time: float
    ):
        breaker = self._breaker_record.get_or_create_breaker(
            service_id=service_id,
            failure_threshold=failure_threshold,
            reset_time=reset_time
        )

        cached = await self._cache_service.get_cached_health(service_id)
        if cached is not None:
            cached["cached"] = True
            return cached

        if not breaker.allow_request():
            result = {
                "service_id": service_id,
                "healthy": False,
                "state": breaker.state.value,
                "failures_count": breaker.failures_count,
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "latency_ms": None,
                "cached": False
            }

            return result

        start = time.monotonic()
        healthy = False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(health_check_url)
                healthy = response.status_code < 400
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

        latency_ms = (time.monotonic() - start) * 1000

        if healthy:
            breaker.record_success()
        else:
            breaker.record_failure()

        result = {
            "service_id": service_id,
            "healthy": healthy,
            "state": breaker.state.value,
            "failures_count": breaker.failures_count,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": round(latency_ms, 2),
            "cached": False
        }

        await self._cache_service.set_cached_health(service_id, result)

        return result

health_check_service = HealthCheckService()