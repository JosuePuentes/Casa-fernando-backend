"""Modelo de cliente (datos para facturación)."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Cliente(Base):
    """Datos del cliente para cada comanda/factura."""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    comandas = relationship("Comanda", back_populates="cliente")
