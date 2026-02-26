"""API común para actualizar estado de comandas."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.comanda import Comanda, ComandaDetalle
from app.schemas.comanda import ComandaUpdate, ComandaResponse, ComandaDetalleResponse
from app.core.dependencies import RequireMesoneraOrPOS

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.patch("/{comanda_id}", response_model=ComandaResponse)
async def actualizar_comanda(
    comanda_id: int,
    data: ComandaUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(RequireMesoneraOrPOS),
):
    """Actualizar estado o forma de pago de una comanda."""
    result = await db.execute(
        select(Comanda)
        .options(
            selectinload(Comanda.detalles).selectinload(ComandaDetalle.plato),
            selectinload(Comanda.cliente),
            selectinload(Comanda.mesa),
        )
        .where(Comanda.id == comanda_id)
    )
    comanda = result.scalar_one_or_none()
    if not comanda:
        raise HTTPException(404, "Comanda no encontrada")
    if data.estado is not None:
        comanda.estado = data.estado
    if data.forma_pago is not None:
        comanda.forma_pago = data.forma_pago
    await db.refresh(comanda)
    return ComandaResponse(
        id=comanda.id,
        numero=comanda.numero,
        mesa_id=comanda.mesa_id,
        mesa_numero=comanda.mesa.numero if comanda.mesa else None,
        cliente_id=comanda.cliente_id,
        estado=comanda.estado,
        forma_pago=comanda.forma_pago,
        origen=comanda.origen,
        subtotal=comanda.subtotal,
        impuesto=comanda.impuesto,
        total=comanda.total,
        observaciones=comanda.observaciones,
        created_at=comanda.created_at,
        detalles=[
            ComandaDetalleResponse(
                id=d.id,
                plato_id=d.plato_id,
                plato_nombre=d.plato.nombre if d.plato else None,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                subtotal=d.subtotal,
                observaciones=d.observaciones,
            )
            for d in comanda.detalles
        ],
        cliente_nombre=f"{comanda.cliente.nombre} {comanda.cliente.apellido}" if comanda.cliente else None,
        cliente_cedula=comanda.cliente.cedula if comanda.cliente else None,
    )
