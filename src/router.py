from fastapi import APIRouter
from src.service_router import service_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(service_router, tags=["service"])