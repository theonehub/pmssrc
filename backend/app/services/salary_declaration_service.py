from fastapi import HTTPException
from models.salary_declaration import SalaryDeclarationCreate, SalaryDeclarationResponse
from database import salary_components_collection, employee_salary_collection
from datetime import datetime
from bson import ObjectId


def convert_objectid_to_str(doc):
    """Converts all ObjectId fields in the document to strings."""
    doc["_id"] = str(doc["_id"])
    if "employee_id" in doc and isinstance(doc["employee_id"], ObjectId):
        doc["employee_id"] = str(doc["employee_id"])
    if "component_id" in doc and isinstance(doc["component_id"], ObjectId):
        doc["component_id"] = str(doc["component_id"])
    return doc


async def get_assigned_components_for_employee(user):
    print(user)
    employee_id = str(user.id)

    assignments =  employee_salary_collection.find({
        "employee_id": employee_id
    }).to_list(None)

    enriched_assignments = []

    for assignment in assignments:
        component_id = assignment.get("component_id")
        if component_id:
            # Fetch component details
            component =  salary_components_collection.find_one({"_id": ObjectId(component_id)})
            if component:
                assignment["component_name"] = component.get("name", "Unnamed Component")
        enriched_assignments.append(convert_objectid_to_str(assignment))

    return enriched_assignments


async def submit_salary_declaration(user, payload: SalaryDeclarationCreate):
    """
    Submits or updates the employee's declared amount for a salary component.

    Args:
        user (dict): Authenticated user object.
        payload (SalaryDeclarationCreate): Declaration input.

    Returns:
        SalaryDeclarationResponse: Confirmation of declaration.
    """
    employee_id = str(user["user_id"])
    component_id = str(payload.component_id)

    assignment =  employee_salary_collection.find_one({
        "employee_id": employee_id,
        "component_id": component_id
    })

    if not assignment:
        raise HTTPException(404, detail="Component not assigned")

    if not assignment.get("is_editable", False):
        raise HTTPException(403, detail="Component not editable")

    min_val = assignment.get("min_amount", 0)
    max_val = assignment.get("max_amount", 0)

    if not (min_val <= payload.declared_amount <= max_val):
        raise HTTPException(400, detail=f"Declared amount must be between {min_val} and {max_val}")

    # Update declared amount and time in the same assignment document
    employee_salary_collection.update_one(
        {"employee_id": employee_id, "component_id": component_id},
        {
            "$set": {
                "declared_amount": payload.declared_amount,
                "declared_on": datetime.utcnow()
            }
        }
    )

    # Prepare response
    response = {
        "employee_id": employee_id,
        "component_id": component_id,
        "declared_amount": payload.declared_amount,
        "declared_on": datetime.utcnow(),
        "id": f"{employee_id}_{component_id}"
    }

    return SalaryDeclarationResponse(**response)
