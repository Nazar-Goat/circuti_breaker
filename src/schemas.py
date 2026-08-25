from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

from src.circuit_breaker import  CircuitBreakerState


class CreateServiceSchema(BaseModel):
    name: str = Field(default=..., max_length=200, description="Service name")
    service_ulr: str = Field(default=..., max_length=500, description="Service URL for health checks")
    failure_threshold: Optional[int] = Field(default=5, description="Service failure threshold")
    reset_time: Optional[float] = Field(default=30.0, description="Service reset time")


class OutputServiceSchema(BaseModel):
    id: int = Field(default=..., description="Service ID")
    name: str = Field(default=..., max_length=200, description="Service name")
    state: CircuitBreakerState
    service_ulr: str = Field(default=..., max_length=500, description="Service URL for health checks")
    created_at: datetime = Field(default=datetime.now(), description="Service creation time")


class HealthCheckResponse(BaseModel):
    service_id: str
    healthy: bool
    state: CircuitBreakerState
    failures_count: int
    checked_at: datetime
    latency_ms: float | None = None
    cached: bool = False


class TripResponse(BaseModel):
    service_id: str
    state: CircuitBreakerState
