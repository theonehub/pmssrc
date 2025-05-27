import logging
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from database.database_connector import (
    employee_salary_collection,
    user_collection,
)
from domain.entities.employee_salary import (
    EmployeeSalaryCreate,
    EmployeeSalaryUpdate,
    EmployeeSalaryInDB,
    BulkEmployeeSalaryCreate
)

logger = logging.getLogger(__name__)

def serialize_employee_salary(doc) -> EmployeeSalaryInDB:
    """
    Convert a MongoDB document into an EmployeeSalaryInDB schema.
    """
    return EmployeeSalaryInDB(
        id=str(doc["_id"]),
        employee_id=doc["employee_id"],
        component_id=doc["component_id"],
        max_amount=doc["max_amount"],
        min_amount=doc["min_amount"],
        is_editable=doc["is_editable"],
        created_at=doc["created_at"]
    )


def create_employee_salary(data: EmployeeSalaryCreate) -> EmployeeSalaryInDB:
    logger.info(f"Creating salary assignment for employee {data.employee_id}")
    
    doc = data.dict()
    doc["created_at"] = datetime.utcnow()
    
    result = employee_salary_collection.insert_one(doc)
    logger.info(f"Salary assignment created with ID: {result.inserted_id}")

    return serialize_employee_salary({**doc, "_id": result.inserted_id})


def get_employee_salary_by_employee_id(employee_id: str) -> list[EmployeeSalaryInDB]:
    logger.info(f"Fetching salary assignments for employee {employee_id}")
    
    cursor = employee_salary_collection.find({"employee_id": employee_id})
    return [serialize_employee_salary(doc) for doc in cursor]


def update_employee_salary(salary_id: str, data: EmployeeSalaryUpdate) -> EmployeeSalaryInDB:
    logger.info(f"Updating salary record {salary_id}")
    
    try:
        obj_id = ObjectId(salary_id)
    except Exception:
        logger.error("Invalid ObjectId format")
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    if not update_fields:
        logger.warning("No fields to update")
        raise HTTPException(status_code=400, detail="No fields to update")

    result = employee_salary_collection.update_one({"_id": obj_id}, {"$set": update_fields})
    if result.matched_count == 0:
        logger.warning(f"No salary entry found with ID: {salary_id}")
        raise HTTPException(status_code=404, detail="Salary entry not found")

    updated_doc = employee_salary_collection.find_one({"_id": obj_id})
    return serialize_employee_salary(updated_doc)


def delete_employee_salary(salary_id: str):
    logger.info(f"Deleting salary entry with ID: {salary_id}")
    
    try:
        obj_id = ObjectId(salary_id)
    except Exception:
        logger.error("Invalid ObjectId format")
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = employee_salary_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        logger.warning(f"No salary entry found to delete with ID: {salary_id}")
        raise HTTPException(status_code=404, detail="Salary entry not found")

    logger.info(f"Successfully deleted salary entry {salary_id}")


def serialize_salary(salary):
    """
    Convert MongoDB document into dictionary with `id` instead of `_id`.
    """
    salary["id"] = str(salary["_id"])
    del salary["_id"]
    return salary


def assign_salary_structure(employee_id: str, components_data: list[EmployeeSalaryCreate]):
    """
    Assign or update a complete salary structure for an employee.
    Replaces all previous components with the new ones.
    """
    try:
        logger.info(f"Assigning salary structure for employee_id={employee_id} with {len(components_data)} components")

        # Step 1: Delete existing entries for the employee
        employee_salary_collection.delete_many({"employee_id": employee_id})
        logger.info("Old salary components deleted")

        # Step 2: Insert new components
        now = datetime.utcnow()
        new_entries = []
        for comp in components_data:
            entry = {
                "employee_id": employee_id,
                "component_id": comp.component_id,
                "max_amount": comp.max_amount,
                "min_amount": comp.min_amount,
                "is_editable": comp.is_editable,
                "created_at": now,
            }
            new_entries.append(entry)

        result = employee_salary_collection.insert_many(new_entries)
        logger.info(f"Inserted {len(result.inserted_ids)} new salary components")

        # Step 3: Fetch and return inserted records
        inserted_docs = employee_salary_collection.find({
            "_id": {"$in": result.inserted_ids}
        }).to_list(length=None)
        salary_docs = [serialize_salary(doc) for doc in inserted_docs]

        # ✅ Step 4: Mark user as salaryAssigned
        user_update_result = user_collection.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": {"salaryAssigned": True}}
        )
        if user_update_result.modified_count:
            logger.info(f"User {employee_id} marked as salaryAssigned")
        else:
            logger.warning(f"Failed to update user {employee_id} with salaryAssigned=True")

        return salary_docs

    except Exception as e:
        logger.error(f"Error assigning salary structure: {e}")
        raise e



def get_salary_structure_with_names(employee_id: str):
    """
    Fetch salary structure assigned to an employee with component names.
    """
    try:
        logger.info(f"Fetching salary structure with component names for employee_id={employee_id}")

        pipeline = [
            {"$match": {"employee_id": employee_id}},
            {
                "$lookup": {
                    "from": "salary_components",
                    "let": { "comp_id": { "$toObjectId": "$component_id" }},
                    "pipeline": [
                        { "$match": { "$expr": { "$eq": [ "$_id", "$$comp_id" ] }}}
                    ],
                    "as": "component_info"
                }
            },
            {"$unwind": "$component_info"},
            {
                "$project": {
                    "_id": 1,
                    "employee_id": 1,
                    "component_id": 1,
                    "component_name": "$component_info.name",
                    "max_amount": 1,
                    "min_amount": 1,
                    "is_editable": 1,
                    "created_at": 1
                }
            }
        ]

        results = employee_salary_collection.aggregate(pipeline).to_list(length=None)

        for doc in results:
            doc["id"] = str(doc["_id"])
            del doc["_id"]

        return results

    except Exception as e:
        logger.error(f"Error in get_salary_structure_with_names: {e}")
        raise e
