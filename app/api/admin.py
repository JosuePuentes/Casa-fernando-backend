"""API Administrativa - CRUD platos, categorías, mesas."""
from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from app.models.plato import Plato, CategoriaPlato
from app.models.mesa import Mesa
from app.schemas.plato import PlatoCreate, PlatoUpdate, PlatoResponse, CategoriaPlatoCreate, CategoriaPlatoResponse
from app.schemas.mesa import MesaCreate, MesaUpdate, MesaResponse
from app.core.dependencies import RequireAdmin

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.get("/categorias", response_model=list[CategoriaPlatoResponse])
async def listar_categorias(_=RequireAdmin):
    cats = await CategoriaPlato.find().sort(CategoriaPlato.orden).to_list()
    return [CategoriaPlatoResponse(id=str(c.id), **c.model_dump(exclude={"id"})) for c in cats]


@router.post("/categorias", response_model=CategoriaPlatoResponse)
async def crear_categoria(data: CategoriaPlatoCreate, _=RequireAdmin):
    cat = CategoriaPlato(**data.model_dump())
    await cat.insert()
    return CategoriaPlatoResponse(id=str(cat.id), **cat.model_dump(exclude={"id"}))


@router.get("/platos", response_model=list[PlatoResponse])
async def listar_platos(_=RequireAdmin):
    platos = await Plato.find().sort(Plato.nombre).to_list()
    cat_map = {}
    for p in platos:
        if p.categoria_id and p.categoria_id not in cat_map:
            cat = await CategoriaPlato.get(PydanticObjectId(p.categoria_id))
            cat_map[p.categoria_id] = CategoriaPlatoResponse(id=str(cat.id), nombre=cat.nombre, descripcion=cat.descripcion, orden=cat.orden) if cat else None
    return [
        PlatoResponse(id=str(p.id), categoria_id=p.categoria_id, categoria=cat_map.get(p.categoria_id), **p.model_dump(exclude={"id", "categoria_id"}))
        for p in platos
    ]


@router.post("/platos", response_model=PlatoResponse)
async def crear_plato(data: PlatoCreate, _=RequireAdmin):
    plato = Plato(**data.model_dump())
    await plato.insert()
    return PlatoResponse(id=str(plato.id), categoria_id=plato.categoria_id, categoria=None, **plato.model_dump(exclude={"id", "categoria_id"}))


@router.put("/platos/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato(plato_id: str, data: PlatoUpdate, _=RequireAdmin):
    plato = await Plato.get(PydanticObjectId(plato_id))
    if not plato:
        raise HTTPException(404, "Plato no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(plato, k, v)
    await plato.save()
    return PlatoResponse(id=str(plato.id), categoria_id=plato.categoria_id, categoria=None, **plato.model_dump(exclude={"id", "categoria_id"}))


@router.delete("/platos/{plato_id}")
async def eliminar_plato(plato_id: str, _=RequireAdmin):
    plato = await Plato.get(PydanticObjectId(plato_id))
    if not plato:
        raise HTTPException(404, "Plato no encontrado")
    await plato.delete()
    return {"ok": True}


@router.get("/mesas", response_model=list[MesaResponse])
async def listar_mesas(_=RequireAdmin):
    mesas = await Mesa.find().sort(Mesa.numero).to_list()
    return [MesaResponse(id=str(m.id), activa=m.activa, **m.model_dump(exclude={"id"})) for m in mesas]


@router.post("/mesas", response_model=MesaResponse)
async def crear_mesa(data: MesaCreate, _=RequireAdmin):
    if await Mesa.find_one(Mesa.numero == data.numero):
        raise HTTPException(400, f"Ya existe una mesa con número {data.numero}")
    mesa = Mesa(**data.model_dump())
    await mesa.insert()
    return MesaResponse(id=str(mesa.id), activa=mesa.activa, **mesa.model_dump(exclude={"id"}))


@router.put("/mesas/{mesa_id}", response_model=MesaResponse)
async def actualizar_mesa(mesa_id: str, data: MesaUpdate, _=RequireAdmin):
    mesa = await Mesa.get(PydanticObjectId(mesa_id))
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(mesa, k, v)
    await mesa.save()
    return MesaResponse(id=str(mesa.id), activa=mesa.activa, **mesa.model_dump(exclude={"id"}))


@router.delete("/mesas/{mesa_id}")
async def eliminar_mesa(mesa_id: str, _=RequireAdmin):
    mesa = await Mesa.get(PydanticObjectId(mesa_id))
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")
    mesa.activa = 0
    await mesa.save()
    return {"ok": True, "mensaje": "Mesa desactivada"}
