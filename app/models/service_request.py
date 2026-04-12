import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, Text, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

VALID_STATUSES = ("pending", "accepted", "in_progress", "completed", "cancelled")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    professional_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    category: Mapped[str] = mapped_column(String(200), nullable=False)
    service: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','accepted','in_progress','completed','cancelled')",
            name="ck_service_requests_status",
        ),
        Index("ix_sr_client_status", "client_id", "status"),
        Index("ix_sr_professional_status", "professional_id", "status"),
    )

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])
    professional: Mapped["User"] = relationship("User", foreign_keys=[professional_id])
    review: Mapped["Review"] = relationship("Review", back_populates="service_request", uselist=False)  # type: ignore[name-defined]
