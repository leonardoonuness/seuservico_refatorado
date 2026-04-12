"""
routes/auth.py — Thin controller

As rotas NÃO contêm lógica de negócio.
Toda lógica fica em app/services/auth_service.py e app/services/user_service.py.

ENDPOINTS (compatíveis com o Flutter):
  POST /auth/register
  POST /auth/login
  POST /auth/refresh
  POST /auth/logout   (stateless — orientação ao cliente)
"""
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    AuthResponse,
)
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    responses={
        201: {"description": "Usuário criado com sucesso"},
        409: {"description": "E-mail já cadastrado"},
        422: {"description": "Dados inválidos"},
    },
)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registra um novo usuário e retorna tokens JWT.

    Body esperado do Flutter:
    ```json
    {
      "name": "João Silva",
      "email": "joao@email.com",
      "password": "minhasenha123",
      "type": "client",
      "phone": "98999999999",
      "city": "São Luís"
    }
    ```
    """
    return auth_service.register(db, data)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login com e-mail e senha",
    responses={
        200: {"description": "Login realizado"},
        401: {"description": "Credenciais inválidas"},
        403: {"description": "Conta bloqueada"},
    },
)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, data.email, data.password)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Renovar tokens usando refresh_token",
)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh(db, data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (stateless — instrui o cliente a descartar o token)",
)
def logout():
    """
    Esta API usa JWT stateless.
    O logout é feito descartando os tokens no cliente (app Flutter).
    Para invalidação server-side, implemente blacklist com Redis.
    """
    return
