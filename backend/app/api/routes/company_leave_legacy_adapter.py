"""
Legacy Company Leave API Adapter
Provides backward compatibility for the old frontend API format
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging

from api.routes.company_leave_routes_v2 import get_company_leave_controller
from application.dto.company_leave_dto import CompanyLeaveCreateRequestDTO, CompanyLeaveUpdateRequestDTO, CompanyLeaveSearchFiltersDTO
from auth.auth import extract_emp_id, extract_hostname, role_checker

logger = logging.getLogger(__name__)

# Create legacy router
router = APIRouter(prefix="/company-leaves", tags=["Company Leaves Legacy Adapter"])


@router.get("/", response_model=List[Dict[str, Any]])
async def get_company_leaves_legacy(
    hostname: str = Depends(extract_hostname),
    controller = Depends(get_company_leave_controller)
):
    """Get company leaves in legacy format"""
    try:
        # Get data from V2 API
        filters = CompanyLeaveSearchFiltersDTO(active_only=True, skip=0, limit=100)
        v2_response = await controller.get_company_leaves(filters, hostname)
        
        # Transform to legacy format
        legacy_response = []
        for leave in v2_response:
            legacy_item = {
                "company_leave_id": leave.company_leave_id,
                "name": leave.leave_type.name if hasattr(leave, 'leave_type') else leave.get('leave_type', {}).get('name', ''),
                "count": leave.policy.annual_allocation if hasattr(leave, 'policy') else leave.get('policy', {}).get('annual_allocation', 0),
                "is_active": leave.is_active
            }
            legacy_response.append(legacy_item)
        
        return legacy_response
        
    except Exception as e:
        logger.error(f"Error in legacy adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Dict[str, Any])
async def create_company_leave_legacy(
    request_data: Dict[str, Any],
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller = Depends(get_company_leave_controller)
):
    """Create company leave in legacy format"""
    try:
        # Transform legacy format to V2 format
        leave_name = request_data.get('name', '')
        leave_code = leave_name.upper().replace(' ', '_')[:5] if leave_name else 'LEAVE'
        
        v2_request = CompanyLeaveCreateRequestDTO(
            leave_type_code=leave_code,
            leave_type_name=leave_name,
            leave_category='casual',  # Default category
            annual_allocation=int(request_data.get('count', 0)),
            created_by=current_emp_id,
            description=f"Legacy leave policy: {leave_name}",
            accrual_type='annually',
            requires_approval=request_data.get('requires_approval', True),
            is_encashable=request_data.get('is_encashable', False),
            available_during_probation=request_data.get('available_during_probation', True),
            min_advance_notice_days=1,
        )
        
        # Call V2 API
        v2_response = await controller.create_company_leave(v2_request, current_emp_id, hostname)
        
        # Transform response to legacy format
        legacy_response = {
            "company_leave_id": v2_response.company_leave_id,
            "name": v2_response.leave_type.name,
            "count": v2_response.policy.annual_allocation,
            "is_active": v2_response.is_active
        }
        
        return legacy_response
        
    except Exception as e:
        logger.error(f"Error creating company leave in legacy adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{leave_id}", response_model=Dict[str, Any])
async def update_company_leave_legacy(
    leave_id: str,
    request_data: Dict[str, Any],
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller = Depends(get_company_leave_controller)
):
    """Update company leave in legacy format"""
    try:
        # Transform legacy format to V2 format
        v2_request = CompanyLeaveUpdateRequestDTO(
            updated_by=current_emp_id,
            leave_type_name=request_data.get('name'),
            annual_allocation=int(request_data.get('count', 0)) if request_data.get('count') is not None else None,
            is_active=request_data.get('is_active')
        )
        
        # Call V2 API
        v2_response = await controller.update_company_leave(leave_id, v2_request, current_emp_id, hostname)
        
        # Transform response to legacy format
        legacy_response = {
            "company_leave_id": v2_response.company_leave_id,
            "name": v2_response.leave_type.name,
            "count": v2_response.policy.annual_allocation,
            "is_active": v2_response.is_active
        }
        
        return legacy_response
        
    except Exception as e:
        logger.error(f"Error updating company leave in legacy adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{leave_id}")
async def delete_company_leave_legacy(
    leave_id: str,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller = Depends(get_company_leave_controller)
):
    """Delete company leave in legacy format"""
    try:
        # Call V2 API
        await controller.delete_company_leave(leave_id, current_emp_id, hostname)
        
        return {"message": "Company leave deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting company leave in legacy adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 