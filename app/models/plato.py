"""Modelos de platos y categorías del menú."""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CategoriaPlato(Base):
    """Categorías del menú (Entradas, Platos fuertes, Bebidas, etc.)."""
    __tablename__ = "categorias_plato"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    orden = Column(Integer, default=0)
    activo = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    platos = relationship("Plato", back_populates="categoria")


class Plato(Base):
    """Platos del menú."""
    __tablename__ = "platos"

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias_plato.id"), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    imagen_url = Column(String(500), nullable=True)
    disponible = Column(Integer, default=1)  # 1=disponible, 0=no disponible
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    categoria = relationship("CategoriaPlato", back_populates="platos")
    comandas_detalle = relationship("ComandaDetalle", back_populates="plato")
