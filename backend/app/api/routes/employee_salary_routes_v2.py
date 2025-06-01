"""
SOLID-Compliant Employee Salary Routes v2
Clean architecture implementation of employee salary HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from datetime import date, datetime

from app.api.controllers.employee_salary_controller import EmployeeSalaryController
from app.application.dto.employee_salary_dto import (
    EmployeeSalaryCreateRequestDTO, EmployeeSalaryUpdateRequestDTO,
    BulkEmployeeSalaryAssignRequestDTO, SalaryStructureQueryRequestDTO,
    SalaryCalculationRequestDTO, EmployeeSalaryResponseDTO, SalaryStructureResponseDTO,
    SalaryAssignmentStatusResponseDTO, BulkSalaryAssignmentResponseDTO,
    SalaryCalculationResponseDTO, SalaryFrequencyEnum, SalaryStatusEnum
)
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role
from app.config.dependency_container import get_dependency_container

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/employee-salary", tags=["employee-salary-v2"])

# Dependency for employee salary controller
async def get_employee_salary_controller() -> EmployeeSalaryController:
    """Get employee salary controller instance."""
    try:
        container = get_dependency_container()
        return container.get_employee_salary_controller()
    except Exception as e:
        logger.warning(f"Could not get employee salary controller from container: {e}")
        return EmployeeSalaryController()

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller)
) -> Dict[str, str]:
    """Health check for employee salary service."""
    return await controller.health_check()

# CRUD Operations
@router.post("", response_model=EmployeeSalaryResponseDTO)
async def create_employee_salary(
    request: EmployeeSalaryCreateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller)
) -> EmployeeSalaryResponseDTO:
    """
    Create a single salary component entry for an employee.
    
    Args:
        request: Employee salary creation request
        current_user: Current user object
        role: User role (admin, superadmin, manager)
        controller: Employee salary controller dependency
        
    Returns:
        Created salary component response
    """
    try:
        logger.info(f"Creating salary component {request.component_id} for employee {request.employee_id}")
        
        result = await controller.create_employee_salary(request, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating employee salary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}", response_model=List[EmployeeSalaryResponseDTO])
async def get_employee_salary_by_employee_id(
    employee_id: str,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> List[EmployeeSalaryResponseDTO]:
    """
    Get all salary components assigned to a specific employee.
    
    Args:
        employee_id: Employee ID to get salary components for
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role
        hostname: Organization hostname
        
    Returns:
        List of employee salary components
    """
    try:
        logger.info(f"Getting salary components for employee {employee_id}")
        
        # Check permissions - admin/manager can access any employee, users only their own
        if role not in ["admin", "superadmin", "manager"] and employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await controller.get_employee_salary_by_id(employee_id, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting employee salary components: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my/salary", response_model=List[EmployeeSalaryResponseDTO])
async def get_my_salary_components(
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    hostname: str = Depends(require_role("admin"))
) -> List[EmployeeSalaryResponseDTO]:
    """
    Get salary components for the current user.
    
    Args:
        controller: Employee salary controller dependency
        current_user: Current user object
        hostname: Organization hostname
        
    Returns:
        List of current user's salary components
    """
    return await controller.get_employee_salary_by_id(current_user.employee_id, hostname)

@router.put("/{salary_id}", response_model=EmployeeSalaryResponseDTO)
async def update_employee_salary(
    salary_id: str,
    request: EmployeeSalaryUpdateRequestDTO,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> EmployeeSalaryResponseDTO:
    """
    Update an employee's salary component details.
    
    Args:
        salary_id: Salary component ID to update
        request: Update request data
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Updated salary component response
    """
    try:
        logger.info(f"Updating salary component {salary_id}")
        
        result = await controller.update_employee_salary(salary_id, request, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating employee salary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{salary_id}")
async def delete_employee_salary(
    salary_id: str,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """
    Delete an employee's salary component entry.
    
    Args:
        salary_id: Salary component ID to delete
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Deletion confirmation
    """
    try:
        logger.info(f"Deleting salary component {salary_id}")
        
        result = await controller.delete_employee_salary(salary_id, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error deleting employee salary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Status and Assignment Operations
@router.get("/status/{employee_id}", response_model=SalaryAssignmentStatusResponseDTO)
async def check_salary_assignment_status(
    employee_id: str,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> SalaryAssignmentStatusResponseDTO:
    """
    Check if salary components are already assigned to the employee.
    
    Args:
        employee_id: Employee ID
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role
        hostname: Organization hostname
        
    Returns:
        Salary assignment status
    """
    try:
        logger.info(f"Checking salary assignment status for employee {employee_id}")
        
        # Check permissions - admin/manager can access any employee, users only their own
        if role not in ["admin", "superadmin", "manager"] and employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await controller.check_salary_assignment_status(employee_id, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking salary assignment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my/status", response_model=SalaryAssignmentStatusResponseDTO)
async def check_my_salary_assignment_status(
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    hostname: str = Depends(require_role("admin"))
) -> SalaryAssignmentStatusResponseDTO:
    """
    Check salary assignment status for the current user.
    
    Args:
        controller: Employee salary controller dependency
        current_user: Current user object
        hostname: Organization hostname
        
    Returns:
        Current user's salary assignment status
    """
    return await controller.check_salary_assignment_status(current_user.employee_id, hostname)

# Bulk Operations
@router.post("/bulk-assign", response_model=BulkSalaryAssignmentResponseDTO)
async def bulk_assign_salary_structure(
    request: BulkEmployeeSalaryAssignRequestDTO,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> BulkSalaryAssignmentResponseDTO:
    """
    Bulk assign salary components to an employee (insert or update).
    
    Args:
        request: Bulk salary assignment request
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Bulk assignment response
    """
    try:
        logger.info(f"Bulk assigning salary structure to employee {request.employee_id}")
        
        result = await controller.assign_salary_structure(request, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk salary assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{employee_id}/salary-structure", response_model=Dict[str, Any])
async def assign_salary_structure_legacy(
    employee_id: str,
    components: List[EmployeeSalaryCreateRequestDTO] = Body(...),
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """
    Legacy endpoint: Bulk assign salary components to an employee.
    
    Args:
        employee_id: Employee ID
        components: List of salary components to assign
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Assignment confirmation
    """
    try:
        logger.info(f"Legacy bulk assigning salary structure to employee {employee_id}")
        
        # Create bulk request
        bulk_request = BulkEmployeeSalaryAssignRequestDTO(
            employee_id=employee_id,
            components=components,
            effective_from=date.today(),
            replace_existing=False
        )
        
        result = await controller.assign_salary_structure(bulk_request, hostname)
        
        return {"message": "Salary structure updated successfully.", "operation_id": result.operation_id}
        
    except Exception as e:
        logger.error(f"Error in legacy salary assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Structure Operations
@router.get("/{employee_id}/salary-structure", response_model=SalaryStructureResponseDTO)
async def get_salary_structure(
    employee_id: str,
    as_of_date: Optional[date] = Query(None, description="Date for structure calculation"),
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> SalaryStructureResponseDTO:
    """
    Get full salary structure assigned to an employee.
    
    Args:
        employee_id: Employee ID
        as_of_date: Date for structure calculation (optional)
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role
        hostname: Organization hostname
        
    Returns:
        Salary structure response
    """
    try:
        logger.info(f"Getting salary structure for employee {employee_id}")
        
        # Check permissions - admin/manager can access any employee, users only their own
        if role not in ["admin", "superadmin", "manager"] and employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await controller.get_salary_structure(employee_id, hostname, as_of_date)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting salary structure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my/salary-structure", response_model=SalaryStructureResponseDTO)
async def get_my_salary_structure(
    as_of_date: Optional[date] = Query(None, description="Date for structure calculation"),
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    hostname: str = Depends(require_role("admin"))
) -> SalaryStructureResponseDTO:
    """
    Get salary structure for the current user.
    
    Args:
        as_of_date: Date for structure calculation (optional)
        controller: Employee salary controller dependency
        current_user: Current user object
        hostname: Organization hostname
        
    Returns:
        Current user's salary structure
    """
    return await controller.get_salary_structure(current_user.employee_id, hostname, as_of_date)

@router.get("/{employee_id}/salary-structure/view", response_model=List[EmployeeSalaryResponseDTO])
async def get_salary_structure_for_view(
    employee_id: str,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> List[EmployeeSalaryResponseDTO]:
    """
    View-only endpoint for salary structure (with component names).
    
    Args:
        employee_id: Employee ID
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role
        hostname: Organization hostname
        
    Returns:
        List of salary components with names
    """
    try:
        logger.info(f"Getting salary structure view for employee {employee_id}")
        
        # Check permissions - admin/manager can access any employee, users only their own
        if role not in ["admin", "superadmin", "manager"] and employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await controller.get_salary_structure_with_names(employee_id, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting salary structure view: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my/salary-structure/view", response_model=List[EmployeeSalaryResponseDTO])
async def get_my_salary_structure_for_view(
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    hostname: str = Depends(require_role("admin"))
) -> List[EmployeeSalaryResponseDTO]:
    """
    View-only endpoint for current user's salary structure.
    
    Args:
        controller: Employee salary controller dependency
        current_user: Current user object
        hostname: Organization hostname
        
    Returns:
        Current user's salary components with names
    """
    return await controller.get_salary_structure_with_names(current_user.employee_id, hostname)

# Calculation Operations
@router.post("/calculate", response_model=SalaryCalculationResponseDTO)
async def calculate_salary(
    request: SalaryCalculationRequestDTO,
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    hostname: str = Depends(require_role("admin"))
) -> SalaryCalculationResponseDTO:
    """
    Calculate salary for an employee on a specific date.
    
    Args:
        request: Salary calculation request
        controller: Employee salary controller dependency
        current_user: Current user object
        role: User role
        hostname: Organization hostname
        
    Returns:
        Salary calculation response
    """
    try:
        logger.info(f"Calculating salary for employee {request.employee_id}")
        
        # Check permissions - admin/manager can calculate for any employee, users only their own
        if role not in ["admin", "superadmin", "manager"] and request.employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await controller.calculate_salary(request, hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating salary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/my/calculate", response_model=SalaryCalculationResponseDTO)
async def calculate_my_salary(
    calculation_date: date = Body(...),
    include_variable_components: bool = Body(True),
    controller: EmployeeSalaryController = Depends(get_employee_salary_controller),
    current_user: CurrentUser = Depends(get_current_user),
    hostname: str = Depends(require_role("admin"))
) -> SalaryCalculationResponseDTO:
    """
    Calculate salary for the current user.
    
    Args:
        calculation_date: Date for salary calculation
        include_variable_components: Include variable components in calculation
        controller: Employee salary controller dependency
        current_user: Current user object
        hostname: Organization hostname
        
    Returns:
        Current user's salary calculation
    """
    # Create calculation request
    request = SalaryCalculationRequestDTO(
        employee_id=current_user.employee_id,
        calculation_date=calculation_date,
        include_variable_components=include_variable_components
    )
    
    return await controller.calculate_salary(request, hostname)

# Note: Exception handlers would be registered at the app level, not router level
# These are commented out for now as they require app-level registration

# async def value_error_handler(request, exc):
#     """Handle validation errors."""
#     logger.error(f"Validation error: {exc}")
#     raise HTTPException(status_code=400, detail=str(exc))

# async def http_exception_handler(request, exc):
#     """Handle HTTP exceptions."""
#     logger.error(f"HTTP error: {exc.detail}")
#     raise exc

# async def general_exception_handler(request, exc):
#     """Handle general exceptions."""
#     logger.error(f"Unexpected error: {exc}", exc_info=True)
#     raise HTTPException(status_code=500, detail="Internal server error")
