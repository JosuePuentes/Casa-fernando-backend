"""API de autenticación."""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from app.schemas.auth import UserLogin, UserCreate, UserResponse, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user, RequireAdmin

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    user = await User.find_one(User.email == data.email, User.activo == 1)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = create_access_token(data={"sub": str(user.id), "rol": user.rol.value})
    return Token(
        access_token=token,
        user=UserResponse(id=str(user.id), email=user.email, nombre=user.nombre, apellido=user.apellido, rol=user.rol),
    )


@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate):
    try:
        if await User.find_one(User.email == data.email):
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            nombre=data.nombre,
            apellido=data.apellido,
            rol=data.rol,
        )
        await user.insert()
        return UserResponse(id=str(user.id), email=user.email, nombre=user.nombre, apellido=user.apellido, rol=user.rol)
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Error en register: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/admin", response_model=UserResponse)
async def register_admin(data: UserCreate, _: User = RequireAdmin):
    if await User.find_one(User.email == data.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        nombre=data.nombre,
        apellido=data.apellido,
        rol=data.rol,
    )
    await user.insert()
    return UserResponse(id=str(user.id), email=user.email, nombre=user.nombre, apellido=user.apellido, rol=user.rol)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(id=str(user.id), email=user.email, nombre=user.nombre, apellido=user.apellido, rol=user.rol)
