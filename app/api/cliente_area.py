"""API Área Cliente - Menú, comandas y notificación mesonera."""
from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.operators import In, NE, And
from app.models.plato import Plato, CategoriaPlato
from app.models.cliente import Cliente
from app.models.comanda import Comanda, ComandaDetalleEmbedded, OrigenComanda, EstadoComanda
from app.models.mesa import Mesa
from app.schemas.plato import PlatoMenuResponse
from app.schemas.comanda import ComandaCreate, ComandaResponse, ComandaDetalleResponse
from app.schemas.mesa import MesaSelectItem

router = APIRouter(prefix="/cliente", tags=["Área Cliente"])


@router.get("/mesas-disponibles", response_model=list[MesaSelectItem])
async def get_mesas_disponibles():
    """Mesas activas sin comanda activa. Público."""
    estados_ocupada = [
        EstadoComanda.PENDIENTE,
        EstadoComanda.EN_PREPARACION,
        EstadoComanda.LISTA,
        EstadoComanda.ENTREGADA,
    ]
    comandas_activas = await Comanda.find(
        And(
            NE(Comanda.mesa_id, None),
            In(Comanda.estado, estados_ocupada),
        )
    ).to_list()
    mesas_ocupadas = {str(c.mesa_id) for c in comandas_activas if c.mesa_id}
    mesas = await Mesa.find(Mesa.activa == 1).sort(Mesa.numero).to_list()
    disponibles = [m for m in mesas if str(m.id) not in mesas_ocupadas]
    return [MesaSelectItem(id=str(m.id), numero=m.numero, capacidad=m.capacidad, ubicacion=m.ubicacion) for m in disponibles]


@router.get("/menu", response_model=list[PlatoMenuResponse])
async def get_menu():
    """Obtener menú completo. Público."""
    categorias = await CategoriaPlato.find(CategoriaPlato.activo == 1).sort(CategoriaPlato.orden).to_list()
    cat_map = {str(c.id): c.nombre for c in categorias}
    platos = await Plato.find(Plato.disponible == 1).sort(Plato.nombre).to_list()
    return [
        PlatoMenuResponse(
            id=str(p.id),
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio=p.precio,
            imagen_url=p.imagen_url,
            categoria=cat_map.get(p.categoria_id),
        )
        for p in platos if p.categoria_id in cat_map
    ]


@router.post("/comanda", response_model=ComandaResponse)
async def crear_comanda_cliente(data: ComandaCreate):
    if data.origen != OrigenComanda.AREA_CLIENTE:
        raise HTTPException(400, "Origen debe ser area_cliente")
    return await _crear_comanda(data, usuario_id=None)


@router.post("/notificar-mesonera")
async def notificar_mesonera(mesa_id: str | None = None, mensaje: str = "El cliente solicita atención"):
    from app.models.notificacion import NotificacionMesonera
    from app.api.websocket import broadcast_notificacion_mesonera
    notif = NotificacionMesonera(mesa_id=mesa_id, mensaje=mensaje)
    await notif.insert()
    await broadcast_notificacion_mesonera(mesa_id, mensaje, str(notif.id))
    return {"ok": True, "mensaje": "Notificación enviada", "id": str(notif.id)}


async def _crear_comanda(data: ComandaCreate, usuario_id: str | None = None):
    if data.mesa_id:
        mesa = await Mesa.get(PydanticObjectId(data.mesa_id))
        if not mesa or mesa.activa != 1:
            raise HTTPException(400, f"Mesa no encontrada o inactiva")

    cliente = await Cliente.find_one(Cliente.cedula == data.cliente.cedula)
    if not cliente:
        cliente = Cliente(
            cedula=data.cliente.cedula,
            nombre=data.cliente.nombre,
            apellido=data.cliente.apellido,
            direccion=data.cliente.direccion,
            telefono=data.cliente.telefono,
            email=data.cliente.email,
        )
        await cliente.insert()
    else:
        cliente.nombre = data.cliente.nombre
        cliente.apellido = data.cliente.apellido
        cliente.direccion = data.cliente.direccion
        cliente.telefono = data.cliente.telefono
        cliente.email = data.cliente.email
        await cliente.save()

    count = await Comanda.count()
    numero = f"CMD-{count + 1:06d}"

    detalles_embed = []
    subtotal = 0.0
    for det in data.platos:
        plato = await Plato.get(PydanticObjectId(det.plato_id))
        if not plato:
            raise HTTPException(400, f"Plato {det.plato_id} no encontrado")
        st = plato.precio * det.cantidad
        subtotal += st
        detalles_embed.append(ComandaDetalleEmbedded(
            plato_id=str(plato.id),
            plato_nombre=plato.nombre,
            cantidad=det.cantidad,
            precio_unitario=plato.precio,
            subtotal=st,
            observaciones=det.observaciones,
        ))

    impuesto = subtotal * 0.12
    comanda = Comanda(
        numero=numero,
        mesa_id=data.mesa_id,
        cliente_id=str(cliente.id),
        usuario_id=usuario_id,
        estado=EstadoComanda.PENDIENTE,
        forma_pago=data.forma_pago,
        origen=data.origen,
        observaciones=data.observaciones,
        subtotal=subtotal,
        impuesto=impuesto,
        total=subtotal + impuesto,
        detalles=detalles_embed,
    )
    await comanda.insert()

    detalles_resp = [
        ComandaDetalleResponse(
            plato_id=d.plato_id,
            plato_nombre=d.plato_nombre,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
            observaciones=d.observaciones,
        )
        for d in comanda.detalles
    ]
    return ComandaResponse(
        id=str(comanda.id),
        numero=comanda.numero,
        mesa_id=comanda.mesa_id,
        mesa_numero=(await Mesa.get(PydanticObjectId(data.mesa_id))).numero if data.mesa_id else None,
        cliente_id=str(cliente.id),
        estado=comanda.estado,
        forma_pago=comanda.forma_pago,
        origen=comanda.origen,
        subtotal=comanda.subtotal,
        impuesto=comanda.impuesto,
        total=comanda.total,
        observaciones=comanda.observaciones,
        created_at=comanda.created_at,
        detalles=detalles_resp,
        cliente_nombre=f"{cliente.nombre} {cliente.apellido}",
        cliente_cedula=cliente.cedula,
    )
