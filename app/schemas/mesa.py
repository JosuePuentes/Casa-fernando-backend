"""Esquemas de mesas."""
from pydantic import BaseModel


class MesaBase(BaseModel):
    numero: str
    capacidad: int = 4
    ubicacion: str | None = None


class MesaCreate(MesaBase):
    pass


class MesaUpdate(BaseModel):
    numero: str | None = None
    capacidad: int | None = None
    ubicacion: str | None = None
    activa: int | None = None


class MesaResponse(MesaBase):
    id: int
    activa: int = 1

    class Config:
        from_attributes = True


class MesaSelectItem(BaseModel):
    """Mesa para selector al crear comanda."""
    id: int
    numero: str
    capacidad: int
    ubicacion: str | None = None

    class Config:
        from_attributes = True
