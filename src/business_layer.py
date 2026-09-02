from fastapi import  HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.schemas import CreateServiceSchema, OutputServiceSchema, HealthCheckResponse, TripResponse
from src.breakers_record import CircuitBreakerRecord
from src.health_check import HealthCheckService
from src.models import Service


class BusinessService:

    @staticmethod
    async def register_service(
            register_data: CreateServiceSchema,
            db: AsyncSession ,
            breaker_record: CircuitBreakerRecord,
    ):
        service = Service(
            name=register_data.name,
            service_url=str(register_data.service_ulr),
            failure_threshold=register_data.failure_threshold,
            reset_time=register_data.reset_time,
        )
        db.add(service)
        await db.commit()
        await db.refresh(service)

        service_breaker = breaker_record.get_or_create_breaker(
            service_id = service.id,
            failure_threshold = service.failure_threshold,
            reset_time = service.reset_time,
        )

        return OutputServiceSchema(
            id=service.id,
            name=service.name,
            state=service_breaker.state.value,
            service_url=service.service_url,
            created_at=service.created_at,
        )

    @staticmethod
    async def health_check_by_service_id(
            service_id: int,
            db: AsyncSession,
            health_check: HealthCheckService,
    ):
        query = await  db.execute(select(Service).where(Service.id == service_id))
        service = query.scalar_one_or_none()

        if service is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

        health_check_result = await health_check.check_service_health(
            service_id = service_id,
            health_check_url=service.service_url,
            failure_threshold=service.failure_threshold,
            reset_time=service.reset_time,
        )

        return HealthCheckResponse(**health_check_result)

    @staticmethod
    async def trip_manually(
            service_id: int,
            db: AsyncSession,
            breaker_record: CircuitBreakerRecord,
    ):
        query = await db.execute(select(Service).where(Service.id == service_id))
        service = query.scalar_one_or_none()

        if service is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

        breaker = breaker_record.get_or_create_breaker(
            service_id = service.id,
            failure_threshold = service.failure_threshold,
            reset_time = service.reset_time,
        )

        breaker.set_open_manually()

        return TripResponse(
            service_id = service.id,
            state = breaker.state.value
        )