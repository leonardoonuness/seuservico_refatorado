from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Banco de dados ────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "b7aa881439b5f64412f35812cc5e842fabdd337af1b6e3f3191bdd34da26f681"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "SeuServiço API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton — importado em todo o projeto
settings = Settings()
