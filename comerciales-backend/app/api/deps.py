"""Dependencias compartidas para la API."""

from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as get_db_original
from app.core.security import verify_access_token
from app.models.core import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtener sesión de base de datos."""
    async for session in get_db_original():
        yield session


async def get_store_id(x_store_id: str = Header(...)) -> UUID:
    """Extraer store_id del header X-Store-ID."""
    try:
        return UUID(x_store_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-Store-ID header")


async def get_current_user(
    token: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Dependency que extrae el usuario autenticado del token JWT.

    Espera el header: Authorization: Bearer <token>
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token.startswith("Bearer "):
        raise credentials_exception

    token_str = token[7:]

    user_id = verify_access_token(token_str)
    if user_id is None:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user
