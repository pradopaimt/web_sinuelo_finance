from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# garante que o pacote backend seja encontrado
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# importa apenas o Base (sem engine!)
from backend.models import Base  

# Carrega config do Alembic
config = context.config

import os

# força pegar do ambiente
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL não definido")

config.set_main_option("sqlalchemy.url", database_url)
# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define os metadados dos modelos para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Rodar migrações em modo offline (gera SQL em texto)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Rodar migrações em modo online (direto no banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
