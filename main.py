

"""
FastAPI Main Application

Production-ready FastAPI application with GraphQL and REST APIs.
Includes:
- JWT authentication for GraphQL and REST
- Comprehensive security middleware
- Request logging and tracing
- Health checks and monitoring
- Proper error handling
- Database lifecycle management
"""

import logging
import logging.handlers
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Optional, Any
from datetime import datetime

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from strawberry.exceptions import GraphQLError

# Import database configuration
try:
    from config.dbconfig import (
        settings,
        engine,
        Base,
        verify_database_connection,
        get_database_health,
        close_database
    )
    DATABASE_CONFIG_LOADED = True
except ImportError as e:
    DATABASE_CONFIG_LOADED = False
    logging.warning(f"Database configuration not found: {e}")
    logging.warning("Starting without database support")

# Import authentication utilities
try:
    from utils.auth_utils import decode_token
    AUTH_UTILS_LOADED = True
except ImportError as e:
    AUTH_UTILS_LOADED = False
    logging.warning(f"Auth utilities not found: {e}")
    logging.warning("Starting without authentication support")

# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging() -> logging.Logger:
    """Configure application logging."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    
    # Set level based on environment
    try:
        if DATABASE_CONFIG_LOADED and settings.debug:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
    except Exception:
        root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (production)
    try:
        if DATABASE_CONFIG_LOADED and settings.is_production:
            file_handler = logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    except Exception:
        pass  # Logging to file is optional
    
    return root_logger

logger = setup_logging()


# ============================================================================
# Load API Modules
# ============================================================================

# Load GraphQL
GRAPHQL_ENABLED = False
graphql_app = None
mainEndpoint = None

try:
    from graphql_folder.end_point.central_endpoint import mainEndpoint
    from strawberry.fastapi import GraphQLRouter
    GRAPHQL_ENABLED = True
    logger.info("GraphQL endpoint module loaded successfully")
except ImportError as e:
    logger.warning(f"GraphQL endpoints disabled: {e}")
except Exception as e:
    logger.error(f"Failed to load GraphQL module: {e}", exc_info=True)

# Load REST API
REST_ENABLED = False
api_router = None

try:
    from api.router import api_router
    REST_ENABLED = True
    logger.info("REST API module loaded successfully")
except ImportError as e:
    logger.warning(f"REST API disabled: {e}")
except Exception as e:
    logger.error(f"Failed to load REST API module: {e}", exc_info=True)

# Verify at least one API is available
if not GRAPHQL_ENABLED and not REST_ENABLED:
    logger.error("Both GraphQL and REST APIs failed to load")
    # Continue anyway - health check endpoint will still work


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    
    Startup: Verify database, create schema
    Shutdown: Close database connections
    """
    # ====== STARTUP ======
    try:
        logger.info("=" * 60)
        logger.info("Starting application...")
        
        if DATABASE_CONFIG_LOADED:
            logger.info(f"Environment: {settings.environment}")
            logger.info(f"Debug mode: {settings.debug}")
        
        # Verify database connection
