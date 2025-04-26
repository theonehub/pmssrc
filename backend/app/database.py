import logging
from pymongo import MongoClient, ASCENDING
from config import MONGO_URI

logger = logging.getLogger(__name__)

# Create a MongoDB client using the provided URI and enable TLS.
client = MongoClient(MONGO_URI, tls=True)
db = client.pms

# Define collections for login and user info.
activity_tracker_collection = db["activity_tracker"]
user_collection = db["users_info"]
attendance_collection = db["attendance_collection"]
public_holidays_collection = db["public_holidays"]
company_leave_collection = db["company_leave_collection"]
employee_leave_collection = db["employee_leave_collection"]
salary_components_collection = db["salary_components"]
salary_component_assignments_collection = db["salary_component_assignments"]

salary_calculations_collection = db["salary_calculations"]


employee_salary_collection = db["employee_salary"]
salary_declaration_collection = db["salary_declaration"]

project_attribute_collection = db["project_attributes"]
reimbursement_types_collection = db["reimbursement_types"]
reimbursement_assignments_collection = db["reimbursement_assignments"]
reimbursement_requests_collection = db["reimbursement_requests_collection"]

# Create indexes to improve query performance and enforce uniqueness.
user_collection.create_index([("emp_id", ASCENDING)], unique=True)
user_collection.create_index([("manager_id", ASCENDING)])

public_holidays_collection.create_index([("date", ASCENDING)], unique=True)


attendance_collection.create_index(
    [("emp_id", 1), ("date", 1), ("month", 1), ("year", 1)],
)

logger.info("Database connected and indexes ensured.")
