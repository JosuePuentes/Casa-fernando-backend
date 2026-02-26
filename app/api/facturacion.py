"""API Módulo de Facturación - Búsqueda y filtros."""
from fastapi import APIRouter, Depends, Query
from datetime import date, datetime
from beanie import PydanticObjectId
from app.models.comanda import Comanda
from app.models.cliente import Cliente
from app.models.mesa import Mesa
from app.schemas.comanda import ComandaFacturacionResponse
from app.core.dependencies import RequireMesoneraOrPOS

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.get("/comandas", response_model=list[ComandaFacturacionResponse])
async def buscar_comandas(
    nombre: str | None = Query(None),
    cedula: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    _=RequireMesoneraOrPOS,
):
    comandas = await Comanda.find().sort(-Comanda.created_at).to_list()
    result = []
    for c in comandas:
        cliente = await Cliente.get(PydanticObjectId(c.cliente_id)) if c.cliente_id else None
        if not cliente:
            continue
        if nombre and nombre.lower() not in cliente.nombre.lower() and nombre.lower() not in cliente.apellido.lower():
            continue
        if cedula and cedula not in cliente.cedula:
            continue
        if fecha_desde and c.created_at and c.created_at.date() < fecha_desde:
            continue
        if fecha_hasta and c.created_at and c.created_at.date() > fecha_hasta:
            continue
        mesa = await Mesa.get(PydanticObjectId(c.mesa_id)) if c.mesa_id else None
        result.append(ComandaFacturacionResponse(
            id=str(c.id),
            numero=c.numero,
            mesa_numero=mesa.numero if mesa else None,
            cliente_nombre=cliente.nombre,
            cliente_apellido=cliente.apellido,
            cliente_cedula=cliente.cedula,
            cliente_telefono=cliente.telefono,
            total=c.total,
            estado=c.estado,
            forma_pago=c.forma_pago,
            created_at=c.created_at,
        ))
    return result


@router.get("/comandas/{comanda_id}")
async def detalle_comanda_facturacion(comanda_id: str, _=RequireMesoneraOrPOS):
    comanda = await Comanda.get(PydanticObjectId(comanda_id))
    if not comanda:
        return {"error": "Comanda no encontrada"}
    cliente = await Cliente.get(PydanticObjectId(comanda.cliente_id)) if comanda.cliente_id else None
    mesa = await Mesa.get(PydanticObjectId(comanda.mesa_id)) if comanda.mesa_id else None
    return {
        "id": str(comanda.id),
        "numero": comanda.numero,
        "mesa": mesa.numero if mesa else None,
        "cliente": {
            "cedula": cliente.cedula,
            "nombre": cliente.nombre,
            "apellido": cliente.apellido,
            "direccion": cliente.direccion,
            "telefono": cliente.telefono,
        } if cliente else {},
        "subtotal": comanda.subtotal,
        "impuesto": comanda.impuesto,
        "total": comanda.total,
        "estado": comanda.estado.value,
        "forma_pago": comanda.forma_pago.value if comanda.forma_pago else None,
        "created_at": comanda.created_at.isoformat() if comanda.created_at else None,
        "detalles": [{"plato": d.plato_nombre, "cantidad": d.cantidad, "precio_unitario": d.precio_unitario, "subtotal": d.subtotal} for d in comanda.detalles],
    }
