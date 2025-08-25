from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from core import constants
from core.database import Base

# ✅ Import your models so Alembic sees them
import models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Inject DB URL from constants.py
config.set_main_option("sqlalchemy.url", constants.POSTGRES_URI)


# ✅ Add include_object here (this stops alembic from auto deleting existing tables)
def include_object(object, name, type_, reflected, compare_to):
    """
    Control which tables/indexes Alembic should manage.
    """
    checkpoint_tables = {
        "checkpoints",
        "checkpoint_writes",
        "checkpoint_blobs",
        "checkpoint_migrations",
    }

    if type_ == "table":
        # ✅ Exclude checkpoint-related tables from Alembic
        if name in checkpoint_tables:
            return False

    if type_ == "index":
        # ✅ Skip indexes belonging to checkpoint-related tables
        if object.table.name in checkpoint_tables:
            return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,  # ✅ added
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,  # ✅ added
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
