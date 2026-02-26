"""Esquemas de comandas."""
from pydantic import BaseModel, model_validator
from datetime import datetime
from app.models.comanda import EstadoComanda, FormaPago, OrigenComanda
from app.schemas.cliente import ClienteCreate


class ComandaDetalleCreate(BaseModel):
    plato_id: str
    cantidad: int = 1
    observaciones: str | None = None


class ComandaDetalleResponse(BaseModel):
    plato_id: str
    plato_nombre: str | None = None
    cantidad: int
    precio_unitario: float
    subtotal: float
    observaciones: str | None = None

    class Config:
        from_attributes = True


class ComandaCreate(BaseModel):
    """Crear comanda - requiere datos del cliente. Mesa obligatoria para mesonera y punto de venta."""
    cliente: ClienteCreate
    mesa_id: str | None = None
    platos: list[ComandaDetalleCreate]
    forma_pago: FormaPago | None = None
    origen: OrigenComanda
    observaciones: str | None = None

    @model_validator(mode="after")
    def validar_mesa_requerida(self):
        if self.origen in (OrigenComanda.MESONERA, OrigenComanda.PUNTO_VENTA):
            if self.mesa_id is None:
                raise ValueError("Debe seleccionar la mesa a donde va la cuenta (mesa_id obligatorio para mesonera y punto de venta)")
        return self


class ComandaUpdate(BaseModel):
    estado: EstadoComanda | None = None
    forma_pago: FormaPago | None = None


class ComandaResponse(BaseModel):
    id: str
    numero: str
    mesa_id: str | None = None
    mesa_numero: str | None = None
    cliente_id: str
    estado: EstadoComanda
    forma_pago: FormaPago | None = None
    origen: OrigenComanda
    subtotal: float
    impuesto: float
    total: float
    observaciones: str | None = None
    created_at: datetime
    detalles: list[ComandaDetalleResponse] = []
    cliente_nombre: str | None = None
    cliente_cedula: str | None = None

    class Config:
        from_attributes = True


class ComandaFacturacionResponse(BaseModel):
    """Comanda para módulo de facturación."""
    id: str
    numero: str
    mesa_numero: str | None = None
    cliente_nombre: str
    cliente_apellido: str
    cliente_cedula: str
    cliente_telefono: str
    total: float
    estado: EstadoComanda
    forma_pago: FormaPago | None = None
    created_at: datetime

    class Config:
        from_attributes = True
