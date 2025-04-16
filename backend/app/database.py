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
salary_components_collection = db["salary_components"]
employee_salary_collection = db["employee_salary"]
salary_declaration_collection = db["salary_declaration"]
attendance_collection = db["attendance_collection"]
project_attribute_collection = db["project_attributes"]
reimbursement_types_collection = db["reimbursement_types"]
reimbursement_assignments_collection = db["reimbursement_assignments"]
reimbursement_requests_collection = db["reimbursement_requests_collection"]

# Create indexes to improve query performance and enforce uniqueness.
user_collection.create_index([("empId", ASCENDING)], unique=True)
user_collection.create_index([("managerId", ASCENDING)])

attendance_collection.create_index(
    [("user_id", 1), ("month", 1)],
    unique=True
)

logger.info("Database connected and indexes ensured.")
