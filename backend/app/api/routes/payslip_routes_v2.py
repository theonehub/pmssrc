"""
SOLID-Compliant Payslip Routes v2
Clean architecture implementation of payslip HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import date, datetime
from io import BytesIO

from app.api.controllers.payslip_controller import PayslipController
from app.application.dto.payslip_dto import (
    PayslipGenerationRequestDTO, PayslipEmailRequestDTO, PayslipHistoryRequestDTO,
    BulkPayslipGenerationRequestDTO, BulkPayslipEmailRequestDTO, PayslipTemplateRequestDTO,
    PayslipScheduleRequestDTO, PayslipResponseDTO, PayslipEmailResponseDTO,
    PayslipHistoryResponseDTO, BulkPayslipOperationResponseDTO, PayslipSummaryResponseDTO,
    PayslipTemplateResponseDTO, PayslipScheduleResponseDTO, PayslipDownloadResponseDTO,
    PayslipFormatEnum, PayslipStatusEnum, BulkOperationTypeEnum,
    PayslipSearchFiltersDTO, PayslipSummaryDTO, PayslipAnalyticsDTO,
    PayslipValidationError, PayslipBusinessRuleError, PayslipNotFoundError
)
from app.config.dependency_container import get_dependency_container
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/payslips", tags=["payslips-v2"])

def get_payslip_controller() -> PayslipController:
    """Get payslip controller instance."""
    try:
        container = get_dependency_container()
        return container.get_payslip_controller()
    except Exception as e:
        logger.warning(f"Could not get payslip controller from container: {e}")
        return PayslipController()

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: PayslipController = Depends(get_payslip_controller)
) -> Dict[str, str]:
    """Health check for payslip service."""
    return await controller.health_check()

# PDF Generation and Download
@router.get("/pdf/{payout_id}")
async def download_payslip_pdf(
    payout_id: str,
    controller: PayslipController = Depends(get_payslip_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin"))
):
    """Download payslip as PDF for a specific payout."""
    try:
        logger.info(f"Downloading PDF payslip for payout {payout_id} by employee {current_user.employee_id}")
        
        # Create generation request
        request = PayslipGenerationRequestDTO(
            payout_id=payout_id,
            format=PayslipFormatEnum.PDF
        )
        
        # Generate PDF
        pdf_buffer = await controller.generate_payslip_pdf(request, current_user.hostname)
        
        # Create filename
        filename = f"payslip_{payout_id}.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading payslip PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading payslip PDF: {str(e)}")

@router.post("/generate", response_model=PayslipResponseDTO)
async def generate_payslip(
    request: PayslipGenerationRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: PayslipController = Depends(get_payslip_controller)
) -> PayslipResponseDTO:
    """Generate payslip for an employee."""
    try:
        logger.info(f"Generating payslip for employee {request.employee_id}")
        return await controller.generate_payslip(request, current_user.hostname)
    except Exception as e:
        logger.error(f"Error generating payslip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Email Operations
@router.post("/email/{payout_id}", response_model=PayslipEmailResponseDTO)
async def email_payslip(
    payout_id: str,
    recipient_email: Optional[str] = Body(None),
    custom_subject: Optional[str] = Body(None),
    custom_message: Optional[str] = Body(None),
    controller: PayslipController = Depends(get_payslip_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin"))
) -> PayslipEmailResponseDTO:
    """
    Email payslip to employee.
    
    Args:
        payout_id: ID of the payout record
        recipient_email: Optional email override
        custom_subject: Custom email subject
        custom_message: Custom email message
        controller: Payslip controller dependency
        current_user: Current user's authentication information
        role: User role
        
    Returns:
        Email status response
    """
    try:
        logger.info(f"Emailing payslip for payout {payout_id} by employee {current_user.employee_id}")
        
        # Create email request
        request = PayslipEmailRequestDTO(
            payout_id=payout_id,
            recipient_email=recipient_email,
            custom_subject=custom_subject,
            custom_message=custom_message
        )
        
        # Send email
        result = await controller.email_payslip(request, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error emailing payslip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# History Operations
@router.get("/history/{employee_id}", response_model=PayslipHistoryResponseDTO)
async def get_payslip_history(
    employee_id: str,
    year: int = Query(datetime.now().year, description="Year for payslip history"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (optional)"),
    controller: PayslipController = Depends(get_payslip_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin"))
) -> PayslipHistoryResponseDTO:
    """
    Get payslip history for an employee.
    
    Args:
        employee_id: Employee ID
        year: Year for history (default: current year)
        month: Month filter (optional)
        controller: Payslip controller dependency
        current_user: Current user's authentication information
        role: User role
        
    Returns:
        Payslip history response
    """
    try:
        logger.info(f"Getting payslip history for employee {employee_id} for year {year}")
        
        # Check permissions - admin/manager can access any employee, users only their own
        if role not in ["admin", "superadmin", "manager"] and employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create history request
        request = PayslipHistoryRequestDTO(
            employee_id=employee_id,
            year=year,
            month=month
        )
        
        # Get history
        history = await controller.get_payslip_history(request, current_user.hostname)
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting payslip history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-history", response_model=PayslipHistoryResponseDTO)
async def get_my_payslip_history(
    year: int = Query(datetime.now().year, description="Year for payslip history"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (optional)"),
    controller: PayslipController = Depends(get_payslip_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> PayslipHistoryResponseDTO:
    """
    Get payslip history for the current user.
    
    Args:
        year: Year for history (default: current year)
        month: Month filter (optional)
        controller: Payslip controller dependency
        current_user: Current user's authentication information
        
    Returns:
        Current user's payslip history
    """
    # Create history request
    request = PayslipHistoryRequestDTO(
        employee_id=current_user.employee_id,
        year=year,
        month=month
    )
    
    return await controller.get_payslip_history(request, current_user.hostname)

# Bulk Operations
@router.post("/generate/bulk", response_model=BulkPayslipOperationResponseDTO)
async def generate_monthly_payslips_bulk(
    request: BulkPayslipGenerationRequestDTO,
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> BulkPayslipOperationResponseDTO:
    """
    Generate payslips for all employees for a specific month (Admin/Manager only).
    
    Args:
        request: Bulk payslip generation request
        controller: Payslip controller dependency
        role: User role (admin, superadmin, manager)
        current_user: Current user's authentication information
        
    Returns:
        Bulk generation results
    """
    try:
        logger.info(f"Starting bulk payslip generation for {request.month:02d}/{request.year}")
        
        result = await controller.generate_bulk_payslips(request, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk payslip generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/bulk", response_model=BulkPayslipOperationResponseDTO)
async def bulk_email_payslips(
    background_tasks: BackgroundTasks,
    request: BulkPayslipEmailRequestDTO,
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> BulkPayslipOperationResponseDTO:
    """
    Email payslips to all employees for a specific month (Admin/Manager only).
    
    Args:
        background_tasks: FastAPI background tasks
        request: Bulk payslip email request
        controller: Payslip controller dependency
        role: User role (admin, superadmin, manager)
        current_user: Current user's authentication information
        
    Returns:
        Bulk email initiation status
    """
    try:
        logger.info(f"Starting bulk payslip email for {request.month:02d}/{request.year}")
        
        # Add bulk email task to background
        result = await controller.send_bulk_emails(request, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error initiating bulk payslip email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bulk/status/{operation_id}", response_model=BulkPayslipOperationResponseDTO)
async def get_bulk_operation_status(
    operation_id: str,
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> BulkPayslipOperationResponseDTO:
    """
    Get status of a bulk payslip operation.
    
    Args:
        operation_id: Bulk operation ID
        controller: Payslip controller dependency
        role: User role (admin, superadmin, manager)
        current_user: Current user's authentication information
        
    Returns:
        Bulk operation status
    """
    try:
        logger.info(f"Getting bulk operation status for {operation_id}")
        
        result = await controller.get_bulk_operation_status(operation_id, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting bulk operation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Summary and Analytics
@router.get("/summary/{year}/{month}", response_model=PayslipSummaryResponseDTO)
async def get_monthly_payslip_summary(
    year: int,
    month: int,
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> PayslipSummaryResponseDTO:
    """Get payslip summary for a specific month."""
    try:
        logger.info(f"Getting monthly payslip summary for {month:02d}/{year}")
        return await controller.get_monthly_summary(month, year, current_user.hostname)
    except Exception as e:
        logger.error(f"Error getting monthly payslip summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Schedule Operations
@router.post("/schedule/monthly", response_model=PayslipScheduleResponseDTO)
async def schedule_monthly_payslip_generation(
    request: PayslipScheduleRequestDTO,
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> PayslipScheduleResponseDTO:
    """
    Schedule monthly payslip generation.
    
    Args:
        request: Payslip schedule request
        controller: Payslip controller dependency
        role: User role (admin, superadmin)
        current_user: Current user's authentication information
        
    Returns:
        Created schedule response
    """
    try:
        logger.info(f"Creating payslip schedule for day {request.day_of_month}")
        
        result = await controller.create_schedule(request, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating payslip schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template Operations
@router.get("/templates", response_model=List[PayslipTemplateResponseDTO])
async def get_payslip_templates(
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> List[PayslipTemplateResponseDTO]:
    """
    Get available payslip templates.
    
    Args:
        controller: Payslip controller dependency
        role: User role (admin, superadmin, manager)
        current_user: Current user's authentication information
        
    Returns:
        List of available templates
    """
    try:
        logger.info("Getting payslip templates")
        
        result = await controller.get_templates(current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting payslip templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/template/default/{template_id}", response_model=Dict[str, Any])
async def set_default_payslip_template(
    template_id: str,
    controller: PayslipController = Depends(get_payslip_controller),
    role: str = Depends(require_role("admin")),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Set default payslip template.
    
    Args:
        template_id: Template ID to set as default
        controller: Payslip controller dependency
        role: User role (admin, superadmin)
        current_user: Current user's authentication information
        
    Returns:
        Operation result
    """
    try:
        logger.info(f"Setting default payslip template to {template_id}")
        
        result = await controller.set_default_template(template_id, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error setting default template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Download Information
@router.get("/download-info/{payout_id}", response_model=PayslipDownloadResponseDTO)
async def get_payslip_download_info(
    payout_id: str,
    controller: PayslipController = Depends(get_payslip_controller),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin"))
) -> PayslipDownloadResponseDTO:
    """
    Get payslip download information.
    
    Args:
        payout_id: Payout ID
        controller: Payslip controller dependency
        current_user: Current user's authentication information
        role: User role 
        
    Returns:
        Payslip download information
    """
    try:
        logger.info(f"Getting payslip download info for payout {payout_id}")
        
        result = await controller.get_payslip_download_info(payout_id, current_user.hostname)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting payslip download info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
