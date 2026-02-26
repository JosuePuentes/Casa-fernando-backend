"""API Módulo de Facturación - Búsqueda y filtros."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime
from app.database import get_db
from app.models.comanda import Comanda
from app.models.cliente import Cliente
from app.models.comanda import ComandaDetalle
from app.schemas.comanda import ComandaFacturacionResponse
from app.core.dependencies import RequireMesoneraOrPOS

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.get("/comandas", response_model=list[ComandaFacturacionResponse])
async def buscar_comandas(
    nombre: str | None = Query(None, description="Buscar por nombre del cliente"),
    cedula: str | None = Query(None, description="Buscar por número de cédula"),
    fecha_desde: date | None = Query(None, description="Filtrar desde fecha"),
    fecha_hasta: date | None = Query(None, description="Filtrar hasta fecha"),
    db: AsyncSession = Depends(get_db),
    _=Depends(RequireMesoneraOrPOS),
):
    """
    Buscar comandas para facturación.
    - Por nombre del cliente
    - Por número de cédula
    - Filtrar por rango de fechas
    """
    q = (
        select(Comanda)
        .join(Cliente, Comanda.cliente_id == Cliente.id)
        .options(selectinload(Comanda.cliente), selectinload(Comanda.mesa))
        .order_by(Comanda.created_at.desc())
    )

    if nombre:
        nombre_lower = f"%{nombre.lower()}%"
        q = q.where(
            or_(
                func.lower(Cliente.nombre).like(nombre_lower),
                func.lower(Cliente.apellido).like(nombre_lower),
            )
        )
    if cedula:
        q = q.where(Cliente.cedula.ilike(f"%{cedula}%"))
    if fecha_desde:
        q = q.where(func.date(Comanda.created_at) >= fecha_desde)
    if fecha_hasta:
        q = q.where(func.date(Comanda.created_at) <= fecha_hasta)

    result = await db.execute(q)
    comandas = result.scalars().all()

    return [
        ComandaFacturacionResponse(
            id=c.id,
            numero=c.numero,
            mesa_numero=c.mesa.numero if c.mesa else None,
            cliente_nombre=c.cliente.nombre if c.cliente else "",
            cliente_apellido=c.cliente.apellido if c.cliente else "",
            cliente_cedula=c.cliente.cedula if c.cliente else "",
            cliente_telefono=c.cliente.telefono if c.cliente else "",
            total=c.total,
            estado=c.estado,
            forma_pago=c.forma_pago,
            created_at=c.created_at,
        )
        for c in comandas
    ]


@router.get("/comandas/{comanda_id}")
async def detalle_comanda_facturacion(
    comanda_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(RequireMesoneraOrPOS),
):
    """Detalle completo de una comanda para facturación."""
    result = await db.execute(
        select(Comanda)
        .options(
            selectinload(Comanda.cliente),
            selectinload(Comanda.detalles).selectinload(ComandaDetalle.plato),
        )
        .where(Comanda.id == comanda_id)
    )
    comanda = result.scalar_one_or_none()
    if not comanda:
        return {"error": "Comanda no encontrada"}

    return {
        "id": comanda.id,
        "numero": comanda.numero,
        "mesa": comanda.mesa.numero if comanda.mesa else None,
        "cliente": {
            "cedula": comanda.cliente.cedula,
            "nombre": comanda.cliente.nombre,
            "apellido": comanda.cliente.apellido,
            "direccion": comanda.cliente.direccion,
            "telefono": comanda.cliente.telefono,
        },
        "subtotal": comanda.subtotal,
        "impuesto": comanda.impuesto,
        "total": comanda.total,
        "estado": comanda.estado.value,
        "forma_pago": comanda.forma_pago.value if comanda.forma_pago else None,
        "created_at": comanda.created_at.isoformat() if comanda.created_at else None,
        "detalles": [
            {
                "plato": d.plato.nombre if d.plato else "",
                "cantidad": d.cantidad,
                "precio_unitario": d.precio_unitario,
                "subtotal": d.subtotal,
            }
            for d in comanda.detalles
        ],
    }
