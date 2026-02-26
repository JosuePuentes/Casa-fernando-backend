"""Seguridad y autenticación."""
import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_for_bcrypt(password: str) -> str:
    """Bcrypt limita a 72 bytes. Si es más largo, pre-hasheamos con SHA256."""
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        return hashlib.sha256(pw_bytes).hexdigest()
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_normalize_for_bcrypt(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(_normalize_for_bcrypt(password))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
