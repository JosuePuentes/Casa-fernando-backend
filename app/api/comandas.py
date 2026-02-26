"""API común para actualizar estado de comandas."""
from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from app.models.comanda import Comanda
from app.models.cliente import Cliente
from app.models.mesa import Mesa
from app.schemas.comanda import ComandaUpdate, ComandaResponse, ComandaDetalleResponse
from app.core.dependencies import RequireMesoneraOrPOS

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.patch("/{comanda_id}", response_model=ComandaResponse)
async def actualizar_comanda(comanda_id: str, data: ComandaUpdate, _=RequireMesoneraOrPOS):
    comanda = await Comanda.get(PydanticObjectId(comanda_id))
    if not comanda:
        raise HTTPException(404, "Comanda no encontrada")
    if data.estado is not None:
        comanda.estado = data.estado
    if data.forma_pago is not None:
        comanda.forma_pago = data.forma_pago
    await comanda.save()
    cliente = await Cliente.get(PydanticObjectId(comanda.cliente_id)) if comanda.cliente_id else None
    mesa = await Mesa.get(PydanticObjectId(comanda.mesa_id)) if comanda.mesa_id else None
    return ComandaResponse(
        id=str(comanda.id),
        numero=comanda.numero,
        mesa_id=comanda.mesa_id,
        mesa_numero=mesa.numero if mesa else None,
        cliente_id=comanda.cliente_id,
        estado=comanda.estado,
        forma_pago=comanda.forma_pago,
        origen=comanda.origen,
        subtotal=comanda.subtotal,
        impuesto=comanda.impuesto,
        total=comanda.total,
        observaciones=comanda.observaciones,
        created_at=comanda.created_at,
        detalles=[ComandaDetalleResponse(plato_id=d.plato_id, plato_nombre=d.plato_nombre, cantidad=d.cantidad, precio_unitario=d.precio_unitario, subtotal=d.subtotal, observaciones=d.observaciones) for d in comanda.detalles],
        cliente_nombre=f"{cliente.nombre} {cliente.apellido}" if cliente else None,
        cliente_cedula=cliente.cedula if cliente else None,
    )
