"""Modelo de usuario del sistema."""
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class RolUsuario(str, enum.Enum):
    """Roles del sistema."""
    ADMIN = "admin"
    MESONERA = "mesonera"
    PUNTO_VENTA = "punto_venta"
    CLIENTE = "cliente"


class User(Base):
    """Usuario del sistema (empleados y acceso administrativo)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.CLIENTE)
    activo = Column(Integer, default=1)  # 1=activo, 0=inactivo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    comandas = relationship("Comanda", back_populates="usuario")
