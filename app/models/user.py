"""Modelo de usuario del sistema."""
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional
import enum


class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    MESONERA = "mesonera"
    PUNTO_VENTA = "punto_venta"
    COCINERO = "cocinero"
    CLIENTE = "cliente"


class User(Document):
    email: Indexed(str, unique=True)
    hashed_password: str
    nombre: str
    apellido: str
    rol: RolUsuario = RolUsuario.CLIENTE
    activo: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"
