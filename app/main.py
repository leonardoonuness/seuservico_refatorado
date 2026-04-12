"""
main.py — Entrypoint da aplicação SeuServiço API

Responsabilidades:
  1. Criar e configurar a instância FastAPI
  2. Registrar middlewares (CORS, logs)
  3. Criar tabelas automaticamente no startup (seguro para MVP)
  4. Montar todos os routers
  5. Handler global de erros inesperados (garante que 500 nunca vaze stacktrace)
"""
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Importa todos os models para que Base.metadata os conheça
import app.models  # noqa: F401

from app.routes import auth, users, professionals, services, admin

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Startup / Shutdown ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Criando tabelas (se não existirem)...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas OK")
    except Exception as exc:
        logger.exception("❌ Falha ao criar tabelas: %s", exc)
        raise
    yield
    logger.info("⛔ Encerrando aplicação.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API do SeuServiço — conecta clientes a prestadores locais.",
    lifespan=lifespan,
    # Em produção, desabilita docs se quiser mais segurança:
    # docs_url=None, redoc_url=None,
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Ajuste para os domínios reais em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Handler global — captura qualquer Exception não tratada ───────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Garante que nenhum erro 500 vaze stacktrace para o cliente.
    O stacktrace completo aparece apenas nos logs do servidor.
    """
    logger.error(
        "Erro não tratado | %s %s | %s",
        request.method,
        request.url,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor. Nossa equipe foi notificada."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router,          prefix=PREFIX)
app.include_router(users.router,         prefix=PREFIX)
app.include_router(professionals.router, prefix=PREFIX)
app.include_router(services.router,      prefix=PREFIX)
app.include_router(admin.router,         prefix=PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"], summary="Health check detalhado")
def health_detailed():
    from sqlalchemy import text
    from app.db.session import engine as _engine
    try:
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.error("DB health check falhou: %s", exc)
        db_status = "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": settings.APP_VERSION,
    }
