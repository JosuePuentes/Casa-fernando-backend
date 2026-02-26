"""Dependencias de FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, RolUsuario
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
        )
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    result = await db.execute(select(User).where(User.id == int(user_id), User.activo == 1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_roles(*roles: RolUsuario):
    """Dependencia que verifica que el usuario tenga uno de los roles permitidos."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este recurso",
            )
        return user
    return role_checker


# Dependencias por rol
RequireAdmin = Depends(require_roles(RolUsuario.ADMIN))
RequireMesonera = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA))
RequirePOS = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.PUNTO_VENTA))
RequireAdminOrMesonera = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA))
RequireAdminOrPOS = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.PUNTO_VENTA))
RequireMesoneraOrPOS = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA, RolUsuario.PUNTO_VENTA))
