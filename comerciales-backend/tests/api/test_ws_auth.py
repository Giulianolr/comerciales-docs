"""Tests para autenticación de WebSocket (TDD - RED → GREEN → REFACTOR).
Verifica: Extracción de token de query params, validación y user retrieval.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps_ws import get_current_user_ws
from app.core.security import create_access_token, hash_password
from app.models.core import Store, User


@pytest.fixture
async def user_with_token(test_session: AsyncSession):
    """Crea un usuario y su token JWT válido."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Crear store y usuario
    store = Store(id=store_id, name="Test Store", address="123 Main St", owner_id=user_id)
    owner_user = User(
        id=user_id,
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash=hash_password("owner_pass"),
        role="ADMIN",
    )
    test_session.add(store)
    test_session.add(owner_user)
    await test_session.commit()

    # Crear token
    token = create_access_token(user_id)

    return {
        "user_id": user_id,
        "store_id": store_id,
        "token": token,
        "user": owner_user,
    }


class TestWebSocketAuth:
    """Tests para autenticación WebSocket."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(
        self, test_session: AsyncSession, user_with_token
    ):
        """
        DADO: Un query param con un token JWT válido
        CUANDO: Llamamos get_current_user_ws
        ENTONCES: Retorna el usuario asociado al token
        """
        user_id = user_with_token["user_id"]
        token = user_with_token["token"]

        # Mock de receive con query_params
        receive = MagicMock()
        query_params = {"token": token}

        # Llamar a la dependencia
        user = await get_current_user_ws(query_params=query_params, session=test_session)

        # Verificar que se retorna el usuario correcto
        assert user is not None
        assert str(user.id) == str(user_id)

    @pytest.mark.asyncio
    async def test_invalid_token_raises_websocket_exception_1008(
        self, test_session: AsyncSession
    ):
        """
        DADO: Un query param con un token JWT inválido
        CUANDO: Llamamos get_current_user_ws
        ENTONCES: Lanza WebSocketException con código 1008 (Policy Violation)
        """
        invalid_token = "invalid.token.string"
        query_params = {"token": invalid_token}

        # Debe lanzar WebSocketException con código 1008
        with pytest.raises(WebSocketException) as exc_info:
            await get_current_user_ws(query_params=query_params, session=test_session)

        # Verificar código 1008
        assert exc_info.value.code == 1008

    @pytest.mark.asyncio
    async def test_missing_token_raises_websocket_exception_1008(
        self, test_session: AsyncSession
    ):
        """
        DADO: Un request sin query param 'token'
        CUANDO: Llamamos get_current_user_ws
        ENTONCES: Lanza WebSocketException con código 1008
        """
        query_params = {}  # Sin token

        # Debe lanzar WebSocketException con código 1008
        with pytest.raises(WebSocketException) as exc_info:
            await get_current_user_ws(query_params=query_params, session=test_session)

        # Verificar código 1008
        assert exc_info.value.code == 1008

    @pytest.mark.asyncio
    async def test_expired_token_raises_websocket_exception_1008(
        self, test_session: AsyncSession
    ):
        """
        DADO: Un query param con un token JWT expirado
        CUANDO: Llamamos get_current_user_ws
        ENTONCES: Lanza WebSocketException con código 1008
        """
        from datetime import timedelta

        user_id = uuid.uuid4()
        # Crear token con expiración en el pasado
        expired_token = create_access_token(user_id, timedelta(seconds=-1))
        query_params = {"token": expired_token}

        # Debe lanzar WebSocketException con código 1008
        with pytest.raises(WebSocketException) as exc_info:
            await get_current_user_ws(query_params=query_params, session=test_session)

        # Verificar código 1008
        assert exc_info.value.code == 1008

    @pytest.mark.asyncio
    async def test_token_user_not_found_raises_websocket_exception_1008(
        self, test_session: AsyncSession
    ):
        """
        DADO: Un query param con un token JWT válido pero para un user_id que no existe
        CUANDO: Llamamos get_current_user_ws
        ENTONCES: Lanza WebSocketException con código 1008
        """
        nonexistent_user_id = uuid.uuid4()
        # Token válido pero para usuario inexistente
        token = create_access_token(nonexistent_user_id)
        query_params = {"token": token}

        # Debe lanzar WebSocketException con código 1008
        with pytest.raises(WebSocketException) as exc_info:
            await get_current_user_ws(query_params=query_params, session=test_session)

        # Verificar código 1008
        assert exc_info.value.code == 1008
