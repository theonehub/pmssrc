import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import json
from fastapi import HTTPException

from database.payout_database import PayoutDatabase
from services.taxation_service import calculate_total_tax, get_or_create_taxation_by_emp_id
from services.user_service import get_user_by_emp_id, get_all_users
from models.payout import (
    PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus,
    BulkPayoutRequest, BulkPayoutResponse, PayoutSummary,
    PayoutSchedule, PayoutHistory, PayslipData
)

logger = logging.getLogger(__name__)

# Service Functions (following leave_service pattern)

def calculate_monthly_payout_service(
    employee_id: str, 
    month: int, 
    year: int,
    hostname: str,
    override_salary: Optional[Dict[str, float]] = None
) -> PayoutCreate:
    """
    Calculate monthly payout for an employee including tax calculations
    """
    try:
        logger.info(f"Calculating monthly payout for employee {employee_id} for {month}/{year}")
        
        payout_db = PayoutDatabase(hostname)
        
        # Get employee information
        employee = get_user_by_emp_id(employee_id, hostname)
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
        
        # Calculate pay period
        pay_period_start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        pay_period_end = date(year, month, last_day)
        payout_date = date(year, month, 30) if last_day >= 30 else date(year, month, last_day)
        
        # Get annual salary calculation from taxation service
        # First, try to get the taxation data for salary components
        tax_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
        
        if not tax_data:
            # If no tax data exists, create default values
            annual_gross_salary = 600000  # Default 5 lakhs per annum
            basic_salary = annual_gross_salary * 0.5 / 12  # 50% basic
            da = annual_gross_salary * 0.2 / 12  # 20% DA
            hra = annual_gross_salary * 0.2 / 12  # 20% HRA
            special_allowance = annual_gross_salary * 0.1 / 12  # 10% special allowance
            bonus = 0
            annual_tax = 0
            monthly_tax = 0
        else:
            # Extract salary components from tax data
            salary_data = tax_data.get("salary", {})
            annual_gross_salary = (
                salary_data.get("basic", 300000) +
                salary_data.get("dearness_allowance", 120000) +
                salary_data.get("hra", 120000) +
                salary_data.get("special_allowance", 60000) +
                salary_data.get("bonus", 0)
            )
            
            # Calculate monthly components from annual values
            basic_salary = salary_data.get("basic", 300000) / 12
            da = salary_data.get("dearness_allowance", 120000) / 12
            hra = salary_data.get("hra", 120000) / 12
            special_allowance = salary_data.get("special_allowance", 60000) / 12
            bonus = salary_data.get("bonus", 0) / 12
            
            # Calculate tax using the taxation service
            try:
                annual_tax = calculate_total_tax(employee_id, hostname)
                monthly_tax = annual_tax / 12
            except Exception as tax_error:
                logger.warning(f"Tax calculation failed for {employee_id}: {str(tax_error)}")
                annual_tax = 0
                monthly_tax = 0
        
        # Apply overrides if provided
        if override_salary:
            basic_salary = override_salary.get("basic_salary", basic_salary)
            da = override_salary.get("da", da)
            hra = override_salary.get("hra", hra)
            special_allowance = override_salary.get("special_allowance", special_allowance)
            bonus = override_salary.get("bonus", bonus)
        
        # Calculate statutory deductions
        epf_rate = 0.12  # 12% of basic + DA
        epf_base = basic_salary + da
        epf_employee = min(epf_base * epf_rate, 1800)  # Max ₹1,800 per month
        epf_employer = epf_employee
        
        # ESI calculation (if applicable - salary < ₹25,000 per month)
        esi_rate = 0.0075  # 0.75% employee, 3.25% employer
        gross_for_esi = basic_salary + da + hra + special_allowance
        esi_employee = gross_for_esi * esi_rate if gross_for_esi <= 25000 else 0
        esi_employer = gross_for_esi * 0.0325 if gross_for_esi <= 25000 else 0
        
        # Calculate monthly gross for professional tax calculation
        monthly_gross = basic_salary + da + hra + special_allowance + bonus
        
        # Professional Tax (varies by state - assuming Maharashtra)
        professional_tax = _calculate_professional_tax(monthly_gross)
        
        # TDS calculation
        monthly_tds = max(0, monthly_tax)
        
        # Recalculate gross with actual components
        actual_gross = (basic_salary + da + hra + special_allowance + bonus)
        
        # Total deductions
        total_deductions = (epf_employee + esi_employee + professional_tax + monthly_tds)
        
        # Net salary
        net_salary = max(0, actual_gross - total_deductions)
        
        # Get tax regime from employee's tax data
        tax_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
        tax_regime = tax_data.get("tax_regime", "new") if tax_data else "new"
        
        payout = PayoutCreate(
            employee_id=employee_id,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            payout_date=payout_date,
            
            # Salary Components
            basic_salary=round(basic_salary, 2),
            da=round(da, 2),
            hra=round(hra, 2),
            special_allowance=round(special_allowance, 2),
            bonus=round(bonus, 2),
            commission=0.0,
            transport_allowance=0.0,
            medical_allowance=0.0,
            other_allowances=0.0,
            
            # Deductions
            epf_employee=round(epf_employee, 2),
            epf_employer=round(epf_employer, 2),
            esi_employee=round(esi_employee, 2),
            esi_employer=round(esi_employer, 2),
            professional_tax=round(professional_tax, 2),
            tds=round(monthly_tds, 2),
            advance_deduction=0.0,
            loan_deduction=0.0,
            other_deductions=0.0,
            
            # Calculated totals
            gross_salary=round(actual_gross, 2),
            total_deductions=round(total_deductions, 2),
            net_salary=round(net_salary, 2),
            
            # Annual projections
            annual_gross_salary=round(annual_gross_salary, 2),
            annual_tax_liability=round(annual_tax, 2),
            monthly_tds=round(monthly_tds, 2),
            
            # Tax details
            tax_regime=tax_regime,
            tax_exemptions=0.0,  # Will be calculated during tax computation
            standard_deduction=0.0,  # Will be calculated during tax computation
            section_80c_claimed=0.0,  # Will be calculated during tax computation
            
            # Reimbursements
            reimbursements=0.0,
            
            # Status
            status=PayoutStatus.PENDING,
            notes=f"Auto-calculated for {month:02d}/{year}"
        )
        
        logger.info(f"Monthly payout calculated successfully for employee {employee_id}")
        return payout
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating monthly payout for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _calculate_professional_tax(monthly_gross: float) -> float:
    """Calculate professional tax based on monthly gross salary (Maharashtra rates)"""
    if monthly_gross <= 15000:
        return 175.0
    elif monthly_gross <= 20000:
        return 300.0
    else:
        return 300.0  # Max PT in Maharashtra

