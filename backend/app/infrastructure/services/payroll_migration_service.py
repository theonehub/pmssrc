"""
Payroll Migration Service
Implements SOLID repository interfaces while bridging to legacy services
This service provides backward compatibility during the migration process
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from io import BytesIO

from app.application.interfaces.repositories.payout_repository import (
    PayoutCommandRepository, PayoutQueryRepository, PayoutAnalyticsRepository
)
from app.application.interfaces.repositories.payslip_repository import (
    PayslipCommandRepository, PayslipQueryRepository, PayslipStorageRepository
)
from app.application.dto.payroll_dto import PayoutSearchFiltersDTO
from app.domain.value_objects.payroll_value_objects import PayslipMetadata
from app.domain.entities.payout import (
    PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus
)

# Import dependencies for legacy functionality
import calendar
from app.database.payout_database import PayoutDatabase
from app.infrastructure.services.taxation_migration_service import (
    TaxationMigrationService,
    LegacyTaxationCalculationRepository
)
from app.infrastructure.services.legacy_migration_service import get_user_by_emp_id, get_all_users
from app.infrastructure.services.employee_leave_legacy_service import calculate_lwp_for_month
from app.domain.entities.payout import (
    PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus,
    BulkPayoutRequest, BulkPayoutResponse, PayoutSummary,
    PayoutSchedule, PayoutHistory, PayslipData
)
from fastapi import HTTPException

# For payslip functionality
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Initialize taxation components
taxation_migration_service = TaxationMigrationService()
legacy_calculation_repo = LegacyTaxationCalculationRepository()

logger = logging.getLogger(__name__)


# ================================
# LEGACY PAYOUT SERVICE FUNCTIONS
# ================================

async def calculate_monthly_payout_service(
    employee_id: str, 
    month: int, 
    year: int,
    hostname: str,
    override_salary: Optional[Dict[str, float]] = None
) -> PayoutCreate:
    """Calculate monthly payout for an employee including tax calculations"""
    try:
        logger.info(f"Calculating monthly payout for employee {employee_id} for {month}/{year}")
        
        # Get employee information
        employee = get_user_by_emp_id(employee_id, hostname)
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
        
        # Calculate pay period and working days
        month_start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        month_end = date(year, month, last_day)
        
        # Get taxation data
        try:
            tax_data = await taxation_migration_service.get_taxation_data_legacy(employee_id, hostname)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Taxation data not found for employee {employee_id}. Please fill taxation data first."
                )
            else:
                raise
        
        # Extract salary components
        salary_data = tax_data.get("salary", {})
        basic_annual = salary_data.get("basic", 0)
        da_annual = salary_data.get("dearness_allowance", 0)
        hra_annual = salary_data.get("hra", 0)
        special_allowance_annual = salary_data.get("special_allowance", 0)
        bonus_annual = salary_data.get("bonus", 0)
        
        # Calculate LWP and working days
        try:
            lwp_days = calculate_lwp_for_month(employee_id, month, year, hostname)
        except Exception:
            lwp_days = 0
        
        working_days_in_period = last_day
        effective_working_days = max(0, working_days_in_period - lwp_days)
        effective_working_ratio = effective_working_days / last_day
        
        # Calculate monthly components
        basic_salary = (basic_annual / 12) * effective_working_ratio
        da = (da_annual / 12) * effective_working_ratio
        hra = (hra_annual / 12) * effective_working_ratio
        special_allowance = (special_allowance_annual / 12) * effective_working_ratio
        bonus = (bonus_annual / 12) * effective_working_ratio
        
        # Calculate tax
        try:
            current_year = datetime.now().year
            tax_year = f"{current_year}-{current_year + 1}"
            tax_result = await legacy_calculation_repo.calculate_tax(
                employee_id, tax_year, hostname, force_recalculate=False
            )
            annual_tax = tax_result.get("total_tax", 0)
            monthly_tax = (annual_tax / 12) * effective_working_ratio
        except Exception:
            monthly_tax = 0
        
        # Apply overrides if provided
        if override_salary:
            basic_salary = override_salary.get("basic_salary", basic_salary)
            da = override_salary.get("da", da)
            hra = override_salary.get("hra", hra)
            special_allowance = override_salary.get("special_allowance", special_allowance)
            bonus = override_salary.get("bonus", bonus)
        
        # Calculate deductions
        epf_base = basic_salary + da
        epf_employee = min(epf_base * 0.12, 1800)
        monthly_gross = basic_salary + da + hra + special_allowance + bonus
        esi_employee = monthly_gross * 0.0075 if monthly_gross <= 25000 else 0
        professional_tax = _calculate_professional_tax(monthly_gross)
        
        gross_salary = monthly_gross
        total_deductions = epf_employee + esi_employee + professional_tax + monthly_tax
        net_salary = max(0, gross_salary - total_deductions)
        
        return PayoutCreate(
            employee_id=employee_id,
            pay_period_start=month_start,
            pay_period_end=month_end,
            payout_date=date(year, month, min(30, last_day)),
            
            # Attendance
            total_days_in_month=last_day,
            working_days_in_period=working_days_in_period,
            lwp_days=lwp_days,
            effective_working_days=effective_working_days,
            
            # Salary Components
            basic_salary=round(basic_salary, 2),
            da=round(da, 2),
            hra=round(hra, 2),
            special_allowance=round(special_allowance, 2),
            bonus=round(bonus, 2),
            
            # Deductions
            epf_employee=round(epf_employee, 2),
            esi_employee=round(esi_employee, 2),
            professional_tax=round(professional_tax, 2),
            tds=round(monthly_tax, 2),
            
            # Totals
            gross_salary=round(gross_salary, 2),
            total_deductions=round(total_deductions, 2),
            net_salary=round(net_salary, 2),
            
            # Tax details
            tax_regime=tax_data.get("regime", "new"),
            status=PayoutStatus.PENDING,
            notes=f"Auto-calculated for {month:02d}/{year}. LWP days: {lwp_days}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating monthly payout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_professional_tax(monthly_gross: float) -> float:
    """Calculate professional tax based on monthly gross salary (Maharashtra rates)"""
    if monthly_gross <= 15000:
        return 175.0
    elif monthly_gross <= 20000:
        return 300.0
    else:
        return 300.0


def create_payout_service(payout_data: PayoutCreate, hostname: str) -> PayoutInDB:
    """Create a new payout record"""
    try:
        payout_db = PayoutDatabase(hostname)
        if payout_db.check_duplicate_payout(
            payout_data.employee_id, payout_data.pay_period_start, payout_data.pay_period_end
        ):
            raise HTTPException(status_code=400, detail="Payout already exists for this period")
        return payout_db.create_payout(payout_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_employee_payouts_service(employee_id: str, hostname: str, year: Optional[int] = None, month: Optional[int] = None) -> List[PayoutInDB]:
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


def update_payout_status_service(payout_id: str, status: PayoutStatus, updated_by: str, hostname: str) -> Dict[str, str]:
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
        payout_db = PayoutDatabase(hostname)
        month = request.pay_period_start.month
        year = request.pay_period_start.year
        
        successful_payouts = []
        errors = []
        
        for employee_id in request.employee_ids:
            try:
                if payout_db.check_duplicate_payout(employee_id, request.pay_period_start, request.pay_period_end):
                    errors.append({"employee_id": employee_id, "error": "Payout already exists"})
                    continue
                
                if request.auto_calculate_tax:
                    payout_data = calculate_monthly_payout_service(employee_id, month, year, hostname)
                else:
                    payout_data = PayoutCreate(
                        employee_id=employee_id,
                        pay_period_start=request.pay_period_start,
                        pay_period_end=request.pay_period_end,
                        payout_date=request.payout_date,
                        notes=request.notes
                    )
                
                created_payout = payout_db.create_payout(payout_data)
                
                if request.auto_approve:
                    payout_db.update_payout_status(created_payout.id, PayoutStatus.APPROVED)
                
                successful_payouts.append(created_payout.id)
                
            except Exception as e:
                errors.append({"employee_id": employee_id, "error": str(e)})
        
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


def get_monthly_payouts_service(month: int, year: int, hostname: str, status: Optional[PayoutStatus] = None) -> List[PayoutInDB]:
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
        
        employee = get_user_by_emp_id(payout.employee_id, hostname)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Prepare earnings and deductions
        earnings = {}
        if payout.basic_salary > 0: earnings["Basic Salary"] = payout.basic_salary
        if payout.da > 0: earnings["Dearness Allowance"] = payout.da
        if payout.hra > 0: earnings["HRA"] = payout.hra
        if payout.special_allowance > 0: earnings["Special Allowance"] = payout.special_allowance
        if payout.bonus > 0: earnings["Bonus"] = payout.bonus
        
        deductions = {}
        if payout.epf_employee > 0: deductions["Employee PF"] = payout.epf_employee
        if payout.esi_employee > 0: deductions["Employee ESI"] = payout.esi_employee
        if payout.professional_tax > 0: deductions["Professional Tax"] = payout.professional_tax
        if payout.tds > 0: deductions["Income Tax"] = payout.tds
        
        # Calculate YTD values
        ytd_payouts = get_employee_payouts_service(payout.employee_id, hostname, year=payout.pay_period_start.year)
        ytd_gross = sum(p.gross_salary for p in ytd_payouts)
        ytd_tax_deducted = sum(p.tds for p in ytd_payouts)
        
        return PayslipData(
            employee_id=payout.employee_id,
            employee_name=employee.get('name', ''),
            employee_code=employee.get('emp_id', ''),
            department=employee.get('department', ''),
            designation=employee.get('designation', ''),
            pan_number=employee.get('pan_number', ''),
            uan_number=employee.get('uan_number', ''),
            bank_account=employee.get('bank_account', ''),
            
            pay_period=f"{payout.pay_period_start.strftime('%B %Y')}",
            payout_date=payout.payout_date.strftime('%d %B %Y'),
            days_in_month=getattr(payout, 'total_days_in_month', calendar.monthrange(payout.pay_period_start.year, payout.pay_period_start.month)[1]),
            days_worked=getattr(payout, 'working_days_in_period', calendar.monthrange(payout.pay_period_start.year, payout.pay_period_start.month)[1]),
            lwp_days=getattr(payout, 'lwp_days', 0),
            effective_working_days=getattr(payout, 'effective_working_days', calendar.monthrange(payout.pay_period_start.year, payout.pay_period_start.month)[1]),
            
            earnings=earnings,
            total_earnings=payout.gross_salary,
            deductions=deductions,
            total_deductions=payout.total_deductions,
            net_pay=payout.net_salary,
            
            tax_regime=payout.tax_regime,
            ytd_gross=ytd_gross,
            ytd_tax_deducted=ytd_tax_deducted,
            
            company_name="Your Company Name",
            company_address="Company Address"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating payslip data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_employee_payout_history_service(employee_id: str, year: int, hostname: str) -> PayoutHistory:
    """Get annual payout history for an employee"""
    try:
        payout_db = PayoutDatabase(hostname)
        return payout_db.get_employee_payout_history(employee_id, year)
    except Exception as e:
        logger.error(f"Error retrieving payout history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# LEGACY PAYSLIP SERVICE FUNCTIONS  
# ================================

def generate_payslip_pdf_service(payout_id: str, hostname: str) -> BytesIO:
    """Generate PDF payslip for a payout"""
    try:
        payslip_data = generate_payslip_data_service(payout_id, hostname)
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue)
        story.append(Paragraph(payslip_data.company_name, title_style))
        story.append(Paragraph("SALARY SLIP", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Employee info table
        info_data = [
            ['Employee Information', '', 'Pay Period Information', ''],
            ['Name:', payslip_data.employee_name, 'Pay Period:', payslip_data.pay_period],
            ['Employee Code:', payslip_data.employee_code or 'N/A', 'Pay Date:', payslip_data.payout_date],
            ['Department:', payslip_data.department or 'N/A', 'Days in Month:', str(payslip_data.days_in_month)],
            ['LWP Days:', str(payslip_data.lwp_days), 'Effective Working Days:', str(payslip_data.effective_working_days)],
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Earnings and deductions table
        earnings_deductions_data = [['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)']]
        
        earnings_list = list(payslip_data.earnings.items())
        deductions_list = list(payslip_data.deductions.items())
        max_rows = max(len(earnings_list), len(deductions_list))
        
        for i in range(max_rows):
            earning_name = earnings_list[i][0] if i < len(earnings_list) else ''
            earning_amount = f"{earnings_list[i][1]:,.2f}" if i < len(earnings_list) else ''
            deduction_name = deductions_list[i][0] if i < len(deductions_list) else ''
            deduction_amount = f"{deductions_list[i][1]:,.2f}" if i < len(deductions_list) else ''
            
            earnings_deductions_data.append([earning_name, earning_amount, deduction_name, deduction_amount])
        
        earnings_deductions_data.append(['TOTAL EARNINGS', f"{payslip_data.total_earnings:,.2f}", 'TOTAL DEDUCTIONS', f"{payslip_data.total_deductions:,.2f}"])
        
        ed_table = Table(earnings_deductions_data, colWidths=[2.5*inch, 1*inch, 2.5*inch, 1*inch])
        ed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(ed_table)
        story.append(Spacer(1, 20))
        
        # Net pay
        net_pay_data = [['NET PAY', f"₹ {payslip_data.net_pay:,.2f}"]]
        net_pay_table = Table(net_pay_data, colWidths=[5*inch, 2*inch])
        net_pay_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ]))
        story.append(net_pay_table)
        
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"Generated PDF payslip for payout {payout_id}")
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating PDF payslip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF payslip: {str(e)}")


def get_payslip_history_service(employee_id: str, year: int, hostname: str) -> List[Dict[str, Any]]:
    """Get payslip history for an employee"""
    try:
        payouts = get_employee_payouts_service(employee_id, hostname, year=year)
        
        payslip_history = []
        for payout in payouts:
            if payout.status in [PayoutStatus.PROCESSED, PayoutStatus.APPROVED, PayoutStatus.PAID]:
                payslip_history.append({
                    "payout_id": payout.id,
                    "pay_period": f"{payout.pay_period_start.strftime('%B %Y')}",
                    "pay_period_start": payout.pay_period_start,
                    "pay_period_end": payout.pay_period_end,
                    "payout_date": payout.payout_date,
                    "gross_salary": payout.gross_salary,
                    "net_salary": payout.net_salary,
                    "status": payout.status,
                    "generated_date": getattr(payout, 'created_at', None)
                })
        
        return sorted(payslip_history, key=lambda x: x['pay_period_start'], reverse=True)
    except Exception as e:
        logger.error(f"Error getting payslip history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def email_payslip_service(payout_id: str, hostname: str, recipient_email: Optional[str] = None) -> Dict[str, str]:
    """Email payslip to employee"""
    try:
        # Get payout and employee details
        payout_db = PayoutDatabase(hostname)
        payout = payout_db.get_payout_by_id(payout_id)
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        
        employee = get_user_by_emp_id(payout.employee_id, hostname)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Use provided email or employee's email
        email = recipient_email or employee.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="No email address available")
        
        # Generate PDF
        pdf_buffer = generate_payslip_pdf_service(payout_id, hostname)
        
        # Get organization details for email
        try:
            from app.infrastructure.services.legacy_migration_service import get_organisation_by_hostname_sync as get_organisation_by_hostname
            organization = get_organisation_by_hostname(hostname)
            company_name = organization.name if organization else "Company"
        except:
            company_name = "Company"
        
        # Send email
        _send_payslip_email(
            recipient_email=email,
            employee_name=employee.get('name', 'Employee'),
            company_name=company_name,
            pay_period=f"{payout.pay_period_start.strftime('%B %Y')}",
            pdf_buffer=pdf_buffer,
            filename=f"payslip_{payout.employee_id}_{payout.pay_period_start.strftime('%m_%Y')}.pdf"
        )
        
        logger.info(f"Payslip emailed successfully to {email} for payout {payout_id}")
        return {"message": "Payslip emailed successfully", "email": email}
        
    except Exception as e:
        logger.error(f"Error emailing payslip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error emailing payslip: {str(e)}")


def _send_payslip_email(recipient_email: str, employee_name: str, company_name: str, 
                       pay_period: str, pdf_buffer: BytesIO, filename: str):
    """Send payslip email with PDF attachment"""
    
    # Email configuration (should be moved to environment variables)
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    if not smtp_username or not smtp_password:
        raise HTTPException(status_code=500, detail="Email configuration not found")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = f"Payslip for {pay_period} - {company_name}"
    
    # Email body
    body = f"""
    Dear {employee_name},

    Please find attached your payslip for {pay_period}.

    If you have any questions regarding your payslip, please contact the HR department.

    Best regards,
    {company_name} HR Team
    
    ---
    This is an automated email. Please do not reply to this email.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF
    pdf_attachment = MIMEBase('application', 'octet-stream')
    pdf_attachment.set_payload(pdf_buffer.getvalue())
    encoders.encode_base64(pdf_attachment)
    pdf_attachment.add_header(
        'Content-Disposition',
        f'attachment; filename= {filename}'
    )
    msg.attach(pdf_attachment)
    
    # Send email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(smtp_username, recipient_email, text)
    server.quit()


