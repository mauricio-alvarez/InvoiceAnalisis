"""FastAPI application entry point"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings
from app.core.dependencies import setup_logging, FirebaseClient
from app.api import auth, invoices, admin

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting GCP Invoice Management Platform API")
    
    # Setup logging
    setup_logging()
    
    # Initialize Firebase
    try:
        FirebaseClient.initialize()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GCP Invoice Management Platform API")


# Create FastAPI application
app = FastAPI(
    title="GCP Invoice Management Platform",
    description="A serverless invoice management platform built on Google Cloud Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred"
            }
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        Dictionary with status and version
    """
    return {
        "status": "healthy",
        "service": "gcp-invoice-platform",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    
    Returns:
        Welcome message with API documentation link
    """
    return {
        "message": "GCP Invoice Management Platform API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# Register API routers
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(admin.router)


# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
