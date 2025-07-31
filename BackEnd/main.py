"""
FastAPI main application for Provider Registration Backend.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from db.database import initialize_database, init_mongodb, close_database_connections
from middlewares.rate_limiting import rate_limit_middleware
from api.v1.router import router as api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Provider Registration API...")
    
    try:
        # Initialize database connections
        initialize_database()
        logger.info("SQL database initialized")
        
        # Initialize MongoDB if configured
        if settings.MONGODB_URL:
            await init_mongodb()
            logger.info("MongoDB initialized")
        
        logger.info("Provider Registration API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Provider Registration API...")
    
    try:
        await close_database_connections()
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Provider Registration API shut down complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    A secure and robust backend API for healthcare provider registration and authentication.
    
    ## Features
    
    * **Comprehensive Validation**: Email, phone, password strength, license number validation
    * **JWT Authentication**: Secure access and refresh token system
    * **Session Management**: Login, logout, and logout-all functionality
    * **Account Security**: Account lockout after failed attempts, rate limiting
    * **Email Verification**: Secure token-based email verification system
    * **Audit Logging**: Complete audit trail of registration and authentication attempts
    * **Rate Limiting**: Protection against abuse and brute force attacks
    * **Multiple Database Support**: SQLite, PostgreSQL, MySQL, and MongoDB support
    
    ## Security Measures
    
    * Passwords hashed with bcrypt (12+ salt rounds)
    * JWT tokens with access/refresh token rotation
    * Account lockout after 5 failed login attempts
    * Rate limiting on all endpoints
    * Input sanitization to prevent injection attacks
    * Comprehensive audit logging
    * Email verification before account activation
    
    ## API Endpoints
    
    ### Provider Registration
    * `POST /api/v1/providers/register` - Register a new provider
    * `GET /api/v1/providers/specializations` - Get allowed specializations
    * `GET /api/v1/providers/password-requirements` - Get password requirements
    * `GET /api/v1/providers/health` - Health check endpoint
    
    ### Authentication
    * `POST /api/v1/auth/login` - Provider login with JWT tokens
    * `POST /api/v1/auth/refresh` - Refresh access token
    * `POST /api/v1/auth/logout` - Logout from current session
    * `POST /api/v1/auth/logout-all` - Logout from all sessions
    * `GET /api/v1/auth/me` - Get current provider information
    * `GET /api/v1/auth/token/verify` - Verify token validity
    """,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code} error: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    validation_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Request validation failed",
            "errors": validation_errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.DEBUG else "Internal server error"
        }
    )


# Include API routers
app.include_router(
    api_v1_router,
    prefix="/api/v1"
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs_url": "/docs" if settings.DEBUG else "Documentation not available in production",
        "endpoints": {
            "register_provider": "/api/v1/provider/register",
            "specializations": "/api/v1/provider/specializations",
            "password_requirements": "/api/v1/provider/password-requirements",
            "health_check": "/api/v1/provider/health"
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Application health check."""
    return {
        "success": True,
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
