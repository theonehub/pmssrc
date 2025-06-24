"""
Monthly Taxation FastAPI Application
Main application entry point for the taxation system
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import the dependency container
from app.config.dependency_container import container

# Import routes
from app.api.routes.salary_component_routes_v2 import router as salary_component_router
from app.api.routes.salary_component_assignment_routes_v2 import router as salary_component_assignment_router

# Import auth for debugging
from app.auth.auth_integration import get_current_user_dict, debug_token

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Keep DEBUG for our application
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable verbose MongoDB/pymongo logs
logging.getLogger('pymongo').setLevel(logging.WARNING)
logging.getLogger('pymongo.topology').setLevel(logging.WARNING)
logging.getLogger('pymongo.connection').setLevel(logging.WARNING)
logging.getLogger('pymongo.pool').setLevel(logging.WARNING)
logging.getLogger('pymongo.serverSelection').setLevel(logging.WARNING)

# Also set auth module to DEBUG
auth_logger = logging.getLogger('app.auth')
auth_logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Monthly Taxation Service...")
    try:
        await container.initialize()
        logger.info("Container initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize container: {e}")
        raise
    
    logger.info("Monthly Taxation Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Monthly Taxation Service...")
    try:
        await container.cleanup()
        logger.info("Container cleanup completed")
    except Exception as e:
        logger.error(f"Error during container cleanup: {e}")
    logger.info("Monthly Taxation Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Monthly Taxation API",
    description="""
    Comprehensive Indian Payroll & Taxation System
    
    This API provides complete functionality for:
    - Salary component configuration
    - Employee salary structure management  
    - Tax computation (Old & New regime)
    - Payroll processing
    - Form 16 and FVU generation
    
    Built with SOLID principles and Clean Architecture.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(salary_component_router)
app.include_router(salary_component_assignment_router)

# Auth debug endpoints
@app.get("/api/debug/auth")
async def debug_auth_endpoint(current_user=Depends(get_current_user_dict)):
    """Debug endpoint to test authentication"""
    return {
        "status": "success",
        "message": "Authentication working",
        "user": current_user
    }

@app.get("/api/debug/token")
async def debug_token_endpoint(token_payload=Depends(debug_token)):
    """Debug endpoint to examine raw token payload"""
    return {
        "status": "success", 
        "message": "Token debug info",
        "payload": token_payload
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal error occurred",
            "status_code": 500
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = await container.get_health_status()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "components": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "service": "Monthly Taxation API",
        "version": "1.0.0",
        "description": "Comprehensive Indian Payroll & Taxation System",
        "modules": [
            "Salary Component Configuration",
            "Employee Salary Management", 
            "Tax Computation Engine",
            "Payroll Processing",
            "Reporting & Compliance"
        ],
        "supported_tax_regimes": ["Old Regime", "New Regime"],
        "compliance": ["Form 16", "FVU/24Q", "TDS Returns"]
    }

# Demo endpoints for architecture demonstration
@app.get("/api/v2/salary-components/demo")
async def demo_salary_components():
    """Demo endpoint for salary components"""
    return {
        "message": "Salary Components Module",
        "features": [
            "Create salary components (BASIC, HRA, LTA, etc.)",
            "Formula-based calculations",
            "Tax exemption mapping",
            "Component type classification"
        ],
        "example_component": {
            "code": "BASIC",
            "name": "Basic Salary",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "default_value": 50000.00
        }
    }

@app.get("/api/v2/employee-salary/demo")
async def demo_employee_salary():
    """Demo endpoint for employee salary"""
    return {
        "message": "Employee Salary Management Module",
        "features": [
            "Assign salary structures to employees",
            "Support for salary revisions",
            "Historical tracking",
            "Component-wise assignment"
        ],
        "example_assignment": {
            "employee_id": "EMP001",
            "gross_salary": 100000.00,
            "components": [
                {"code": "BASIC", "value": 50000.00},
                {"code": "HRA", "formula": "BASIC * 0.4"}
            ]
        }
    }

@app.get("/api/v2/tax-computation/demo")
async def demo_tax_computation():
    """Demo endpoint for tax computation"""
    return {
        "message": "Tax Computation Engine",
        "features": [
            "Old vs New regime comparison",
            "Comprehensive exemption calculations",
            "Monthly TDS projections",
            "Form 16 generation ready"
        ],
        "example_computation": {
            "employee_id": "EMP001",
            "annual_salary": 1200000.00,
            "regime": "new",
            "exemptions": 150000.00,
            "tax_liability": 75000.00
        }
    }

@app.get("/api/v2/payroll/demo")
async def demo_payroll():
    """Demo endpoint for payroll"""
    return {
        "message": "Payroll Processing Module",
        "features": [
            "Monthly payroll generation",
            "Statutory compliance (EPF, ESI, PT)",
            "TDS computation and deduction",
            "Payslip generation"
        ],
        "example_payroll": {
            "employee_id": "EMP001",
            "month": "2024-01",
            "gross_salary": 100000.00,
            "deductions": 15000.00,
            "net_salary": 85000.00
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API overview"""
    return {
        "service": "Monthly Taxation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/health",
        "debug_auth": "/api/debug/auth",
        "debug_token": "/api/debug/token"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 