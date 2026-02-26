"""API de Mesas - Listar mesas para seleccionar al crear comanda."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.mesa import Mesa
from app.schemas.mesa import MesaSelectItem
from app.core.dependencies import RequireMesoneraOrPOS

router = APIRouter(prefix="/mesas", tags=["Mesas"])


@router.get("", response_model=list[MesaSelectItem])
async def listar_mesas_para_comanda(
    db: AsyncSession = Depends(get_db),
    _=Depends(RequireMesoneraOrPOS),
):
    """
    Listar mesas disponibles para seleccionar al montar/crear una comanda.
    Usado por módulo mesonera y punto de venta para elegir a qué mesa va la cuenta.
    """
    result = await db.execute(
        select(Mesa).where(Mesa.activa == 1).order_by(Mesa.numero)
    )
    mesas = result.scalars().all()
    return [
        MesaSelectItem(
            id=m.id,
            numero=m.numero,
            capacidad=m.capacidad,
            ubicacion=m.ubicacion,
        )
        for m in mesas
    ]
