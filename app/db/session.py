"""
Configuração da engine e sessão SQLAlchemy.
pool_pre_ping=True garante que conexões mortas sejam descartadas automaticamente —
essencial para o PostgreSQL da Render que fecha conexões ociosas.
"""
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,        # Re-testa conexão antes de usar
    pool_size=5,               # Conexões mantidas abertas
    max_overflow=10,           # Conexões extras em pico
    pool_timeout=30,           # Espera máxima por conexão (s)
    pool_recycle=1800,         # Recicla conexões a cada 30 min
    echo=False,                # True para debug SQL (não usar em prod)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Dependência do FastAPI: abre e fecha a sessão por request.
    Faz rollback automático em caso de exceção.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
