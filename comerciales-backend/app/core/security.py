"""Utilidades de seguridad: password hashing y JWT tokens."""

from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Optional

import jwt
from passlib.context import CryptContext

TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str | UUID,
    expires_delta: timedelta | None = None,
    store_id: Optional[str | UUID] = None
) -> str:
    """Crea un JWT token con el user_id y store_id.

    Args:
        user_id: ID del usuario
        expires_delta: Timedelta personalizado para expiración (default: TOKEN_EXPIRE_MINUTES)
        store_id: ID del store (opcional)

    Returns:
        JWT token como string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "store_id": str(store_id) if store_id else None,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str) -> str | None:
    """Verifica y extrae el user_id de un JWT token.

    Args:
        token: JWT token a verificar

    Returns:
        user_id (string) si el token es válido, None si es inválido o expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True})
        user_id = payload.get("sub")
        return user_id if user_id else None
    except jwt.InvalidTokenError:
        return None
