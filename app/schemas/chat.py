"""
Schemas para chat e mensagens.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────────────────────

class CreateConversationRequest(BaseModel):
    """Criar uma conversa 1-a-1 ou grupo."""
    participant_ids: List[str] = Field(..., min_items=1, description="IDs dos participantes")
    name: Optional[str] = Field(None, max_length=255, description="Nome (para grupos)")
    is_group: bool = Field(False, description="Se é um grupo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "participant_ids": ["user-2", "user-3"],
                "name": None,
                "is_group": False
            }
        }


class SendMessageRequest(BaseModel):
    """Enviar mensagem via WebSocket."""
    conversation_id: str = Field(..., description="ID da conversa")
    content: str = Field(..., min_length=1, max_length=10000, description="Conteúdo da mensagem")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv-123",
                "content": "Olá! Tudo bem?"
            }
        }


class MarkAsReadRequest(BaseModel):
    """Marcar mensagens como lidas."""
    conversation_id: str
    message_ids: List[str]


# ── Responses ─────────────────────────────────────────────────────────────────

class UserInConversation(BaseModel):
    """Usuário dentro de uma conversa."""
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Resposta de uma mensagem."""
    id: str = Field(description="ID único da mensagem")
    conversation_id: str = Field(description="ID da conversa")
    sender_id: str = Field(description="ID de quem enviou")
    sender: Optional[UserInConversation] = Field(None, description="Dados do remetente")
    content: str = Field(description="Conteúdo da mensagem")
    is_read: bool = Field(description="Se foi lida")
    created_at: datetime = Field(description="Quando foi enviada")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "msg-123",
                "conversation_id": "conv-456",
                "sender_id": "user-789",
                "sender": {
                    "id": "user-789",
                    "name": "João Silva",
                    "email": "joao@email.com"
                },
                "content": "Olá! Como vai?",
                "is_read": False,
                "created_at": "2026-04-12T10:30:00Z"
            }
        }


class ConversationResponse(BaseModel):
    """Resposta de uma conversa."""
    id: str = Field(description="ID único")
    name: Optional[str] = Field(None, description="Nome (grupos)")
    is_group: bool = Field(description="Se é grupo")
    participants: List[UserInConversation] = Field(description="Participantes")
    created_at: datetime = Field(description="Quando foi criada")
    updated_at: datetime = Field(description="Última atualização")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "conv-123",
                "name": None,
                "is_group": False,
                "participants": [
                    {"id": "user-1", "name": "João", "email": "joao@email.com"},
                    {"id": "user-2", "name": "Maria", "email": "maria@email.com"}
                ],
                "created_at": "2026-04-12T10:00:00Z",
                "updated_at": "2026-04-12T10:30:00Z"
            }
        }


class ConversationDetailResponse(ConversationResponse):
    """Conversa com últimas mensagens."""
    last_message: Optional[MessageResponse] = Field(None, description="Última mensagem")
    unread_count: int = Field(0, description="Contagem de não lidas")


# ── WebSocket Messages ────────────────────────────────────────────────────────

class WebSocketMessageContent(BaseModel):
    """Conteúdo de uma mensagem via WebSocket."""
    conversation_id: str
    sender_id: str
    sender_name: str
    content: str
    timestamp: datetime
    message_id: str
    is_read: bool = False


class WebSocketTypingIndicator(BaseModel):
    """Indicador de "digitando..."."""
    conversation_id: str
    user_id: str
    user_name: str
    is_typing: bool


class WebSocketStatusUpdate(BaseModel):
    """Atualização de status (online/offline)."""
    user_id: str
    user_name: str
    is_online: bool
    timestamp: datetime


class WebSocketResponse(BaseModel):
    """Resposta genérica do WebSocket."""
    type: str = Field(..., description="Tipo: 'message', 'typing', 'status', 'error'")
    data: dict = Field(..., description="Dados da mensagem")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "message",
                "data": {
                    "conversation_id": "conv-123",
                    "sender_id": "user-1",
                    "sender_name": "João",
                    "content": "Olá!",
                    "timestamp": "2026-04-12T10:30:00Z",
                    "message_id": "msg-123",
                    "is_read": False
                }
            }
        }