# Create tables if needed
        if DATABASE_CONFIG_LOADED:
            logger.info("Initializing database schema...")
            try:
                # Only attempt to create tables if Base and metadata are properly configured
                if hasattr(Base, 'metadata') and hasattr(Base.metadata, 'create_all'):
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    logger.info("✓ Database schema initialized")
                else:
                    logger.warning("Database schema creation skipped - SQLAlchemy not fully configured")
            except Exception as e:
                logger.warning(f"Could not initialize schema automatically: {e}")
                logger.info("You may need to run migrations manually or configure SQLAlchemy")
        else:
            logger.warning("Starting without database configuration")
        
        # Log API status
        apis = []
        if GRAPHQL_ENABLED:
            apis.append("GraphQL (/graphql)")
        if REST_ENABLED:
            apis.append("REST (/api)")
        
        logger.info(f"Enabled APIs: {', '.join(apis) if apis else 'None'}")
        logger.info("=" * 60)
        logger.info("Application started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        if DATABASE_CONFIG_LOADED:
            raise SystemExit(1)
    
    yield
    
    # ====== SHUTDOWN ======
    try:
        logger.info("=" * 60)
        logger.info("Shutting down application...")
        
        if DATABASE_CONFIG_LOADED:
            await engine.dispose()
            logger.info("✓ Database connections closed")
        
        logger.info("Application shutdown complete")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# ============================================================================
# Security & Middleware
# ============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses.
    
    Adds request ID for tracing throughout the system.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"[{request_id}] {response.status_code}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Protects against common web vulnerabilities:
    - XSS (Cross-Site Scripting)
    - Clickjacking
    - MIME-type sniffing
    - Insecure HTTPS
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Disable clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy - FIXED
        try:
            if DATABASE_CONFIG_LOADED and settings.environment == "production":
                # Strict CSP for production
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self'; "
                    "style-src 'self'; "
                    "img-src 'self' data:; "
                    "font-src 'self'; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none';"
                )
            else:
                # Development/staging CSP - Allow tools like GraphiQL and Swagger
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com; "
                    "img-src 'self' data: blob: https:; "
                    "font-src 'self' data: https://fonts.gstatic.com; "
                    "connect-src 'self' ws: wss: https:; "
                    "frame-ancestors 'self'; "
                    "child-src 'self' blob:;"
                )
        except Exception:
            # Fallback CSP if settings not available
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com; "
                "img-src 'self' data: blob: https:; "
                "font-src 'self' data: https://fonts.gstatic.com; "
                "connect-src 'self' ws: wss: https:; "
                "frame-ancestors 'self';"
            )
        
        # Remove server header (don't advertise software)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


# ============================================================================
# Authentication
# ============================================================================

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to validate JWT token for REST endpoints.
    
    Args:
        credentials: HTTP Bearer token
    
    Returns:
        User payload from token
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not AUTH_UTILS_LOADED:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentication not configured",
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = await decode_token(token)
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_graphql_context(request: Request) -> Dict[str, Any]:
    """
    Extract and validate JWT token from GraphQL request.
    
    Returns context dict with authenticated user if valid token,
    otherwise returns guest context.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Context dictionary with user (if authenticated) and request
    """
    request_id = getattr(request.state, "request_id", "unknown")
    auth_header = request.headers.get('Authorization', '')
    
    # No auth header - return guest context
    if not auth_header:
        logger.debug(f"[{request_id}] GraphQL request without authentication")
        return {"request": request, "user": None, "request_id": request_id}
    
    # Check if authentication is configured
    if not AUTH_UTILS_LOADED:
        raise GraphQLError(
            "Authentication not configured",
            extensions={"code": "AUTHENTICATION_ERROR"}
        )
    
    # Invalid format
    if not auth_header.startswith('Bearer '):
        logger.warning(
            f"[{request_id}] Invalid auth header format",
            extra={"request_id": request_id}
        )
        raise GraphQLError(
            "Invalid authentication header. Use 'Bearer <token>'",
            extensions={"code": "UNAUTHENTICATED"}
        )
    
    # Extract token
    try:
        token = auth_header[7:]  # Skip 'Bearer '
    except Exception as e:
        logger.warning(f"[{request_id}] Failed to parse auth header: {e}")
        raise GraphQLError(
            "Invalid authentication header",
            extensions={"code": "UNAUTHENTICATED"}
        )
    
    # Validate token
    try:
        payload = await decode_token(token)
    except Exception as e:
        logger.warning(
            f"[{request_id}] Token validation error: {e}",
            extra={"request_id": request_id}
        )
        raise GraphQLError(
            "Invalid or expired token. Please login again",
            extensions={"code": "UNAUTHENTICATED"}
        )
    
    # Verify payload is not None
    if not payload:
        logger.warning(
            f"[{request_id}] Token returned empty payload",
            extra={"request_id": request_id}
        )
        raise GraphQLError(
            "Invalid token",
            extensions={"code": "UNAUTHENTICATED"}
        )
    
    logger.debug(
        f"[{request_id}] User authenticated",
        extra={"request_id": request_id, "user_id": payload.get("user_id")}
    )
    
    return {
        "user": payload,
        "request": request,
        "request_id": request_id,
    }


