"""Modelos de base de datos."""
from app.models.user import User
from app.models.cliente import Cliente
from app.models.plato import Plato, CategoriaPlato
from app.models.comanda import Comanda, ComandaDetalle, EstadoComanda, FormaPago
from app.models.mesa import Mesa
from app.models.notificacion import NotificacionMesonera

__all__ = [
    "User",
    "Cliente",
    "Plato",
    "CategoriaPlato",
    "Comanda",
    "ComandaDetalle",
    "EstadoComanda",
    "FormaPago",
    "Mesa",
    "NotificacionMesonera",
]
