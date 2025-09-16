from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine for PostgreSQL
if settings.database_url.startswith("postgresql://"):
    # Convert to async URL
    async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(
        async_database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
else:
    # Fallback to SQLite for development
    engine = create_async_engine(
        "sqlite+aiosqlite:///./open_edu.db",
        echo=False,
        connect_args={"check_same_thread": False}
    )

# Create sync engine for migrations
if settings.database_url.startswith("postgresql://"):
    sync_engine = create_engine(settings.database_url)
else:
    sync_engine = create_engine("sqlite:///./open_edu.db")

# Session factories
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for models
Base = declarative_base()

# Metadata
metadata = MetaData()


async def get_async_db():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """Dependency to get sync database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
