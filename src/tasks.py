from celery import Celery
from src.config import settings

celery_app = Celery("resilience", broker=settings.CELERY_BROKER_URL)


@celery_app.task(name="log_audit_event")
def log_audit_event(event_type: str, service_id: str, details: dict) -> str:
    import structlog
    logger = structlog.get_logger()
    logger.info("audit_event", event_type=event_type, service_id=service_id, details=details)
    return f"logged {event_type} for {service_id}"