import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.dependencies import get_health_check
from src.health_check import HealthCheckService
from src.breakers_record import CircuitBreakerRecord
from src.main import app


@pytest.mark.asyncio
async def test_register_service_creates_record(client):
    response = await client.post(
        "/api/v1/circuit_breaker/register-service",
        json={"name": "Test Service", "service_ulr": "http://example.com/health"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Service"
    assert data["service_url"] == "http://example.com/health"
    assert data["state"] == "CLOSED"


@pytest.mark.asyncio
async def test_health_check_for_unknown_service_returns_404(client):
    response = await client.get("/api/v1/circuit_breaker/health/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_trip_manually_after_register(client):
    register_response = await client.post(
        "/api/v1/circuit_breaker/register-service",
        json={"name": "Svc", "service_ulr": "http://example.com/health"},
    )
    service_id = register_response.json()["id"]

    trip_response = await client.post(f"/api/v1/circuit_breaker/circuit-breaker/{service_id}/trip")

    assert trip_response.status_code == 200
    assert trip_response.json()["state"] == "OPEN"


@pytest.mark.asyncio
async def test_health_check_after_register_with_mocked_httpx(client):
    register_response = await client.post(
        "/api/v1/circuit_breaker/register-service",
        json={"name": "Svc", "service_ulr": "http://example.com/health"},
    )
    service_id = register_response.json()["id"]

    fake_cache = MagicMock()
    fake_cache.get_cached_health = AsyncMock(return_value=None)
    fake_cache.set_cached_health = AsyncMock(return_value=None)
    fake_health_service = HealthCheckService(breaker_record=CircuitBreakerRecord(), cache_service=fake_cache)

    app.dependency_overrides[get_health_check] = lambda: fake_health_service

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_http_client = MagicMock()
    mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
    mock_http_client.get = AsyncMock(return_value=mock_response)

    try:
        with patch("src.health_check.httpx.AsyncClient", return_value=mock_http_client):
            health_response = await client.get(f"/api/v1/circuit_breaker/health/{service_id}")
    finally:
        del app.dependency_overrides[get_health_check]

    assert health_response.status_code == 200
    assert health_response.json()["healthy"] is True