"""
Alembic environment configuration for SQLModel integration.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los modelos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar los modelos de SQLModel para autogenerate
from src.core.models import SQLModel  # noqa: E402

# Configurar la URL de la base de datos desde la variable de entorno
database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/jota")
config.set_main_option("sqlalchemy.url", database_url)

# target_metadata es el MetaData de SQLModel
target_metadata = SQLModel.metadata


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
        compare_type=True,  # Detectar cambios de tipo de columna
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detectar cambios de tipo de columna
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
