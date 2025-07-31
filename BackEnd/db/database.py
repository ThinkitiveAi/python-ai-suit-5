"""
Database connection setup for both SQL and NoSQL databases.
"""
from typing import Optional, AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()
metadata = MetaData()

# Database engines and sessions
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

# MongoDB setup
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_database: Optional[AsyncIOMotorDatabase] = None


def init_sql_database():
    """Initialize SQL database connection."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    try:
        if settings.DATABASE_TYPE in ["postgresql", "mysql"]:
            # For PostgreSQL/MySQL
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.DEBUG
            )
            
            # Async engine for PostgreSQL
            if settings.DATABASE_TYPE == "postgresql":
                async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
                async_engine = create_async_engine(
                    async_url,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=settings.DEBUG
                )
                AsyncSessionLocal = async_sessionmaker(
                    async_engine, 
                    class_=AsyncSession, 
                    expire_on_commit=False
                )
        else:
            # For SQLite
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG
            )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"SQL Database initialized: {settings.DATABASE_TYPE}")
        
    except Exception as e:
        logger.error(f"Failed to initialize SQL database: {e}")
        raise


async def init_mongodb():
    """Initialize MongoDB connection."""
    global mongodb_client, mongodb_database
    
    try:
        if settings.MONGODB_URL:
            mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
            mongodb_database = mongodb_client.get_database("provider_registration")
            
            # Test connection
            await mongodb_client.admin.command('ping')
            logger.info("MongoDB connection established")
        else:
            logger.warning("MongoDB URL not provided")
            
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def get_sql_db() -> Session:
    """Get SQL database session."""
    if not SessionLocal:
        raise RuntimeError("SQL database not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Alias for compatibility
get_db = get_sql_db


async def get_async_sql_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async SQL database session."""
    if not AsyncSessionLocal:
        raise RuntimeError("Async SQL database not initialized")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_mongodb() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance."""
    if not mongodb_database:
        raise RuntimeError("MongoDB not initialized")
    return mongodb_database


async def close_database_connections():
    """Close all database connections."""
    global mongodb_client, engine, async_engine
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")
    
    if engine:
        engine.dispose()
        logger.info("SQL engine disposed")
    
    if async_engine:
        await async_engine.dispose()
        logger.info("Async SQL engine disposed")


# Database initialization based on configuration
def initialize_database():
    """Initialize database based on configuration."""
    if settings.DATABASE_TYPE in ["sqlite", "postgresql", "mysql"]:
        init_sql_database()
    
    # MongoDB can be initialized alongside SQL for hybrid setups
    if settings.MONGODB_URL:
        # MongoDB initialization will be done async in startup event
        pass
