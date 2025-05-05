from fastapi import APIRouter, Depends, status, HTTPException, Body, UploadFile, File, Form
from auth.auth import extract_emp_id, extract_hostname
from typing import List
import io
import pandas as pd
from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB,
    SalaryComponentAssignment,
    SalaryComponentDeclaration
)
from services.salary_component_service import (
    create_salary_component,
    get_all_salary_components,
    get_salary_component_by_id,
    update_salary_component,
    delete_salary_component,
    create_salary_component_assignments,
    get_salary_component_assignments,
    create_salary_component_declarations,
    get_salary_component_declarations,
    import_salary_component_assignments_from_file
)
import logging
from utils.file_handler import validate_file

router = APIRouter(prefix="/salary-components", tags=["Salary Components"])

# Logger configuration
logger = logging.getLogger(__name__)

@router.post("/", response_model=SalaryComponentInDB, status_code=status.HTTP_201_CREATED)
def create_component(
    component: SalaryComponentCreate = Body(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Create a new salary component using JSON.
    """
    logger.info("API Call: Create salary component", component)
    return create_salary_component(component, hostname)

@router.get("/", response_model=List[SalaryComponentInDB])
def get_components(hostname: str = Depends(extract_hostname)):
    """
    Get all salary components.
    """
    logger.info("API Call: Get all salary components")
    return get_all_salary_components(hostname)

@router.get("/{sc_id}", response_model=SalaryComponentInDB)
def get_component(
    sc_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Get a specific salary component by ID.
    """
    logger.info("API Call: Get salary component with ID: %s", sc_id)
    return get_salary_component_by_id(sc_id, hostname)

@router.put("/{sc_id}", response_model=SalaryComponentInDB)
def update_component(
    sc_id: str,
    component: SalaryComponentUpdate = Body(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Update a salary component using JSON.
    """
    logger.info("API Call: Update salary component with ID: %s", sc_id)
    return update_salary_component(sc_id, component, hostname)

@router.delete("/{sc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_component(
    sc_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Delete a salary component.
    """
    logger.info("API Call: Delete salary component with ID: %s", sc_id)
    delete_salary_component(sc_id, hostname)
    return None

@router.post("/assignments/{emp_id}", status_code=status.HTTP_201_CREATED)
def create_assignments(
    emp_id: str,
    components: List[SalaryComponentAssignment] = Body(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Create salary component assignments for an employee using JSON.
    """
    logger.info("API Call: Create salary component assignments for employee with ID: %s", emp_id)
    return create_salary_component_assignments(emp_id, components, hostname)

@router.post("/assignments/import/with-file", status_code=status.HTTP_201_CREATED)
async def import_assignments_with_file(
    file: UploadFile = File(...),
    hostname: str = Depends(extract_hostname),
    current_emp_id: str = Depends(extract_emp_id)
):
    """
    Import salary component assignments from an Excel file.
    """
    # Validate file type and size
    is_valid, error = validate_file(
        file, 
        allowed_types=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
        max_size=5*1024*1024
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    try:
        # Read file content
        contents = await file.read()
        
        # Parse Excel file
        df = pd.read_excel(io.BytesIO(contents))
        
        # Convert DataFrame to list of dictionaries
        assignments_data = df.to_dict('records')
        
        # Import assignments
        result = import_salary_component_assignments_from_file(assignments_data, hostname)
        
        return {"message": f"Successfully imported {result['imported']} assignments", "details": result}
    except Exception as e:
        logger.error(f"Error importing salary component assignments: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assignments/{emp_id}", response_model=List[SalaryComponentInDB])
def get_assignments(
    emp_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Get salary component assignments for an employee.
    """
    logger.info("API Call: Get salary component assignments for employee with ID: %s", emp_id)
    return get_salary_component_assignments(emp_id, hostname)

@router.post("/declarations/{emp_id}", status_code=status.HTTP_201_CREATED)
def create_declarations(
    emp_id: str,
    components: List[SalaryComponentDeclaration] = Body(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Create salary component declarations for an employee using JSON.
    """
    logger.info("API Call: Create salary component declarations for employee with ID: %s", emp_id)
    return create_salary_component_declarations(emp_id, components, hostname)

@router.get("/declarations/{emp_id}")
def get_declarations(
    emp_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Get salary component declarations for an employee.
    """
    logger.info("API Call: Get salary component declarations for employee with ID: %s", emp_id)
    return get_salary_component_declarations(emp_id, hostname)

