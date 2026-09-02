from sqlalchemy.ext.asyncio import AsyncSession

from src.breakers_record import breaker_record, CircuitBreakerRecord
from src.database import async_session_maker
from src.health_check import health_check_service, HealthCheckService


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

def get_health_check() -> HealthCheckService:
    return health_check_service

def get_breaker_record() -> CircuitBreakerRecord:
    return breaker_record