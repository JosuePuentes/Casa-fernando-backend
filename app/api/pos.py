"""API Punto de Venta - Comandas."""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.comanda import ComandaCreate, ComandaResponse
from app.models.comanda import OrigenComanda
from app.core.dependencies import RequireMesoneraOrPOS
from app.models.user import User

router = APIRouter(prefix="/pos", tags=["Punto de Venta"])


@router.post("/comanda", response_model=ComandaResponse)
async def crear_comanda_pos(data: ComandaCreate, user: User = Depends(RequireMesoneraOrPOS)):
    if data.origen != OrigenComanda.PUNTO_VENTA:
        raise HTTPException(400, "Origen debe ser punto_venta")
    from app.api.cliente_area import _crear_comanda
    return await _crear_comanda(data, str(user.id))
