"""
Health Check Routes
API endpoints for application health monitoring
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.config.dependency_container import health_check_dependencies
from app.infrastructure.database.database_connector import database_connector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Taxation Management System"
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with dependency status."""
    try:
        # Get dependency health status
        dependency_status = await health_check_dependencies()
        
        # Overall health based on all dependencies
        overall_healthy = all(
            status == 'healthy' 
            for status in dependency_status.values() 
            if not status.startswith('unhealthy')
        )
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Taxation Management System",
            "dependencies": dependency_status
        }
        
    except Exception as e:
        logger.error(f"Error during detailed health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Taxation Management System",
            "error": str(e)
        }


@router.get("/health/database")
async def database_health_check() -> Dict[str, Any]:
    """Database-specific health check."""
    try:
        # Check database connection
        db_healthy = await database_connector.health_check()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "MongoDB",
            "connection": "active" if db_healthy else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Error during database health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "MongoDB",
            "error": str(e)
        } 