import os

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _normalize_database_url(url: str) -> str:
    """Use psycopg 3, which supports Neon URLs with sslmode=require."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql+pg8000://"):
        return "postgresql+psycopg://" + url[len("postgresql+pg8000://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


# Keep the API importable even when a deployment is missing DATABASE_URL.
# Readiness checks report the configuration problem; database routes return 503.
engine = (
    create_engine(_normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    if DATABASE_URL
    else None
)

SessionLocal = (
    sessionmaker(bind=engine, autocommit=False, autoflush=False)
    if engine is not None
    else None
)


def get_db():
    if SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured. Set DATABASE_URL in the backend deployment environment.",
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
