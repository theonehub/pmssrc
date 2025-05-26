from fastapi import APIRouter, HTTPException, Depends, Query, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from io import BytesIO

from services.payslip_service import (
    generate_payslip_pdf_service,
    generate_monthly_payslips_bulk_service,
    email_payslip_service,
    bulk_email_payslips_service,
    get_payslip_history_service
)
from auth.auth import extract_emp_id, extract_hostname, role_checker
from models.payout import PayoutStatus

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/payslip/pdf/{payout_id}")
def download_payslip_pdf(
    payout_id: str,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Download payslip as PDF for a specific payout
    
    Args:
        payout_id: ID of the payout record
        
    Returns:
        PDF file as streaming response
    """
    try:
        logger.info(f"Generating PDF payslip for payout {payout_id} by employee {current_emp_id}")
        
        # Generate PDF
        pdf_buffer = generate_payslip_pdf_service(payout_id, hostname)
        
        # Create filename
        filename = f"payslip_{payout_id}.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading payslip PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading payslip PDF: {str(e)}")

@router.post("/payslip/email/{payout_id}")
def email_payslip(
    payout_id: str,
    recipient_email: Optional[str] = None,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Email payslip to employee
    
    Args:
        payout_id: ID of the payout record
        recipient_email: Optional email override
        
    Returns:
        Email status message
    """
    try:
        logger.info(f"Emailing payslip for payout {payout_id} by employee {current_emp_id}")
        
        result = email_payslip_service(payout_id, hostname, recipient_email)
        
        return {
            "message": "Payslip emailed successfully",
            "payout_id": payout_id,
            "email": result["email"]
        }
        
    except Exception as e:
        logger.error(f"Error emailing payslip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error emailing payslip: {str(e)}")

@router.get("/payslip/history/{employee_id}")
def get_payslip_history(
    employee_id: str,
    year: int = Query(datetime.now().year, description="Year for payslip history"),
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Get payslip history for an employee
    
    Args:
        employee_id: Employee ID
        year: Year for history (default: current year)
        
    Returns:
        List of payslip records
    """
    try:
        logger.info(f"Getting payslip history for employee {employee_id} for year {year}")
        
        # Check if user can access this employee's data
        # (Allow access to own data or if user has admin role)
        if current_emp_id != employee_id:
            # This would need proper role checking implementation
            pass
        
        history = get_payslip_history_service(employee_id, year, hostname)
        
        return {
            "employee_id": employee_id,
            "year": year,
            "payslip_count": len(history),
            "payslips": history
        }
        
    except Exception as e:
        logger.error(f"Error getting payslip history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting payslip history: {str(e)}")

@router.post("/payslip/generate/bulk")
def generate_monthly_payslips_bulk(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, description="Year"),
    status_filter: Optional[PayoutStatus] = Query(None, description="Filter by payout status"),
    current_role: str = Depends(role_checker(["admin", "hr", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Generate payslips for all employees for a specific month (Admin/HR only)
    
    Args:
        month: Month (1-12)
        year: Year
        status_filter: Optional status filter
        
    Returns:
        Bulk generation results
    """
    try:
        logger.info(f"Starting bulk payslip generation for {month:02d}/{year}")
        
        result = generate_monthly_payslips_bulk_service(month, year, hostname, status_filter)
        
        return {
            "message": "Bulk payslip generation completed",
            "results": result
        }
        
    except Exception as e:
        logger.error(f"Error in bulk payslip generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in bulk payslip generation: {str(e)}")

@router.post("/payslip/email/bulk")
def bulk_email_payslips(
    background_tasks: BackgroundTasks,
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, description="Year"),
    current_role: str = Depends(role_checker(["admin", "hr", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Email payslips to all employees for a specific month (Admin/HR only)
    
    Args:
        month: Month (1-12)
        year: Year
        
    Returns:
        Bulk email initiation status
    """
    try:
        logger.info(f"Starting bulk payslip email for {month:02d}/{year}")
        
        # Add bulk email task to background
        background_tasks.add_task(bulk_email_payslips_service, month, year, hostname)
        
        return {
            "message": "Bulk payslip email process initiated",
            "month": month,
            "year": year,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error initiating bulk payslip email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating bulk payslip email: {str(e)}")

@router.get("/payslip/bulk/status")
def get_bulk_operation_status(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, description="Year"),
    operation: str = Query(..., description="Operation type: 'generate' or 'email'"),
    current_role: str = Depends(role_checker(["admin", "hr", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get status of bulk operations (Admin/HR only)
    
    Args:
        month: Month (1-12)
        year: Year
        operation: Operation type ('generate' or 'email')
        
    Returns:
        Operation status
    """
    try:
        # This would need to be implemented with a proper task queue system
        # For now, return a placeholder response
        return {
            "message": "Bulk operation status check",
            "month": month,
            "year": year,
            "operation": operation,
            "status": "completed",
            "note": "Status tracking requires task queue implementation"
        }
        
    except Exception as e:
        logger.error(f"Error getting bulk operation status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting bulk operation status: {str(e)}")

@router.get("/payslip/monthly/summary")
def get_monthly_payslip_summary(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, description="Year"),
    current_role: str = Depends(role_checker(["admin", "hr", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get monthly payslip generation summary (Admin/HR only)
    
    Args:
        month: Month (1-12)
        year: Year
        
    Returns:
        Monthly summary statistics
    """
    try:
        # This would integrate with the payout database to get statistics
        # For now, return a placeholder response
        return {
            "month": month,
            "year": year,
            "summary": {
                "total_employees": 0,
                "payslips_generated": 0,
                "payslips_emailed": 0,
                "pending_generation": 0,
                "pending_email": 0
            },
            "note": "Summary requires database integration"
        }
        
    except Exception as e:
        logger.error(f"Error getting monthly payslip summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting monthly payslip summary: {str(e)}")

@router.post("/payslip/schedule/monthly")
def schedule_monthly_payslip_generation(
    day_of_month: int = Query(..., ge=1, le=28, description="Day of month to generate payslips"),
    auto_email: bool = Query(False, description="Automatically email after generation"),
    current_role: str = Depends(role_checker(["admin", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Schedule automatic monthly payslip generation (Admin only)
    
    Args:
        day_of_month: Day of month to generate payslips (1-28)
        auto_email: Whether to automatically email after generation
        
    Returns:
        Scheduling status
    """
    try:
        # This would integrate with a scheduler like Celery or APScheduler
        # For now, return a placeholder response
        return {
            "message": "Monthly payslip generation scheduled",
            "day_of_month": day_of_month,
            "auto_email": auto_email,
            "status": "scheduled",
            "note": "Scheduling requires task scheduler implementation"
        }
        
    except Exception as e:
        logger.error(f"Error scheduling monthly payslip generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scheduling monthly payslip generation: {str(e)}")

@router.get("/payslip/templates")
def get_payslip_templates(
    current_role: str = Depends(role_checker(["admin", "hr", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get available payslip templates (Admin/HR only)
    
    Returns:
        List of available templates
    """
    try:
        # This would return available payslip templates
        templates = [
            {
                "id": "standard",
                "name": "Standard Template",
                "description": "Standard corporate payslip template",
                "is_default": True
            },
            {
                "id": "detailed",
                "name": "Detailed Template",
                "description": "Detailed payslip with comprehensive breakdown",
                "is_default": False
            },
            {
                "id": "minimal",
                "name": "Minimal Template",
                "description": "Minimal payslip template",
                "is_default": False
            }
        ]
        
        return {
            "templates": templates,
            "note": "Template customization requires implementation"
        }
        
    except Exception as e:
        logger.error(f"Error getting payslip templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting payslip templates: {str(e)}")

@router.put("/payslip/template/default")
def set_default_payslip_template(
    template_id: str,
    current_role: str = Depends(role_checker(["admin", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Set default payslip template (Admin only)
    
    Args:
        template_id: ID of the template to set as default
        
    Returns:
        Update status
    """
    try:
        # This would update the default template setting
        return {
            "message": "Default payslip template updated",
            "template_id": template_id,
            "note": "Template management requires implementation"
        }
        
    except Exception as e:
        logger.error(f"Error setting default payslip template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting default payslip template: {str(e)}") 