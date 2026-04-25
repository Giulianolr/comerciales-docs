"""FastAPI WebSocket dependencies."""

from uuid import UUID

from fastapi import Depends, WebSocketException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_access_token
from app.models.core import User


async def get_current_user_ws(
    query_params: dict[str, str],
    session: AsyncSession = Depends(get_db),
) -> User:
    """Extrae y valida el usuario de un token en query params para WebSocket.

    WebSocket no soporta headers nativamente, así que usamos query params.
    El cliente debe conectar a: ws://server/ws?token=<JWT>

    Args:
        query_params: Dict de query parameters (?token=ey...)
        session: Sesión de BD async

    Returns:
        User instance si el token es válido

    Raises:
        WebSocketException 1008 (Policy Violation) si:
        - No hay token en query params
        - Token es inválido o expirado
        - Usuario no existe
    """
    # 1. Extraer token de query params
    token = query_params.get("token")
    if not token:
        raise WebSocketException(code=1008, reason="Missing token in query params")

    # 2. Validar token
    user_id_str = verify_access_token(token)
    if user_id_str is None:
        raise WebSocketException(code=1008, reason="Invalid or expired token")

    # 3. Convertir user_id a UUID
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise WebSocketException(code=1008, reason="Invalid token format")

    # 4. Obtener usuario de la BD
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise WebSocketException(code=1008, reason="User not found")

    return user
