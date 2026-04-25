"""Endpoints de autenticación."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import create_access_token, verify_password
from app.models.core import User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Request para login."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Respuesta con datos del usuario."""
    id: str
    email: str
    name: str
    role: str
    store_id: str | None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response exitoso de login."""
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Login con email y contraseña.

    Retorna un JWT token válido por 60 minutos + datos del usuario.
    """
    stmt = select(User).where(User.email == request.email)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    # Crear token con store_id incluido
    access_token = create_access_token(
        user_id=user.id,
        store_id=user.store_id
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            store_id=str(user.store_id) if user.store_id else None
        )
    )
