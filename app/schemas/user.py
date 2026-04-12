"""
Schemas Pydantic para User.

COMPATIBILIDADE FLUTTER:
  O app envia exatamente:
  { "name", "email", "password", "type", "phone", "city" }

  O campo "type" do Flutter mapeia para "user_type" no banco.
  Usamos model_validator para fazer essa tradução de forma transparente.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ── Tipos válidos ──────────────────────────────────────────────────────────────
UserType = Literal["client", "professional", "admin"]


# ── Registro ───────────────────────────────────────────────────────────────────
class UserRegisterRequest(BaseModel):
    """
    Exatamente o JSON que o Flutter envia em /auth/register.
    NÃO alterar nomes de campos sem sincronizar com o app.
    """
    name: str = Field(..., min_length=2, max_length=200, examples=["João Silva"])
    email: EmailStr = Field(..., examples=["joao@email.com"])
    password: str = Field(..., min_length=8, examples=["minhasenha123"])
    type: UserType = Field(default="client", examples=["client"])
    phone: str = Field(..., min_length=8, max_length=30, examples=["98999999999"])
    city: str = Field(..., min_length=2, max_length=100, examples=["São Luís"])

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome não pode ser vazio.")
        return v

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, v: str) -> str:
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) < 8:
            raise ValueError("Telefone deve ter ao menos 8 dígitos.")
        return v.strip()

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Cidade não pode ser vazia.")
        return v


# ── Login ──────────────────────────────────────────────────────────────────────
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower().strip()


# ── Refresh token ─────────────────────────────────────────────────────────────
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Troca de senha ─────────────────────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# ── Atualização de perfil ──────────────────────────────────────────────────────
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone: Optional[str] = Field(None, min_length=8, max_length=30)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    fcm_token: Optional[str] = None


# ── Resposta: usuário público (NUNCA inclui senha) ─────────────────────────────
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    # Retornamos "type" para manter compatibilidade com o Flutter
    type: str = Field(alias="user_type")
    city: str
    profile_image: Optional[str] = None
    is_verified: bool
    is_blocked: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,   # aceita tanto "type" quanto "user_type"
    }


# ── Resposta de autenticação ───────────────────────────────────────────────────
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
