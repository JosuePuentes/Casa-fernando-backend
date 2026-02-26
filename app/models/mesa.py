"""Modelo de mesa."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Mesa(Base):
    """Mesas del restaurante."""
    __tablename__ = "mesas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False)
    capacidad = Column(Integer, default=4)
    ubicacion = Column(String(100), nullable=True)
    activa = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    comandas = relationship("Comanda", back_populates="mesa")
    notificaciones = relationship("NotificacionMesonera", back_populates="mesa")
