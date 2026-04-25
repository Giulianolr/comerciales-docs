"""Fixtures compartidas para tests."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.main import app
from app.api import deps as api_deps
from app.core.database import get_db as get_db_original


@pytest.fixture
async def test_engine():
    """Engine de SQLite in-memory para tests.

    Se crea UNA SOLA VEZ por sesión de pytest.
    Las tablas se crean una sola vez.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Sesión de test para CADA test individual.

    - Crea una sesión nueva para cada test
    - Limpia (rollback) después de cada test
    - Garantiza aislamiento entre tests
    """
    TestingSessionLocal = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with TestingSessionLocal() as session:
        yield session
        # Rollback de cualquier cambio para mantener BD limpia
        await session.rollback()


@pytest.fixture
async def test_client(test_session):
    """Cliente HTTP async para tests.

    - Override la dependencia get_db en FastAPI
    - Todos los endpoints usan test_session en lugar de BD real
    - Limpia overrides después del test
    """
    async def override_get_db():
        yield test_session

    app.dependency_overrides[api_deps.get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_client_sync(test_engine):
    """Cliente síncrono para WebSocket tests.

    TestClient de FastAPI soporta WebSocket.
    Nota: Este es síncrono, no async. Para WebSocket es necesario.
    """
    import asyncio
    from sqlalchemy.orm import sessionmaker

    # Crear sessionmaker de test
    TestingSessionLocal = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db_sync():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[api_deps.get_db] = override_get_db_sync

    # Inicializar redis_manager para tests desde events module
    from app.core.events import init_redis_manager, reset_redis_manager

    asyncio.run(init_redis_manager(use_fake=True))

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
    reset_redis_manager()
