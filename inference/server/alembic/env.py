import asyncio
from logging.config import fileConfig

import sqlmodel
from alembic import context
from loguru import logger
from oasst_inference_server import models  # noqa: F401
from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.ext.asyncio import AsyncEngine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = sqlmodel.SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.get_context()._ensure_version_table()
        connection.execute(text("LOCK TABLE alembic_version IN ACCESS EXCLUSIVE MODE"))
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    connectable = AsyncEngine(connectable)

    logger.info(f"Running migrations on {connectable.url}")

    async with connectable.connect() as connection:
        logger.info("Connected to database")
        await connection.run_sync(do_run_migrations)
        logger.info("Migrations complete")
    logger.info("Disconnecting from database")
    await connectable.dispose()
    logger.info("Disconnected from database")


if context.is_offline_mode():
    run_migrations_offline()
else:
    connection = config.attributes.get("connection", None)
    if connection is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connection)
