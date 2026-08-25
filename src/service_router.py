from fastapi import  APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.health_check import HealthCheckService
from src.schemas import CreateServiceSchema, OutputServiceSchema, HealthCheckResponse, TripResponse
from src.dependencies import get_db, get_breaker_record, get_health_check
from src.business_layer import  BusinessService


service_router = APIRouter(
    prefix="/circuit_breaker",
    tags=["Auth"],
)

business_service = BusinessService()

@service_router.post(
    "/register-service",
    response_model=OutputServiceSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    register_data: CreateServiceSchema,
    db: AsyncSession = Depends(get_db),
    breaker_record = Depends(get_breaker_record),
):
    return await business_service.register_service(
        register_data=register_data,
        db=db,
        breaker_record=breaker_record,
    )


@service_router.get(
    "/health/{service_id}",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check(
        service_id: int,
        db: AsyncSession = Depends(get_db),
        health_check: HealthCheckService = Depends(get_health_check),
):
    return await business_service.health_check_by_service_id(
        service_id=service_id,
        db=db,
        health_check=health_check,
    )

@service_router.post(
    "/circuit-breaker/{service_id}/trip",
    response_model=TripResponse,
)
async def trip(
        service_id: int,
        db: AsyncSession = Depends(get_db),
        breaker_record = Depends(get_breaker_record)
):
    return await business_service.trip_manually(
        service_id=service_id,
        db=db,
        breaker_record=breaker_record,
    )