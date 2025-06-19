"""
User Microservice
Handles user authentication, profiles, and permissions
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add shared libraries to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from common.database import get_database_connector, MongoDBConnector
from common.auth import get_current_user, CurrentUser, JWTManager
from infrastructure.repositories.user_repository import UserRepository
from application.use_cases.auth_use_case import AuthUseCase
from application.use_cases.user_management_use_case import UserManagementUseCase
from api.routes.auth_routes import router as auth_router
from api.routes.user_routes import router as user_router

# Service configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "user_service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8000))
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

# Global dependencies
db_connector: MongoDBConnector = None
user_repository: UserRepository = None
auth_use_case: AuthUseCase = None
user_management_use_case: UserManagementUseCase = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service dependencies on startup"""
    global db_connector, user_repository, auth_use_case, user_management_use_case
    
    try:
        # Initialize database connection
        db_connector = get_database_connector(SERVICE_NAME)
        await db_connector.connect(MONGODB_URL)
        
        # Initialize repository
        user_repository = UserRepository(db_connector)
        
        # Initialize use cases
        auth_use_case = AuthUseCase(user_repository)
        user_management_use_case = UserManagementUseCase(user_repository)
        
        # Create database indexes
        await setup_database_indexes()
        
        print(f"✅ {SERVICE_NAME} started successfully on port {SERVICE_PORT}")
        yield
        
    except Exception as e:
        print(f"❌ Failed to start {SERVICE_NAME}: {e}")
        raise
    finally:
        # Cleanup on shutdown
        if db_connector:
            await db_connector.disconnect()
        print(f"🔴 {SERVICE_NAME} shutting down")


async def setup_database_indexes():
    """Setup database indexes for performance"""
    indexes = {
        "users": [
            "employee_id",
            "email", 
            "username",
            [("employee_id", 1), ("hostname", 1)]
        ],
        "user_sessions": [
            "employee_id",
            "session_token",
            "expires_at"
        ]
    }
    
    # Create indexes for default hostname (you can add more as needed)
    await db_connector.create_indexes("default", indexes)


# Create FastAPI app
app = FastAPI(
    title="User Service",
    description="Microservice for user authentication and management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    if not user_repository:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return user_repository


def get_auth_use_case() -> AuthUseCase:
    """Get auth use case instance"""
    if not auth_use_case:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return auth_use_case


def get_user_management_use_case() -> UserManagementUseCase:
    """Get user management use case instance"""
    if not user_management_use_case:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return user_management_use_case


# Include routes
app.include_router(
    auth_router, 
    prefix="/api/v2/auth", 
    tags=["Authentication"]
)
app.include_router(
    user_router, 
    prefix="/api/v2/users", 
    tags=["User Management"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected" if db_connector and db_connector.is_connected() else "disconnected"
    }


@app.get("/")
async def root():
    """Service info endpoint"""
    return {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "description": "User authentication and management microservice",
        "endpoints": {
            "health": "/health",
            "auth": "/api/v2/auth",
            "users": "/api/v2/users"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Implement metrics collection here
    return {
        "total_users": await user_repository.count_documents("default") if user_repository else 0,
        "service_name": SERVICE_NAME,
        "uptime": "TODO: implement uptime tracking"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
        log_level="info"
    ) 