"""
Services para lógica de negócio de chat.

Responsabilidades:
- Criar/buscar conversas
- Salvar mensagens
- Marcar como lidas
- Buscar histórico
"""
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.chat import Conversation, Message, conversation_participants_table
from app.models.user import User
from app.schemas.chat import CreateConversationRequest, MessageResponse, ConversationResponse
from app.core.exceptions import NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)


class ConversationService:
    """Serviço para gerenciar conversas."""

    @staticmethod
    def get_or_create_1v1_conversation(
        db: Session,
        user_id: str,
        other_user_id: str
    ) -> Conversation:
        """
        Obtém ou cria uma conversa 1-a-1.
        Se já existe, retorna a existente.
        """
        # Buscar conversa existente
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.is_group == False,
                Conversation.participants.any(User.id == user_id),
                Conversation.participants.any(User.id == other_user_id),
            )
            .first()
        )
        
        if conversation:
            logger.info(f"Conversa 1v1 encontrada: {conversation.id}")
            return conversation
        
        # Criar nova
        user = db.query(User).filter(User.id == user_id).first()
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        if not user or not other_user:
            raise NotFoundError("Usuário não encontrado")
        
        conversation = Conversation(is_group=False)
        conversation.participants = [user, other_user]
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Nova conversa 1v1 criada: {conversation.id}")
        return conversation

    @staticmethod
    def create_group_conversation(
        db: Session,
        data: CreateConversationRequest,
        creator_id: str
    ) -> Conversation:
        """Cria uma conversa em grupo."""
        # Buscar participantes
        participants = (
            db.query(User)
            .filter(User.id.in_(data.participant_ids))
            .all()
        )
        
        if len(participants) != len(data.participant_ids):
            raise NotFoundError("Um ou mais usuários não encontrados")
        
        # Garantir que criador está nos participantes
        creator = db.query(User).filter(User.id == creator_id).first()
        if creator not in participants:
            participants.append(creator)
        
        # Criar conversa
        conversation = Conversation(
            name=data.name,
            is_group=True,
            participants=participants
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Novo grupo criado: {conversation.id} ({conversation.name})")
        return conversation

    @staticmethod
    def get_user_conversations(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Conversation], int]:
        """Retorna conversas do usuário."""
        query = (
            db.query(Conversation)
            .filter(Conversation.participants.any(User.id == user_id))
            .order_by(Conversation.updated_at.desc())
        )
        
        total = query.count()
        conversations = query.offset(offset).limit(limit).all()
        
        return conversations, total

    @staticmethod
    def get_conversation(db: Session, conversation_id: str, user_id: str) -> Conversation:
        """Obtém conversa se usuário é participante."""
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.participants.any(User.id == user_id),
        ).first()
        
        if not conversation:
            raise ForbiddenError("Você não tem acesso a esta conversa")
        
        return conversation

    @staticmethod
    def is_participant(
        db: Session,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Verifica se usuário é participante da conversa."""
        return (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.participants.any(User.id == user_id),
            )
            .first() is not None
        )


class MessageService:
    """Serviço para gerenciar mensagens."""

    @staticmethod
    def send_message(
        db: Session,
        conversation_id: str,
        sender_id: str,
        content: str
    ) -> Message:
        """Salva mensagem no banco."""
        # Validar conversa e participação
        if not ConversationService.is_participant(db, conversation_id, sender_id):
            raise ForbiddenError("Você não tem permissão para enviar mensagens nesta conversa")
        
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            is_read=False,
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        logger.info(f"Mensagem enviada: {message.id}")
        return message

    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Message], int]:
        """Retorna mensagens da conversa."""
        # Validar participação
        if not ConversationService.is_participant(db, conversation_id, user_id):
            raise ForbiddenError("Você não tem acesso a esta conversa")
        
        query = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
        )
        
        total = query.count()
        messages = query.offset(offset).limit(limit).all()
        
        return list(reversed(messages)), total

    @staticmethod
    def mark_as_read(
        db: Session,
        conversation_id: str,
        user_id: str,
        message_ids: List[str] = None
    ) -> int:
        """Marca mensagens como lidas."""
        # Se não especificar mensagens, marca todas da conversa
        if message_ids:
            updated = (
                db.query(Message)
                .filter(
                    Message.id.in_(message_ids),
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user_id,  # Não marca próprias mensagens
                )
                .update({"is_read": True})
            )
        else:
            # Marcar todas as mensagens que não são do usuário
            updated = (
                db.query(Message)
                .filter(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user_id,
                )
                .update({"is_read": True})
            )
        
        db.commit()
        logger.info(f"Marcadas {updated} mensagens como lidas")
        return updated

    @staticmethod
    def get_unread_count(
        db: Session,
        conversation_id: str,
        user_id: str
    ) -> int:
        """Conta mensagens não lidas."""
        count = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.is_read == False,
                Message.sender_id != user_id,
            )
            .count()
        )
        return count

    @staticmethod
    def get_last_message(db: Session, conversation_id: str) -> Optional[Message]:
        """Obtém última mensagem da conversa."""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .first()
        )
