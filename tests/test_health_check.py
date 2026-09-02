import httpx
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from fastapi import HTTPException

from src.health_check import HealthCheckService
from src.circuit_breaker import CircuitBreakerState


class TestHealthCheckService:

    @pytest.fixture()
    def mocks(self):
        breaker = MagicMock()
        breaker.state = CircuitBreakerState.CLOSED
        breaker.failures_count = 0
        breaker.allow_request.return_value = True

        breaker_record = MagicMock()
        breaker_record.get_or_create_breaker.return_value = breaker

        cache_service = MagicMock()
        cache_service.get_cached_health = AsyncMock(return_value=None)
        cache_service.set_cached_health = AsyncMock()

        return breaker_record, breaker, cache_service

    @pytest.fixture()
    def health_check_service(self, mocks):
        breaker_record, breaker, cache_service = mocks

        return HealthCheckService(
            breaker_record,
            cache_service,
        )

    @pytest.mark.asyncio
    async def test_check_service_health_return_cached(
        self,
        health_check_service,
        mocks,
    ):
        breaker_record, breaker, cache_service = mocks

        cache_service.get_cached_health.return_value = {
            "service_id": 1,
            "healthy": True,
            "state": CircuitBreakerState.CLOSED.value,
            "failures_count": 0,
            "checked_at": 123,
            "latency_ms": 50,
            "cached": False,
        }

        result = await health_check_service.check_service_health(
            service_id=1,
            health_check_url="http://example.com",
            failure_threshold=3,
            reset_time=30.0,
        )

        assert result["service_id"] == 1
        assert result["healthy"] is True
        assert result["state"] == CircuitBreakerState.CLOSED.value
        assert result["cached"] is True

        breaker.allow_request.assert_not_called()
        breaker.record_success.assert_not_called()
        breaker.record_failure.assert_not_called()

        cache_service.set_cached_health.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_check_service_health_breaker_open(
        self,
        health_check_service,
        mocks,
    ):
        breaker_record, breaker, cache_service = mocks

        breaker.state = CircuitBreakerState.OPEN
        breaker.failures_count = 3
        breaker.allow_request.return_value = False

        result = await health_check_service.check_service_health(
            service_id=1,
            health_check_url="http://example.com",
            failure_threshold=3,
            reset_time=30.0,
        )

        assert result["service_id"] == 1
        assert result["healthy"] is False
        assert result["state"] == CircuitBreakerState.OPEN.value
        assert result["failures_count"] == 3
        assert result["latency_ms"] is None
        assert result["cached"] is False

        breaker.allow_request.assert_called_once()

        breaker.record_success.assert_not_called()
        breaker.record_failure.assert_not_called()

        cache_service.set_cached_health.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_check_service_health_success(
        self,
        health_check_service,
        mocks,
    ):
        breaker_record, breaker, cache_service = mocks

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch(
            "src.health_check.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await health_check_service.check_service_health(
                service_id=1,
                health_check_url="http://example.com",
                failure_threshold=3,
                reset_time=30.0,
            )

        assert result["service_id"] == 1
        assert result["healthy"] is True
        assert result["cached"] is False

        breaker.allow_request.assert_called_once()
        breaker.record_success.assert_called_once()
        breaker.record_failure.assert_not_called()

        mock_client.get.assert_awaited_once_with(
            "http://example.com"
        )

        cache_service.set_cached_health.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_check_service_health_failure(
            self,
            health_check_service,
            mocks,
    ):
        breaker_record, breaker, cache_service = mocks

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch(
                "src.health_check.httpx.AsyncClient",
                return_value=mock_client,
        ):
            result = await health_check_service.check_service_health(
                service_id=1,
                health_check_url="http://example.com",
                failure_threshold=3,
                reset_time=30.0,
            )

        assert result["service_id"] == 1
        assert result["healthy"] is False
        assert result["cached"] is False

        breaker.allow_request.assert_called_once()
        breaker.record_failure.assert_called_once()
        breaker.record_success.assert_not_called()

        mock_client.get.assert_awaited_once_with(
            "http://example.com"
        )

        cache_service.set_cached_health.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_check_service_health_http_error(
            self,
            health_check_service,
            mocks,
    ):
        breaker_record, breaker, cache_service = mocks

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)

        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )

        with patch(
                "src.health_check.httpx.AsyncClient",
                return_value=mock_client,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await health_check_service.check_service_health(
                    service_id=1,
                    health_check_url="http://example.com",
                    failure_threshold=3,
                    reset_time=30.0,
                )

        assert exc_info.value.status_code == 503
        assert "Health check failed" in exc_info.value.detail

        breaker.allow_request.assert_called_once()
        breaker.record_success.assert_not_called()
        breaker.record_failure.assert_not_called()

        cache_service.set_cached_health.assert_not_awaited()
