"""Modelos de comandas."""
from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import enum


class ComandaDetalleEmbedded(BaseModel):
    plato_id: str
    plato_nombre: str
    cantidad: int = 1
    precio_unitario: float
    subtotal: float
    observaciones: Optional[str] = None


class EstadoComanda(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    LISTA = "lista"
    ENTREGADA = "entregada"
    PAGADA = "pagada"
    CANCELADA = "cancelada"


class FormaPago(str, enum.Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    OTRO = "otro"


class OrigenComanda(str, enum.Enum):
    AREA_CLIENTE = "area_cliente"
    MESONERA = "mesonera"
    PUNTO_VENTA = "punto_venta"


class Comanda(Document):
    numero: str
    mesa_id: Optional[str] = None
    cliente_id: str
    usuario_id: Optional[str] = None
    estado: EstadoComanda = EstadoComanda.PENDIENTE
    forma_pago: Optional[FormaPago] = None
    origen: OrigenComanda
    subtotal: float = 0.0
    impuesto: float = 0.0
    total: float = 0.0
    observaciones: Optional[str] = None
    detalles: list[ComandaDetalleEmbedded] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "comandas"
