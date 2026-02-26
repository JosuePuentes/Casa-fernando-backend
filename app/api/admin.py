"""API Administrativa - CRUD platos, categorías, mesas, usuarios."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.plato import Plato, CategoriaPlato
from app.models.mesa import Mesa
from app.schemas.plato import PlatoCreate, PlatoUpdate, PlatoResponse, CategoriaPlatoCreate, CategoriaPlatoResponse
from app.schemas.mesa import MesaCreate, MesaUpdate, MesaResponse
from app.core.dependencies import RequireAdmin

router = APIRouter(prefix="/admin", tags=["Administración"])


# --- Categorías ---
@router.get("/categorias", response_model=list[CategoriaPlatoResponse])
async def listar_categorias(db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(CategoriaPlato).order_by(CategoriaPlato.orden))
    return result.scalars().all()


@router.post("/categorias", response_model=CategoriaPlatoResponse)
async def crear_categoria(data: CategoriaPlatoCreate, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    cat = CategoriaPlato(**data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


# --- Platos ---
@router.get("/platos", response_model=list[PlatoResponse])
async def listar_platos(db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(Plato).options(selectinload(Plato.categoria)).order_by(Plato.nombre))
    return result.scalars().all()


@router.post("/platos", response_model=PlatoResponse)
async def crear_plato(data: PlatoCreate, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    plato = Plato(**data.model_dump())
    db.add(plato)
    await db.flush()
    await db.refresh(plato)
    return plato


@router.put("/platos/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato(plato_id: int, data: PlatoUpdate, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(Plato).where(Plato.id == plato_id))
    plato = result.scalar_one_or_none()
    if not plato:
        raise HTTPException(404, "Plato no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(plato, k, v)
    await db.refresh(plato)
    return plato


@router.delete("/platos/{plato_id}")
async def eliminar_plato(plato_id: int, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(Plato).where(Plato.id == plato_id))
    plato = result.scalar_one_or_none()
    if not plato:
        raise HTTPException(404, "Plato no encontrado")
    await db.delete(plato)
    return {"ok": True}


# --- Mesas ---
@router.get("/mesas", response_model=list[MesaResponse])
async def listar_mesas(db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(Mesa).order_by(Mesa.numero))
    return result.scalars().all()


@router.post("/mesas", response_model=MesaResponse)
async def crear_mesa(data: MesaCreate, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    r = await db.execute(select(Mesa).where(Mesa.numero == data.numero))
    if r.scalar_one_or_none():
        raise HTTPException(400, f"Ya existe una mesa con número {data.numero}")
    mesa = Mesa(**data.model_dump())
    db.add(mesa)
    await db.flush()
    await db.refresh(mesa)
    return mesa


@router.put("/mesas/{mesa_id}", response_model=MesaResponse)
async def actualizar_mesa(mesa_id: int, data: MesaUpdate, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(Mesa).where(Mesa.id == mesa_id))
    mesa = result.scalar_one_or_none()
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(mesa, k, v)
    await db.refresh(mesa)
    return mesa


@router.delete("/mesas/{mesa_id}")
async def eliminar_mesa(mesa_id: int, db: AsyncSession = Depends(get_db), _=Depends(RequireAdmin)):
    result = await db.execute(select(Mesa).where(Mesa.id == mesa_id))
    mesa = result.scalar_one_or_none()
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")
    mesa.activa = 0
    await db.refresh(mesa)
    return {"ok": True, "mensaje": "Mesa desactivada"}
