# app/core/database.py
import logging
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from core import constants 

logger = logging.getLogger(__name__)

# --- SQLAlchemy Engine Setup ---
engine = create_engine(
    constants.POSTGRES_URI,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True,  # Make False if too noisy
    future=True,
    connect_args={
        "options": "-c timezone=utc",
        "application_name": "Agent 2.0",
        "connect_timeout": 10,
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base for models
Base = declarative_base()


# --- ORM Helpers ---
def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for services."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all_tables():
    """Create ORM tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("All ORM tables created successfully")


def drop_all_tables():
    """Drop ORM tables (dangerous)."""
    Base.metadata.drop_all(bind=engine)
    logger.warning("All ORM tables dropped")


# --- Custom Initialization (pgvector + semantic_memories) ---
def initialize_database():
    """
    Initialize PostgreSQL with pgvector and semantic_memories table.
    Runs once at startup alongside ORM.
    """
    try:
        with engine.begin() as conn:
            # Ensure pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

            # Semantic memory table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance TEXT DEFAULT 'medium',
                    embedding vector(768),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """))

            # ANN index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_semantic_memories_embedding
                ON semantic_memories
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """))

        logger.info("PostgreSQL database initialized with pgvector + semantic_memories")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
