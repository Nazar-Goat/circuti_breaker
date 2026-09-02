import pytest

from src.circuit_breaker import  CircuitBreaker, CircuitBreakerState


class TestCircuitBreaker:

    @pytest.fixture(scope="function")
    def get_breaker_obj(self):
        breaker = CircuitBreaker(
            service_id=1,
            failure_threshold=5,
            reset_time=30.0,
        )
        return breaker

    def test_initial_state(self, get_breaker_obj):
        assert get_breaker_obj.state == CircuitBreakerState.CLOSED
        assert get_breaker_obj.failures_count == 0
        assert get_breaker_obj.opened_at is None

    @pytest.mark.parametrize(
        "state",
        [
            CircuitBreakerState.CLOSED,
            CircuitBreakerState.HALF_OPEN,
        ]
    )
    def test_allow_request_true(self, state, get_breaker_obj):
        get_breaker_obj.state = state
        assert get_breaker_obj.allow_request() == True

    def test_allow_request_false(self, get_breaker_obj):
        get_breaker_obj.state = CircuitBreakerState.OPEN
        assert get_breaker_obj.allow_request() == False

    def test_record_success(self, get_breaker_obj):
        get_breaker_obj.state = CircuitBreakerState.OPEN
        get_breaker_obj.opened_at = 123
        get_breaker_obj.failures_count = 3

        get_breaker_obj.record_success()

        assert get_breaker_obj.state == CircuitBreakerState.CLOSED
        assert get_breaker_obj.failures_count == 0
        assert get_breaker_obj.opened_at is None

    def test_record_failure(self, get_breaker_obj):
        get_breaker_obj.failures_count = 3

        get_breaker_obj.record_failure()
        assert get_breaker_obj.state == CircuitBreakerState.CLOSED

        get_breaker_obj.record_failure()
        assert get_breaker_obj.state == CircuitBreakerState.OPEN

    def test_set_open_manually(self, get_breaker_obj):
        get_breaker_obj.failures_count = 3

        get_breaker_obj.set_open_manually()

        assert get_breaker_obj.state == CircuitBreakerState.OPEN
        assert get_breaker_obj.opened_at is not None
        assert get_breaker_obj.failures_count == 0