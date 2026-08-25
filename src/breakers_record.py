from src.circuit_breaker import CircuitBreaker


class CircuitBreakerRecord:
    def __init__(self):
        self._breaker_record: [int, CircuitBreaker] = {}

    def get_or_create_breaker(self, service_id: int, failure_threshold = 5, reset_time = 30.0):
        if service_id not in self._breaker_record:
            self._breaker_record[service_id] = CircuitBreaker(
                service_id = service_id,
                failure_threshold = failure_threshold,
                reset_time = reset_time,
            )

        return self._breaker_record[service_id]

breaker_record = CircuitBreakerRecord()