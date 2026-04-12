import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, Numeric, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_ratings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    premium_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    portfolio: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    categories: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    services: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    availability: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    user: Mapped["User"] = relationship("User", back_populates="professional_profile")

    def __repr__(self) -> str:
        return f"<Professional id={self.id} user_id={self.user_id}>"
