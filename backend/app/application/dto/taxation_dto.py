"""
Taxation Data Transfer Objects
DTOs for taxation-related operations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from decimal import Decimal

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime


@dataclass
class SalaryComponentsDTO:
    """DTO for salary components"""
    basic: float = 0.0
    dearness_allowance: float = 0.0
    hra: float = 0.0
    actual_rent_paid: float = 0.0
    hra_city: str = "Others"
    special_allowance: float = 0.0
    bonus: float = 0.0
    transport_allowance: float = 0.0
    other_allowances: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'basic': self.basic,
            'dearness_allowance': self.dearness_allowance,
            'hra': self.hra,
            'actual_rent_paid': self.actual_rent_paid,
            'hra_city': self.hra_city,
            'special_allowance': self.special_allowance,
            'bonus': self.bonus,
            'transport_allowance': self.transport_allowance,
            'other_allowances': self.other_allowances
        }


@dataclass
class DeductionsDTO:
    """DTO for tax deductions"""
    section_80c: float = 0.0
    section_80d: float = 0.0
    section_80e: float = 0.0
    section_80g: float = 0.0
    section_80ccd: float = 0.0
    other_deductions: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'section_80c': self.section_80c,
            'section_80d': self.section_80d,
            'section_80e': self.section_80e,
            'section_80g': self.section_80g,
            'section_80ccd': self.section_80ccd,
            'other_deductions': self.other_deductions
        }


# Alias for backward compatibility and consistency
DeductionComponentsDTO = DeductionsDTO


@dataclass
class CapitalGainsDTO:
    """DTO for capital gains"""
    stcg_111a: float = 0.0
    stcg_any_other_asset: float = 0.0
    ltcg_112a: float = 0.0
    ltcg_any_other_asset: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'stcg_111a': self.stcg_111a,
            'stcg_any_other_asset': self.stcg_any_other_asset,
            'ltcg_112a': self.ltcg_112a,
            'ltcg_any_other_asset': self.ltcg_any_other_asset
        }


@dataclass
class TaxationCreateRequestDTO:
    """
    DTO for taxation creation request.
    
    Follows SOLID principles:
    - SRP: Only handles taxation creation request data
    - OCP: Can be extended with new fields without breaking existing code
    - LSP: Can be substituted with other request DTOs
    - ISP: Contains only taxation creation related fields
    - DIP: Doesn't depend on concrete implementations
    """
    
    employee_id: str
    tax_year: str
    regime: str = "old"
    emp_age: int = 0
    is_govt_employee: bool = False
    
    # Salary information
    salary: Optional[SalaryComponentsDTO] = None
    
    # Other income sources
    other_income: float = 0.0
    house_property_income: float = 0.0
    capital_gains: Optional[CapitalGainsDTO] = None
    
    # Deductions
    deductions: Optional[DeductionsDTO] = None
    
    # Special income components
    leave_encashment: float = 0.0
    pension_income: float = 0.0
    gratuity_income: float = 0.0
    
    # Metadata
    created_by: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxationCreateRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            employee_id=data['employee_id'],
            tax_year=data.get('tax_year', ''),
            regime=data.get('regime', 'old'),
            emp_age=data.get('emp_age', 0),
            is_govt_employee=data.get('is_govt_employee', False),
            salary=SalaryComponentsDTO(**data.get('salary', {})) if data.get('salary') else None,
            other_income=data.get('other_income', 0.0),
            house_property_income=data.get('house_property_income', 0.0),
            capital_gains=CapitalGainsDTO(**data.get('capital_gains', {})) if data.get('capital_gains') else None,
            deductions=DeductionsDTO(**data.get('deductions', {})) if data.get('deductions') else None,
            leave_encashment=data.get('leave_encashment', 0.0),
            pension_income=data.get('pension_income', 0.0),
            gratuity_income=data.get('gratuity_income', 0.0),
            created_by=data.get('created_by', '')
        )
    
    def validate(self) -> List[str]:
        """Validate DTO data and return list of errors"""
        errors = []
        
        if not self.employee_id or not self.employee_id.strip():
            errors.append("Employee ID is required")
        
        if not self.tax_year or not self.tax_year.strip():
            errors.append("Tax year is required")
        
        if self.regime not in ['old', 'new']:
            errors.append("Tax regime must be 'old' or 'new'")
        
        if self.emp_age < 0 or self.emp_age > 120:
            errors.append("Employee age must be between 0 and 120")
        
        if not self.created_by or not self.created_by.strip():
            errors.append("Created by is required")
        
        return errors


@dataclass
class TaxationUpdateRequestDTO:
    """
    DTO for taxation update request.
    """
    
    employee_id: str
    regime: Optional[str] = None
    salary: Optional[SalaryComponentsDTO] = None
    other_income: Optional[float] = None
    house_property_income: Optional[float] = None
    capital_gains: Optional[CapitalGainsDTO] = None
    deductions: Optional[DeductionsDTO] = None
    leave_encashment: Optional[float] = None
    pension_income: Optional[float] = None
    gratuity_income: Optional[float] = None
    updated_by: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxationUpdateRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            employee_id=data['employee_id'],
            regime=data.get('regime'),
            salary=SalaryComponentsDTO(**data.get('salary', {})) if data.get('salary') else None,
            other_income=data.get('other_income'),
            house_property_income=data.get('house_property_income'),
            capital_gains=CapitalGainsDTO(**data.get('capital_gains', {})) if data.get('capital_gains') else None,
            deductions=DeductionsDTO(**data.get('deductions', {})) if data.get('deductions') else None,
            leave_encashment=data.get('leave_encashment'),
            pension_income=data.get('pension_income'),
            gratuity_income=data.get('gratuity_income'),
            updated_by=data.get('updated_by', '')
        )
    
    def validate(self) -> List[str]:
        """Validate update data"""
        errors = []
        
        if not self.employee_id or not self.employee_id.strip():
            errors.append("Employee ID is required")
        
        if self.regime and self.regime not in ['old', 'new']:
            errors.append("Tax regime must be 'old' or 'new'")
        
        if not self.updated_by or not self.updated_by.strip():
            errors.append("Updated by is required")
        
        return errors


@dataclass
class TaxCalculationRequestDTO:
    """
    DTO for tax calculation request.
    """
    
    employee_id: str
    force_recalculate: bool = False
    include_projections: bool = False
    calculation_type: str = "full"  # full, quick, projection
    calculated_by: str = ""
    
    def validate(self) -> List[str]:
        """Validate calculation request"""
        errors = []
        
        if not self.employee_id or not self.employee_id.strip():
            errors.append("Employee ID is required")
        
        if self.calculation_type not in ['full', 'quick', 'projection']:
            errors.append("Calculation type must be 'full', 'quick', or 'projection'")
        
        return errors


@dataclass
class TaxBreakdownDTO:
    """DTO for tax calculation breakdown"""
    gross_income: float
    taxable_income: float
    total_deductions: float
    tax_before_rebate: float
    rebate_87a: float
    tax_after_rebate: float
    surcharge: float
    cess: float
    total_tax: float
    effective_tax_rate: float
    
    # Detailed breakdowns
    income_breakdown: Dict[str, float]
    deduction_breakdown: Dict[str, float]
    tax_slab_breakdown: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'gross_income': self.gross_income,
            'taxable_income': self.taxable_income,
            'total_deductions': self.total_deductions,
            'tax_before_rebate': self.tax_before_rebate,
            'rebate_87a': self.rebate_87a,
            'tax_after_rebate': self.tax_after_rebate,
            'surcharge': self.surcharge,
            'cess': self.cess,
            'total_tax': self.total_tax,
            'effective_tax_rate': self.effective_tax_rate,
            'income_breakdown': self.income_breakdown,
            'deduction_breakdown': self.deduction_breakdown,
            'tax_slab_breakdown': self.tax_slab_breakdown
        }


@dataclass
class TaxationResponseDTO:
    """
    DTO for taxation response.
    """
    
    taxation_id: str
    employee_id: str
    emp_age: int
    tax_year: str
    regime: str
    filing_status: str
    is_govt_employee: bool
    
    # Financial details
    gross_income: float
    taxable_income: float
    total_deductions: float
    total_tax: float
    tax_payable: float
    tax_paid: float
    tax_due: float
    tax_refundable: float
    
    # Components
    salary: Optional[Dict[str, Any]] = None
    deductions: Optional[Dict[str, Any]] = None
    other_income: Optional[Dict[str, Any]] = None
    
    # Tax breakdown
    tax_breakdown: Optional[TaxBreakdownDTO] = None
    
    # LWP adjustments
    lwp_adjustment: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    calculated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    @classmethod
    def from_entity(cls, taxation) -> 'TaxationResponseDTO':
        """Create DTO from Taxation entity"""
        return cls(
            taxation_id=str(taxation.taxation_id) if hasattr(taxation, 'taxation_id') else taxation.employee_id,
            employee_id=taxation.employee_id,
            emp_age=taxation.emp_age,
            tax_year=taxation.tax_year,
            regime=taxation.regime,
            filing_status=taxation.filing_status,
            is_govt_employee=taxation.is_govt_employee,
            gross_income=float(getattr(taxation, 'gross_income', 0)),
            taxable_income=float(getattr(taxation, 'taxable_income', 0)),
            total_deductions=float(getattr(taxation, 'total_deductions', 0)),
            total_tax=float(taxation.total_tax),
            tax_payable=float(taxation.tax_payable),
            tax_paid=float(taxation.tax_paid),
            tax_due=float(taxation.tax_due),
            tax_refundable=float(taxation.tax_refundable),
            salary=taxation.salary.to_dict() if hasattr(taxation.salary, 'to_dict') else None,
            deductions=taxation.deductions.to_dict() if hasattr(taxation.deductions, 'to_dict') else None,
            other_income=taxation.other_sources.to_dict() if hasattr(taxation.other_sources, 'to_dict') else None,
            tax_breakdown=getattr(taxation, 'tax_breakdown', None),
            lwp_adjustment=getattr(taxation, 'lwp_adjustment', None),
            created_at=taxation.created_at.isoformat() if hasattr(taxation, 'created_at') and taxation.created_at else None,
            updated_at=taxation.updated_at.isoformat() if hasattr(taxation, 'updated_at') and taxation.updated_at else None,
            created_by=getattr(taxation, 'created_by', None),
            updated_by=getattr(taxation, 'updated_by', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary for API response"""
        return {
            'taxation_id': self.taxation_id,
            'employee_id': self.employee_id,
            'emp_age': self.emp_age,
            'tax_year': self.tax_year,
            'regime': self.regime,
            'filing_status': self.filing_status,
            'is_govt_employee': self.is_govt_employee,
            'gross_income': self.gross_income,
            'taxable_income': self.taxable_income,
            'total_deductions': self.total_deductions,
            'total_tax': self.total_tax,
            'tax_payable': self.tax_payable,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'salary': self.salary,
            'deductions': self.deductions,
            'other_income': self.other_income,
            'tax_breakdown': self.tax_breakdown.to_dict() if self.tax_breakdown else None,
            'lwp_adjustment': self.lwp_adjustment,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'calculated_at': self.calculated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }


