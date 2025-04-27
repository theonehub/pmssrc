import logging
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from database.database_connector import salary_components_collection, salary_component_assignments_collection
import uuid
from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB,
    SalaryComponentAssignment,
    SalaryComponentDeclaration
)

from typing import List

# Configure logger
logger = logging.getLogger(__name__)

def serialize_salary_component(doc) -> SalaryComponentInDB:
    """
    Serialize MongoDB document into a SalaryComponentInDB Pydantic model.
    """
    return SalaryComponentInDB(
        sc_id=doc["sc_id"],
        name=doc["name"],
        type=doc["type"],
        is_active=doc["is_active"],
        is_visible=doc["is_visible"],
        is_mandatory=doc["is_mandatory"],
        declaration_required=doc["declaration_required"],
        description=doc.get("description"),
    )


async def create_salary_component(component: SalaryComponentCreate) -> SalaryComponentInDB:
    """
    Create a new salary component in the database.

    Args:
        component: SalaryComponentCreate Pydantic model with input data.

    Returns:
        SalaryComponentInDB: The created salary component.
    """
    logger.info("Creating a new salary component: %s", component.name)

    # Check for existing component with the same name
    existing = salary_components_collection.find_one({"name": component.name})
    if existing:
        logger.warning("Salary component with name '%s' already exists", component.name)
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
    print(doc)
    result = salary_components_collection.insert_one(doc)
    logger.info("Salary component created with ID: %s", result.inserted_id)

    return serialize_salary_component({**doc, "_id": result.inserted_id})


async def get_all_salary_components() -> list[SalaryComponentInDB]:
    """
    Retrieve all salary components from the database.

    Returns:
        List of SalaryComponentInDB
    """
    logger.info("Fetching all salary components")
    cursor = salary_components_collection.find()
    results = []
    for doc in cursor:
        results.append(serialize_salary_component(doc))
    logger.info("Fetched %d salary components", len(results))
    return results


async def get_salary_component_by_id(component_id: str) -> SalaryComponentInDB:
    """
    Get a salary component by its ID.

    Args:
        component_id: The ID of the component to fetch.

    Returns:
        SalaryComponentInDB
    """
    logger.info("Fetching salary component with ID: %s", component_id)

    doc = salary_components_collection.find_one({"sc_id": component_id})
    if not doc:
        logger.warning("Salary component not found with ID: %s", component_id)
        raise HTTPException(status_code=404, detail="Component not found")

    return serialize_salary_component(doc)


async def update_salary_component(component_id: str, update_data: SalaryComponentUpdate) -> SalaryComponentInDB:
    """
    Update an existing salary component.

    Args:
        component_id: ID of the component to update.
        update_data: Fields to update.

    Returns:
        Updated SalaryComponentInDB
    """
    logger.info("Updating salary component with ID: %s", component_id)

    update_fields = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_fields:
        logger.warning("No valid fields to update for ID: %s", component_id)
        raise HTTPException(status_code=400, detail="No fields to update")

    result = salary_components_collection.update_one({"sc_id": component_id}, {"$set": update_fields})
    if result.matched_count == 0:
        logger.warning("No salary component found to update with ID: %s", component_id)
        raise HTTPException(status_code=404, detail="Component not found")

    logger.info("Updated salary component with ID: %s", component_id)
    updated_doc = salary_components_collection.find_one({"sc_id": component_id})
    return serialize_salary_component(updated_doc)


async def delete_salary_component(component_id: str) -> dict:
    """
    Delete a salary component from the database.

    Args:
        component_id: ID of the component to delete.

    Returns:
        Dict with success message.
    """
    logger.info("Deleting salary component with ID: %s", component_id)

    result = salary_components_collection.delete_one({"sc_id": component_id})
    if result.deleted_count == 0:
        logger.warning("No salary component found to delete with ID: %s", component_id)
        raise HTTPException(status_code=404, detail="Component not found")

    logger.info("Deleted salary component with ID: %s", component_id)
    return {"msg": "Salary component deleted successfully"}


