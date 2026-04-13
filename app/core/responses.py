"""
core/responses.py

Modelos e funções para padronizar respostas da API.
"""
from typing import Any, Optional, List
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Resposta bem-sucedida."""
    success: bool = Field(default=True)
    data: Any = Field(description="Dados retornados")
    message: Optional[str] = Field(default="Operação realizada com sucesso")


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""
    success: bool = Field(default=False)
    message: str = Field(description="Mensagem para o usuário")
    error: str = Field(description="Código técnico do erro")
    code: int = Field(description="HTTP Status code")
    details: Optional[dict[str, Any]] = Field(default=None)


class ListResponse(BaseModel):
    """Resposta com lista."""
    success: bool = Field(default=True)
    data: List[Any] = Field(description="Lista de itens")
    count: int = Field(description="Quantidade de itens")
    message: Optional[str] = Field(default=None)


# ── Funções helper ────────────────────────────────────────────────────────────

def success_response(
    data: Any,
    message: str = "Operação realizada com sucesso"
) -> dict:
    """Constrói resposta de sucesso."""
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def error_response(
    message: str,
    error_code: str,
    status_code: int,
    details: Optional[dict] = None,
) -> dict:
    """Constrói resposta de erro."""
    return {
        "success": False,
        "message": message,
        "error": error_code,
        "code": status_code,
        **({"details": details} if details else {}),
    }


def list_response(
    data: Any,
    message: str = "Operação realizada com sucesso"
) -> dict:
    """Constrói resposta com lista."""
    count = len(data) if isinstance(data, list) else len(data.items()) if isinstance(data, dict) else 0
    return {
        "success": True,
        "data": data,
        "count": count,
        "message": message,
    }