def generate_monthly_payslips_bulk_service(month: int, year: int, hostname: str, status_filter: Optional[PayoutStatus] = None) -> Dict[str, Any]:
    """Generate payslips for all employees for a given month"""
    try:
        logger.info(f"Starting bulk payslip generation for {month:02d}/{year}")
        
        # Get all payouts for the month
        payout_db = PayoutDatabase(hostname)
        payouts = payout_db.get_monthly_payouts(month, year, status_filter)
        
        # Filter only processed/approved/paid payouts
        eligible_payouts = [p for p in payouts if p.status in [PayoutStatus.PROCESSED, PayoutStatus.APPROVED, PayoutStatus.PAID]]
        
        successful_generations = []
        failed_generations = []
        
        for payout in eligible_payouts:
            try:
                # Generate PDF
                pdf_buffer = generate_payslip_pdf_service(payout.id, hostname)
                
                # Save PDF to file system (optional)
                filename = f"payslip_{payout.employee_id}_{month:02d}_{year}.pdf"
                filepath = _save_payslip_pdf(pdf_buffer, filename, hostname)
                
                successful_generations.append({
                    "employee_id": payout.employee_id,
                    "payout_id": payout.id,
                    "filename": filename,
                    "filepath": filepath
                })
                
            except Exception as e:
                logger.error(f"Failed to generate payslip for {payout.employee_id}: {str(e)}")
                failed_generations.append({
                    "employee_id": payout.employee_id,
                    "payout_id": payout.id,
                    "error": str(e)
                })
        
        result = {
            "month": month,
            "year": year,
            "total_payouts": len(eligible_payouts),
            "successful_generations": len(successful_generations),
            "failed_generations": len(failed_generations),
            "generated_payslips": successful_generations,
            "errors": failed_generations
        }
        
        logger.info(f"Bulk payslip generation completed: {len(successful_generations)} successful, {len(failed_generations)} failed")
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk payslip generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in bulk payslip generation: {str(e)}")


