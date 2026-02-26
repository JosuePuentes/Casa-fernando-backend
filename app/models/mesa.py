"""Modelo de mesa."""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class Mesa(Document):
    numero: str
    capacidad: int = 4
    ubicacion: Optional[str] = None
    activa: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "mesas"
