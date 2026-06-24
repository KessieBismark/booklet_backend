"""Alembic environment. Migrations run synchronously; the async driver (if any) is
swapped for a sync one so this works whether the app is sync or async."""
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Project root is the parent of migrations/ — make config/ and models/ importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.dbconfig import Base  # noqa: E402
import models  # noqa: E402,F401  -- importing the package registers EVERY model on Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set; export it before running alembic.")
    # Alembic migrations are synchronous — use a sync driver.
    return (
        url.replace("postgresql+asyncpg", "postgresql+psycopg2")
        .replace("mysql+aiomysql", "mysql+pymysql")
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
