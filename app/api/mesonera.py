"""API Módulo Mesonera - Comandas y notificaciones."""
from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from app.models.comanda import Comanda, EstadoComanda, OrigenComanda
from app.models.cliente import Cliente
from app.models.mesa import Mesa
from app.models.notificacion import NotificacionMesonera
from app.schemas.comanda import ComandaCreate, ComandaResponse, ComandaDetalleResponse, ComandaUpdate
from app.core.dependencies import RequireMesoneraOrPOS
from app.models.user import User

router = APIRouter(prefix="/mesonera", tags=["Mesonera"])


@router.get("/notificaciones")
async def listar_notificaciones_pendientes(user: User = Depends(RequireMesoneraOrPOS)):
    notifs = await NotificacionMesonera.find(NotificacionMesonera.atendida == 0).sort(-NotificacionMesonera.created_at).to_list()
    return [{"id": str(n.id), "mesa_id": n.mesa_id, "mensaje": n.mensaje, "created_at": n.created_at.isoformat() if n.created_at else None} for n in notifs]


@router.post("/notificaciones/{notif_id}/atender")
async def marcar_notificacion_atendida(notif_id: str, user: User = Depends(RequireMesoneraOrPOS)):
    notif = await NotificacionMesonera.get(PydanticObjectId(notif_id))
    if not notif:
        raise HTTPException(404, "Notificación no encontrada")
    notif.atendida = 1
    await notif.save()
    return {"ok": True}


@router.post("/comanda", response_model=ComandaResponse)
async def crear_comanda_mesonera(data: ComandaCreate, user: User = Depends(RequireMesoneraOrPOS)):
    if data.origen != OrigenComanda.MESONERA:
        raise HTTPException(400, "Origen debe ser mesonera")
    from app.api.cliente_area import _crear_comanda
    data_copy = data.model_copy()
    data_copy.origen = OrigenComanda.MESONERA
    return await _crear_comanda(data_copy, str(user.id))


@router.get("/comandas", response_model=list[ComandaResponse])
async def listar_comandas_mesonera(user: User = Depends(RequireMesoneraOrPOS), estado: str | None = None):
    if estado:
        try:
            comandas = await Comanda.find(Comanda.estado == EstadoComanda(estado)).sort(-Comanda.created_at).to_list()
        except ValueError:
            comandas = await Comanda.find().sort(-Comanda.created_at).to_list()
    else:
        comandas = await Comanda.find().sort(-Comanda.created_at).to_list()
    result = []
    for c in comandas:
        cliente = await Cliente.get(PydanticObjectId(c.cliente_id)) if c.cliente_id else None
        mesa = await Mesa.get(PydanticObjectId(c.mesa_id)) if c.mesa_id else None
        result.append(ComandaResponse(
            id=str(c.id),
            numero=c.numero,
            mesa_id=c.mesa_id,
            mesa_numero=mesa.numero if mesa else None,
            cliente_id=c.cliente_id,
            estado=c.estado,
            forma_pago=c.forma_pago,
            origen=c.origen,
            subtotal=c.subtotal,
            impuesto=c.impuesto,
            total=c.total,
            observaciones=c.observaciones,
            created_at=c.created_at,
            detalles=[ComandaDetalleResponse(plato_id=d.plato_id, plato_nombre=d.plato_nombre, cantidad=d.cantidad, precio_unitario=d.precio_unitario, subtotal=d.subtotal, observaciones=d.observaciones) for d in c.detalles],
            cliente_nombre=f"{cliente.nombre} {cliente.apellido}" if cliente else None,
            cliente_cedula=cliente.cedula if cliente else None,
        ))
    return result
