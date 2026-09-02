from prometheus_client import Counter, Histogram, Gauge

health_check_requests_total = Counter(
    "health_check_requests_total", "Total health check requests", ["service_id", "result"]
)

health_check_latency_seconds = Histogram(
    "health_check_latency_seconds", "Health check latency in seconds", ["service_id"]
)

circuit_breaker_state = Gauge(
    "circuit_breaker_state", "Current circuit breaker state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)", ["service_id"]
)

_STATE_TO_VALUE = {"CLOSED": 0, "HALF_OPEN": 1, "OPEN": 2}


def record_health_check_metrics(service_id: str, healthy: bool, latency_ms: float | None, state: str) -> None:
    health_check_requests_total.labels(service_id=service_id, result="success" if healthy else "failure").inc()
    if latency_ms is not None:
        health_check_latency_seconds.labels(service_id=service_id).observe(latency_ms / 1000)
    circuit_breaker_state.labels(service_id=service_id).set(_STATE_TO_VALUE.get(state, 0))