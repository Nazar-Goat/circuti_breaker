import time
from enum import Enum


class CircuitBreakerState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, service_id: int, failure_threshold: int, reset_time: str):
        self.service_id = service_id
        self.failure_threshold = failure_threshold
        self.reset_time = reset_time

        self.failures_count = 0
        self.opened_at = None
        self.state = CircuitBreakerState.CLOSED


    def allow_request(self):
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:

            if self.opened_at is not  None and (time.monotonic() - self.opened_at) > self.reset_time:
                self.state = CircuitBreakerState.HALF_OPEN
                return True

            return False

    def record_success(self):
        self.failures_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.opened_at = None

    def record_failure(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._set_open_state()

        self.failures_count += 1

        if self.failures_count >= self.failure_threshold:
            self._set_open_state()

    def set_open_manually(self):
        self._set_open_state()

    def _set_open_state(self):
        self.state = CircuitBreakerState.OPEN
        self.opened_at = time.monotonic()
        self.failures_count = 0