@dataclass
class TaxProjectionDTO:
    """DTO for tax projection"""
    employee_id: str
    projection_period: str  # monthly, quarterly, annual
    projected_income: float
    projected_tax: float
    current_tax_paid: float
    remaining_tax_liability: float
    monthly_tax_suggestion: float
    investment_suggestions: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'employee_id': self.employee_id,
            'projection_period': self.projection_period,
            'projected_income': self.projected_income,
            'projected_tax': self.projected_tax,
            'current_tax_paid': self.current_tax_paid,
            'remaining_tax_liability': self.remaining_tax_liability,
            'monthly_tax_suggestion': self.monthly_tax_suggestion,
            'investment_suggestions': self.investment_suggestions
        }


@dataclass
class TaxComparisonDTO:
    """DTO for comparing tax between regimes"""
    employee_id: str
    old_regime_tax: float
    new_regime_tax: float
    savings_amount: float
    savings_percentage: float
    recommended_regime: str
    comparison_details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'employee_id': self.employee_id,
            'old_regime_tax': self.old_regime_tax,
            'new_regime_tax': self.new_regime_tax,
            'savings_amount': self.savings_amount,
            'savings_percentage': self.savings_percentage,
            'recommended_regime': self.recommended_regime,
            'comparison_details': self.comparison_details
        }


