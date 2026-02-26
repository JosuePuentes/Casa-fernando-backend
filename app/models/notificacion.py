"""Modelo de notificaciones para mesonera."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NotificacionMesonera(Base):
    """Notificaciones enviadas por clientes para llamar a la mesonera."""
    __tablename__ = "notificaciones_mesonera"

    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=True)
    mensaje = Column(String(255), default="El cliente solicita atención")
    atendida = Column(Integer, default=0)  # 0=pendiente, 1=atendida
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mesa = relationship("Mesa", back_populates="notificaciones")
