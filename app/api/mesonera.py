"""API Módulo Mesonera - Comandas y notificaciones."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.comanda import Comanda, ComandaDetalle
from app.models.cliente import Cliente
from app.models.notificacion import NotificacionMesonera
from app.models.plato import Plato
from app.schemas.comanda import ComandaCreate, ComandaResponse, ComandaDetalleResponse, ComandaUpdate
from app.models.comanda import OrigenComanda
from app.core.dependencies import get_current_user, RequireMesoneraOrPOS
from app.models.user import User

router = APIRouter(prefix="/mesonera", tags=["Mesonera"])


@router.get("/notificaciones")
async def listar_notificaciones_pendientes(
    user: User = Depends(RequireMesoneraOrPOS),
    db: AsyncSession = Depends(get_db),
):
    """Listar notificaciones pendientes de clientes (para vibración en app)."""
    result = await db.execute(
        select(NotificacionMesonera)
        .where(NotificacionMesonera.atendida == 0)
        .order_by(NotificacionMesonera.created_at.desc())
    )
    notifs = result.scalars().all()
    return [
        {
            "id": n.id,
            "mesa_id": n.mesa_id,
            "mensaje": n.mensaje,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


@router.post("/notificaciones/{notif_id}/atender")
async def marcar_notificacion_atendida(
    notif_id: int,
    user: User = Depends(RequireMesoneraOrPOS),
    db: AsyncSession = Depends(get_db),
):
    """Marcar notificación como atendida."""
    result = await db.execute(select(NotificacionMesonera).where(NotificacionMesonera.id == notif_id))
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(404, "Notificación no encontrada")
    notif.atendida = 1
    return {"ok": True}


@router.post("/comanda", response_model=ComandaResponse)
async def crear_comanda_mesonera(
    data: ComandaCreate,
    user: User = Depends(RequireMesoneraOrPOS),
    db: AsyncSession = Depends(get_db),
):
    """Crear comanda desde módulo mesonera. Especificar platos y forma de pago."""
    if data.origen != OrigenComanda.MESONERA:
        raise HTTPException(400, "Origen debe ser mesonera")
    return await _crear_comanda_mesonera(data, db, user.id)


async def _crear_comanda_mesonera(data: ComandaCreate, db: AsyncSession, usuario_id: int):
    """Lógica común para crear comanda desde mesonera."""
    from app.api.cliente_area import _crear_comanda as _crear_base
    data_copy = data.model_copy()
    data_copy.origen = OrigenComanda.MESONERA
    return await _crear_base(data_copy, db, usuario_id)


@router.get("/comandas", response_model=list[ComandaResponse])
async def listar_comandas_mesonera(
    user: User = Depends(RequireMesoneraOrPOS),
    db: AsyncSession = Depends(get_db),
    estado: str | None = None,
):
    """Listar comandas del día."""
    q = select(Comanda).options(
        selectinload(Comanda.detalles).selectinload(ComandaDetalle.plato),
        selectinload(Comanda.cliente),
        selectinload(Comanda.mesa),
    ).order_by(Comanda.created_at.desc())
    if estado:
        from app.models.comanda import EstadoComanda
        try:
            q = q.where(Comanda.estado == EstadoComanda(estado))
        except ValueError:
            pass
    result = await db.execute(q)
    comandas = result.scalars().all()
    return [
        ComandaResponse(
            id=c.id,
            numero=c.numero,
            mesa_id=c.mesa_id,
            mesa_numero=c.mesa.numero if c.mesa else None,
            cliente_id=c.cliente_id,
            estado=c.estado,
            forma_pago=c.forma_pago,
            origen=c.origen,
            subtotal=c.subtotal,
            impuesto=c.impuesto,
            total=c.total,
            observaciones=c.observaciones,
            created_at=c.created_at,
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
                for d in c.detalles
            ],
            cliente_nombre=f"{c.cliente.nombre} {c.cliente.apellido}" if c.cliente else None,
            cliente_cedula=c.cliente.cedula if c.cliente else None,
        )
        for c in comandas
    ]
