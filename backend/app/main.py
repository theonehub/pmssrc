import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from services.user_service import create_default_user
from routes import auth_routes, user_routes, salary_component_routes, \
    attendance_routes, project_attributes_routes, reimbursement_type_routes, \
    reimbursement_assignment_route, reimbursement_routes, public_holiday_routes, \
    company_leave_routes, leave_routes, salary_computation_routes

# Configure the root logger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 👇 Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running startup tasks...")
    await create_default_user()
    yield
    logger.info("Running shutdown tasks...")

# Initialize FastAPI app with metadata and lifespan.
app = FastAPI(
    title="Payroll Management System",
    description="API for managing users and payroll",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(user_routes.router, tags=["User Management"])
app.include_router(salary_component_routes.router, tags=["Salary Components"])
app.include_router(attendance_routes.routes, tags=["Attendance"])
app.include_router(project_attributes_routes.router, tags=["Attributes"])
app.include_router(reimbursement_type_routes.router, tags=["Reimbursement Types"])
app.include_router(reimbursement_assignment_route.router, tags=["Reimbursements Assignment"])
app.include_router(reimbursement_routes.router, tags=["My-Reimbursements"])
app.include_router(public_holiday_routes.router, tags=["Public Holidays"])
app.include_router(company_leave_routes.router, tags=["Company Leaves"])
app.include_router(leave_routes.router, tags=["Leave Management"])
app.include_router(salary_computation_routes.router, tags=["Salary Computation"])

# Run the server
if __name__ == "__main__":
    logger.info("Starting application...")
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
