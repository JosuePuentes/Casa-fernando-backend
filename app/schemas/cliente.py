"""Esquemas de cliente."""
from pydantic import BaseModel


class ClienteBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    direccion: str | None = None
    telefono: str
    email: str | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: str

    class Config:
        from_attributes = True
