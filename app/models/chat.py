"""
Models para o sistema de chat.

Tabelas:
- Conversation: Conversas entre usuários
- ConversationParticipant: Participantes de uma conversa
- Message: Mensagens da conversa
"""
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Tabela de Associação (muitos-para-muitos) ─────────────────────────────────

conversation_participants_table = Table(
    "conversation_participants",
    Base.metadata,
    Column("conversation_id", String(36), ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


# ── Modelo: Conversa ──────────────────────────────────────────────────────────

class Conversation(Base):
    """
    Representa uma conversa entre 2 ou mais usuários.
    Pode ser um chat 1-a-1 ou um grupo.
    """
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid, index=True)
    
    # Nome da conversa (para grupos; None para 1-a-1)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Descrição (para grupos)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Indicador de conversa em grupo
    is_group: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    
    # Relacionamentos
    participants: Mapped[List["User"]] = relationship(
        "User",
        secondary=conversation_participants_table,
        lazy="select",
        cascade="all",
    )
    
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} name={self.name or 'DM'} participants={len(self.participants)}>"


# ── Modelo: Mensagem ─────────────────────────────────────────────────────────

class Message(Base):
    """
    Representa uma mensagem em uma conversa.
    Inclui metadados como leitura, reações, etc.
    """
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid, index=True)
    
    # Referência à conversa
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Quem enviou a mensagem
    sender_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Conteúdo da mensagem
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Se foi lida
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    
    # Relacionamentos
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        lazy="select",
    )

    def __repr__(self) -> str:
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message id={self.id} sender_id={self.sender_id} content={content_preview}>"
