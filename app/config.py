"""Configuración de la aplicación."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración cargada desde variables de entorno."""
    SECRET_KEY: str = "clave-secreta-desarrollo-cambiar-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas
    DATABASE_URL: str = "sqlite+aiosqlite:///./casa_fernando.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
