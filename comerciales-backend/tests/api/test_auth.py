"""Tests para el endpoint de autenticación."""

import pytest
from decimal import Decimal

from app.models.core import Store, User


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(test_client, test_session):
    """Verifica que login con credenciales inválidas devuelve 401."""
    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local Test",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="1234",
        password_hash="hashed",
        role="OPERADOR",
    )
    test_session.add(user)
    await test_session.flush()

    response = await test_client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "password123"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_wrong_password(test_client, test_session):
    """Verifica que login con contraseña incorrecta devuelve 401."""
    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local Test",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    from app.core.security import hash_password

    user = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="1234",
        password_hash=hash_password("correct_password"),
        role="OPERADOR",
    )
    test_session.add(user)
    await test_session.flush()

    response = await test_client.post(
        "/api/v1/auth/login",
        json={"email": "operador@example.com", "password": "wrong_password"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_valid_credentials(test_client, test_session):
    """Verifica que login con credenciales válidas devuelve token."""
    from app.core.security import hash_password

    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash=hash_password("owner_pass"),
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local Test",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="1234",
        password_hash=hash_password("operador_password"),
        role="OPERADOR",
    )
    test_session.add(user)
    await test_session.flush()

    response = await test_client.post(
        "/api/v1/auth/login",
        json={"email": "operador@example.com", "password": "operador_password"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_returns_correct_user_id_in_token(test_client, test_session):
    """Verifica que el token contiene el user_id correcto."""
    from app.core.security import hash_password, verify_access_token

    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash=hash_password("owner_pass"),
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local Test",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="1234",
        password_hash=hash_password("operador_password"),
        role="OPERADOR",
    )
    test_session.add(user)
    await test_session.flush()

    response = await test_client.post(
        "/api/v1/auth/login",
        json={"email": "operador@example.com", "password": "operador_password"}
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    extracted_user_id = verify_access_token(token)
    assert extracted_user_id == str(user.id)
