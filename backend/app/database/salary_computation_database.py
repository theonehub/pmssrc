from database.database_connector import connect_to_database

def get_salary_computation_collection(hostname: str):
    db = connect_to_database(hostname)
    return db["salary_computation"]

def get_salary_computation(emp_id: str, hostname: str):
    collection = get_salary_computation_collection(hostname)
    return collection.find_one({"emp_id": emp_id})