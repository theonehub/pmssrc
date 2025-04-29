from fastapi import HTTPException
from models.salary_component import SalaryComponentCreate, SalaryComponentInDB, SalaryComponentUpdate, SalaryComponentAssignment, SalaryComponentDeclaration
import logging
from database.database_connector import connect_to_database
from datetime import datetime
import uuid
from typing import List

logger = logging.getLogger(__name__)

def get_salary_components_collection(hostname: str):
    """
    Get the salary components collection for the given hostname.
    """
    db = connect_to_database(hostname)
    return db["salary_components"]

def get_salary_component_assignments_collection(hostname: str):
    """
    Get the salary component assignments collection for the given hostname.
    """
    db = connect_to_database(hostname)
    return db["salary_component_assignments"]

def serialize_salary_component(doc) -> SalaryComponentInDB:
    """
    Serialize MongoDB document into a SalaryComponentInDB Pydantic model.
    """
    return SalaryComponentInDB(
        sc_id=doc["sc_id"],
        name=doc["name"],
        type=doc["type"],
        key=doc.get("key"),
        max_value=doc.get("max_value"),
        declared_value=doc.get("declared_value"),
        actual_value=doc.get("actual_value"),
        is_active=doc["is_active"],
        is_visible=doc["is_visible"],
        is_mandatory=doc["is_mandatory"],
        declaration_required=doc["declaration_required"],
        description=doc.get("description"),
    )

def create_salary_component_db(component: SalaryComponentCreate, hostname: str) -> dict:
    """
    Create a new salary component in the database.
    """
    collection = get_salary_components_collection(hostname)

    # Check for existing component with the same name
    existing = collection.find_one({"name": component.name})
    if existing:
        raise HTTPException(status_code=400, detail="Component with this name already exists")

    doc = {
        "sc_id": str(uuid.uuid4()),
        "name": component.name,
        "type": component.type,
        "key": component.name.lower().replace(" ", ""),
        "is_active": component.is_active,
        "is_visible": component.is_visible,
        "is_mandatory": component.is_mandatory,
        "declaration_required": component.declaration_required,
        "description": component.description,
        "created_at": datetime.now()
    }

    result = collection.insert_one(doc)
    return doc

def get_all_salary_components_db(hostname: str) -> List[dict]:
    """
    Retrieve all salary components from the database.
    """
    collection = get_salary_components_collection(hostname)
    cursor = collection.find()
    return list(cursor)

def get_salary_component_by_id_db(sc_id: str, hostname: str) -> dict:
    """
    Get a salary component by its ID.
    """
    collection = get_salary_components_collection(hostname)
    doc = collection.find_one({"sc_id": sc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Component not found")
    return doc

def update_salary_component_db(sc_id: str, update_data: dict, hostname: str) -> dict:
    """
    Update an existing salary component.
    """
    collection = get_salary_components_collection(hostname)
    result = collection.update_one({"sc_id": sc_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Component not found")
    return collection.find_one({"sc_id": sc_id})

def delete_salary_component_db(sc_id: str, hostname: str) -> bool:
    """
    Delete a salary component from the database.
    """
    collection = get_salary_components_collection(hostname)
    result = collection.delete_one({"sc_id": sc_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Component not found")
    return True

def create_salary_component_assignments_db(emp_id: str, components: List[dict], hostname: str) -> dict:
    """
    Create salary component assignments for an employee.
    """
    collection = get_salary_component_assignments_collection(hostname)
    
    assignment_doc = {
        "emp_id": str(emp_id),
        "components": components,
        "updated_at": datetime.utcnow()
    }

    result = collection.update_one(
        {"emp_id": emp_id},
        {"$set": assignment_doc},
        upsert=True
    )

    created_assignment = collection.find_one({"emp_id": emp_id})
    if created_assignment:
        created_assignment.pop('_id', None)
        return created_assignment
    
    raise HTTPException(
        status_code=404,
        detail="Failed to retrieve created assignment"
    )

def get_salary_component_assignments_db(emp_id: str, hostname: str) -> List[dict]:
    """
    Get salary component assignments for an employee.
    """
    collection = get_salary_component_assignments_collection(hostname)
    pipeline = [
        {"$match": {"emp_id": emp_id}},
        {"$unwind": "$components"},
        {
            "$lookup": {
                "from": "salary_components",
                "localField": "components.sc_id",
                "foreignField": "sc_id",
                "as": "component_details"
            }
        },
        {"$unwind": "$component_details"},
        {
            "$project": {
                "sc_id": "$components.sc_id",
                "max_value": "$components.max_value",
                "name": "$component_details.name",
                "type": "$component_details.type",
                "description": "$component_details.description",
                "is_mandatory": "$component_details.is_mandatory",
                "declaration_required": "$component_details.declaration_required",
                "is_active": "$component_details.is_active",
                "is_visible": "$component_details.is_visible"
            }
        }
    ]
    
    return list(collection.aggregate(pipeline))

def create_salary_component_declarations_db(emp_id: str, components: List[dict], hostname: str) -> dict:
    """
    Create salary component declarations for an employee.
    """
    collection = get_salary_component_assignments_collection(hostname)
    
    existing_assignments = collection.find_one({"emp_id": emp_id})
    if not existing_assignments:
        raise HTTPException(
            status_code=404,
            detail="No component assignments found for this employee"
        )

    for component in components:
        for assigned_component in existing_assignments["components"]:
            if assigned_component["sc_id"] == component["sc_id"]:
                if component["declared_value"] > assigned_component["max_value"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Declared value for component {component['sc_id']} must be less than or equal to {assigned_component['max_value']}"
                    )
                assigned_component["declared_value"] = component["declared_value"]
                break

    result = collection.update_one(
        {"emp_id": emp_id},
        {"$set": {"components": existing_assignments["components"], "updated_at": datetime.now()}}
    )

    updated_assignment = collection.find_one({"emp_id": emp_id})
    if updated_assignment:
        updated_assignment.pop('_id', None)
        return updated_assignment
    
    raise HTTPException(
        status_code=404,
        detail="Failed to retrieve updated assignment"
    )

def get_salary_component_declarations_db(emp_id: str, hostname: str) -> List[dict]:
    """
    Get salary component declarations for an employee.
    """
    collection = get_salary_component_assignments_collection(hostname)
    pipeline = [
        {"$match": {"emp_id": emp_id}},
        {"$unwind": "$components"},
        {
            "$lookup": {
                "from": "salary_components",
                "localField": "components.sc_id",
                "foreignField": "sc_id",
                "as": "component_details"
            }
        },
        {"$unwind": "$component_details"},
        {
            "$project": {
                "sc_id": "$components.sc_id",
                "max_value": "$components.max_value",
                "declared_value": "$components.declared_value",
                "name": "$component_details.name",
                "type": "$component_details.type",
                "description": "$component_details.description",
                "is_mandatory": "$component_details.is_mandatory",
                "declaration_required": "$component_details.declaration_required",
                "is_active": "$component_details.is_active",
                "is_visible": "$component_details.is_visible"
            }
        }
    ]
    
    return list(collection.aggregate(pipeline))
