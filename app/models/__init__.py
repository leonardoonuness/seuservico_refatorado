"""
Importa todos os models para que o Alembic detecte as tabelas
ao executar `alembic revision --autogenerate`.
"""
from app.models.user import User
from app.models.professional import Professional
from app.models.service_request import ServiceRequest
from app.models.review import Review

__all__ = ["User", "Professional", "ServiceRequest", "Review"]
