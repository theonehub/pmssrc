"""
Export API Routes
FastAPI route definitions for file export operations
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.auth.auth_dependencies import CurrentUser, get_current_user
from app.config.dependency_container import get_export_controller
from app.api.controllers.export_controller import ExportController


logger = logging.getLogger(__name__)

# Create router
export_v2_router = APIRouter(prefix="/v2/exports", tags=["exports"])


@export_v2_router.get("/processed-salaries/{format_type}")
async def export_processed_salaries(
    format_type: str = Path(..., description="Export format (csv, excel, bank_transfer)"),
    month: int = Query(..., description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    status: Optional[str] = Query(None, description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ExportController = Depends(get_export_controller)
):
    """Export processed salaries in specified format"""
    try:
        # Validate format type
        valid_formats = ['csv', 'excel', 'bank_transfer']
        if format_type.lower() not in valid_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
            )
        
        # Prepare filters
        filters = {
            'month': month,
            'year': year,
            'status': status,
            'department': department
        }
        
        # Generate file
        file_data, filename, content_type = await controller.export_processed_salaries(
            format_type=format_type,
            filters=filters,
            organisation_id=current_user.hostname
        )
        
        # Return file as streaming response
        return StreamingResponse(
            BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting processed salaries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@export_v2_router.get("/tds-report/{format_type}")
async def export_tds_report(
    format_type: str = Path(..., description="Export format (csv, excel, form_16, form_24q, fvu)"),
    month: int = Query(..., description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    quarter: Optional[int] = Query(None, description="Quarter (1-4) for Form 24Q and FVU"),
    status: Optional[str] = Query(None, description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ExportController = Depends(get_export_controller)
):
    """Export TDS report in specified format"""
    try:
        # Validate format type
        valid_formats = ['csv', 'excel', 'form_16', 'form_24q', 'fvu']
        if format_type.lower() not in valid_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
            )
        
        # Validate quarter for Form 24Q and FVU
        if format_type.lower() in ['form_24q', 'fvu'] and not quarter:
            raise HTTPException(
                status_code=400,
                detail="Quarter is required for Form 24Q and FVU formats"
            )
        
        if quarter and (quarter < 1 or quarter > 4):
            raise HTTPException(
                status_code=400,
                detail="Quarter must be between 1 and 4"
            )
        
        # Prepare filters
        filters = {
            'month': month,
            'year': year,
            'status': status,
            'department': department
        }
        
        # Generate file
        file_data, filename, content_type = await controller.export_tds_report(
            format_type=format_type,
            filters=filters,
            quarter=quarter,
            tax_year=year,
            organisation_id=current_user.hostname
        )
        
        # Return file as streaming response
        return StreamingResponse(
            BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting TDS report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@export_v2_router.get("/form-16/{employee_id}")
async def export_form_16(
    employee_id: str = Path(..., description="Employee ID"),
    tax_year: Optional[str] = Query(None, description="Tax year (e.g., 2024-2025)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ExportController = Depends(get_export_controller)
):
    """Export Form 16 for specific employee"""
    try:
        # Generate file
        file_data, filename, content_type = await controller.export_form_16(
            employee_id=employee_id,
            tax_year=tax_year,
            organisation_id=current_user.hostname
        )
        
        # Return file as streaming response
        return StreamingResponse(
            BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting Form 16: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@export_v2_router.get("/form-24q/quarter/{quarter}/year/{year}")
async def export_form_24q(
    quarter: int = Path(..., description="Quarter (1-4)"),
    year: int = Path(..., description="Tax year"),
    format_type: str = Query("csv", description="Format (csv, fvu)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ExportController = Depends(get_export_controller)
):
    """Export Form 24Q for specific quarter and year"""
    try:
        # Validate quarter
        if quarter < 1 or quarter > 4:
            raise HTTPException(
                status_code=400,
                detail="Quarter must be between 1 and 4"
            )
        
        # Validate format
        if format_type.lower() not in ['csv', 'fvu']:
            raise HTTPException(
                status_code=400,
                detail="Format must be either 'csv' or 'fvu'"
            )
        
        # Generate file
        file_data, filename, content_type = await controller.export_form_24q(
            quarter=quarter,
            tax_year=year,
            format_type=format_type,
            organisation_id=current_user.hostname
        )
        
        # Return file as streaming response
        return StreamingResponse(
            BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting Form 24Q: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@export_v2_router.get("/pf-report/{format_type}")
async def export_pf_report(
    format_type: str = Path(..., description="Export format (csv, excel, challan, return)"),
    month: int = Query(..., description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    quarter: Optional[int] = Query(None, description="Quarter (1-4) for challan and return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ExportController = Depends(get_export_controller)
):
    """Export PF report in specified format"""
    try:
        # Validate format type
        valid_formats = ['csv', 'excel', 'challan', 'return']
        if format_type.lower() not in valid_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
            )
        
        # Validate quarter for challan and return
        if format_type.lower() in ['challan', 'return'] and not quarter:
            raise HTTPException(
                status_code=400,
                detail="Quarter is required for challan and return formats"
            )
        
        if quarter and (quarter < 1 or quarter > 4):
            raise HTTPException(
                status_code=400,
                detail="Quarter must be between 1 and 4"
            )
        
        # Prepare filters
        filters = {
            'month': month,
            'year': year,
            'status': status,
            'department': department
        }
        
        # Generate file
        file_data, filename, content_type = await controller.export_pf_report(
            format_type=format_type,
            filters=filters,
            quarter=quarter,
            tax_year=year,
            organisation_id=current_user.hostname
        )
        
        # Return file as streaming response
        return StreamingResponse(
            BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PF report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")