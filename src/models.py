from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Service(Base):
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    service_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    failure_threshold: Mapped[int] = mapped_column(Integer, default=5)
    reset_time: Mapped[float] = mapped_column(Float, default=30.0)