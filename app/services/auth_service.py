"""
auth_service.py

Responsável por operações de autenticação: login, register, refresh.
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
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": user,
    }


def register(db: Session, data: UserRegisterRequest) -> dict:
    user = user_service.create_user(db, data)
    logger.info("Novo registro: user_id=%s type=%s", user.id, user.user_type)
    return _build_auth_response(user)


def login(db: Session, email: str, password: str) -> dict:
    user = user_service.authenticate(db, email, password)
    logger.info("Login: user_id=%s", user.id)
    return _build_auth_response(user)


def refresh(db: Session, refresh_token: str) -> dict:
    """
    Gera novo access_token a partir de um refresh_token válido.
    Nota: para produção robusta, implemente blacklist de refresh tokens no Redis.
    """
    payload = decode_access_token(refresh_token)
    # refresh tokens têm type="access" na implementação atual
    # se quiser diferenciar, ajuste create_refresh_token em security.py
    user_id: str = payload.get("sub", "")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )
    return _build_auth_response(user)