@dataclass
class TaxSearchFiltersDTO:
    """DTO for tax search filters"""
    employee_ids: Optional[List[str]] = None
    tax_year: Optional[str] = None
    regime: Optional[str] = None
    filing_status: Optional[str] = None
    min_tax: Optional[float] = None
    max_tax: Optional[float] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    skip: int = 0
    limit: int = 100


@dataclass
class TaxStatisticsDTO:
    """DTO for tax statistics"""
    total_employees: int
    total_tax_calculated: float
    average_tax: float
    regime_distribution: Dict[str, int]
    tax_brackets: Dict[str, int]
    top_taxpayers: List[Dict[str, Any]]
    department_wise_stats: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_employees': self.total_employees,
            'total_tax_calculated': self.total_tax_calculated,
            'average_tax': self.average_tax,
            'regime_distribution': self.regime_distribution,
            'tax_brackets': self.tax_brackets,
            'top_taxpayers': self.top_taxpayers,
            'department_wise_stats': self.department_wise_stats
        }


@dataclass
class LWPAdjustmentRequestDTO:
    """DTO for LWP tax adjustment request"""
    employee_id: str
    lwp_days: int
    adjustment_period: str
    calculation_method: str = "proportional"
    adjusted_by: str = ""
    
    def validate(self) -> List[str]:
        """Validate LWP adjustment request"""
        errors = []
        
        if not self.employee_id or not self.employee_id.strip():
            errors.append("Employee ID is required")
        
        if self.lwp_days < 0:
            errors.append("LWP days cannot be negative")
        
        if not self.adjustment_period or not self.adjustment_period.strip():
            errors.append("Adjustment period is required")
        
        if not self.adjusted_by or not self.adjusted_by.strip():
            errors.append("Adjusted by is required")
        
        return errors


# Custom Exceptions for Taxation DTOs
class TaxationDTOError(Exception):
    """Base exception for taxation DTO operations"""
    pass


class TaxationValidationError(TaxationDTOError):
    """Exception raised when taxation validation fails"""
    
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation error for {field} '{value}': {reason}")


class TaxationBusinessRuleError(TaxationDTOError):
    """Exception raised when taxation business rule is violated"""
    
    def __init__(self, rule: str, context: Dict[str, Any] = None):
        self.rule = rule
        self.context = context or {}
        super().__init__(f"Business rule violation: {rule}")


class TaxationCalculationError(TaxationDTOError):
    """Exception raised when tax calculation fails"""
    
    def __init__(self, reason: str, calculation_data: Dict[str, Any] = None):
        self.reason = reason
        self.calculation_data = calculation_data or {}
        super().__init__(f"Tax calculation error: {reason}")


class TaxationNotFoundError(TaxationDTOError):
    """Exception raised when taxation record is not found"""
    
    def __init__(self, employee_id: str, tax_year: str = None):
        self.employee_id = employee_id
        self.tax_year = tax_year
        message = f"Taxation record not found for employee {employee_id}"
        if tax_year:
            message += f" for tax year {tax_year}"
        super().__init__(message) 