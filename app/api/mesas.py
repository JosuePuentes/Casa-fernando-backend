"""API de Mesas - Listar mesas para seleccionar al crear comanda."""
from fastapi import APIRouter, Depends
from app.models.mesa import Mesa
from app.schemas.mesa import MesaSelectItem
from app.core.dependencies import RequireMesoneraOrPOS

router = APIRouter(prefix="/mesas", tags=["Mesas"])


@router.get("", response_model=list[MesaSelectItem])
async def listar_mesas_para_comanda(_=Depends(RequireMesoneraOrPOS)):
    mesas = await Mesa.find(Mesa.activa == 1).sort(Mesa.numero).to_list()
    return [MesaSelectItem(id=str(m.id), numero=m.numero, capacidad=m.capacidad, ubicacion=m.ubicacion) for m in mesas]
