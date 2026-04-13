"""
Exceções customizadas da aplicação.

Usadas para tratamento de erros padronizado em toda a API.
"""


class AppException(Exception):
    """Exceção base da aplicação."""
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Recurso não encontrado."""
    def __init__(self, message: str = "Recurso não encontrado", details: dict = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ForbiddenError(AppException):
    """Usuário não tem permissão."""
    def __init__(self, message: str = "Você não tem permissão", details: dict = None):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class UnauthorizedError(AppException):
    """Usuário não autenticado."""
    def __init__(self, message: str = "Não autorizado", details: dict = None):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ValidationError(AppException):
    """Erro na validação de dados."""
    def __init__(self, message: str = "Dados inválidos", details: dict = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ConflictError(AppException):
    """Recurso em conflito."""
    def __init__(self, message: str = "Conflito no recurso", details: dict = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class InternalServerError(AppException):
    """Erro interno do servidor."""
    def __init__(self, message: str = "Erro interno", details: dict = None):
        super().__init__(
            message=message,
            error_code="INTERNAL_ERROR",
            status_code=500,
            details=details,
        )
