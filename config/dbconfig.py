
import logging
import os
import ssl
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urlunparse

from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv('API_V1_STR')





"""
Database Configuration

Manages database connections, connection pooling, and settings validation.
Supports PostgreSQL, MySQL, and SQLite with async drivers.

Environment variables:
    DATABASE_URL: Database connection URL (required)
    SECRET_KEY: JWT secret key (required, min 32 chars)
    PASSWORD_ENCRYPTION_KEY: Password encryption key (required, min 32 chars)
    ENVIRONMENT: Environment (development/staging/production, default: development)
    DEBUG: Enable debug mode (default: false)
    DB_POOL_SIZE: Connection pool size (default: 5)
    DB_MAX_OVERFLOW: Max overflow connections (default: 10)
    DB_POOL_TIMEOUT: Connection timeout in seconds (default: 30)
    DB_ECHO: Log SQL statements (default: false)
    REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime (days, default: 7, used by auto-refresh)
"""
# ============================================================================
# Settings Configuration
# ============================================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are validated on initialization.
    """
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    database_url: str = Field(
        ...,
        description="Async database URL (e.g., postgresql+asyncpg://...)",
        min_length=10
    )
    
    db_pool_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of database connections to maintain"
    )
    
    db_max_overflow: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Maximum overflow connections when pool exhausted"
    )
    
    db_pool_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Connection acquisition timeout (seconds)"
    )
    
    db_pool_recycle: int = Field(
        default=3600,
        ge=60,
        description="Recycle connections after N seconds (prevents stale connections)"
    )
    
    db_echo: bool = Field(
        default=False,
        description="Log all SQL statements (disable in production)"
    )
    
    db_ssl_mode: str = Field(
        default="prefer",
        description="SSL mode (disable/allow/prefer/require)"
    )
    
    # ========================================================================
    # Security Configuration
    # ========================================================================
    
    secret_key: str = Field(
        ...,
        description="Secret key for JWT signing",
        min_length=32
    )
    
    password_encryption_key: str = Field(
        ...,
        description="Key for password encryption",
        min_length=32
    )
    
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    # ========================================================================
    # Token Configuration
    # ========================================================================
    
    access_token_expire_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="Access token expiration (minutes, max 24h)"
    )
    
    refresh_token_expire_days: float = Field(
        default=7,
        ge=1,
        le=365,
        description="Refresh token expiration (days, max 1 year)"
    )
    
    # ========================================================================
    # Environment Configuration
    # ========================================================================
    
    environment: str = Field(
        default="development",
        description="Execution environment (development/staging/production)"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # ========================================================================
    # API Configuration
    # ========================================================================
    
    api_v1_str: str = Field(
        default=APP_VERSION,
        description="API v1 endpoint prefix"
    )
    
    # ========================================================================
    # Validation & Properties
    # ========================================================================
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra environment variables
    }
    
    @field_validator('secret_key', 'password_encryption_key')
    @classmethod
    def validate_security_keys(cls, v: str) -> str:
        """Validate security keys meet minimum requirements."""
        if len(v) < 32:
            raise ValueError("Keys must be at least 32 characters")
        
        # Prevent test/weak keys in production
        weak_patterns = ['test', 'dev', '12345', 'password', 'secret']
        if any(pattern in v.lower() for pattern in weak_patterns):
            logger.warning("Using weak security key pattern")
        
        return v
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid = {'development', 'staging', 'production'}
        if v not in valid:
            raise ValueError(f"Environment must be one of {valid}")
        return v
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        try:
            urlparse(v)
        except Exception as e:
            raise ValueError(f"Invalid database URL: {e}")
        
        # Check for async driver
        async_drivers = ('asyncpg', 'aiomysql', 'aiosqlite')
        if not any(driver in v for driver in async_drivers):
            logger.warning(
                "Database URL may not be using async driver. "
                "Consider using postgresql+asyncpg://, mysql+aiomysql://, etc."
            )
        
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment ==  'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == 'development'
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self.environment == 'staging'


# ============================================================================
# Load Settings
# ============================================================================

try:
    settings = Settings()
    logger.info(
        f"Settings loaded successfully: "
        f"environment={settings.environment}, "
        f"app_version={settings.api_v1_str}, "
        f"db_pool_size={settings.db_pool_size}"
    )
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    raise SystemExit(1)


# ============================================================================
# Database Engine Configuration
# ============================================================================

def get_database_url() -> str:
    """
    Get the database URL, converting to async driver if needed.
    
    Converts:
        postgresql://... → postgresql+asyncpg://...
        mysql://... → mysql+aiomysql://...
        sqlite://... → sqlite+aiosqlite://...
    
    Returns:
        Async database URL
    
    Raises:
        ValueError: If URL cannot be converted
    """
    url = settings.database_url
    
    scheme_mapping = {
        'postgresql': 'postgresql+asyncpg',
        'postgres': 'postgresql+asyncpg',
        'mysql': 'mysql+aiomysql',
        'sqlite': 'sqlite+aiosqlite',
    }
    
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid database URL: {e}")
    
    # If already async, return as-is
    if any(async_driver in parsed.scheme for async_driver in 
           ['asyncpg', 'aiomysql', 'aiosqlite']):
        return url
    
    # Convert sync to async
    if parsed.scheme not in scheme_mapping:
        raise ValueError(
            f"Unsupported database scheme: {parsed.scheme}. "
            f"Supported: {list(scheme_mapping.keys())}"
        )
    
    new_scheme = scheme_mapping[parsed.scheme]
    async_url = urlunparse((
        new_scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    logger.info(f"Converted database URL scheme: {parsed.scheme} → {new_scheme}")
    return async_url


def get_connect_args() -> Dict[str, Any]:
    """
    Get database-specific connection arguments.
    
    Returns:
        Dictionary of connection arguments
    """
    connect_args = {}
    url = settings.database_url
    
    # PostgreSQL settings
    if 'postgresql' in url or 'postgres' in url:
        connect_args = {
            'timeout': 10,
            'command_timeout': 30,
            'server_settings': {
                'application_name': 'balance-bot',
                # 'jitLevel': 'off',  # Disable JIT for predictability
            },
        }
        
        # Add SSL
        if settings.db_ssl_mode == 'require':
            connect_args['ssl'] = ssl.create_default_context()
        else:
            connect_args['ssl'] = settings.db_ssl_mode
    
    # MySQL settings
    elif 'mysql' in url:
        connect_args = {
            'charset': 'utf8mb4',
            'timeout': 10,
        }
        
        # Add SSL if required
        if settings.db_ssl_mode == 'require':
            connect_args['ssl'] = {'ca': '/etc/ssl/certs/ca-certificates.crt'}
    
    # SQLite settings
    elif 'sqlite' in url:
        connect_args = {
            'timeout': 20,
            'check_same_thread': False,
        }
    
    return connect_args


# Create database engine
ASYNC_DATABASE_URL = get_database_url()
CONNECT_ARGS = get_connect_args()


def _scrub_null_bytes(value):
    """Recursively remove NUL bytes from any string inside a parameter set.

    PostgreSQL TEXT/VARCHAR cannot store ``\x00`` ("invalid byte sequence for
    encoding UTF8"), so a single dirty string — e.g. text extracted from a PDF
    that carries NUL bytes — would abort the whole INSERT and surface as a
    generic database error. Scrubbing at the cursor boundary keeps every
    write path (ORM and Core alike) working with dirty input.
    """
    if isinstance(value, str):
        return value.replace('\x00', '')
    if isinstance(value, dict):
        return {k: _scrub_null_bytes(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_scrub_null_bytes(v) for v in value]
    return value


def _scrub_parameters(conn, cursor, statement, parameters, context, executemany):
    """Sanitize bound parameters right before they reach the database driver.

    Returns ``(statement, parameters)`` — ``before_cursor_execute`` is
    registered with ``retval=True`` so the scrubbed parameter set replaces
    the original (parameters may be an immutable tuple on the asyncpg path).
    """
    if parameters is None:
        return statement, None
    if isinstance(parameters, dict):
        return statement, {k: _scrub_null_bytes(v) for k, v in parameters.items()}
    if isinstance(parameters, tuple):
        return statement, tuple(_scrub_null_bytes(v) for v in parameters)
    if isinstance(parameters, list):
        return statement, [_scrub_null_bytes(v) for v in parameters]
    return statement, parameters


engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    # Connection pool settings
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,  # Test connections before use (prevents stale connections)
    
    # Engine settings
    echo=settings.db_echo,
    echo_pool=False,
    future=True,
    
    # Connection settings
    connect_args=CONNECT_ARGS,
    
    # Performance
    isolation_level="READ_COMMITTED",
)

# Scrub NUL bytes from every write at the cursor boundary (see _scrub_null_bytes).
# retval=True lets the handler return the replacement (statement, parameters).
event.listen(engine.sync_engine, "before_cursor_execute", _scrub_parameters, retval=True)

logger.info(
    f"Database engine initialized: "
    f"pool_size={settings.db_pool_size}, "
    f"max_overflow={settings.db_max_overflow}, "
    f"pool_recycle={settings.db_pool_recycle}s, "
    f"pool_pre_ping=True, "
    f"ssl_mode={settings.db_ssl_mode}"
)

# Create session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)

# ORM base class
Base = declarative_base()


# ============================================================================
# Database Connection Management
# ============================================================================

async def verify_database_connection() -> bool:
    """
    Verify that database connection works.
    
    Called on application startup to ensure database is accessible.
    
    Returns:
        True if connection successful
    
    Raises:
        ConnectionError: If database is unreachable
    """
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            logger.info(f"Database connection verified: {row}")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        raise ConnectionError(
            f"Unable to connect to database. "
            f"Please check DATABASE_URL and ensure database server is running. "
            f"Error: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error verifying database connection: {e}")
        raise


async def get_database_health() -> Dict[str, Any]:
    """
    Get database connection pool health status.
    
    Returns:
        Dictionary with pool statistics
    """
    try:
        pool = engine.pool
        return {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
        }
    except Exception as e:
        logger.error(f"Error getting database health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@asynccontextmanager
async def get_db():
    """
    Async context manager for database sessions.
    
    Handles connection acquisition, transaction management, and cleanup.
    Automatically rolls back on errors.
    
    Usage:
        async with get_db() as db:
            result = await db.execute(select(User))
    
    Yields:
        AsyncSession: Database session
    
    Raises:
        SQLAlchemyError: If database operations fail
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error in database session: {e}", exc_info=True)
        raise
    finally:
        try:
            await db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}", exc_info=True)


async def get_db_dependency():
    """
    FastAPI dependency function for database sessions.
    
    Use this with FastAPI's Depends() for automatic session injection.
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db_dependency)):
            result = await db.execute(select(User))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Database session
    """
    async with get_db() as db:
        yield db


async def close_database():
    """
    Close all database connections.
    
    Call this on application shutdown.
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# ============================================================================
# Application Lifecycle (FastAPI)
# ============================================================================

async def lifespan(app):
    """
    Manage FastAPI application lifecycle.
    
    Runs on startup and shutdown.
    
    Usage:
        app = FastAPI(lifespan=lifespan)
    """
    # Startup
    try:
        await verify_database_connection()
        logger.info("Application started successfully")
    except ConnectionError as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        await close_database()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

