"""
Monthly Payout Record Entity

This module contains the MonthlyPayoutRecord entity that represents
a monthly payout computation with LWP integration.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum

from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.taxation.monthly_payroll import MonthlyPayroll
from app.domain.value_objects.employee_id import EmployeeId


class MonthlyPayoutStatus(str, Enum):
    """Status of monthly payout computation"""
    DRAFT = "draft"
    CALCULATED = "calculated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSED = "processed"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MonthlyPayoutRecord(BaseEntity):
    """
    Monthly Payout Record Entity
    
    Represents a complete monthly payout computation for an employee
    with LWP integration and status management.
    """
    
    def __init__(
        self,
        employee_id: EmployeeId,
        month: int,
        year: int,
        organisation_id: str,
        monthly_payroll: MonthlyPayroll,
        status: MonthlyPayoutStatus = MonthlyPayoutStatus.DRAFT,
        gross_salary: Optional[Decimal] = None,
        net_salary: Optional[Decimal] = None,
        total_deductions: Optional[Decimal] = None,
        lwp_days: Optional[int] = None,
        lwp_factor: Optional[Decimal] = None,
        lwp_deduction: Optional[Decimal] = None,
        epf_deduction: Optional[Decimal] = None,
        esi_deduction: Optional[Decimal] = None,
        professional_tax: Optional[Decimal] = None,
        tds_deduction: Optional[Decimal] = None,
        other_deductions: Optional[Decimal] = None,
        calculation_date: Optional[datetime] = None,
        approved_by: Optional[str] = None,
        approved_date: Optional[datetime] = None,
        processed_by: Optional[str] = None,
        processed_date: Optional[datetime] = None,
        payment_reference: Optional[str] = None,
        payment_date: Optional[datetime] = None,
        remarks: Optional[str] = None,
        payslip_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.employee_id = employee_id
        self.month = month
        self.year = year
        self.organisation_id = organisation_id
        self.monthly_payroll = monthly_payroll
        self.status = status
        
        # Salary components
        self.gross_salary = gross_salary or Decimal('0')
        self.net_salary = net_salary or Decimal('0')
        self.total_deductions = total_deductions or Decimal('0')
        
        # LWP details
        self.lwp_days = lwp_days or 0
        self.lwp_factor = lwp_factor or Decimal('0')
        self.lwp_deduction = lwp_deduction or Decimal('0')
        
        # Statutory deductions
        self.epf_deduction = epf_deduction or Decimal('0')
        self.esi_deduction = esi_deduction or Decimal('0')
        self.professional_tax = professional_tax or Decimal('0')
        self.tds_deduction = tds_deduction or Decimal('0')
        self.other_deductions = other_deductions or Decimal('0')
        
        # Workflow fields
        self.calculation_date = calculation_date or datetime.now()
        self.approved_by = approved_by
        self.approved_date = approved_date
        self.processed_by = processed_by
        self.processed_date = processed_date
        self.payment_reference = payment_reference
        self.payment_date = payment_date
        self.remarks = remarks
        self.payslip_data = payslip_data or {}
    
    def calculate_payout(self) -> None:
        """Calculate the monthly payout based on monthly payroll and LWP"""
        if not self.monthly_payroll:
            raise ValueError("Monthly payroll data is required for calculation")
        
        # Get base salary components from monthly payroll
        base_gross = self.monthly_payroll.gross_salary or Decimal('0')
        
        # Apply LWP factor if available
        if hasattr(self.monthly_payroll, 'lwp_details') and self.monthly_payroll.lwp_details:
            lwp_details = self.monthly_payroll.lwp_details
            self.lwp_days = lwp_details.lwp_days
            self.lwp_factor = lwp_details.lwp_factor
            
            # Calculate LWP deduction
            self.lwp_deduction = base_gross * (Decimal('1') - self.lwp_factor)
            
            # Adjust gross salary for LWP
            self.gross_salary = base_gross * self.lwp_factor
        else:
            self.gross_salary = base_gross
            self.lwp_days = 0
            self.lwp_factor = Decimal('1')
            self.lwp_deduction = Decimal('0')
        
        # Calculate statutory deductions
        self._calculate_statutory_deductions()
        
        # Calculate total deductions
        self.total_deductions = (
            self.epf_deduction + 
            self.esi_deduction + 
            self.professional_tax + 
            self.tds_deduction + 
            self.other_deductions
        )
        
        # Calculate net salary
        self.net_salary = self.gross_salary - self.total_deductions
        
        # Update status and calculation date
        self.status = MonthlyPayoutStatus.CALCULATED
        self.calculation_date = datetime.now()
    
    def _calculate_statutory_deductions(self) -> None:
        """Calculate statutory deductions (EPF, ESI, Professional Tax)"""
        # EPF calculation (12% of basic salary, capped at ₹1,800)
        if hasattr(self.monthly_payroll, 'basic_salary') and self.monthly_payroll.basic_salary:
            basic_salary = self.monthly_payroll.basic_salary * self.lwp_factor
            epf_amount = basic_salary * Decimal('0.12')
            self.epf_deduction = min(epf_amount, Decimal('1800'))
        
        # ESI calculation (0.75% of gross salary if gross <= ₹21,000)
        if self.gross_salary <= Decimal('21000'):
            self.esi_deduction = self.gross_salary * Decimal('0.0075')
        
        # Professional Tax (state-specific, using Karnataka as default)
        if self.gross_salary > Decimal('15000'):
            self.professional_tax = Decimal('200')
        elif self.gross_salary > Decimal('10000'):
            self.professional_tax = Decimal('150')
        else:
            self.professional_tax = Decimal('0')
    
    def approve(self, approved_by: str, remarks: Optional[str] = None) -> None:
        """Approve the payout calculation"""
        if self.status != MonthlyPayoutStatus.CALCULATED:
            raise ValueError("Only calculated payouts can be approved")
        
        self.status = MonthlyPayoutStatus.APPROVED
        self.approved_by = approved_by
        self.approved_date = datetime.now()
        if remarks:
            self.remarks = remarks
    
    def process(self, processed_by: str, payment_reference: Optional[str] = None) -> None:
        """Process the approved payout"""
        if self.status != MonthlyPayoutStatus.APPROVED:
            raise ValueError("Only approved payouts can be processed")
        
        self.status = MonthlyPayoutStatus.PROCESSED
        self.processed_by = processed_by
        self.processed_date = datetime.now()
        if payment_reference:
            self.payment_reference = payment_reference
    
    def mark_as_paid(self, payment_date: Optional[datetime] = None) -> None:
        """Mark the payout as paid"""
        if self.status != MonthlyPayoutStatus.PROCESSED:
            raise ValueError("Only processed payouts can be marked as paid")
        
        self.status = MonthlyPayoutStatus.PAID
        self.payment_date = payment_date or datetime.now()
    
    def cancel(self, remarks: Optional[str] = None) -> None:
        """Cancel the payout"""
        if self.status in [MonthlyPayoutStatus.PAID, MonthlyPayoutStatus.PROCESSED]:
            raise ValueError("Cannot cancel paid or processed payouts")
        
        self.status = MonthlyPayoutStatus.CANCELLED
        if remarks:
            self.remarks = remarks
    
    def generate_payslip_data(self) -> Dict[str, Any]:
        """Generate payslip data for the payout"""
        payslip_data = {
            "employee_id": str(self.employee_id),
            "month": self.month,
            "year": self.year,
            "organisation_id": self.organisation_id,
            "calculation_date": self.calculation_date.isoformat() if self.calculation_date else None,
            
            # Salary components
            "gross_salary": float(self.gross_salary),
            "net_salary": float(self.net_salary),
            "total_deductions": float(self.total_deductions),
            
            # LWP details
            "lwp_days": self.lwp_days,
            "lwp_factor": float(self.lwp_factor),
            "lwp_deduction": float(self.lwp_deduction),
            
            # Deductions breakdown
            "deductions": {
                "epf": float(self.epf_deduction),
                "esi": float(self.esi_deduction),
                "professional_tax": float(self.professional_tax),
                "tds": float(self.tds_deduction),
                "other": float(self.other_deductions)
            },
            
            # Status information
            "status": self.status.value,
            "approved_by": self.approved_by,
            "approved_date": self.approved_date.isoformat() if self.approved_date else None,
            "processed_by": self.processed_by,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "payment_reference": self.payment_reference,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "remarks": self.remarks
        }
        
        # Add monthly payroll data if available
        if self.monthly_payroll:
            payslip_data["monthly_payroll"] = self.monthly_payroll.to_dict()
        
        self.payslip_data = payslip_data
        return payslip_data
    
    def get_lwp_impact_analysis(self) -> Dict[str, Any]:
        """Get LWP impact analysis"""
        if not self.monthly_payroll:
            return {}
        
        base_gross = self.monthly_payroll.gross_salary or Decimal('0')
        
        return {
            "lwp_days": self.lwp_days,
            "total_working_days": 30,  # Assuming 30 days per month
            "lwp_percentage": float(self.lwp_days / 30 * 100) if self.lwp_days else 0,
            "base_gross_salary": float(base_gross),
            "lwp_factor": float(self.lwp_factor),
            "lwp_deduction": float(self.lwp_deduction),
            "adjusted_gross_salary": float(self.gross_salary),
            "salary_loss_percentage": float((1 - self.lwp_factor) * 100) if self.lwp_factor else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for storage"""
        return {
            **super().to_dict(),
            "employee_id": str(self.employee_id),
            "month": self.month,
            "year": self.year,
            "organisation_id": self.organisation_id,
            "monthly_payroll": self.monthly_payroll.to_dict() if self.monthly_payroll else None,
            "status": self.status.value,
            
            # Salary components
            "gross_salary": float(self.gross_salary),
            "net_salary": float(self.net_salary),
            "total_deductions": float(self.total_deductions),
            
            # LWP details
            "lwp_days": self.lwp_days,
            "lwp_factor": float(self.lwp_factor),
            "lwp_deduction": float(self.lwp_deduction),
            
            # Statutory deductions
            "epf_deduction": float(self.epf_deduction),
            "esi_deduction": float(self.esi_deduction),
            "professional_tax": float(self.professional_tax),
            "tds_deduction": float(self.tds_deduction),
            "other_deductions": float(self.other_deductions),
            
            # Workflow fields
            "calculation_date": self.calculation_date.isoformat() if self.calculation_date else None,
            "approved_by": self.approved_by,
            "approved_date": self.approved_date.isoformat() if self.approved_date else None,
            "processed_by": self.processed_by,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "payment_reference": self.payment_reference,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "remarks": self.remarks,
            "payslip_data": self.payslip_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonthlyPayoutRecord':
        """Create entity from dictionary"""
        # Parse dates
        calculation_date = None
        if data.get("calculation_date"):
            calculation_date = datetime.fromisoformat(data["calculation_date"])
        
        approved_date = None
        if data.get("approved_date"):
            approved_date = datetime.fromisoformat(data["approved_date"])
        
        processed_date = None
        if data.get("processed_date"):
            processed_date = datetime.fromisoformat(data["processed_date"])
        
        payment_date = None
        if data.get("payment_date"):
            payment_date = datetime.fromisoformat(data["payment_date"])
        
        # Parse monthly payroll
        monthly_payroll = None
        if data.get("monthly_payroll"):
            monthly_payroll = MonthlyPayroll.from_dict(data["monthly_payroll"])
        
        return cls(
            employee_id=EmployeeId(data["employee_id"]),
            month=data["month"],
            year=data["year"],
            organisation_id=data["organisation_id"],
            monthly_payroll=monthly_payroll,
            status=MonthlyPayoutStatus(data.get("status", "draft")),
            
            # Salary components
            gross_salary=Decimal(str(data.get("gross_salary", 0))),
            net_salary=Decimal(str(data.get("net_salary", 0))),
            total_deductions=Decimal(str(data.get("total_deductions", 0))),
            
            # LWP details
            lwp_days=data.get("lwp_days", 0),
            lwp_factor=Decimal(str(data.get("lwp_factor", 1))),
            lwp_deduction=Decimal(str(data.get("lwp_deduction", 0))),
            
            # Statutory deductions
            epf_deduction=Decimal(str(data.get("epf_deduction", 0))),
            esi_deduction=Decimal(str(data.get("esi_deduction", 0))),
            professional_tax=Decimal(str(data.get("professional_tax", 0))),
            tds_deduction=Decimal(str(data.get("tds_deduction", 0))),
            other_deductions=Decimal(str(data.get("other_deductions", 0))),
            
            # Workflow fields
            calculation_date=calculation_date,
            approved_by=data.get("approved_by"),
            approved_date=approved_date,
            processed_by=data.get("processed_by"),
            processed_date=processed_date,
            payment_reference=data.get("payment_reference"),
            payment_date=payment_date,
            remarks=data.get("remarks"),
            payslip_data=data.get("payslip_data", {}),
            
            # Base entity fields
            id=data.get("id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            version=data.get("version", 1)
        )
    
    def __str__(self) -> str:
        return f"MonthlyPayoutRecord(employee_id={self.employee_id}, month={self.month}, year={self.year}, status={self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__() 