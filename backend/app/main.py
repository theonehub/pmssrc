import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from bson import ObjectId
import json
import os

from services.user_service import create_default_user
from routes import auth_routes, user_routes, project_attributes_routes,\
    public_holiday_routes, attendance_routes, company_leave_routes, leave_routes, \
    reimbursement_routes, reimbursement_type_routes,\
    organisation_routes, taxation_routes, payout_routes, payslip_routes
from api.controllers.company_leave_controller import router as company_leave_v1_router
from utils.json_encoder import mongodb_jsonable_encoder, MongoJSONResponse

# Configure the root logger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d]: %(message)s",
)
logger = logging.getLogger(__name__)

# 👇 Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running startup tasks...")
    create_default_user()
    yield
    logger.info("Running shutdown tasks...")

# Initialize FastAPI app with metadata and lifespan.
app = FastAPI(
    title="Payroll Management System",
    description="API for managing users and payroll",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=MongoJSONResponse
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

# Include routers
app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(user_routes.router, tags=["User Management"])
app.include_router(attendance_routes.routes, tags=["Attendance"])
app.include_router(project_attributes_routes.router, tags=["Attributes"])
app.include_router(reimbursement_type_routes.router, tags=["Reimbursement Types"])
app.include_router(reimbursement_routes.router, tags=["My-Reimbursements"])
app.include_router(public_holiday_routes.router, tags=["Public Holidays"])
app.include_router(company_leave_routes.router, tags=["Company Leaves (Legacy)"])
app.include_router(company_leave_v1_router, tags=["Company Leaves V1"])
app.include_router(leave_routes.router, tags=["Leave Management"])
app.include_router(organisation_routes.router, tags=["Organization"])
app.include_router(taxation_routes.router, tags=["Taxation"])
app.include_router(payout_routes.router, tags=["Payouts"])
app.include_router(payslip_routes.router, tags=["Payslips"])

# Run the server
if __name__ == "__main__":
    logger.info("Starting application...")
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
