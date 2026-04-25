"""Tests para utilidades de seguridad: password hashing y JWT tokens."""

import pytest
from datetime import timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    TOKEN_EXPIRE_MINUTES,
)


def test_hash_password():
    """Verifica que hash_password genera un hash válido."""
    password = "my_secure_password_123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
    # Phpass hashes start with $2a$, $2b$, $2x$, or $2y$
    assert hashed.startswith("$2")


def test_verify_password_correct():
    """Verifica que verify_password funciona con password correcto."""
    password = "my_secure_password_123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Verifica que verify_password falla con password incorrecto."""
    password = "my_secure_password_123"
    wrong_password = "different_password"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_create_access_token():
    """Verifica que create_access_token genera un JWT válido."""
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    token = create_access_token(user_id)

    assert isinstance(token, str)
    assert len(token) > 0
    # JWT tiene formato: header.payload.signature
    assert token.count(".") == 2


def test_create_access_token_with_custom_expires():
    """Verifica que se puede especificar tiempo de expiración personalizado."""
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    expires_delta = timedelta(hours=2)
    token = create_access_token(user_id, expires_delta)

    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_access_token_valid():
    """Verifica que verify_access_token extrae el user_id correctamente."""
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    token = create_access_token(user_id)

    extracted_user_id = verify_access_token(token)

    assert extracted_user_id == user_id


def test_verify_access_token_invalid():
    """Verifica que verify_access_token devuelve None con token inválido."""
    invalid_token = "invalid.token.string"

    result = verify_access_token(invalid_token)

    assert result is None


def test_verify_access_token_expired():
    """Verifica que verify_access_token falla con token expirado."""
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    # Crear token con expiración en el pasado
    expires_delta = timedelta(seconds=-1)
    token = create_access_token(user_id, expires_delta)

    result = verify_access_token(token)

    assert result is None
