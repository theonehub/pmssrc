"""
Salary Management Domain Models
Handles salary changes, projections, and history tracking
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid

from app.domain.entities.taxation_models.salary_components import SalaryComponents


class SalaryChangeReason(Enum):
    PROMOTION = "promotion"
    ANNUAL_HIKE = "annual_hike"
    PERFORMANCE_HIKE = "performance_hike"
    MARKET_ADJUSTMENT = "market_adjustment"
    ROLE_CHANGE = "role_change"
    TRANSFER = "transfer"
    DEMOTION = "demotion"
    SALARY_REDUCTION = "salary_reduction"
    CORRECTION = "correction"
    OTHER = "other"


class SalaryChangeStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


@dataclass
class SalaryChange:
    """
    Represents a salary change event with complete audit trail
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    effective_date: date = field(default_factory=date.today)
    previous_salary: Optional[SalaryComponents] = None
    new_salary: Optional[SalaryComponents] = None
    change_reason: SalaryChangeReason = SalaryChangeReason.OTHER
    change_description: str = ""
    is_retroactive: bool = False
    retroactive_from_date: Optional[date] = None
    percentage_change: float = 0.0
    absolute_change: float = 0.0
    approved_by: str = ""
    requested_by: str = ""
    status: SalaryChangeStatus = SalaryChangeStatus.PENDING
    approval_date: Optional[datetime] = None
    implementation_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_change_metrics(self) -> Dict[str, float]:
        """Calculate change metrics between old and new salary"""
        if not self.previous_salary or not self.new_salary:
            return {}
        
        old_gross = self.previous_salary.total_taxable_income_per_slab("old")
        new_gross = self.new_salary.total_taxable_income_per_slab("old")
        
        absolute_change = new_gross - old_gross
        percentage_change = (absolute_change / old_gross * 100) if old_gross > 0 else 0
        
        return {
            "old_gross_annual": old_gross,
            "new_gross_annual": new_gross,
            "absolute_change": absolute_change,
            "percentage_change": percentage_change,
            "old_monthly": old_gross / 12,
            "new_monthly": new_gross / 12,
            "monthly_change": absolute_change / 12
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "effective_date": self.effective_date.isoformat(),
            "previous_salary": self.previous_salary.to_dict() if self.previous_salary else None,
            "new_salary": self.new_salary.to_dict() if self.new_salary else None,
            "change_reason": self.change_reason.value,
            "change_description": self.change_description,
            "is_retroactive": self.is_retroactive,
            "retroactive_from_date": self.retroactive_from_date.isoformat() if self.retroactive_from_date else None,
            "percentage_change": self.percentage_change,
            "absolute_change": self.absolute_change,
            "approved_by": self.approved_by,
            "requested_by": self.requested_by,
            "status": self.status.value,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "implementation_date": self.implementation_date.isoformat() if self.implementation_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SalaryChange':
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            employee_id=data.get("employee_id", ""),
            effective_date=date.fromisoformat(data.get("effective_date", date.today().isoformat())),
            previous_salary=SalaryComponents.from_dict(data["previous_salary"]) if data.get("previous_salary") else None,
            new_salary=SalaryComponents.from_dict(data["new_salary"]) if data.get("new_salary") else None,
            change_reason=SalaryChangeReason(data.get("change_reason", "other")),
            change_description=data.get("change_description", ""),
            is_retroactive=data.get("is_retroactive", False),
            retroactive_from_date=date.fromisoformat(data["retroactive_from_date"]) if data.get("retroactive_from_date") else None,
            percentage_change=data.get("percentage_change", 0.0),
            absolute_change=data.get("absolute_change", 0.0),
            approved_by=data.get("approved_by", ""),
            requested_by=data.get("requested_by", ""),
            status=SalaryChangeStatus(data.get("status", "pending")),
            approval_date=datetime.fromisoformat(data["approval_date"]) if data.get("approval_date") else None,
            implementation_date=datetime.fromisoformat(data["implementation_date"]) if data.get("implementation_date") else None,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


@dataclass
class MonthlyProjection:
    """
    Monthly salary projection considering all changes
    """
    month: int
    year: int
    projected_gross: float
    projected_basic: float
    projected_allowances: float
    working_days: int = 30
    effective_working_days: int = 30
    lwp_days: int = 0
    salary_change_applied: Optional[str] = None  # SalaryChange ID if applicable
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "month": self.month,
            "year": self.year,
            "projected_gross": self.projected_gross,
            "projected_basic": self.projected_basic,
            "projected_allowances": self.projected_allowances,
            "working_days": self.working_days,
            "effective_working_days": self.effective_working_days,
            "lwp_days": self.lwp_days,
            "salary_change_applied": self.salary_change_applied
        }


