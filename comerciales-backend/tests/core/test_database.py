"""Tests para configuración de base de datos asincrónica."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine


@pytest.mark.asyncio
async def test_database_config_from_env(monkeypatch):
    """RED: Verifica que DatabaseConfig se cargue desde env."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "comerciales")
    monkeypatch.setenv("DB_PASSWORD", "comerciales2026")
    monkeypatch.setenv("DB_NAME", "comerciales")

    from app.core.database import DatabaseConfig

    config = DatabaseConfig()

    assert config.host == "localhost"
    assert config.port == 5432
    assert config.user == "comerciales"
    assert config.password == "comerciales2026"
    assert config.name == "comerciales"


@pytest.mark.asyncio
async def test_database_url_generation(monkeypatch):
    """RED: Verifica que la DATABASE_URL se construya correctamente."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "comerciales")
    monkeypatch.setenv("DB_PASSWORD", "comerciales2026")
    monkeypatch.setenv("DB_NAME", "comerciales")

    from app.core.database import DatabaseConfig

    config = DatabaseConfig()
    expected_url = "postgresql+asyncpg://comerciales:comerciales2026@localhost:5432/comerciales"

    assert config.database_url == expected_url


@pytest.mark.asyncio
async def test_async_engine_creation(monkeypatch):
    """RED: Verifica que el engine async se cree correctamente."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "comerciales")
    monkeypatch.setenv("DB_PASSWORD", "comerciales2026")
    monkeypatch.setenv("DB_NAME", "comerciales")

    from app.core.database import get_engine

    engine = get_engine()

    assert isinstance(engine, AsyncEngine)
    assert "postgresql+asyncpg" in str(engine.url)

    await engine.dispose()


@pytest.mark.asyncio
async def test_session_factory_creation(monkeypatch):
    """RED: Verifica que la sessionmaker se cree correctamente."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "comerciales")
    monkeypatch.setenv("DB_PASSWORD", "comerciales2026")
    monkeypatch.setenv("DB_NAME", "comerciales")

    from app.core.database import get_session_factory

    session_factory = get_session_factory()

    assert session_factory is not None
    assert callable(session_factory)