def create_payout_service(payout_data: PayoutCreate, hostname: str) -> PayoutInDB:
    """Create a new payout record"""
    try:
        payout_db = PayoutDatabase(hostname)
        
        # Check for duplicate payout
        if payout_db.check_duplicate_payout(
            payout_data.employee_id,
            payout_data.pay_period_start,
            payout_data.pay_period_end
        ):
            raise HTTPException(status_code=400, detail="Payout already exists for this period")
        
        return payout_db.create_payout(payout_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_employee_payouts_service(
    employee_id: str, 
    hostname: str,
    year: Optional[int] = None,
    month: Optional[int] = None
) -> List[PayoutInDB]:
    """Get payouts for an employee"""
    try:
        payout_db = PayoutDatabase(hostname)
        return payout_db.get_employee_payouts(employee_id, year, month)
    except Exception as e:
        logger.error(f"Error retrieving employee payouts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_payout_by_id_service(payout_id: str, hostname: str) -> PayoutInDB:
    """Get payout by ID"""
    try:
        payout_db = PayoutDatabase(hostname)
        payout = payout_db.get_payout_by_id(payout_id)
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        return payout
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_payout_service(payout_id: str, update_data: PayoutUpdate, hostname: str) -> PayoutInDB:
    """Update payout"""
    try:
        payout_db = PayoutDatabase(hostname)
        updated_payout = payout_db.update_payout(payout_id, update_data)
        if not updated_payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        return updated_payout
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_payout_status_service(
    payout_id: str, 
    status: PayoutStatus,
    updated_by: str,
    hostname: str
) -> Dict[str, str]:
    """Update payout status"""
    try:
        payout_db = PayoutDatabase(hostname)
        success = payout_db.update_payout_status(payout_id, status, updated_by)
        if not success:
            raise HTTPException(status_code=404, detail="Payout not found")
        return {"message": "Payout status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payout status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def bulk_process_monthly_payouts_service(request: BulkPayoutRequest, hostname: str) -> BulkPayoutResponse:
    """Process monthly payouts for multiple employees"""
    try:
        logger.info(f"Starting bulk payout processing for {len(request.employee_ids)} employees")
        
        payout_db = PayoutDatabase(hostname)
        
        month = request.pay_period_start.month
        year = request.pay_period_start.year
        
        successful_payouts = []
        errors = []
        
        for employee_id in request.employee_ids:
            try:
                # Check if payout already exists
                if payout_db.check_duplicate_payout(
                    employee_id,
                    request.pay_period_start,
                    request.pay_period_end
                ):
                    errors.append({
                        "employee_id": employee_id,
                        "error": "Payout already exists for this period"
                    })
                    continue
                
                # Calculate payout
                if request.auto_calculate_tax:
                    payout_data = calculate_monthly_payout_service(employee_id, month, year, hostname)
                else:
                    # Basic payout without tax calculations
                    payout_data = PayoutCreate(
                        employee_id=employee_id,
                        pay_period_start=request.pay_period_start,
                        pay_period_end=request.pay_period_end,
                        payout_date=request.payout_date,
                        notes=request.notes
                    )
                
                # Create payout
                created_payout = payout_db.create_payout(payout_data)
                
                # Auto-approve if requested
                if request.auto_approve:
                    payout_db.update_payout_status(
                        created_payout.id,
                        PayoutStatus.APPROVED
                    )
                
                successful_payouts.append(created_payout.id)
                
            except Exception as e:
                errors.append({
                    "employee_id": employee_id,
                    "error": str(e)
                })
        
        logger.info(f"Bulk payout processing completed: {len(successful_payouts)} successful, {len(errors)} errors")
        
        return BulkPayoutResponse(
            total_employees=len(request.employee_ids),
            successful_payouts=len(successful_payouts),
            failed_payouts=len(errors),
            payout_ids=successful_payouts,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error in bulk payout processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_monthly_payout_summary_service(month: int, year: int, hostname: str) -> PayoutSummary:
    """Get payout summary for a month"""
    try:
        payout_db = PayoutDatabase(hostname)
        return payout_db.get_payout_summary(month, year)
    except Exception as e:
        logger.error(f"Error retrieving payout summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_monthly_payouts_service(
    month: int, 
    year: int, 
    hostname: str,
    status: Optional[PayoutStatus] = None
) -> List[PayoutInDB]:
    """Get all payouts for a specific month"""
    try:
        payout_db = PayoutDatabase(hostname)
        return payout_db.get_monthly_payouts(month, year, status)
    except Exception as e:
        logger.error(f"Error retrieving monthly payouts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_payslip_data_service(payout_id: str, hostname: str) -> PayslipData:
    """Generate payslip data for download"""
    try:
        payout_db = PayoutDatabase(hostname)
        
        payout = payout_db.get_payout_by_id(payout_id)
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        
        # Get employee details
        employee = get_user_by_emp_id(payout.employee_id, hostname)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get company details (assuming from organization service)
        company_name = "Your Company Name"  # TODO: Get from organization service
        
        # Format pay period
        pay_period = f"{payout.pay_period_start.strftime('%B %Y')}"
        payout_date_str = payout.payout_date.strftime('%d %B %Y')
        
        # Prepare earnings
        earnings = {}
        if payout.basic_salary > 0:
            earnings["Basic Salary"] = payout.basic_salary
        if payout.da > 0:
            earnings["Dearness Allowance"] = payout.da
        if payout.hra > 0:
            earnings["House Rent Allowance"] = payout.hra
        if payout.special_allowance > 0:
            earnings["Special Allowance"] = payout.special_allowance
        if payout.bonus > 0:
            earnings["Bonus"] = payout.bonus
        if payout.transport_allowance > 0:
            earnings["Transport Allowance"] = payout.transport_allowance
        if payout.medical_allowance > 0:
            earnings["Medical Allowance"] = payout.medical_allowance
        if payout.other_allowances > 0:
            earnings["Other Allowances"] = payout.other_allowances
        if payout.reimbursements > 0:
            earnings["Reimbursements"] = payout.reimbursements
        
        # Prepare deductions
        deductions = {}
        if payout.epf_employee > 0:
            deductions["Employee PF"] = payout.epf_employee
        if payout.esi_employee > 0:
            deductions["Employee ESI"] = payout.esi_employee
        if payout.professional_tax > 0:
            deductions["Professional Tax"] = payout.professional_tax
        if payout.tds > 0:
            deductions["Income Tax (TDS)"] = payout.tds
        if payout.advance_deduction > 0:
            deductions["Advance Deduction"] = payout.advance_deduction
        if payout.loan_deduction > 0:
            deductions["Loan Deduction"] = payout.loan_deduction
        if payout.other_deductions > 0:
            deductions["Other Deductions"] = payout.other_deductions
        
        # Calculate YTD values
        ytd_payouts = get_employee_payouts_service(
            payout.employee_id,
            hostname,
            year=payout.pay_period_start.year
        )
        ytd_gross = sum(p.gross_salary for p in ytd_payouts)
        ytd_tax_deducted = sum(p.tds for p in ytd_payouts)
        
        payslip_data = PayslipData(
            employee_id=payout.employee_id,
            employee_name=employee.get('name', ''),
            employee_code=employee.get('emp_id', ''),
            department=employee.get('department', ''),
            designation=employee.get('designation', ''),
            pan_number=employee.get('pan_number', ''),
            uan_number=employee.get('uan_number', ''),
            bank_account=employee.get('bank_account', ''),
            
            pay_period=pay_period,
            payout_date=payout_date_str,
            days_in_month=calendar.monthrange(
                payout.pay_period_start.year, 
                payout.pay_period_start.month
            )[1],
            days_worked=calendar.monthrange(
                payout.pay_period_start.year, 
                payout.pay_period_start.month
            )[1],  # TODO: Get actual attendance
            
            earnings=earnings,
            total_earnings=payout.gross_salary,
            
            deductions=deductions,
            total_deductions=payout.total_deductions,
            
            net_pay=payout.net_salary,
            
            tax_regime=payout.tax_regime,
            ytd_gross=ytd_gross,
            ytd_tax_deducted=ytd_tax_deducted,
            
            company_name=company_name,
            company_address="Company Address"  # TODO: Get from organization
        )
        
        return payslip_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating payslip data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def create_payout_schedule_service(schedule: PayoutSchedule, hostname: str) -> Dict[str, str]:
    """Create or update payout schedule"""
    try:
        payout_db = PayoutDatabase(hostname)
        success = payout_db.create_payout_schedule(schedule)
        if success:
            return {"message": "Payout schedule created/updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create schedule")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payout schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def process_monthly_payout_schedule_service(hostname: str, target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Process scheduled monthly payouts (to be called by cron job on 30th)
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        month = target_date.month
        year = target_date.year
        
        logger.info(f"Processing scheduled payouts for {month}/{year}")
        
        payout_db = PayoutDatabase(hostname)
        
        # Check if there's an active schedule for this month
        schedule = payout_db.get_payout_schedule(month, year)
        if not schedule or not schedule.is_active or not schedule.auto_process:
            logger.info(f"No active auto-processing schedule found for {month}/{year}")
            return {
                "processed": False,
                "reason": "No active auto-processing schedule",
                "month": month,
                "year": year
            }
        
        # Check if it's the correct date to process
        if target_date.day != schedule.payout_date:
            logger.info(f"Not the scheduled payout date. Expected: {schedule.payout_date}, Current: {target_date.day}")
            return {
                "processed": False,
                "reason": f"Not scheduled payout date (expected: {schedule.payout_date})",
                "month": month,
                "year": year
            }
        
        # Get all active employees
        all_employees = get_all_users(hostname)
        active_employee_ids = [emp.get('emp_id', emp.get('_id')) for emp in all_employees if emp.get('is_active', True)]
        
        if not active_employee_ids:
            logger.warning("No active employees found for payout processing")
            return {
                "processed": False,
                "reason": "No active employees found",
                "month": month,
                "year": year
            }
        
        # Create bulk payout request
        last_day = calendar.monthrange(year, month)[1]
        bulk_request = BulkPayoutRequest(
            employee_ids=active_employee_ids,
            pay_period_start=date(year, month, 1),
            pay_period_end=date(year, month, last_day),
            payout_date=date(year, month, min(schedule.payout_date, last_day)),
            auto_calculate_tax=True,
            auto_approve=schedule.auto_approve,
            notes=f"Auto-generated payout for {month:02d}/{year}"
        )
        
        # Process bulk payouts
        result = bulk_process_monthly_payouts_service(bulk_request, hostname)
        
        logger.info(f"Scheduled payout processing completed: {result.successful_payouts} successful, {result.failed_payouts} failed")
        
        return {
            "processed": True,
            "month": month,
            "year": year,
            "total_employees": result.total_employees,
            "successful_payouts": result.successful_payouts,
            "failed_payouts": result.failed_payouts,
            "errors": result.errors
        }
        
    except Exception as e:
        logger.error(f"Error processing scheduled payouts: {str(e)}")
        return {
            "processed": False,
            "reason": f"Error: {str(e)}",
            "month": month if 'month' in locals() else None,
            "year": year if 'year' in locals() else None
        }

def get_employee_payout_history_service(employee_id: str, year: int, hostname: str) -> PayoutHistory:
    """Get annual payout history for an employee"""
    try:
        payout_db = PayoutDatabase(hostname)
        return payout_db.get_employee_payout_history(employee_id, year)
    except Exception as e:
        logger.error(f"Error retrieving payout history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy class for backward compatibility (if needed)
class PayoutService:
    def __init__(self, company_id: str):
        self.company_id = company_id
        self.payout_db = PayoutDatabase(company_id)
    
    def calculate_monthly_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int,
        override_salary: Optional[Dict[str, float]] = None
    ) -> PayoutCreate:
        return calculate_monthly_payout_service(employee_id, month, year, self.company_id, override_salary)
    
    def create_payout(self, payout_data: PayoutCreate) -> PayoutInDB:
        return create_payout_service(payout_data, self.company_id)
    
    def get_employee_payouts(
        self, 
        employee_id: str, 
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[PayoutInDB]:
        return get_employee_payouts_service(employee_id, self.company_id, year, month)
    
    def get_payout_by_id(self, payout_id: str) -> Optional[PayoutInDB]:
        try:
            return get_payout_by_id_service(payout_id, self.company_id)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise
    
    def update_payout(self, payout_id: str, update_data: PayoutUpdate) -> Optional[PayoutInDB]:
        try:
            return update_payout_service(payout_id, update_data, self.company_id)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise
    
    def update_payout_status(
        self, 
        payout_id: str, 
        status: PayoutStatus,
        updated_by: Optional[str] = None
    ) -> bool:
        try:
            update_payout_status_service(payout_id, status, updated_by or "", self.company_id)
            return True
        except HTTPException as e:
            if e.status_code == 404:
                return False
            raise
    
    def bulk_process_monthly_payouts(self, request: BulkPayoutRequest) -> BulkPayoutResponse:
        return bulk_process_monthly_payouts_service(request, self.company_id)
    
    def get_monthly_payout_summary(self, month: int, year: int) -> PayoutSummary:
        return get_monthly_payout_summary_service(month, year, self.company_id)
    
    def get_monthly_payouts(
        self, 
        month: int, 
        year: int, 
        status: Optional[PayoutStatus] = None
    ) -> List[PayoutInDB]:
        return get_monthly_payouts_service(month, year, self.company_id, status)
    
    def generate_payslip_data(self, payout_id: str) -> PayslipData:
        return generate_payslip_data_service(payout_id, self.company_id)
    
    def process_monthly_payout_schedule(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        return process_monthly_payout_schedule_service(self.company_id, target_date)
    
    def create_payout_schedule(self, schedule: PayoutSchedule) -> bool:
        try:
            create_payout_schedule_service(schedule, self.company_id)
            return True
        except HTTPException:
            return False
    
    def get_employee_payout_history(self, employee_id: str, year: int) -> PayoutHistory:
        return get_employee_payout_history_service(employee_id, year, self.company_id) 