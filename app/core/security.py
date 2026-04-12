"""
Funções de segurança centralizadas:
  - hash / verificação de senha com SHA256 + bcrypt (compatível com senhas longas)
  - criação / decodificação de tokens JWT
"""
import logging
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Senha ─────────────────────────────────────────────────────────────────────
# ESTRATÉGIA: SHA256 (pré-hash) + bcrypt (hash final)
# Razão: bcrypt tem limite de 72 bytes. SHA256 reduz qualquer senha para 64 bytes hexadecimais.
# Benefí­cio: compatível com senhas arbitrariamente longas sem perder segurança.

def _pre_hash_sha256(plain: str) -> str:
    """
    Pré-hash com SHA256. Reduz qualquer senha para 64 bytes (hexadecimal).
    Esta string é então passada ao bcrypt, garantindo sempre < 72 bytes.
    """
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def hash_password(plain: str) -> str:
    """
    Cria hash seguro de senha com SHA256 + bcrypt.
    
    Processo:
      1. plain → SHA256 (reduz para 64 bytes)
      2. pre_hash → bcrypt (hash final armazenado no DB)
    
    Args:
        plain: Senha em texto plano (qualquer comprimento)
    
    Returns:
        Hash bcrypt (começa com $2b$...)
    
    Exceções:
        ValueError: Se plain estiver vazio
    """
    if not plain:
        raise ValueError("Senha não pode estar vazia")
    
    pre_hash = _pre_hash_sha256(plain)
    return _pwd_context.hash(pre_hash)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifica senha contra hash usando SHA256 + bcrypt.
    
    Processo:
      1. plain → SHA256 (mesmo que em hash_password)
      2. pre_hash → bcrypt.verify(pre_hash, hashed)
    
    Args:
        plain: Senha em texto plano
        hashed: Hash armazenado no banco
    
    Returns:
        True se senha está correta, False caso contrário
    
    Notas:
        - Sempre executa bcrypt.verify() mesmo se plain estiver vazio (timing attack protection)
        - Retorna False para qualquer erro (não revela diferença entre plain inválido e hash inválido)
    """
    try:
        if not plain:
            # Ainda executa verify com hash dummy para evitar timing attacks
            return _pwd_context.verify("", hashed)
        
        pre_hash = _pre_hash_sha256(plain)
        return _pwd_context.verify(pre_hash, hashed)
    except Exception:
        # Qualquer erro (hash corrompido, etc) retorna False sem revelar detalhes
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────

def _make_token(subject: Any, token_type: str, expire: timedelta) -> str:
    payload = {
        "sub": str(subject),
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: Any) -> str:
    return _make_token(
        subject,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: Any) -> str:
    return _make_token(
        subject,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida um access token.
    Lança HTTP 401 para qualquer problema.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            raise JWTError("tipo inválido")
        return payload
    except JWTError as exc:
        logger.warning("Token inválido: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