# ============================================================================
# Create FastAPI Application
# ============================================================================

# Get environment-specific configuration
# CORS origins/credentials are configured in config/cors.py (driven by the ALLOWED_ORIGINS env
# var; never pairs a wildcard origin with credentials).
from config.cors import get_cors_origins, get_cors_credentials

# Error monitoring (OPS008): initialize Sentry when SENTRY_DSN is set (no-op otherwise).
import os as _os
_sentry_dsn = _os.getenv("SENTRY_DSN")
if _sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=_sentry_dsn,
            environment=_os.getenv("ENVIRONMENT", "development"),
            traces_sample_rate=float(_os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        )
    except ImportError:
        pass

# Create the app
app = FastAPI(
    title="Generated Backend API",
    description="Auto-generated backend with GraphQL and REST APIs with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ============================================================================
# Middleware (Order matters!)
# ============================================================================

# Security headers (should be first)
app.add_middleware(SecurityHeadersMiddleware)

# Request logging and tracing
app.add_middleware(RequestLoggingMiddleware)

# CORS (configure based on environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=get_cors_credentials(),
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Total-Count", "X-Request-ID"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Response compression (for responses larger than 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper formatting."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(
        f"[{request_id}] HTTP {exc.status_code}: {exc.detail}",
        extra={"request_id": request_id, "status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": request_id,
            "status_code": exc.status_code,
        },
        headers=exc.headers or {},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle any uncaught exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"[{request_id}] Unhandled exception: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    
    # Hide error details in production
    error_detail = "An unexpected error occurred"
    
    # Show more details in development
    try:
        if DATABASE_CONFIG_LOADED and settings.debug:
            error_detail = str(exc)
    except Exception:
        pass  # Use default message
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "message": error_detail,
        },
    )


# ============================================================================
# API Routes
# ============================================================================

# GraphQL endpoint
if GRAPHQL_ENABLED and mainEndpoint:
    graphql_app = GraphQLRouter(
        mainEndpoint,
        context_getter=get_graphql_context,
        # graphiql=True,  # Enable GraphiQL interface
    )
    app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])
    logger.info("GraphQL endpoint mounted at /graphql")

# REST API endpoints
if REST_ENABLED and api_router:
    app.include_router(api_router, prefix="/api", tags=["rest"])
    logger.info("REST API endpoints mounted at /api")

# SEC003: mount email-verification / password-reset routes if generated (auth model present).
try:
    from auth.verification import router as verification_router
    app.include_router(verification_router)
except ImportError:
    pass

# Self-serve docs portal: a landing page (sidebar + jump-to) linking the API's docs
# and endpoints; opens in your browser on startup in development (OPEN_BROWSER=0 to skip).
try:
    import docs_portal as _docs_portal
    _docs_portal.mount(app)
except Exception as _portal_exc:  # never let the portal break app startup
    import logging as _logging
    _logging.getLogger(__name__).warning('docs portal not mounted: %s', _portal_exc)

