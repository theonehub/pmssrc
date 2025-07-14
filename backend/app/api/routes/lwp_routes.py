"""
LWP (Leave Without Pay) Routes
Standalone routes for LWP management operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import io

from app.api.controllers.employee_leave_controller import EmployeeLeaveController
from app.application.dto.employee_leave_dto import (
    EmployeeLeaveResponseDTO,
    LWPCalculationDTO,
    EmployeeLeaveValidationError,
    EmployeeLeaveBusinessRuleError,
    EmployeeLeaveNotFoundError
)
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role
from app.config.dependency_container import get_dependency_container

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/lwp", tags=["LWP Management"])

def get_employee_leave_controller() -> EmployeeLeaveController:
    """Get employee leave controller instance."""
    try:
        container = get_dependency_container()
        return container.get_employee_leave_controller()
    except Exception as e:
        logger.warning(f"Could not get employee leave controller from container: {e}")
        return EmployeeLeaveController()

def get_lwp_calculation_service():
    """Get LWP calculation service instance."""
    try:
        container = get_dependency_container()
        return container.get_lwp_calculation_service()
    except Exception as e:
        logger.warning(f"Could not get LWP calculation service from container: {e}")
        return None

def handle_lwp_exceptions(func):
    """Decorator to handle LWP-specific exceptions."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except EmployeeLeaveValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except EmployeeLeaveBusinessRuleError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except EmployeeLeaveNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in LWP operation: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

