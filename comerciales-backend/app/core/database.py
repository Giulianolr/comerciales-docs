"""Configuración de base de datos asincrónica.
SQLAlchemy 2.0 + asyncpg + PostgreSQL 15
"""

import os
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker


class DatabaseConfig(BaseSettings):
    """Configuración de base de datos desde variables de entorno."""

    host: str = "localhost"
    port: int = 5432
    user: str = "comerciales"
    password: str = "comerciales2026"
    name: str = "comerciales"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    model_config = ConfigDict(env_prefix="DB_", case_sensitive=False)

    @property
    def database_url(self) -> str:
        """Construye la DATABASE_URL para asyncpg."""
        # Usar DATABASE_URL si está disponible en variables de entorno
        if db_url := os.getenv('DATABASE_URL'):
            return db_url
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[sessionmaker] = None


def get_config() -> DatabaseConfig:
    """Obtiene la configuración de BD."""
    return DatabaseConfig()


def get_engine() -> AsyncEngine:
    """Obtiene o crea el engine async."""
    global _engine
    if _engine is None:
        config = get_config()
        _engine = create_async_engine(
            config.database_url,
            echo=config.echo,
            future=True,
            pool_pre_ping=True,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            connect_args={"ssl": False},
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Obtiene o crea la sessionmaker."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


async def get_db() -> AsyncSession:
    """Dependency injection de sesión de BD."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