async def create_salary_component_assignments(emp_id: str, components: List[SalaryComponentAssignment]) -> dict:
    """
    Create salary component assignments for an employee.
    Stores all components in a single document with the employee ID.

    Args:
        emp_id (str): Employee ID
        components (List[SalaryComponentAssignment]): List of components with min/max values

    Returns:
        dict: Created assignment document
    """
    try:
        logger.info(f"Creating salary component assignments for employee {emp_id}")
        
        # Convert Pydantic models to dictionaries
        components_array = [
            {
                "sc_id": str(component.sc_id),
                "max_value": float(component.max_value)
            }
            for component in components
        ]

        # Create the document structure
        assignment_doc = {
            "emp_id": str(emp_id),
            "components": components_array,
            "updated_at": datetime.utcnow()
        }

        # Upsert the document (update if exists, insert if not)
        result = salary_component_assignments_collection.update_one(
            {"emp_id": emp_id},
            {"$set": assignment_doc},
            upsert=True
        )

        # Fetch and return the created/updated document
        created_assignment = salary_component_assignments_collection.find_one({"emp_id": emp_id})
        
        if created_assignment:
            # Remove MongoDB's _id field before returning
            created_assignment.pop('_id', None)
            return created_assignment
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to retrieve created assignment"
        )

    except Exception as e:
        logger.error(f"Error creating salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary component assignments: {str(e)}"
        )

async def get_salary_component_assignments(emp_id: str) -> List[SalaryComponentInDB]:
    """
    Get salary component assignments for an employee.

    Args:
        emp_id (str): Employee ID

    Returns:
        List[SalaryComponentInDB]: List of assigned salary components with their values
    """
    try:
        # Get assignments with component details using aggregation
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
        
        # Use list() to convert cursor to list
        assignments = list(salary_component_assignments_collection.aggregate(pipeline))
        
        if not assignments:
            return []
            
        return assignments
        
    except Exception as e:
        logger.error(f"Error fetching salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching salary component assignments: {str(e)}"
        )

async def create_salary_component_declarations(emp_id: str, components: List[SalaryComponentDeclaration]) -> dict:
    """
    Create salary component declarations for an employee.
    Updates the declared_value in the existing assignments.

    Args:
        emp_id (str): Employee ID
        components (List[SalaryComponentDeclaration]): List of components with declared values

    Returns:
        dict: Updated assignment document
    """
    try:
        logger.info(f"Creating salary component declarations for employee {emp_id}")
        
        # Get existing assignments
        existing_assignments = salary_component_assignments_collection.find_one({"emp_id": emp_id})
        if not existing_assignments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No component assignments found for this employee"
            )

        # Update declared values
        for component in components:
            # Find the component in assignments
            for assigned_component in existing_assignments["components"]:
                if assigned_component["sc_id"] == component.sc_id:
                    # Validate declared value is within min/max range
                    if component.declared_value > assigned_component["max_value"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Declared value for component {component.sc_id} must be less than or equal to {assigned_component['max_value']}"
                        )
                    # Update the declared value
                    assigned_component["declared_value"] = component.declared_value
                    break

        # Update the document
        result = salary_component_assignments_collection.update_one(
            {"emp_id": emp_id},
            {"$set": {"components": existing_assignments["components"], "updated_at": datetime.now()}}
        )

        # Fetch and return the updated document
        updated_assignment = salary_component_assignments_collection.find_one({"emp_id": emp_id})
        if updated_assignment:
            # Remove MongoDB's _id field before returning
            updated_assignment.pop('_id', None)
            return updated_assignment
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to retrieve updated assignment"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating salary component declarations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary component declarations: {str(e)}"
        )

async def get_salary_component_declarations(emp_id: str) -> List[dict]:
    """
    Get salary component declarations for an employee.

    Args:
        emp_id (str): Employee ID

    Returns:
        List[dict]: List of assigned salary components with their declared values
    """
    try:
        # Get assignments with component details using aggregation
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
        
        # Use list() to convert cursor to list
        declarations = list(salary_component_assignments_collection.aggregate(pipeline))
        
        if not declarations:
            return []
            
        return declarations
        
    except Exception as e:
        logger.error(f"Error fetching salary component declarations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching salary component declarations: {str(e)}"
        )


