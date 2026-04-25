"""
Alembic environment configuration.
Soporta migraciones asincronías con asyncpg.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# Importar Base metadata y DatabaseConfig
from app.models import Base
from app.core.database import DatabaseConfig

config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Definir target_metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'."""
    url = DatabaseConfig().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        as_sql=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Ejecutar migraciones con la conexión proporcionada."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Ejecutar migraciones en modo 'online' (asincrónico)."""
    url = DatabaseConfig().database_url

    engine = create_async_engine(
        url,
        poolclass=pool.NullPool,
        echo=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


# Para autogenerate, usar offline mode (no requiere conexión)
if context.is_offline_mode():
    run_migrations_offline()
else:
    try:
        asyncio.run(run_migrations_online())
    except Exception:
        # Si falla la conexión, usar offline mode para autogenerate
        run_migrations_offline()
