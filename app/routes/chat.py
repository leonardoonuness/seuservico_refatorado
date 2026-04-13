"""
Rotas para chat em tempo real.

Endpoints:
- GET  /conversations          - Listar conversas do usuário
- POST /conversations          - Criar nova conversa
- GET  /conversations/{id}     - Detalhes da conversa
- GET  /conversations/{id}/messages - Mensagens
- POST /messages               - Enviar mensagem
- PATCH /messages/read         - Marcar como lido
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, WebSocket, WebSocketDisconnect, status
import logging
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.responses import success_response, list_response, error_response
from app.core.websocket import connection_manager
from app.core.exceptions import NotFoundError, ForbiddenError, AppException
from app.models.user import User
from app.models.chat import Message
from app.schemas.chat import (
    CreateConversationRequest,
    SendMessageRequest,
    MarkAsReadRequest,
    MessageResponse,
    ConversationResponse,
    ConversationDetailResponse,
    WebSocketResponse,
)
from app.services.chat_service import ConversationService, MessageService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["chat"])


# ── REST Endpoints ────────────────────────────────────────────────────────────


@router.get("/conversations", response_model=dict)
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Lista conversas do usuário com paginação.
    
    Cada conversa retorna:
    - Participantes
    - Última mensagem
    - Contador de não lidas
    - Timestamp de atualização
    """
    try:
        conversations, total = ConversationService.get_user_conversations(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
        
        # Construir response com detalhes
        data = []
        for conv in conversations:
            last_msg = MessageService.get_last_message(db, conv.id)
            unread = MessageService.get_unread_count(db, conv.id, current_user.id)
            
            conv_data = {
                "id": conv.id,
                "name": conv.name,
                "is_group": conv.is_group,
                "participants": [
                    {"id": p.id, "name": p.name, "profile_image": p.profile_image}
                    for p in conv.participants
                ],
                "last_message": {
                    "id": last_msg.id,
                    "content": last_msg.content,
                    "sender": {"id": last_msg.sender.id, "name": last_msg.sender.name},
                    "created_at": last_msg.created_at.isoformat() if last_msg else None,
                } if last_msg else None,
                "unread_count": unread,
                "updated_at": conv.updated_at.isoformat(),
            }
            data.append(conv_data)
        
        return {
            **list_response(data, "Conversas listadas com sucesso"),
            "total": total,
        }
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar conversas")


@router.post("/conversations", response_model=dict)
async def create_conversation(
    data: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cria nova conversa (1-a-1 ou grupo).
    
    Body:
    - participant_ids (List[str]): IDs dos participantes
    - is_group (bool): Se é grupo
    - name (str, optional): Nome do grupo
    """
    try:
        if not data.is_group and len(data.participant_ids) == 1:
            # Conversa 1-a-1
            other_user_id = data.participant_ids[0]
            conversation = ConversationService.get_or_create_1v1_conversation(
                db=db,
                user_id=current_user.id,
                other_user_id=other_user_id,
            )
        else:
            # Grupo
            conversation = ConversationService.create_group_conversation(
                db=db,
                data=data,
                creator_id=current_user.id,
            )
        
        conv_response = {
            "id": conversation.id,
            "name": conversation.name,
            "is_group": conversation.is_group,
            "participants": [
                {"id": p.id, "name": p.full_name}
                for p in conversation.participants
            ],
            "created_at": conversation.created_at.isoformat(),
        }
        
        return success_response(conv_response, "Conversa criada/obtida com sucesso")
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Erro ao criar conversa: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao criar conversa")


@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém detalhes da conversa se usuário é participante."""
    try:
        conversation = ConversationService.get_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
        
        conv_data = {
            "id": conversation.id,
            "name": conversation.name,
            "is_group": conversation.is_group,
            "participants": [
                {"id": p.id, "name": p.name, "profile_image": p.profile_image}
                for p in conversation.participants
            ],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
        
        return success_response(conv_data, "Conversa obtida com sucesso")
    
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Erro ao buscar conversa: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar conversa")


@router.get("/conversations/{conversation_id}/messages", response_model=dict)
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Obtém mensagens da conversa com paginação.
    
    Retorna em ordem cronológica crescente (mais recentes por último).
    """
    try:
        messages, total = MessageService.get_conversation_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
        
        data = [
            {
                "id": msg.id,
                "content": msg.content,
                "sender": {
                    "id": msg.sender.id,
                    "name": msg.sender.name,
                    "profile_image": msg.sender.profile_image,
                },
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]
        
        return {
            **list_response(data, "Mensagens obtidas com sucesso"),
            "total": total,
        }
    
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar mensagens")


@router.post("/messages", response_model=dict)
async def send_message(
    data: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Envia mensagem via REST (por compatibilidade).
    
    Nota: Preferir WebSocket para tempo real.
    """
    try:
        message = MessageService.send_message(
            db=db,
            conversation_id=data.conversation_id,
            sender_id=current_user.id,
            content=data.content,
        )
        
        msg_data = {
            "id": message.id,
            "content": message.content,
            "sender": {"id": message.sender.id, "name": message.sender.name},
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat(),
        }
        
        # Notificar via WebSocket se disponível
        await connection_manager.broadcast_to_conversation(
            conversation_id=data.conversation_id,
            message={
                "type": "message",
                "data": msg_data,
            }
        )
        
        return success_response(msg_data, "Mensagem enviada com sucesso")
    
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao enviar mensagem")


@router.patch("/messages/read", response_model=dict)
async def mark_as_read(
    data: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marca mensagens como lidas.
    
    Se message_ids vazio, marca todas da conversa.
    """
    try:
        count = MessageService.mark_as_read(
            db=db,
            conversation_id=data.conversation_id,
            user_id=current_user.id,
            message_ids=data.message_ids,
        )
        
        # Notificar via WebSocket
        await connection_manager.broadcast_to_conversation(
            conversation_id=data.conversation_id,
            message={
                "type": "messages_read",
                "user_id": current_user.id,
                "count": count,
            }
        )
        
        return success_response({"count": count}, "Mensagens marcadas como lidas")
    
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except Exception as e:
        logger.error(f"Erro ao marcar como lido: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao marcar como lido")


# ── WebSocket Endpoint ────────────────────────────────────────────────────────


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket para chat em tempo real.
    
    Autenticação: ?token=JWT_TOKEN&user_id=USER_ID&conversation_id=CONV_ID
    
    Mensagens esperadas:
    {
        "type": "message" | "typing" | "stop_typing",
        "data": {...}
    }
    """
    # Extrair parâmetros
    token = websocket.query_params.get("token")
    conversation_id = websocket.query_params.get("conversation_id")
    user_id = websocket.query_params.get("user_id")
    
    if not conversation_id or not user_id:
        try:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        except:
            pass
        return
    
    try:
        # TODO: Validar JWT token em produção
        # from app.core.security import verify_token
        # verify_token(token)
        
        # Conectar
        await connection_manager.connect(websocket, conversation_id, user_id)
        logger.info(f"✅ Usuário {user_id} conectado em {conversation_id}")
        
        # Notificar outros que usuário entrou online
        await connection_manager.broadcast_to_conversation(
            conversation_id=conversation_id,
            message={
                "type": "user_online",
                "user_id": user_id,
                "online_users": connection_manager.get_online_users(conversation_id),
            },
            exclude_user=user_id,
        )
        
        # Loop de processamento
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                msg_type = message.get("type")
                msg_data = message.get("data", {})
                
                if msg_type == "message":
                    # Salvar e broadcast
                    from app.db.session import SessionLocal
                    db = SessionLocal()
                    try:
                        saved_msg = MessageService.send_message(
                            db=db,
                            conversation_id=conversation_id,
                            sender_id=user_id,
                            content=msg_data.get("content"),
                        )
                        
                        # Broadcast para todos na conversa
                        await connection_manager.broadcast_to_conversation(
                            conversation_id=conversation_id,
                            message={
                                "type": "message",
                                "id": saved_msg.id,
                                "user_id": user_id,
                                "content": saved_msg.content,
                                "timestamp": saved_msg.created_at.isoformat(),
                            }
                        )
                    finally:
                        db.close()
                
                elif msg_type == "typing":
                    # Notificar que está digitando
                    await connection_manager.broadcast_to_conversation(
                        conversation_id=conversation_id,
                        message={
                            "type": "typing",
                            "user_id": user_id,
                        },
                        exclude_user=user_id,
                    )
                
                elif msg_type == "stop_typing":
                    # Parou de digitar
                    await connection_manager.broadcast_to_conversation(
                        conversation_id=conversation_id,
                        message={
                            "type": "stop_typing",
                            "user_id": user_id,
                        },
                        exclude_user=user_id,
                    )
                
                else:
                    logger.warning(f"Tipo de mensagem desconhecido: {msg_type}")
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "JSON inválido",
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {str(e)}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Erro ao processar mensagem",
                    })
                except:
                    break
    
    except Exception as e:
        logger.error(f"Erro no WebSocket: {str(e)}")
    
    finally:
        await connection_manager.disconnect(websocket, conversation_id)
        
        # Notificar que desconectou
        await connection_manager.broadcast_to_conversation(
            conversation_id=conversation_id,
            message={
                "type": "user_offline",
                "user_id": user_id,
                "online_users": connection_manager.get_online_users(conversation_id),
            },
        )
        logger.info(f"❌ Usuário {user_id} desconectado de {conversation_id}")
