"""
Taxation Management System - Main Application
FastAPI application with Clean Architecture implementation
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config.settings import settings
from app.infrastructure.database.database_connector import database_connector
from app.config.dependency_container import health_check_dependencies

# Import routes
from app.api.routes.user_routes_v2 import router as user_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.taxation_routes import router as taxation_router
# Enhanced taxation routes merged into main taxation routes

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    
    # Startup
    logger.info("Starting Taxation Management System...")
    
    try:
        # Connect to database
        await database_connector.connect()
        logger.info("Database connection established")
        
        # Perform health check
        health_status = await health_check_dependencies()
        logger.info(f"Dependency health check: {health_status}")
        
        # Create default indexes (optional, for development)
        if settings.debug:
            try:
                await database_connector.create_indexes("default")
                logger.info("Created default database indexes")
            except Exception as e:
                logger.warning(f"Could not create default indexes: {e}")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Taxation Management System...")
    
    try:
        # Disconnect from database
        await database_connector.disconnect()
        logger.info("Database connection closed")
        
        logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A FastAPI-based taxation management application following Clean Architecture principles",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception on {request.url}: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests."""
    start_time = request.state.start_time = __import__('time').time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = __import__('time').time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs" if settings.debug else "disabled",
        "architecture": "Clean Architecture with SOLID principles",
        "database": "MongoDB with multi-tenant support",
        "authentication": "JWT-based with organization context"
    }


# Include routers
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(auth_router, prefix=settings.api_v2_prefix, tags=["authentication"])
app.include_router(user_router, prefix=settings.api_v2_prefix, tags=["users"])
app.include_router(taxation_router, prefix=settings.api_v2_prefix, tags=["taxation"])


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 