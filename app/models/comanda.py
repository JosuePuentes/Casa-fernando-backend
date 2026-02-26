"""Modelos de comandas."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class EstadoComanda(str, enum.Enum):
    """Estados de una comanda."""
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    LISTA = "lista"
    ENTREGADA = "entregada"
    PAGADA = "pagada"
    CANCELADA = "cancelada"


class FormaPago(str, enum.Enum):
    """Formas de pago."""
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    OTRO = "otro"


class OrigenComanda(str, enum.Enum):
    """Origen de la comanda."""
    AREA_CLIENTE = "area_cliente"
    MESONERA = "mesonera"
    PUNTO_VENTA = "punto_venta"


class Comanda(Base):
    """Comanda principal."""
    __tablename__ = "comandas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, index=True, nullable=False)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Mesonera/POS que registró
    estado = Column(Enum(EstadoComanda), default=EstadoComanda.PENDIENTE)
    forma_pago = Column(Enum(FormaPago), nullable=True)
    origen = Column(Enum(OrigenComanda), nullable=False)
    subtotal = Column(Float, default=0.0)
    impuesto = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cliente = relationship("Cliente", back_populates="comandas")
    mesa = relationship("Mesa", back_populates="comandas")
    usuario = relationship("User", back_populates="comandas")
    detalles = relationship("ComandaDetalle", back_populates="comanda", cascade="all, delete-orphan")


class ComandaDetalle(Base):
    """Detalle de platos en una comanda."""
    __tablename__ = "comandas_detalle"

    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    plato_id = Column(Integer, ForeignKey("platos.id"), nullable=False)
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    observaciones = Column(String(255), nullable=True)

    comanda = relationship("Comanda", back_populates="detalles")
    plato = relationship("Plato", back_populates="comandas_detalle")
