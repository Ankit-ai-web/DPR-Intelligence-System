from logging.config import fileConfig
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from alembic import context

from app.models.base import Base

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.dpr_project import DPRProject
from app.models.document import Document
from app.models.analysis import DocumentAnalysis


# Load environment variables from .env
load_dotenv()


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not set")

    # Use pg8000 instead of psycopg
    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql+pg8000://"
    )

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not set")

    # Use pg8000 instead of psycopg
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+pg8000://",
        1,
    ).replace(
        "postgresql+psycopg://",
        "postgresql+pg8000://",
        1,
    )

    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()