def _save_payslip_pdf(pdf_buffer: BytesIO, filename: str, hostname: str) -> str:
    """Save PDF buffer to file system"""
    try:
        # Create payslips directory if it doesn't exist
        payslips_dir = f"payslips/{hostname}"
        os.makedirs(payslips_dir, exist_ok=True)
        
        # Save file
        filepath = os.path.join(payslips_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving payslip PDF: {str(e)}")
        raise


def bulk_email_payslips_service(month: int, year: int, hostname: str) -> Dict[str, Any]:
    """Email payslips to all employees for a given month"""
    try:
        logger.info(f"Starting bulk payslip email for {month:02d}/{year}")
        
        # Get all processed payouts for the month
        payout_db = PayoutDatabase(hostname)
        payouts = payout_db.get_monthly_payouts(month, year, PayoutStatus.PROCESSED)
        
        successful_emails = []
        failed_emails = []
        
        for payout in payouts:
            try:
                result = email_payslip_service(payout.id, hostname)
                successful_emails.append({
                    "employee_id": payout.employee_id,
                    "payout_id": payout.id,
                    "email": result["email"]
                })
                
            except Exception as e:
                logger.error(f"Failed to email payslip for {payout.employee_id}: {str(e)}")
                failed_emails.append({
                    "employee_id": payout.employee_id,
                    "payout_id": payout.id,
                    "error": str(e)
                })
        
        result = {
            "month": month,
            "year": year,
            "total_payouts": len(payouts),
            "successful_emails": len(successful_emails),
            "failed_emails": len(failed_emails),
            "emailed_payslips": successful_emails,
            "errors": failed_emails
        }
        
        logger.info(f"Bulk payslip email completed: {len(successful_emails)} successful, {len(failed_emails)} failed")
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk payslip email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in bulk payslip email: {str(e)}")


# ================================
# SOLID ARCHITECTURE IMPLEMENTATION
# ================================

class PayrollMigrationService:
    """
    Central migration service that provides SOLID architecture compliance
    while maintaining backward compatibility with legacy services
    """
    
    def __init__(self, hostname: str):
        self.hostname = hostname
        self.payout_command_repo = PayoutCommandRepositoryImpl(hostname)
        self.payout_query_repo = PayoutQueryRepositoryImpl(hostname)
        self.payout_analytics_repo = PayoutAnalyticsRepositoryImpl(hostname)
        self.payslip_command_repo = PayslipCommandRepositoryImpl(hostname)
        self.payslip_query_repo = PayslipQueryRepositoryImpl(hostname)
        self.payslip_storage_repo = PayslipStorageRepositoryImpl(hostname)


class PayoutCommandRepositoryImpl(PayoutCommandRepository):
    """Implementation of payout command repository using legacy services"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
    
    async def create_payout(self, payout: PayoutCreate, hostname: str) -> PayoutInDB:
        """Create a new payout record"""
        try:
            return create_payout_service(payout, hostname)
        except Exception as e:
            logger.error(f"Error creating payout: {str(e)}")
            raise
    
    async def update_payout(self, payout_id: str, update: PayoutUpdate, 
                           hostname: str, updated_by: str) -> PayoutInDB:
        """Update an existing payout record"""
        try:
            return update_payout_service(payout_id, update, hostname)
        except Exception as e:
            logger.error(f"Error updating payout: {str(e)}")
            raise
    
    async def update_payout_status(self, payout_id: str, status: PayoutStatus,
                                  hostname: str, updated_by: str, 
                                  reason: Optional[str] = None) -> bool:
        """Update payout status"""
        try:
            result = update_payout_status_service(payout_id, status, updated_by, hostname)
            return result.get("message") == "Payout status updated successfully"
        except Exception as e:
            logger.error(f"Error updating payout status: {str(e)}")
            raise
    
    async def bulk_create_payouts(self, payouts: List[PayoutCreate], 
                                 hostname: str, created_by: str) -> List[PayoutInDB]:
        """Create multiple payout records in bulk"""
        try:
            # Convert to legacy bulk request format
            from app.domain.entities.payout import BulkPayoutRequest
            
            if not payouts:
                return []
            
            # Extract common pay period from first payout
            first_payout = payouts[0]
            bulk_request = BulkPayoutRequest(
                employee_ids=[p.employee_id for p in payouts],
                pay_period_start=first_payout.pay_period_start,
                pay_period_end=first_payout.pay_period_end,
                payout_date=first_payout.payout_date,
                auto_calculate_tax=True,
                auto_approve=False,
                notes=f"Bulk created by {created_by}"
            )
            
            result = bulk_process_monthly_payouts_service(bulk_request, hostname)
            
            # Get created payouts
            created_payouts = []
            for payout_id in result.payout_ids:
                payout = get_payout_by_id_service(payout_id, hostname)
                if payout:
                    created_payouts.append(payout)
            
            return created_payouts
            
        except Exception as e:
            logger.error(f"Error in bulk payout creation: {str(e)}")
            raise
    
    async def bulk_update_status(self, payout_ids: List[str], status: PayoutStatus,
                                hostname: str, updated_by: str) -> Dict[str, bool]:
        """Update status for multiple payouts"""
        results = {}
        
        for payout_id in payout_ids:
            try:
                success = await self.update_payout_status(payout_id, status, hostname, updated_by)
                results[payout_id] = success
            except Exception as e:
                logger.error(f"Error updating status for payout {payout_id}: {str(e)}")
                results[payout_id] = False
        
        return results
    
    async def delete_payout(self, payout_id: str, hostname: str, 
                           deleted_by: str) -> bool:
        """Soft delete a payout record"""
        # Legacy service doesn't support soft delete, so we'll update status to cancelled
        try:
            return await self.update_payout_status(
                payout_id, PayoutStatus.CANCELLED, hostname, deleted_by
            )
        except Exception as e:
            logger.error(f"Error deleting payout: {str(e)}")
            raise


class PayoutQueryRepositoryImpl(PayoutQueryRepository):
    """Implementation of payout query repository using legacy services"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
    
    async def get_by_id(self, payout_id: str, hostname: str) -> Optional[PayoutInDB]:
        """Get payout by ID"""
        try:
            return get_payout_by_id_service(payout_id, hostname)
        except Exception as e:
            logger.error(f"Error getting payout by ID: {str(e)}")
            return None
    
    async def get_employee_payouts(self, employee_id: str, hostname: str,
                                  year: Optional[int] = None,
                                  month: Optional[int] = None) -> List[PayoutInDB]:
        """Get payouts for a specific employee"""
        try:
            return get_employee_payouts_service(employee_id, hostname, year, month)
        except Exception as e:
            logger.error(f"Error getting employee payouts: {str(e)}")
            return []
    
    async def get_monthly_payouts(self, month: int, year: int, hostname: str,
                                 status: Optional[PayoutStatus] = None) -> List[PayoutInDB]:
        """Get all payouts for a specific month"""
        try:
            return get_monthly_payouts_service(month, year, hostname, status)
        except Exception as e:
            logger.error(f"Error getting monthly payouts: {str(e)}")
            return []
    
    async def search_payouts(self, filters: PayoutSearchFiltersDTO,
                           hostname: str) -> Dict[str, Any]:
        """Search payouts with filters and pagination"""
        try:
            # Convert filters to legacy service calls
            payouts = []
            
            if filters.employee_id:
                payouts = await self.get_employee_payouts(
                    filters.employee_id, hostname, filters.year, filters.month
                )
            elif filters.month and filters.year:
                payouts = await self.get_monthly_payouts(
                    filters.month, filters.year, hostname, filters.status
                )
            else:
                # Get all payouts (this might be expensive)
                payouts = get_monthly_payouts_service(
                    filters.month or datetime.now().month,
                    filters.year or datetime.now().year,
                    hostname,
                    filters.status
                )
            
            # Apply additional filters
            if filters.min_gross_salary:
                payouts = [p for p in payouts if p.gross_salary >= filters.min_gross_salary]
            
            if filters.max_gross_salary:
                payouts = [p for p in payouts if p.gross_salary <= filters.max_gross_salary]
            
            # Apply pagination
            total_count = len(payouts)
            start_idx = (filters.page - 1) * filters.page_size
            end_idx = start_idx + filters.page_size
            paginated_payouts = payouts[start_idx:end_idx]
            
            return {
                "payouts": paginated_payouts,
                "total_count": total_count,
                "page": filters.page,
                "page_size": filters.page_size
            }
            
        except Exception as e:
            logger.error(f"Error searching payouts: {str(e)}")
            return {"payouts": [], "total_count": 0, "page": filters.page, "page_size": filters.page_size}
    
    async def check_duplicate_payout(self, employee_id: str, pay_period_start: date,
                                   pay_period_end: date, hostname: str) -> bool:
        """Check if payout already exists for employee and period"""
        try:
            from app.database.payout_database import PayoutDatabase
            payout_db = PayoutDatabase(hostname)
            return payout_db.check_duplicate_payout(employee_id, pay_period_start, pay_period_end)
        except Exception as e:
            logger.error(f"Error checking duplicate payout: {str(e)}")
            return False
    
    async def get_payout_summary(self, month: int, year: int, 
                                hostname: str) -> Dict[str, Any]:
        """Get payout summary for a month"""
        try:
            summary = get_monthly_payout_summary_service(month, year, hostname)
            return {
                "month": month,
                "year": year,
                "total_employees": summary.total_employees,
                "total_gross_salary": summary.total_gross_salary,
                "total_net_salary": summary.total_net_salary,
                "total_deductions": summary.total_deductions,
                "average_gross_salary": summary.average_gross_salary,
                "average_net_salary": summary.average_net_salary
            }
        except Exception as e:
            logger.error(f"Error getting payout summary: {str(e)}")
            return {}
    
    async def get_employee_payout_history(self, employee_id: str, year: int,
                                        hostname: str) -> Dict[str, Any]:
        """Get comprehensive payout history for employee"""
        try:
            history = get_employee_payout_history_service(employee_id, year, hostname)
            return {
                "employee_id": employee_id,
                "year": year,
                "payouts": history.payouts,
                "yearly_summary": {
                    "total_gross": history.total_gross_salary,
                    "total_net": history.total_net_salary,
                    "total_deductions": history.total_deductions,
                    "months_paid": history.months_paid
                }
            }
        except Exception as e:
            logger.error(f"Error getting payout history: {str(e)}")
            return {}
    
    async def get_payouts_by_status(self, status: PayoutStatus, hostname: str,
                                   limit: Optional[int] = None) -> List[PayoutInDB]:
        """Get payouts by status"""
        try:
            # Get current month payouts with status filter
            current_date = datetime.now()
            payouts = get_monthly_payouts_service(
                current_date.month, current_date.year, hostname, status
            )
            
            if limit:
                payouts = payouts[:limit]
            
            return payouts
        except Exception as e:
            logger.error(f"Error getting payouts by status: {str(e)}")
            return []
    
    async def get_pending_approvals(self, hostname: str, 
                                   approver_id: Optional[str] = None) -> List[PayoutInDB]:
        """Get payouts pending approval"""
        return await self.get_payouts_by_status(PayoutStatus.PENDING, hostname)


class PayoutAnalyticsRepositoryImpl(PayoutAnalyticsRepository):
    """Implementation of payout analytics repository"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
    
    async def get_department_wise_summary(self, month: int, year: int,
                                        hostname: str) -> Dict[str, Dict[str, float]]:
        """Get department-wise payout summary"""
        try:
            # This would require integration with employee service for department data
            # For now, return empty summary
            return {}
        except Exception as e:
            logger.error(f"Error getting department wise summary: {str(e)}")
            return {}
    
    async def get_monthly_trends(self, start_month: int, start_year: int,
                               end_month: int, end_year: int,
                               hostname: str) -> List[Dict[str, Any]]:
        """Get monthly payout trends"""
        try:
            trends = []
            # Simplified implementation - would need more sophisticated logic
            current_date = date(start_year, start_month, 1)
            end_date = date(end_year, end_month, 1)
            
            while current_date <= end_date:
                try:
                    summary = get_monthly_payout_summary_service(
                        current_date.month, current_date.year, hostname
                    )
                    trends.append({
                        "month": current_date.month,
                        "year": current_date.year,
                        "total_gross": summary.total_gross_salary,
                        "total_net": summary.total_net_salary,
                        "employee_count": summary.total_employees
                    })
                except:
                    pass  # Skip months with no data
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            return trends
        except Exception as e:
            logger.error(f"Error getting monthly trends: {str(e)}")
            return []
    
    async def get_salary_distribution(self, month: int, year: int,
                                    hostname: str) -> Dict[str, Any]:
        """Get salary distribution analytics"""
        try:
            payouts = get_monthly_payouts_service(month, year, hostname)
            
            if not payouts:
                return {}
            
            gross_salaries = [p.gross_salary for p in payouts]
            gross_salaries.sort()
            
            return {
                "min_salary": min(gross_salaries),
                "max_salary": max(gross_salaries),
                "median_salary": gross_salaries[len(gross_salaries) // 2],
                "average_salary": sum(gross_salaries) / len(gross_salaries),
                "total_employees": len(payouts)
            }
        except Exception as e:
            logger.error(f"Error getting salary distribution: {str(e)}")
            return {}
    
    async def get_top_earners(self, month: int, year: int, hostname: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Get top earners for a month"""
        try:
            payouts = get_monthly_payouts_service(month, year, hostname)
            
            # Sort by gross salary descending
            sorted_payouts = sorted(payouts, key=lambda p: p.gross_salary, reverse=True)
            top_payouts = sorted_payouts[:limit]
            
            return [
                {
                    "employee_id": p.employee_id,
                    "gross_salary": p.gross_salary,
                    "net_salary": p.net_salary,
                    "rank": idx + 1
                }
                for idx, p in enumerate(top_payouts)
            ]
        except Exception as e:
            logger.error(f"Error getting top earners: {str(e)}")
            return []
    
    async def get_deduction_analysis(self, month: int, year: int,
                                   hostname: str) -> Dict[str, float]:
        """Get deduction analysis"""
        try:
            payouts = get_monthly_payouts_service(month, year, hostname)
            
            if not payouts:
                return {}
            
            total_epf = sum(p.epf_employee for p in payouts)
            total_esi = sum(p.esi_employee for p in payouts)
            total_pt = sum(p.professional_tax for p in payouts)
            total_tds = sum(p.tds for p in payouts)
            total_other = sum(p.other_deductions for p in payouts)
            
            return {
                "total_epf": total_epf,
                "total_esi": total_esi,
                "total_professional_tax": total_pt,
                "total_tds": total_tds,
                "total_other_deductions": total_other,
                "total_deductions": total_epf + total_esi + total_pt + total_tds + total_other
            }
        except Exception as e:
            logger.error(f"Error getting deduction analysis: {str(e)}")
            return {}
    
    async def get_compliance_metrics(self, month: int, year: int,
                                   hostname: str) -> Dict[str, Any]:
        """Get compliance metrics"""
        try:
            payouts = get_monthly_payouts_service(month, year, hostname)
            
            if not payouts:
                return {}
            
            processed_count = len([p for p in payouts if p.status == PayoutStatus.PROCESSED])
            pending_count = len([p for p in payouts if p.status == PayoutStatus.PENDING])
            
            return {
                "total_payouts": len(payouts),
                "processed_payouts": processed_count,
                "pending_payouts": pending_count,
                "processing_rate": (processed_count / len(payouts)) * 100 if payouts else 0,
                "compliance_score": 95.0  # Placeholder - would calculate based on actual compliance rules
            }
        except Exception as e:
            logger.error(f"Error getting compliance metrics: {str(e)}")
            return {}


class PayslipCommandRepositoryImpl(PayslipCommandRepository):
    """Implementation of payslip command repository"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
    
    async def save_generated_payslip(self, payslip_metadata: PayslipMetadata,
                                   file_content: BytesIO, hostname: str) -> str:
        """Save generated payslip file and metadata"""
        try:
            # Generate payslip using legacy service
            pdf_buffer = generate_payslip_pdf_service(payslip_metadata.payout_id, hostname)
            
            # In a real implementation, we would save the metadata to database
            # For now, return the payslip_id
            return payslip_metadata.payslip_id
        except Exception as e:
            logger.error(f"Error saving generated payslip: {str(e)}")
            raise
    
    async def update_payslip_metadata(self, payslip_id: str, 
                                    update_data: Dict[str, Any],
                                    hostname: str) -> bool:
        """Update payslip metadata"""
        try:
            # Legacy service doesn't support metadata updates directly
            # This would need to be implemented with a proper database
            return True
        except Exception as e:
            logger.error(f"Error updating payslip metadata: {str(e)}")
            return False
    
    async def update_email_status(self, payslip_id: str, email_status: str,
                                email_sent_at: datetime, recipient_email: str,
                                hostname: str) -> bool:
        """Update email status for payslip"""
        try:
            # This would be implemented with proper database storage
            return True
        except Exception as e:
            logger.error(f"Error updating email status: {str(e)}")
            return False
    
    async def increment_download_count(self, payslip_id: str,
                                     hostname: str) -> bool:
        """Increment download count for payslip"""
        try:
            # This would be implemented with proper database storage
            return True
        except Exception as e:
            logger.error(f"Error incrementing download count: {str(e)}")
            return False
    
    async def bulk_save_payslips(self, payslips_data: List[Dict[str, Any]],
                               hostname: str) -> List[str]:
        """Save multiple payslips in bulk"""
        try:
            payslip_ids = []
            
            for payslip_data in payslips_data:
                payout_id = payslip_data.get("payout_id")
                if payout_id:
                    # Generate PDF
                    pdf_buffer = generate_payslip_pdf_service(payout_id, hostname)
                    payslip_ids.append(f"payslip_{payout_id}")
            
            return payslip_ids
        except Exception as e:
            logger.error(f"Error in bulk save payslips: {str(e)}")
            return []
    
    async def delete_payslip(self, payslip_id: str, hostname: str,
                           deleted_by: str) -> bool:
        """Delete payslip file and metadata"""
        try:
            # This would be implemented with proper file and database management
            return True
        except Exception as e:
            logger.error(f"Error deleting payslip: {str(e)}")
            return False


class PayslipQueryRepositoryImpl(PayslipQueryRepository):
    """Implementation of payslip query repository"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
    
    async def get_by_id(self, payslip_id: str, hostname: str) -> Optional[PayslipMetadata]:
        """Get payslip metadata by ID"""
        try:
            # Extract payout_id from payslip_id (assuming format payslip_{payout_id})
            if payslip_id.startswith("payslip_"):
                payout_id = payslip_id.replace("payslip_", "")
                payout = get_payout_by_id_service(payout_id, hostname)
                
                if payout:
                    return PayslipMetadata(
                        payslip_id=payslip_id,
                        payout_id=payout_id,
                        employee_id=payout.employee_id,
                        format="PDF",
                        generated_at=datetime.now()
                    )
            return None
        except Exception as e:
            logger.error(f"Error getting payslip by ID: {str(e)}")
            return None
    
    async def get_by_payout_id(self, payout_id: str, hostname: str) -> Optional[PayslipMetadata]:
        """Get payslip metadata by payout ID"""
        payslip_id = f"payslip_{payout_id}"
        return await self.get_by_id(payslip_id, hostname)
    
    async def get_employee_payslips(self, employee_id: str, year: int,
                                  hostname: str) -> List[PayslipMetadata]:
        """Get all payslips for an employee in a year"""
        try:
            payslip_history = get_payslip_history_service(employee_id, year, hostname)
            
            payslip_metadata_list = []
            for payslip in payslip_history:
                metadata = PayslipMetadata(
                    payslip_id=f"payslip_{payslip['payout_id']}",
                    payout_id=payslip["payout_id"],
                    employee_id=employee_id,
                    format="PDF",
                    generated_at=payslip.get("generated_date")
                )
                payslip_metadata_list.append(metadata)
            
            return payslip_metadata_list
        except Exception as e:
            logger.error(f"Error getting employee payslips: {str(e)}")
            return []
    
    async def get_monthly_payslips(self, month: int, year: int,
                                 hostname: str, 
                                 format_filter: Optional[str] = None) -> List[PayslipMetadata]:
        """Get all payslips for a specific month"""
        try:
            payouts = get_monthly_payouts_service(month, year, hostname)
            
            payslip_metadata_list = []
            for payout in payouts:
                if payout.status in [PayoutStatus.PROCESSED, PayoutStatus.APPROVED, PayoutStatus.PAID]:
                    metadata = PayslipMetadata(
                        payslip_id=f"payslip_{payout.id}",
                        payout_id=payout.id,
                        employee_id=payout.employee_id,
                        format="PDF",
                        generated_at=getattr(payout, 'created_at', None)
                    )
                    payslip_metadata_list.append(metadata)
            
            return payslip_metadata_list
        except Exception as e:
            logger.error(f"Error getting monthly payslips: {str(e)}")
            return []
    
    async def search_payslips(self, filters: Dict[str, Any],
                            hostname: str) -> Dict[str, Any]:
        """Search payslips with filters and pagination"""
        try:
            # This would be implemented with proper search functionality
            return {"payslips": [], "total_count": 0, "page": 1, "page_size": 20}
        except Exception as e:
            logger.error(f"Error searching payslips: {str(e)}")
            return {"payslips": [], "total_count": 0, "page": 1, "page_size": 20}
    
    async def get_payslip_file(self, payslip_id: str, hostname: str) -> Optional[BytesIO]:
        """Get payslip file content"""
        try:
            # Extract payout_id from payslip_id
            if payslip_id.startswith("payslip_"):
                payout_id = payslip_id.replace("payslip_", "")
                return generate_payslip_pdf_service(payout_id, hostname)
            return None
        except Exception as e:
            logger.error(f"Error getting payslip file: {str(e)}")
            return None
    
    async def check_payslip_exists(self, payout_id: str, format: str,
                                 hostname: str) -> bool:
        """Check if payslip already exists for payout and format"""
        try:
            payout = get_payout_by_id_service(payout_id, hostname)
            return payout is not None and payout.status in [
                PayoutStatus.PROCESSED, PayoutStatus.APPROVED, PayoutStatus.PAID
            ]
        except Exception as e:
            logger.error(f"Error checking payslip exists: {str(e)}")
            return False
    
    async def get_payslip_download_stats(self, payslip_id: str,
                                       hostname: str) -> Dict[str, Any]:
        """Get download statistics for payslip"""
        try:
            # This would be implemented with proper analytics
            return {"download_count": 0, "last_downloaded": None}
        except Exception as e:
            logger.error(f"Error getting download stats: {str(e)}")
            return {}
    
    async def get_bulk_generation_status(self, batch_id: str,
                                       hostname: str) -> Dict[str, Any]:
        """Get status of bulk payslip generation"""
        try:
            # This would be implemented with proper batch tracking
            return {"status": "completed", "total": 0, "completed": 0, "failed": 0}
        except Exception as e:
            logger.error(f"Error getting bulk generation status: {str(e)}")
            return {}


class PayslipStorageRepositoryImpl(PayslipStorageRepository):
    """Implementation of payslip storage repository"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
    
    async def store_file(self, file_content: BytesIO, file_path: str,
                       content_type: str) -> bool:
        """Store payslip file"""
        try:
            # This would be implemented with proper file storage
            return True
        except Exception as e:
            logger.error(f"Error storing file: {str(e)}")
            return False
    
    async def retrieve_file(self, file_path: str) -> Optional[BytesIO]:
        """Retrieve payslip file"""
        try:
            # This would be implemented with proper file retrieval
            return None
        except Exception as e:
            logger.error(f"Error retrieving file: {str(e)}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete payslip file"""
        try:
            # This would be implemented with proper file deletion
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            # This would be implemented with proper file metadata
            return None
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None
    
    async def generate_download_url(self, file_path: str,
                                  expiry_minutes: int = 60) -> Optional[str]:
        """Generate temporary download URL"""
        try:
            # This would be implemented with proper URL generation
            return None
        except Exception as e:
            logger.error(f"Error generating download URL: {str(e)}")
            return None
    
    async def cleanup_old_files(self, older_than_days: int,
                              hostname: str) -> int:
        """Cleanup old payslip files"""
        try:
            # This would be implemented with proper cleanup logic
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")
            return 0 