@dataclass
class SalaryProjection:
    """
    Annual salary projection considering all changes and LWP
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    tax_year: str = ""
    base_annual_gross: float = 0.0
    projected_annual_gross: float = 0.0
    salary_changes: List[SalaryChange] = field(default_factory=list)
    monthly_projections: List[MonthlyProjection] = field(default_factory=list)
    calculation_date: datetime = field(default_factory=datetime.now)
    remaining_months: int = 0
    salary_changes_count: int = 0
    last_change_date: Optional[date] = None
    lwp_adjustment_applied: bool = False
    total_lwp_days: int = 0
    lwp_adjustment_ratio: float = 1.0
    
    def get_monthly_projection(self, month: int, year: int) -> Optional[MonthlyProjection]:
        """Get projection for specific month"""
        for projection in self.monthly_projections:
            if projection.month == month and projection.year == year:
                return projection
        return None
    
    def get_projected_salary_for_month(self, month: int, year: int) -> float:
        """Get projected salary for specific month"""
        projection = self.get_monthly_projection(month, year)
        return projection.projected_gross if projection else 0.0
    
    def calculate_remaining_annual_gross(self, from_month: int) -> float:
        """Calculate remaining annual gross from given month"""
        remaining_gross = 0.0
        current_year = int(self.tax_year.split('-')[0])
        
        for month in range(from_month, 13):  # April to March
            actual_year = current_year if month >= 4 else current_year + 1
            projection = self.get_monthly_projection(month, actual_year)
            if projection:
                remaining_gross += projection.projected_gross
        
        return remaining_gross
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "tax_year": self.tax_year,
            "base_annual_gross": self.base_annual_gross,
            "projected_annual_gross": self.projected_annual_gross,
            "salary_changes": [change.to_dict() for change in self.salary_changes],
            "monthly_projections": [proj.to_dict() for proj in self.monthly_projections],
            "calculation_date": self.calculation_date.isoformat(),
            "remaining_months": self.remaining_months,
            "salary_changes_count": self.salary_changes_count,
            "last_change_date": self.last_change_date.isoformat() if self.last_change_date else None,
            "lwp_adjustment_applied": self.lwp_adjustment_applied,
            "total_lwp_days": self.total_lwp_days,
            "lwp_adjustment_ratio": self.lwp_adjustment_ratio
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SalaryProjection':
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            employee_id=data.get("employee_id", ""),
            tax_year=data.get("tax_year", ""),
            base_annual_gross=data.get("base_annual_gross", 0.0),
            projected_annual_gross=data.get("projected_annual_gross", 0.0),
            salary_changes=[SalaryChange.from_dict(change) for change in data.get("salary_changes", [])],
            monthly_projections=[MonthlyProjection(**proj) for proj in data.get("monthly_projections", [])],
            calculation_date=datetime.fromisoformat(data.get("calculation_date", datetime.now().isoformat())),
            remaining_months=data.get("remaining_months", 0),
            salary_changes_count=data.get("salary_changes_count", 0),
            last_change_date=date.fromisoformat(data["last_change_date"]) if data.get("last_change_date") else None,
            lwp_adjustment_applied=data.get("lwp_adjustment_applied", False),
            total_lwp_days=data.get("total_lwp_days", 0),
            lwp_adjustment_ratio=data.get("lwp_adjustment_ratio", 1.0)
        )


@dataclass
class ArrearsCalculation:
    """
    Calculation for arrears/backdated payments with Section 89 relief
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    arrears_amount: float = 0.0
    arrears_period_start: date = field(default_factory=date.today)
    arrears_period_end: date = field(default_factory=date.today)
    years_covered: int = 1
    average_arrears_per_year: float = 0.0
    gross_tax_on_arrears: float = 0.0
    section_89_relief: float = 0.0
    net_tax_on_arrears: float = 0.0
    current_year_impact: float = 0.0
    calculation_method: str = "averaging"  # "averaging" or "lump_sum"
    calculated_at: datetime = field(default_factory=datetime.now)
    
    def calculate_section_89_relief(self, employee_tax_history: List[Dict]) -> float:
        """
        Calculate Section 89 relief for arrears payment
        Relief = Tax on (Salary + Arrears) - Tax on Salary - Tax on Arrears as current year income
        """
        # This would involve complex calculations based on historical tax rates
        # For now, returning a placeholder calculation
        return min(self.gross_tax_on_arrears * 0.3, self.arrears_amount * 0.1)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "arrears_amount": self.arrears_amount,
            "arrears_period_start": self.arrears_period_start.isoformat(),
            "arrears_period_end": self.arrears_period_end.isoformat(),
            "years_covered": self.years_covered,
            "average_arrears_per_year": self.average_arrears_per_year,
            "gross_tax_on_arrears": self.gross_tax_on_arrears,
            "section_89_relief": self.section_89_relief,
            "net_tax_on_arrears": self.net_tax_on_arrears,
            "current_year_impact": self.current_year_impact,
            "calculation_method": self.calculation_method,
            "calculated_at": self.calculated_at.isoformat()
        }


