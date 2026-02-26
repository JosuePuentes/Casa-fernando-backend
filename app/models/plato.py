"""Modelos de platos y categorías."""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class CategoriaPlato(Document):
    nombre: str
    descripcion: Optional[str] = None
    orden: int = 0
    activo: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "categorias_plato"


class Plato(Document):
    categoria_id: str  # ObjectId ref
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    imagen_url: Optional[str] = None
    disponible: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "platos"
