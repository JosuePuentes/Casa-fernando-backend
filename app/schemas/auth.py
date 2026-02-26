"""Esquemas de autenticación."""
from pydantic import BaseModel, EmailStr, Field, AliasChoices, field_validator
from app.models.user import RolUsuario


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None
    rol: RolUsuario | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nombre: str = Field(..., validation_alias=AliasChoices("nombre", "firstName", "name"))
    apellido: str = Field(..., validation_alias=AliasChoices("apellido", "lastName"))
    rol: RolUsuario = RolUsuario.CLIENTE

    model_config = {"extra": "ignore", "populate_by_name": True}

    @field_validator("rol", mode="before")
    @classmethod
    def normalize_rol(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class UserResponse(BaseModel):
    id: str
    email: str
    nombre: str
    apellido: str
    rol: RolUsuario

    class Config:
        from_attributes = True
