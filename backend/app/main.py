import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.user_service import create_default_user
from routes import auth_routes, user_routes, salary_component_routes, \
        employee_salary_routes, salary_declaration_routes, \
        attendance_routes, project_attributes_routes, reimbursement_type_routes, \
        reimbursement_assignment_route, reimbursements


create_default_user()

# Configure the root logger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with metadata.
app = FastAPI(
    title="Payroll Management System",
    description="API for managing users and payroll",
    version="1.0.0",
)

# Add CORS middleware to allow requests from the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and user routes with tags for documentation.
app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(user_routes.router, tags=["User Management"])
app.include_router(salary_component_routes.router, tags=["Salary Components"])
app.include_router(employee_salary_routes.router, tags=["Employee Salary"])
app.include_router(salary_declaration_routes.router,tags=["Salary Declaration"])
app.include_router(attendance_routes.routes, tags=["Attendance"])
app.include_router(project_attributes_routes.router, tags=["Attibutes"])
app.include_router(reimbursement_type_routes.router, tags=["Reimbursement Types"])
app.include_router(reimbursement_assignment_route.router, tags=["Reimbursements Assignment"])
app.include_router(reimbursements.router, tags=["My-Reimbursements"])


if __name__ == "__main__":
    logger.info("Starting application...")    
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
