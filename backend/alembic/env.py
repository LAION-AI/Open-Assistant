@@ -1,63 +1,61 @@
import logging
from alembic import context
from oasst_backend import models  # noqa: F401
from sqlalchemy import engine_from_config, pool
# Read in the Alembic config file.
config = context.config
# Set up loggers.
if config.config_file_name is not None:
    logging.config.fileConfig(config.config_file_name)
# Add the model's MetaData object here for 'autogenerate' support.
target_metadata = models.Base.metadata
# Other values from the config file can be acquired as follows:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though
    an Engine is acceptable here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()
def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.get_context()._ensure_version_table()
            connection.execute("LOCK TABLE alembic_version IN ACCESS EXCLUSIVE MODE")
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
