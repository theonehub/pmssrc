import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import os

# SOLID V2 Routes (Clean Architecture) - Our New Working Routes
from app.api.routes.auth_routes_v2 import router as auth_routes_v2_router
from app.api.routes.employee_salary_routes_v2 import router as employee_salary_routes_v2_router
from app.api.routes.payslip_routes_v2 import router as payslip_routes_v2_router

# Configure the root logger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d]: %(message)s",
)
logger = logging.getLogger(__name__)

# 👇 Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SOLID v2 routes application...")
    yield
    logger.info("Shutting down application...")

# Initialize FastAPI app with metadata and lifespan.
app = FastAPI(
    title="Payroll Management System - SOLID Architecture v2",
    description="Modern API using SOLID principles - New Routes Only",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount static files
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# SOLID V2 Routes (Clean Architecture) - Primary API
logger.info("Registering SOLID v2 routes...")
app.include_router(auth_routes_v2_router, tags=["🔐 Authentication V2 (SOLID)"])
app.include_router(employee_salary_routes_v2_router, tags=["💰 Employee Salary V2 (SOLID)"])
app.include_router(payslip_routes_v2_router, tags=["📄 Payslips V2 (SOLID)"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check"""
    try:
        route_count = len(app.routes)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "version": "2.0.0",
                "architecture": "SOLID-compliant",
                "active_routes": route_count,
                "solid_v2_routes": ["auth", "employee_salary", "payslip"],
                "components": {
                    "auth": "healthy", 
                    "employee_salary": "healthy", 
                    "payslip": "healthy"
                }
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Payroll Management System - SOLID Architecture v2",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "solid_v2_endpoints": {
            "auth": "/api/v2/auth/",
            "employee_salary": "/api/v2/employee-salary/",
            "payslips": "/api/v2/payslips/"
        },
        "features": [
            "🔐 Complete Authentication System",
            "💰 Employee Salary Management", 
            "📄 Payslip Generation and Management",
            "✅ SOLID Architecture Compliance",
            "🛡️ Type-Safe DTOs",
            "🔍 Comprehensive Error Handling"
        ]
    }

# Run the server
if __name__ == "__main__":
    logger.info("Starting SOLID-compliant PMS application...")
    import uvicorn
    uvicorn.run("app.main_minimal:app", host="0.0.0.0", port=8000, reload=True) 