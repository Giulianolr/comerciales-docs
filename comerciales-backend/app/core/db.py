"""
Configuración de base de datos asincrónica.
SQLAlchemy 2.0 + asyncpg + PostgreSQL 15
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://comerciales:comerciales2026@localhost:5432/comerciales"

# Engine asincrónico
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncSession:
    """Dependency injection de sesión de BD."""
    async with AsyncSessionLocal() as session:
        yield session
