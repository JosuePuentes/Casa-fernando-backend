"""Modelo de cliente."""
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional


class Cliente(Document):
    cedula: Indexed(str)
    nombre: str
    apellido: str
    direccion: Optional[str] = None
    telefono: str
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "clientes"