@app.get("/api/whoami", tags=["meta"])
async def whoami(request: Request):
    """Return the caller's IP address and user-agent."""
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else None)
    )
    return {"ip": client_ip, "user_agent": request.headers.get("user-agent")}


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """
    API health check endpoint.
    
    Used by Kubernetes and load balancers to verify the service is running.
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "apis": {
            "graphql": GRAPHQL_ENABLED,
            "rest": REST_ENABLED,
            "database": DATABASE_CONFIG_LOADED,
            "authentication": AUTH_UTILS_LOADED,
        }
    }
    
    try:
        if DATABASE_CONFIG_LOADED:
            health_data["environment"] = settings.environment
            
            # Check database health
            db_health = await get_database_health()
            health_data["database"] = db_health
            
            if db_health.get("status") != "healthy":
                health_data["status"] = "degraded"
    except Exception as e:
        health_data["database"] = {"error": str(e)}
        health_data["status"] = "degraded"
    
    return health_data


@app.get("/health/live", tags=["health"])
async def liveness_check():
    """
    Kubernetes liveness probe.
    
    Returns 200 if the container is running.
    """
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    """
    Kubernetes readiness probe.
    
    Returns 200 if the service is ready to accept traffic.
    """
    try:
        if DATABASE_CONFIG_LOADED:
            health = await get_database_health()
            if health.get("status") == "healthy":
                return {
                    "status": "ready",
                    "database": health,
                }
            else:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "not_ready",
                        "database": health,
                    }
                )
        else:
            return {"status": "ready", "database": "not_configured"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e),
            }
        )


# ============================================================================
# Info Endpoints
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """
    API root endpoint.
    
    Returns information about available endpoints.
    """
    # Get environment info
    env_info = "development"
    try:
        if DATABASE_CONFIG_LOADED:
            env_info = settings.environment
    except Exception:
        pass
    
    if env_info == "production":
        # Minimal info in production
        return {"message": "Generated Backend API", "version": "1.0.0"}
    
    # Detailed info in development/staging
    endpoints = []
    
    if GRAPHQL_ENABLED:
        endpoints.append({
            "type": "GraphQL",
            "url": "/graphql",
            "description": "GraphQL API endpoint with JWT authentication",
            "playground": "/graphql",
        })
    
    if REST_ENABLED:
        endpoints.append({
            "type": "REST",
            "url": "/api",
            "docs": "/docs",
            "redoc": "/redoc",
            "description": "REST API endpoints with JWT authentication",
        })
    
    endpoints.append({
        "type": "Health",
        "url": "/health",
        "description": "API health check",
    })
    
    return {
        "message": "Welcome to the Generated Backend API",
        "version": "1.0.0",
        "environment": env_info,
        "endpoints": endpoints,
    }


@app.get("/api/info", tags=["api"])
async def api_info():
    """
    Get API information and enabled features.
    """
    info = {
        "name": "Generated Backend API",
        "version": "1.0.0",
        "authentication": "JWT Bearer token" if AUTH_UTILS_LOADED else "Not configured",
        "enabled_apis": [],
        "features": [
            "JWT authentication" if AUTH_UTILS_LOADED else "No authentication",
            "CRUD operations",
            "Real-time GraphQL" if GRAPHQL_ENABLED else "GraphQL disabled",
            "RESTful endpoints" if REST_ENABLED else "REST disabled",
            "OpenAPI documentation",
            "Database integration" if DATABASE_CONFIG_LOADED else "No database"
        ]
    }
    
    # Get environment
    try:
        if DATABASE_CONFIG_LOADED:
            info["environment"] = settings.environment
            info["debug"] = settings.debug
    except Exception:
        pass
    
    if GRAPHQL_ENABLED:
        info["enabled_apis"].append("GraphQL")
    
    if REST_ENABLED:
        info["enabled_apis"].append("REST")
    
    return info


# ============================================================================
# Development-only Endpoints
# ============================================================================

def is_development() -> bool:
    """Check if running in development environment."""
    try:
        if DATABASE_CONFIG_LOADED:
            return settings.environment == "development"
    except Exception:
        pass
    return True  # Default to development if can't determine


if is_development():
    
    @app.get("/api/protected-test", tags=["development"])
    async def protected_test(current_user: dict = Depends(get_current_user)):
        """
        Test endpoint to verify JWT authentication for REST.
        
        Only available in development mode.
        """
        return {
            "message": "JWT authentication is working",
            "user": current_user,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/api/debug/headers", tags=["development"])
    async def debug_headers(request: Request):
        """
        Debug endpoint to view request headers.
        
        Useful for troubleshooting authentication and CORS issues.
        """
        return {
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "method": request.method,
            "url": str(request.url),
        }
    
    logger.info("Development endpoints enabled")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Determine reload setting
    reload_enabled = is_development()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_enabled,
        log_level="debug" if is_development() else "info",
        access_log=True,
    )


