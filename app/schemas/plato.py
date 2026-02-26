"""Esquemas de platos y categorías."""
from pydantic import BaseModel


class CategoriaPlatoBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    orden: int = 0


class CategoriaPlatoCreate(CategoriaPlatoBase):
    pass


class CategoriaPlatoResponse(CategoriaPlatoBase):
    id: str

    class Config:
        from_attributes = True


class PlatoBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    precio: float
    imagen_url: str | None = None
    disponible: int = 1


class PlatoCreate(PlatoBase):
    categoria_id: int


class PlatoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    disponible: int | None = None


class PlatoResponse(PlatoBase):
    id: str
    categoria_id: str
    categoria: CategoriaPlatoResponse | None = None

    class Config:
        from_attributes = True


class PlatoMenuResponse(BaseModel):
    """Plato para mostrar en menú del cliente."""
    id: str
    nombre: str
    descripcion: str | None = None
    precio: float
    imagen_url: str | None = None
    categoria: str | None = None

    class Config:
        from_attributes = True