@dataclass
class CatchUpTaxResult:
    """
    Result of catch-up tax calculation after salary changes
    """
    employee_id: str = ""
    effective_from_month: int = 1
    additional_annual_tax: float = 0.0
    additional_monthly_tds: float = 0.0
    remaining_months: int = 0
    previous_monthly_tds: float = 0.0
    new_monthly_tds: float = 0.0
    total_catch_up_amount: float = 0.0
    calculation_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "effective_from_month": self.effective_from_month,
            "additional_annual_tax": self.additional_annual_tax,
            "additional_monthly_tds": self.additional_monthly_tds,
            "remaining_months": self.remaining_months,
            "previous_monthly_tds": self.previous_monthly_tds,
            "new_monthly_tds": self.new_monthly_tds,
            "total_catch_up_amount": self.total_catch_up_amount,
            "calculation_date": self.calculation_date.isoformat()
        }


@dataclass
class SalaryChangeResult:
    """
    Complete result of salary change processing
    """
    change: SalaryChange
    projection: SalaryProjection
    tax_impact: Dict[str, float]
    catch_up_tax: CatchUpTaxResult
    arrears_calculation: Optional[ArrearsCalculation] = None
    notifications_sent: List[str] = field(default_factory=list)
    processing_status: str = "completed"
    processing_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "change": self.change.to_dict(),
            "projection": self.projection.to_dict(),
            "tax_impact": self.tax_impact,
            "catch_up_tax": self.catch_up_tax.to_dict(),
            "arrears_calculation": self.arrears_calculation.to_dict() if self.arrears_calculation else None,
            "notifications_sent": self.notifications_sent,
            "processing_status": self.processing_status,
            "processing_errors": self.processing_errors
        }


@dataclass
class PreviousEmployment:
    """
    Previous employment details for new joiners
    """
    employer_name: str = ""
    employment_start_date: date = field(default_factory=date.today)
    employment_end_date: date = field(default_factory=date.today)
    annual_salary: float = 0.0
    tds_deducted: float = 0.0
    form_16_available: bool = False
    pan_number: str = ""
    employer_tan: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employer_name": self.employer_name,
            "employment_start_date": self.employment_start_date.isoformat(),
            "employment_end_date": self.employment_end_date.isoformat(),
            "annual_salary": self.annual_salary,
            "tds_deducted": self.tds_deducted,
            "form_16_available": self.form_16_available,
            "pan_number": self.pan_number,
            "employer_tan": self.employer_tan
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreviousEmployment':
        return cls(
            employer_name=data.get("employer_name", ""),
            employment_start_date=date.fromisoformat(data.get("employment_start_date", date.today().isoformat())),
            employment_end_date=date.fromisoformat(data.get("employment_end_date", date.today().isoformat())),
            annual_salary=data.get("annual_salary", 0.0),
            tds_deducted=data.get("tds_deducted", 0.0),
            form_16_available=data.get("form_16_available", False),
            pan_number=data.get("pan_number", ""),
            employer_tan=data.get("employer_tan", "")
        )


@dataclass
class NewJoinerResult:
    """
    Result of new joiner tax calculation
    """
    employee_id: str = ""
    join_date: date = field(default_factory=date.today)
    prorated_annual_salary: float = 0.0
    prorated_annual_tax: float = 0.0
    previous_tds: float = 0.0
    remaining_tax_liability: float = 0.0
    monthly_tds: float = 0.0
    months_remaining: int = 0
    previous_employment: Optional[PreviousEmployment] = None
    calculation_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "join_date": self.join_date.isoformat(),
            "prorated_annual_salary": self.prorated_annual_salary,
            "prorated_annual_tax": self.prorated_annual_tax,
            "previous_tds": self.previous_tds,
            "remaining_tax_liability": self.remaining_tax_liability,
            "monthly_tds": self.monthly_tds,
            "months_remaining": self.months_remaining,
            "previous_employment": self.previous_employment.to_dict() if self.previous_employment else None,
            "calculation_date": self.calculation_date.isoformat()
        } 