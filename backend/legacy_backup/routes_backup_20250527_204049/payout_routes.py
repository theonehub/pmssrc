from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import calendar
import json
from io import BytesIO
import logging

from auth.auth import extract_emp_id, extract_hostname, role_checker
from app.infrastructure.services.payroll_migration_service import (
    calculate_monthly_payout_service,
    create_payout_service,
    get_employee_payouts_service,
    get_payout_by_id_service,
    update_payout_service,
    update_payout_status_service,
    bulk_process_monthly_payouts_service,
    get_monthly_payouts_service,
    get_monthly_payout_summary_service,
    generate_payslip_data_service,
    get_employee_payout_history_service
)
from app.domain.entities.payout import (
    PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus,
    BulkPayoutRequest, BulkPayoutResponse, PayoutSummary,
    PayoutSchedule, PayoutHistory, PayslipData
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payouts", tags=["payouts"])

@router.post("/calculate", response_model=PayoutCreate)
async def calculate_monthly_payout(
    employee_id: str,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2050),
    override_salary: Optional[Dict[str, float]] = Body(None),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
):
    """
    Calculate monthly payout for an employee
    """
    return calculate_monthly_payout_service(
        employee_id, month, year, hostname, override_salary
    )

@router.post("/create", response_model=PayoutInDB)
async def create_payout(
    payout_data: PayoutCreate,
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
):
    """
    Create a new payout record
    """
    return create_payout_service(payout_data, hostname)

@router.get("/employee/{employee_id}", response_model=List[PayoutInDB])
async def get_employee_payouts(
    employee_id: str,
    year: Optional[int] = Query(None, ge=2020, le=2050),
    month: Optional[int] = Query(None, ge=1, le=12),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname),
):
    """
    Get payouts for a specific employee
    """
    # Check permissions - admin/manager can access any employee, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return get_employee_payouts_service(employee_id, hostname, year, month)

@router.get("/my-payouts", response_model=List[PayoutInDB])
async def get_my_payouts(
    year: Optional[int] = Query(None, ge=2020, le=2050),
    month: Optional[int] = Query(None, ge=1, le=12),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
):
    """
    Get payouts for the current user
    """
    return get_employee_payouts_service(emp_id, hostname, year, month)

@router.get("/{payout_id}", response_model=PayoutInDB)
async def get_payout_by_id(
    payout_id: str,
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname),
):
    """
    Get payout by ID
    """
    payout = get_payout_by_id_service(payout_id, hostname)
    
    # Check permissions - admin/manager can access any payout, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != payout.employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return payout

@router.put("/{payout_id}", response_model=PayoutInDB)
async def update_payout(
    payout_id: str,
    update_data: PayoutUpdate,
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
):
    """
    Update a payout record
    """
    return update_payout_service(payout_id, update_data, hostname)

@router.put("/{payout_id}/status")
async def update_payout_status(
    payout_id: str,
    status: PayoutStatus = Body(...),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
):
    """
    Update payout status
    """
    return update_payout_status_service(payout_id, status, emp_id, hostname)

@router.post("/bulk-process", response_model=BulkPayoutResponse)
async def bulk_process_payouts(
    request: BulkPayoutRequest,
    role: str = Depends(role_checker(["admin", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Process payouts for multiple employees
    """
    return bulk_process_monthly_payouts_service(request, hostname)

@router.get("/monthly/{year}/{month}", response_model=List[PayoutInDB])
async def get_monthly_payouts(
    year: int,
    month: int,
    status: Optional[PayoutStatus] = Query(None),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get all payouts for a specific month
    """
    return get_monthly_payouts_service(month, year, hostname, status)

@router.get("/summary/{year}/{month}", response_model=PayoutSummary)
async def get_monthly_payout_summary(
    year: int,
    month: int,
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get payout summary for a month
    """
    return get_monthly_payout_summary_service(month, year, hostname)

@router.get("/{payout_id}/payslip", response_model=PayslipData)
async def get_payslip_data(
    payout_id: str,
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get payslip data for a payout
    """
    # First check if payout exists and user has access
    payout = get_payout_by_id_service(payout_id, hostname)
    
    # Check permissions - admin/manager can access any payslip, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != payout.employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return generate_payslip_data_service(payout_id, hostname)

@router.get("/{payout_id}/payslip/download")
async def download_payslip(
    payout_id: str,
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Download payslip as JSON file
    """
    # First check if payout exists and user has access
    payout = get_payout_by_id_service(payout_id, hostname)
    
    # Check permissions - admin/manager can access any payslip, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != payout.employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    payslip_data = generate_payslip_data_service(payout_id, hostname)
    
    # Convert to JSON and create downloadable file
    payslip_json = payslip_data.dict()
    json_str = json.dumps(payslip_json, indent=2, default=str)
    
    # Create filename
    filename = f"payslip_{payslip_data.employee_name}_{payslip_data.pay_period.replace(' ', '_')}.json"
    
    # Create BytesIO object
    buffer = BytesIO()
    buffer.write(json_str.encode('utf-8'))
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/schedule", response_model=Dict[str, Any])
async def create_payout_schedule(
    schedule: PayoutSchedule,
    role: str = Depends(role_checker(["admin", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Create or update payout schedule
    """
    return create_payout_schedule_service(schedule, hostname)

@router.post("/process-scheduled")
async def process_scheduled_payouts(
    target_date: Optional[date] = Body(None),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Process scheduled payouts (manual trigger)
    """
    return process_monthly_payout_schedule_service(hostname, target_date)

@router.get("/history/{employee_id}/{year}", response_model=PayoutHistory)
async def get_employee_payout_history(
    employee_id: str,
    year: int,
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Get annual payout history for an employee
    """
    # Check permissions - admin/manager can access any employee, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return get_employee_payout_history_service(employee_id, year, hostname)

@router.get("/my-history/{year}", response_model=PayoutHistory)
async def get_my_payout_history(
    year: int,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Get annual payout history for the current user
    """
    return get_employee_payout_history_service(emp_id, year, hostname)

@router.post("/auto-generate/{employee_id}", response_model=PayoutInDB)
async def auto_generate_current_month_payout(
    employee_id: str,
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname)
):
    """
    Auto-generate payout for current month for an employee
    """
    # Get current month and year
    today = date.today()
    month = today.month
    year = today.year
    
    # Calculate payout
    payout_data = calculate_monthly_payout_service(employee_id, month, year, hostname)
    
    # Create payout
    return create_payout_service(payout_data, hostname) 