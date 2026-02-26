"""API de autenticación."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserLogin, UserCreate, UserResponse, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user, RequireAdmin

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login - retorna token JWT."""
    result = await db.execute(select(User).where(User.email == data.email, User.activo == 1))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    token = create_access_token(data={"sub": str(user.id), "rol": user.rol.value})
    return Token(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            rol=user.rol,
        ),
    )


@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registro de cliente (área pública)."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        nombre=data.nombre,
        apellido=data.apellido,
        rol=data.rol,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        rol=user.rol,
    )


@router.post("/register/admin", response_model=UserResponse)
async def register_admin(data: UserCreate, _: User = Depends(RequireAdmin), db: AsyncSession = Depends(get_db)):
    """Registro de empleados (solo admin)."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        nombre=data.nombre,
        apellido=data.apellido,
        rol=data.rol,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        rol=user.rol,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Obtener usuario actual."""
    return UserResponse(
        id=user.id,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        rol=user.rol,
    )
