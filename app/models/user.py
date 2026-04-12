"""
Model User — campo user_type como String simples.

POR QUE String em vez de Enum:
  - Enum do SQLAlchemy exige ALTER TYPE no PostgreSQL para adicionar valores
  - String evita migration manual e erros de sincronização em produção
  - Validação do Enum fica no Pydantic (schema), não no banco
"""
import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

logger = logging.getLogger(__name__)

VALID_USER_TYPES = ("client", "professional", "admin")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    # ── Chave primária ────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid, index=True
    )

    # ── Dados pessoais ────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)

    # ── Tipo de usuário (String — sem Enum nativo do SQLAlchemy) ──────────────
    user_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="client", index=True
    )

    # ── Perfil ────────────────────────────────────────────────────────────────
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fcm_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Status ────────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    block_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )

    # ── Constraints no banco ──────────────────────────────────────────────────
    __table_args__ = (
        CheckConstraint(
            "user_type IN ('client', 'professional', 'admin')",
            name="ck_users_user_type",
        ),
        Index("ix_users_email_lower", "email"),
    )

    # ── Relacionamentos ───────────────────────────────────────────────────────
    professional_profile: Mapped["Professional"] = relationship(  # type: ignore[name-defined]
        "Professional", back_populates="user", uselist=False, lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} type={self.user_type}>"
