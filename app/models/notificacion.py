"""Modelo de notificaciones para mesonera."""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class NotificacionMesonera(Document):
    mesa_id: Optional[str] = None
    mensaje: str = "El cliente solicita atención"
    atendida: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notificaciones_mesonera"
