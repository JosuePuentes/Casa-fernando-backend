"""Configuración de la aplicación."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración cargada desde variables de entorno."""
    SECRET_KEY: str = "clave-secreta-desarrollo-cambiar-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas
    MONGODB_URL: str = "mongodb://localhost:27017/casa_fernando"
    CORS_ORIGINS: str = "http://localhost:3000"  # Separar por coma. En prod: https://tu-app.vercel.app

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
