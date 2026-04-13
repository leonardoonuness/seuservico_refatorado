"""
Gerenciador de conexões WebSocket para chat em tempo real.

Responsabilidades:
- Manter registro de conexões ativas
- Enviar mensagens para usuários específicos
- Broadcast para grupos
- Gerenciar desconexões
"""
import logging
import json
from typing import Dict, List, Set, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gerencia conexões WebSocket para chat em tempo real.
    
    Suporta:
    - Conversas 1-a-1
    - Grupos
    - Broadcast
    - Status online/offline
    """
    
    def __init__(self):
        # conversation_id -> {user_id: Set[WebSocket]}
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
        
        # user_id -> bool (status online/offline)
        self.online_users: Set[str] = set()

    async def connect(
        self,
        websocket: WebSocket,
        conversation_id: str,
        user_id: str
    ):
        """Registra uma conexão ativa."""
        await websocket.accept()
        
        # Inicializar conversa se necessário
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = {}
        
        # Adicionar usuário à conversa
        if user_id not in self.active_connections[conversation_id]:
            self.active_connections[conversation_id][user_id] = set()
        
        self.active_connections[conversation_id][user_id].add(websocket)
        
        # Marcar como online
        self.online_users.add(user_id)
        logger.info(f"✅ Usuário {user_id} conectado à conversa {conversation_id}")

    async def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Remove uma conexão."""
        if conversation_id not in self.active_connections:
            return
        
        # Encontrar e remover o WebSocket
        user_to_delete = None
        for user_id, sockets in self.active_connections[conversation_id].items():
            if websocket in sockets:
                sockets.discard(websocket)
                if not sockets:
                    user_to_delete = user_id
                logger.info(f"❌ Usuário {user_id} desconectado da conversa {conversation_id}")
                break
        
        # Remover usuário se não tem mais sockets
        if user_to_delete:
            del self.active_connections[conversation_id][user_to_delete]
        
        # Limpar conversa se vazia
        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]

    async def broadcast_to_conversation(
        self,
        conversation_id: str,
        message: dict,
        exclude_user: Optional[str] = None
    ):
        """Envia mensagem para todos na conversa."""
        if conversation_id not in self.active_connections:
            return
        
        disconnected = []
        for user_id, sockets in self.active_connections[conversation_id].items():
            # Pular usuário se necessário
            if exclude_user and user_id == exclude_user:
                continue
            
            for websocket in sockets:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Erro ao enviar para {user_id}: {e}")
                    disconnected.append((user_id, websocket))
        
        # Limpar conexões com erro
        for user_id, ws in disconnected:
            if conversation_id in self.active_connections:
                if user_id in self.active_connections[conversation_id]:
                    self.active_connections[conversation_id][user_id].discard(ws)


    async def send_personal_message(
        self,
        user_id: str,
        message: dict
    ):
        """Envia mensagem para um usuário específico em todas as suas conexões."""
        logger.warning(f"send_personal_message não implementado para {user_id}")
        # Implementação futura para notificações globais

    def is_user_online(self, user_id: str) -> bool:
        """Verifica se um usuário está online."""
        return user_id in self.online_users

    def get_online_users(self, conversation_id: str) -> List[str]:
        """Retorna usuários online em uma conversa."""
        if conversation_id not in self.active_connections:
            return []
        return list(self.active_connections[conversation_id].keys())

    def get_active_conversations(self) -> List[str]:
        """Retorna IDs de conversas com conexões ativas."""
        return list(self.active_connections.keys())

    def get_conversation_user_count(self, conversation_id: str) -> int:
        """Conta quantos usuários únicos estão conectados."""
        if conversation_id not in self.active_connections:
            return 0
        return len(self.active_connections[conversation_id])

    def __repr__(self) -> str:
        return (
            f"ConnectionManager("
            f"conversations={len(self.active_connections)}, "
            f"online_users={len(self.online_users)}"
            f")"
        )


# Instância global
connection_manager = ConnectionManager()

