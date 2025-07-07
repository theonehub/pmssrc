import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from bson import ObjectId
import json
import os
from datetime import datetime

# Import centralized logger
from app.utils.logger import get_logger

# from app.infrastructure.services.legacy_migration_service import create_default_user

from app.api.routes.auth_routes_v2 import router as auth_routes_v2_router
from app.api.routes.user_routes_v2 import router as user_routes_v2_router
from app.api.routes.organisation_routes_v2 import organisation_v2_router
from app.api.routes.reimbursement_routes_v2 import router as reimbursement_routes_v2_router
from app.api.routes.attendance_routes_v2 import router as attendance_routes_v2_router
from app.api.routes.public_holiday_routes_v2 import router as public_holiday_routes_v2_router
from app.api.routes.company_leave_routes_v2 import router as company_leave_routes_v2_router
from app.api.routes.employee_leave_routes_v2 import router as employee_leave_routes_v2_router
from app.api.routes.leaves_routes_v2 import router as leaves_routes_v2_router
from app.api.routes.lwp_routes import router as lwp_routes_router
from app.api.routes.project_attributes_routes_v2 import router as project_attributes_routes_v2_router
from app.api.routes.reporting_routes_v2 import router as reporting_routes_v2_router
from app.api.routes.taxation_routes import router as taxation_routes_router
from app.api.routes.export_routes_v2 import export_v2_router

# Configure centralized logging
logger = get_logger(__name__)

# 👇 Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running startup tasks...")
    yield
    logger.info("Running shutdown tasks...")

# Initialize FastAPI app with metadata and lifespan.
app = FastAPI(
    title="Payroll Management System - By TheOne",
    description="Payroll management system that allows you to manage your employees and payroll.",
    version="2.0.0",
    lifespan=lifespan,
    default_response_class=JSONResponse
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://theonetech:3000"],
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

# Core working routes (always available)
app.include_router(auth_routes_v2_router, tags=["🔐 Authentication V2 (SOLID)"])
app.include_router(user_routes_v2_router, tags=["👥 Users V2 (SOLID)"])
app.include_router(organisation_v2_router, tags=["🏛️ Organisation V2 (SOLID)"])
app.include_router(company_leave_routes_v2_router, tags=["🏢 Company Leaves V2 (SOLID)"])
app.include_router(employee_leave_routes_v2_router, tags=["🏖️ Employee Leaves V2 (SOLID)"])
app.include_router(leaves_routes_v2_router, tags=["🏖️ Leaves V2 (Frontend Compatible)"])
app.include_router(lwp_routes_router, tags=["📋 LWP Management"])
app.include_router(project_attributes_routes_v2_router, tags=["📊 Project Attributes V2 (SOLID)"])
app.include_router(reimbursement_routes_v2_router, tags=["💳 Reimbursements V2 (SOLID)"])
app.include_router(attendance_routes_v2_router, tags=["⏰ Attendance V2 (SOLID)"])
app.include_router(public_holiday_routes_v2_router, tags=["🎉 Public Holidays V2 (SOLID)"])
app.include_router(reporting_routes_v2_router, tags=["📊 Reporting V2 (SOLID)"])
app.include_router(taxation_routes_router, tags=["💰 Taxation V2 (SOLID)"])
app.include_router(export_v2_router, tags=["📁 File Exports V2 (SOLID)"])
logger.info("✅ Critical routes registered: taxation, payout, user management, reimbursement, attendance, public holidays, employee leave, company leave, project attributes, reporting, exports")

# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     """Application health check"""
#     try:
#         container = get_dependency_container()
#         health_status = container.health_check()
        
#         route_count = len(app.routes)
        
#         return {
#             "status": "healthy",
#             "timestamp": datetime.now().isoformat(),
#             "routes_registered": route_count,
#             "container_status": health_status,
#             "version": "2.0.0"
#         }
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         return {
#             "status": "unhealthy",
#             "timestamp": datetime.now().isoformat(),
#             "error": str(e),
#             "version": "2.0.0"
#         }

# Run the server
if __name__ == "__main__":
    logger.info("Starting PMS application by TheOne")
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