@router.get("/", response_model=List[Dict[str, Any]])
@handle_lwp_exceptions
async def get_lwp_records(
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get all LWP records for management interface."""
    logger.info(f"Fetching LWP records by: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get all leave records with LWP type
        from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
        
        filters = EmployeeLeaveSearchFiltersDTO(
            leave_type="lwp",
            limit=1000
        )
        
        leaves = await controller.search_leaves(filters, current_user)
        
        # Get current month and year for LWP calculation
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Get LWP calculation service
        lwp_service = get_lwp_calculation_service()
        
        # Transform to frontend format
        lwp_records = []
        for leave in leaves:
            # Calculate actual LWP days for this leave if service is available
            calculated_lwp_days = None
            if lwp_service:
                try:
                    lwp_result = await lwp_service.calculate_lwp_for_month(
                        leave.employee_id, current_month, current_year, current_user
                    )
                    calculated_lwp_days = lwp_result.lwp_days
                except Exception as e:
                    logger.warning(f"Could not calculate LWP for {leave.employee_id}: {e}")
            
            record = {
                "id": leave.leave_id if hasattr(leave, 'leave_id') else leave.id,
                "employee_id": leave.employee_id,
                "employee_name": leave.employee_name if hasattr(leave, 'employee_name') else "Unknown",
                "start_date": leave.start_date,
                "end_date": leave.end_date,
                "days": leave.days_requested if hasattr(leave, 'days_requested') else leave.leave_count,
                "status": leave.status,
                "present_days": getattr(leave, 'present_days', None),
                "calculated_lwp_days": calculated_lwp_days
            }
            lwp_records.append(record)
        
        return lwp_records
        
    except Exception as e:
        logger.error(f"Error fetching LWP records: {e}")
        return []

@router.put("/{lwp_id}", response_model=Dict[str, Any])
@handle_lwp_exceptions
async def update_lwp_record(
    lwp_id: str = Path(..., description="LWP record ID"),
    request: Dict[str, Any] = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Update LWP record."""
    logger.info(f"Updating LWP record {lwp_id} by: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get existing leave record
        existing_leave = await controller.get_leave_by_id(lwp_id, current_user)
        if not existing_leave:
            raise HTTPException(status_code=404, detail="LWP record not found")
        
        # Update present days if provided
        present_days = request.get('present_days')
        if present_days is not None:
            # Create update request
            from app.application.dto.employee_leave_dto import EmployeeLeaveUpdateRequestDTO
            
            update_request = EmployeeLeaveUpdateRequestDTO(
                present_days=present_days,
                updated_by=current_user.employee_id
            )
            
            response = await controller.update_leave(lwp_id, update_request, current_user)
            
            return {
                "message": "LWP record updated successfully",
                "lwp": response.dict()
            }
        
        return {"message": "No updates provided"}
        
    except Exception as e:
        logger.error(f"Error updating LWP record: {e}")
        raise HTTPException(status_code=500, detail="Failed to update LWP record")

@router.post("/update-bulk", response_model=Dict[str, Any])
@handle_lwp_exceptions
async def bulk_update_lwp(
    records: List[Dict[str, Any]] = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Bulk update LWP records."""
    logger.info(f"Bulk updating {len(records)} LWP records by: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        updated_count = 0
        errors = []
        
        for record in records:
            try:
                lwp_id = record.get('id')
                present_days = record.get('present_days')
                
                if lwp_id and present_days is not None:
                    from app.application.dto.employee_leave_dto import EmployeeLeaveUpdateRequestDTO
                    
                    update_request = EmployeeLeaveUpdateRequestDTO(
                        present_days=present_days,
                        updated_by=current_user.employee_id
                    )
                    
                    await controller.update_leave(lwp_id, update_request, current_user)
                    updated_count += 1
                    
            except Exception as e:
                errors.append(f"Failed to update record {record.get('id', 'unknown')}: {str(e)}")
        
        return {
            "message": f"Bulk update completed. Updated {updated_count} records.",
            "updated_count": updated_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk update")

@router.post("/import", response_model=Dict[str, Any])
@handle_lwp_exceptions
async def import_lwp_data(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Import LWP data from Excel file."""
    logger.info(f"Importing LWP data by: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # For now, return a placeholder response
        # TODO: Implement actual Excel import functionality
        return {
            "msg": "Import functionality is not yet implemented. Please use the API to create LWP records.",
            "imported_count": 0,
            "errors": ["Import functionality not implemented"]
        }
        
    except Exception as e:
        logger.error(f"Error importing LWP data: {e}")
        raise HTTPException(status_code=500, detail="Failed to import LWP data")

@router.get("/export", response_class=StreamingResponse)
@handle_lwp_exceptions
async def export_lwp_data(
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Export LWP data to Excel file."""
    logger.info(f"Exporting LWP data by: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get LWP records
        from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
        
        filters = EmployeeLeaveSearchFiltersDTO(
            leave_type="lwp",
            limit=10000
        )
        
        leaves = await controller.search_leaves(filters, current_user)
        
        # Create CSV content
        csv_content = "Employee ID,Employee Name,Start Date,End Date,Days,Status,Present Days\n"
        for leave in leaves:
            employee_name = leave.employee_name if hasattr(leave, 'employee_name') else "Unknown"
            days = leave.days_requested if hasattr(leave, 'days_requested') else leave.leave_count
            present_days = getattr(leave, 'present_days', '')
            
            csv_content += f"{leave.employee_id},{employee_name},{leave.start_date},{leave.end_date},{days},{leave.status},{present_days}\n"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LWP_Export_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting LWP data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export LWP data")

@router.delete("/{lwp_id}", response_model=Dict[str, Any])
@handle_lwp_exceptions
async def delete_lwp_record(
    lwp_id: str = Path(..., description="LWP record ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Delete LWP record."""
    logger.info(f"Deleting LWP record {lwp_id} by: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get existing leave record
        existing_leave = await controller.get_leave_by_id(lwp_id, current_user)
        if not existing_leave:
            raise HTTPException(status_code=404, detail="LWP record not found")
        
        # Soft delete the record
        from app.application.dto.employee_leave_dto import EmployeeLeaveUpdateRequestDTO
        
        update_request = EmployeeLeaveUpdateRequestDTO(
            is_deleted=True,
            updated_by=current_user.employee_id
        )
        
        await controller.update_leave(lwp_id, update_request, current_user)
        
        return {"message": "LWP record deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting LWP record: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete LWP record")

# Health check endpoint
@router.get("/health")
async def lwp_health_check():
    """Health check endpoint for LWP service."""
    return {
        "status": "healthy",
        "service": "lwp-management",
        "version": "1.0.0"
    } 