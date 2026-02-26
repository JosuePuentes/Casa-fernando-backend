"""API Área Cliente - Menú, comandas y notificación mesonera."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.plato import Plato, CategoriaPlato
from app.models.cliente import Cliente
from app.models.comanda import Comanda, ComandaDetalle, OrigenComanda
from app.schemas.plato import PlatoMenuResponse
from app.schemas.comanda import ComandaCreate, ComandaResponse, ComandaDetalleResponse
from app.schemas.cliente import ClienteCreate
router = APIRouter(prefix="/cliente", tags=["Área Cliente"])


@router.get("/menu", response_model=list[PlatoMenuResponse])
async def get_menu(db: AsyncSession = Depends(get_db)):
    """Obtener menú completo (platos disponibles). Público."""
    result = await db.execute(
        select(Plato)
        .join(CategoriaPlato)
        .where(Plato.disponible == 1, CategoriaPlato.activo == 1)
        .order_by(CategoriaPlato.orden, Plato.nombre)
    )
    platos = result.scalars().all()
    return [
        PlatoMenuResponse(
            id=p.id,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio=p.precio,
            imagen_url=p.imagen_url,
            categoria=p.categoria.nombre if p.categoria else None,
        )
        for p in platos
    ]


@router.post("/comanda", response_model=ComandaResponse)
async def crear_comanda_cliente(
    data: ComandaCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crear comanda desde área cliente. Requiere datos del cliente (cédula, nombre, apellido, dirección, teléfono)."""
    if data.origen != OrigenComanda.AREA_CLIENTE:
        raise HTTPException(400, "Origen debe ser area_cliente")
    return await _crear_comanda(data, db, usuario_id=None)


@router.post("/notificar-mesonera")
async def notificar_mesonera(
    mesa_id: int | None = None,
    mensaje: str = "El cliente solicita atención",
    db: AsyncSession = Depends(get_db),
):
    """Enviar notificación a mesoneras (botón mantener presionado). Público. Vibra el teléfono de las mesoneras conectadas."""
    from app.models.notificacion import NotificacionMesonera
    from app.api.websocket import broadcast_notificacion_mesonera
    notif = NotificacionMesonera(mesa_id=mesa_id, mensaje=mensaje)
    db.add(notif)
    await db.flush()
    await broadcast_notificacion_mesonera(mesa_id, mensaje, notif.id)
    return {"ok": True, "mensaje": "Notificación enviada", "id": notif.id}


async def _crear_comanda(data: ComandaCreate, db: AsyncSession, usuario_id: int | None = None):
    """Lógica común para crear comanda."""
    from app.models.comanda import EstadoComanda
    from app.models.mesa import Mesa

    # Validar mesa si se proporciona
    if data.mesa_id is not None:
        r_mesa = await db.execute(select(Mesa).where(Mesa.id == data.mesa_id, Mesa.activa == 1))
        if not r_mesa.scalar_one_or_none():
            raise HTTPException(400, f"Mesa {data.mesa_id} no encontrada o inactiva")

    # Crear o buscar cliente
    result = await db.execute(select(Cliente).where(Cliente.cedula == data.cliente.cedula))
    cliente = result.scalar_one_or_none()
    if not cliente:
        cliente = Cliente(
            cedula=data.cliente.cedula,
            nombre=data.cliente.nombre,
            apellido=data.cliente.apellido,
            direccion=data.cliente.direccion,
            telefono=data.cliente.telefono,
            email=data.cliente.email,
        )
        db.add(cliente)
        await db.flush()
    else:
        cliente.nombre = data.cliente.nombre
        cliente.apellido = data.cliente.apellido
        cliente.direccion = data.cliente.direccion
        cliente.telefono = data.cliente.telefono
        cliente.email = data.cliente.email

    # Número de comanda
    from sqlalchemy import func
    r = await db.execute(select(func.count(Comanda.id)))
    count = r.scalar() or 0
    numero = f"CMD-{count + 1:06d}"

    comanda = Comanda(
        numero=numero,
        mesa_id=data.mesa_id,
        cliente_id=cliente.id,
        usuario_id=usuario_id,
        estado=EstadoComanda.PENDIENTE,
        forma_pago=data.forma_pago,
        origen=data.origen,
        observaciones=data.observaciones,
    )
    db.add(comanda)
    await db.flush()

    subtotal = 0.0
    for det in data.platos:
        plato_result = await db.execute(select(Plato).where(Plato.id == det.plato_id))
        plato = plato_result.scalar_one_or_none()
        if not plato:
            raise HTTPException(400, f"Plato {det.plato_id} no encontrado")
        st = plato.precio * det.cantidad
        subtotal += st
        cd = ComandaDetalle(
            comanda_id=comanda.id,
            plato_id=plato.id,
            cantidad=det.cantidad,
            precio_unitario=plato.precio,
            subtotal=st,
            observaciones=det.observaciones,
        )
        db.add(cd)

    impuesto = subtotal * 0.12  # 12% IVA
    comanda.subtotal = subtotal
    comanda.impuesto = impuesto
    comanda.total = subtotal + impuesto

    await db.refresh(comanda)
    await db.execute(
        select(Comanda)
        .options(selectinload(Comanda.detalles).selectinload(ComandaDetalle.plato))
        .where(Comanda.id == comanda.id)
    )
    c = (await db.execute(select(Comanda).options(
        selectinload(Comanda.detalles).selectinload(ComandaDetalle.plato),
        selectinload(Comanda.cliente),
        selectinload(Comanda.mesa),
    ).where(Comanda.id == comanda.id))).scalar_one()

    detalles_resp = [
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
    ]
    return ComandaResponse(
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
        detalles=detalles_resp,
        cliente_nombre=f"{c.cliente.nombre} {c.cliente.apellido}" if c.cliente else None,
        cliente_cedula=c.cliente.cedula if c.cliente else None,
    )
