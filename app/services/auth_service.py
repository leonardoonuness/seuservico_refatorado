"""
auth_service.py

Responsável por operações de autenticação: login, register, refresh.

FLUXO:
  1. register: cria novo usuário (valida email duplicado)
  2. login:    autentica com email/senha (verifica status)
  3. refresh:  renova access_token a partir de refresh_token

SEGURANÇA:
  - Senhas com SHA256 + bcrypt (compatível com qualquer comprimento)
  - Timing attack protection no authenticate()
  - Logs detalhados para auditoria
"""
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)
from app.models.user import User
from app.schemas.user import UserRegisterRequest, AuthResponse
from app.services import user_service

logger = logging.getLogger(__name__)


def _build_auth_response(user: User) -> dict:
    """
    Constrói a resposta de autenticação com tokens e dados do usuário.
    """
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": user,
    }


def register(db: Session, data: UserRegisterRequest) -> dict:
    """
    Registra novo usuário e retorna tokens JWT.
    
    Args:
        db: Sessão de banco de dados
        data: Dados de registro (name, email, password, type, phone, city)
    
    Returns:
        AuthResponse: tokens e dados do usuário
    
    Exceções:
        HTTPException 409: Email duplicado
        HTTPException 422: Dados inválidos (validado por Pydantic antes)
        HTTPException 500: Erro internal (raro)
    """
    try:
        user = user_service.create_user(db, data)
        logger.info(
            "Novo usuário registrado: id=%s email=%s type=%s",
            user.id,
            user.email,
            user.user_type,
        )
        return _build_auth_response(user)
    except HTTPException:
        # Re-raise erros HTTP esperados (409, 422, etc)
        raise
    except Exception as exc:
        logger.exception("Erro inesperado em register: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário. Tente novamente.",
        )


def login(db: Session, email: str, password: str) -> dict:
    """
    Autentica usuário com email e senha.
    
    Args:
        db: Sessão de banco de dados
        email: E-mail do usuário
        password: Senha em texto plano
    
    Returns:
        AuthResponse: tokens e dados do usuário
    
    Exceções:
        HTTPException 401: Email ou senha incorretos
        HTTPException 403: Conta bloqueada ou desativada
    """
    try:
        user = user_service.authenticate(db, email, password)
        logger.info("Login bem-sucedido: id=%s email=%s", user.id, user.email)
        return _build_auth_response(user)
    except HTTPException:
        # Re-raise erros HTTP esperados (401, 403, etc)
        raise
    except Exception as exc:
        logger.exception("Erro inesperado em login: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao autenticar. Tente novamente.",
        )


def refresh(db: Session, refresh_token: str) -> dict:
    """
    Gera novo access_token a partir de um refresh_token válido.
    
    Args:
        db: Sessão de banco de dados
        refresh_token: Token de renovação (JWT)
    
    Returns:
        AuthResponse: novo access_token + mantém refresh_token
    
    Exceções:
        HTTPException 401: Token inválido ou expirado
        HTTPException 404: Usuário não encontrado
    
    Notas:
        Para produção robusta, implemente blacklist de refresh tokens no Redis.
        Isso permitiria invalidar tokens antes da expiração (logout server-side).
    """
    try:
        payload = decode_access_token(refresh_token)
        user_id: str = payload.get("sub", "")
        
        if not user_id:
            logger.warning("Refresh token sem 'sub': token_data=%s", payload)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("Usuário não encontrado em refresh: user_id=%s", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        
        if not user.is_active:
            logger.warning("Tentativa de refresh com usuário desativado: user_id=%s", user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sua conta foi desativada.",
            )
        
        logger.info("Token renovado: user_id=%s", user_id)
        return _build_auth_response(user)
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Erro inesperado em refresh: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao renovar token. Tente novamente.",
        )
