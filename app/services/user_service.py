"""
user_service.py

Lógica de negócio para usuários.
As rotas (thin controllers) chamam estas funções — nunca acessam o banco diretamente.

TRATAMENTO DE ERROS:
  - IntegrityError  → 409 Conflict (email duplicado)
  - Erros previsíveis → HTTPException com código correto
  - Erros inesperados → log + re-raise (vira 500 com mensagem genérica)
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserRegisterRequest, UpdateProfileRequest
from app.core.security import hash_password, verify_password

logger = logging.getLogger(__name__)


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def get_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, data: UserRegisterRequest) -> User:
    """
    Cria novo usuário.
    Retorna 409 se o e-mail já existir.
    """
    # Verificação antecipada (mais legível que pegar IntegrityError)
    if get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado.",
        )

    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        phone=data.phone.strip(),
        city=data.city.strip(),
        user_type=data.type,  # Flutter envia "type", mapeamos para "user_type"
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
        logger.info("Usuário criado: id=%s email=%s", user.id, user.email)
        return user
    except IntegrityError:
        db.rollback()
        logger.warning("IntegrityError ao criar usuário com email=%s", data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado.",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Erro inesperado ao criar usuário: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


def authenticate(db: Session, email: str, password: str) -> User:
    """
    Valida credenciais.
    Retorna 401 para qualquer problema (não revela se o email existe).
    """
    user = get_by_email(db, email)

    # Sempre roda verify_password mesmo se user=None para evitar timing attack
    dummy_hash = "$2b$12$" + "x" * 53
    password_ok = verify_password(password, user.hashed_password if user else dummy_hash)

    if not user or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )
    if user.is_blocked:
        reason = user.block_reason or "sem motivo informado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Conta bloqueada: {reason}.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )
    return user


def update_profile(db: Session, user: User, data: UpdateProfileRequest) -> User:
    changed = False
    for field, value in data.model_dump(exclude_none=True).items():
        if value is not None:
            setattr(user, field, value)
            changed = True

    if changed:
        try:
            db.commit()
            db.refresh(user)
            logger.info("Perfil atualizado: user_id=%s", user.id)
        except Exception as exc:
            db.rollback()
            logger.exception("Erro ao atualizar perfil user_id=%s: %s", user.id, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar alterações.",
            )
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta.",
        )
    user.hashed_password = hash_password(new_password)
    try:
        db.commit()
        logger.info("Senha alterada: user_id=%s", user.id)
    except Exception as exc:
        db.rollback()
        logger.exception("Erro ao alterar senha user_id=%s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar nova senha.",
        )
