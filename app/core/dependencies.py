"""Dependencias de FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from beanie import PydanticObjectId
from app.models.user import User, RolUsuario
from app.core.security import decode_token

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="No se proporcionó token de autenticación")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    try:
        user = await User.get(PydanticObjectId(user_id))
    except Exception:
        user = None
    if not user or user.activo != 1:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_roles(*roles: RolUsuario):
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.rol not in roles:
            raise HTTPException(status_code=403, detail="No tiene permisos para acceder a este recurso")
        return user
    return role_checker


RequireAdmin = Depends(require_roles(RolUsuario.ADMIN))
RequireMesonera = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA))
RequirePOS = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.PUNTO_VENTA))
RequireAdminOrMesonera = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA))
RequireAdminOrPOS = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.PUNTO_VENTA))
RequireMesoneraOrPOS = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA, RolUsuario.PUNTO_VENTA, RolUsuario.COCINERO))
RequirePanelAdmin = Depends(require_roles(RolUsuario.ADMIN, RolUsuario.MESONERA, RolUsuario.PUNTO_VENTA, RolUsuario.COCINERO))
