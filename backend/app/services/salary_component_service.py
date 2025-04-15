import logging
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from database import salary_components_collection
from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB
)

# Configure logger
logger = logging.getLogger(__name__)

def serialize_salary_component(doc) -> SalaryComponentInDB:
    """
    Serialize MongoDB document into a SalaryComponentInDB Pydantic model.
    """
    return SalaryComponentInDB(
        id=str(doc["_id"]),
        name=doc["name"],
        type=doc["type"],
        description=doc.get("description"),
        created_at=doc["created_at"]
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
        "name": component.name,
        "type": component.type,
        "description": component.description,
        "created_at": datetime.utcnow()
    }

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
    try:
        obj_id = ObjectId(component_id)
    except Exception as e:
        logger.error("Invalid ObjectId format: %s", component_id)
        raise HTTPException(status_code=400, detail="Invalid ID format")

    doc = salary_components_collection.find_one({"_id": obj_id})
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
    try:
        obj_id = ObjectId(component_id)
    except Exception as e:
        logger.error("Invalid ObjectId format: %s", component_id)
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_fields = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_fields:
        logger.warning("No valid fields to update for ID: %s", component_id)
        raise HTTPException(status_code=400, detail="No fields to update")

    result = salary_components_collection.update_one({"_id": obj_id}, {"$set": update_fields})
    if result.matched_count == 0:
        logger.warning("No salary component found to update with ID: %s", component_id)
        raise HTTPException(status_code=404, detail="Component not found")

    logger.info("Updated salary component with ID: %s", component_id)
    updated_doc = salary_components_collection.find_one({"_id": obj_id})
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
    try:
        obj_id = ObjectId(component_id)
    except Exception:
        logger.error("Invalid ObjectId format: %s", component_id)
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = salary_components_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        logger.warning("No salary component found to delete with ID: %s", component_id)
        raise HTTPException(status_code=404, detail="Component not found")

    logger.info("Deleted salary component with ID: %s", component_id)
    return {"msg": "Salary component deleted successfully"}
