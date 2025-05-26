"""
Taxation Data Transfer Objects
DTOs for taxation-related operations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

from domain.value_objects.money import Money
from domain.value_objects.tax_regime import TaxRegime


@dataclass
class TaxCalculationRequestDTO:
    """
    DTO for tax calculation request.
    
    Follows SOLID principles:
    - SRP: Only handles tax calculation request data
    - OCP: Can be extended with new fields without breaking existing code
    - LSP: Can be substituted with other request DTOs
    - ISP: Contains only tax calculation related fields
    - DIP: Doesn't depend on concrete implementations
    """
    
    employee_id: str
    tax_year: str
    regime: TaxRegime
    gross_annual_salary: Money
    deductions: Dict[str, float]
    send_notification: bool = True
    include_optimization_suggestions: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxCalculationRequestDTO':
        """Create DTO from dictionary"""
        
        # Convert regime string to TaxRegime object
        regime_str = data.get('regime', 'old')
        if regime_str.lower() == 'new':
            regime = TaxRegime.new_regime()
        else:
            regime = TaxRegime.old_regime()
        
        # Convert salary to Money object
        gross_salary = Money.from_float(data['gross_annual_salary'])
        
        return cls(
            employee_id=data['employee_id'],
            tax_year=data['tax_year'],
            regime=regime,
            gross_annual_salary=gross_salary,
            deductions=data.get('deductions', {}),
            send_notification=data.get('send_notification', True),
            include_optimization_suggestions=data.get('include_optimization_suggestions', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'employee_id': self.employee_id,
            'tax_year': self.tax_year,
            'regime': str(self.regime),
            'gross_annual_salary': float(self.gross_annual_salary.amount),
            'deductions': self.deductions,
            'send_notification': self.send_notification,
            'include_optimization_suggestions': self.include_optimization_suggestions
        }
    
    def validate(self) -> List[str]:
        """Validate DTO data and return list of errors"""
        errors = []
        
        if not self.employee_id or not self.employee_id.strip():
            errors.append("Employee ID is required")
        
        if not self.tax_year or not self.tax_year.strip():
            errors.append("Tax year is required")
        
        if not self._is_valid_tax_year_format(self.tax_year):
            errors.append("Invalid tax year format. Expected format: YYYY-YY")
        
        if not self.gross_annual_salary.is_positive():
            errors.append("Gross annual salary must be positive")
        
        # Validate deductions
        for section, amount in self.deductions.items():
            if amount < 0:
                errors.append(f"Deduction amount for section {section} cannot be negative")
        
        return errors
    
    def _is_valid_tax_year_format(self, tax_year: str) -> bool:
        """Validate tax year format (YYYY-YY)"""
        import re
        pattern = r'^\d{4}-\d{2}$'
        return bool(re.match(pattern, tax_year))


@dataclass
class TaxCalculationResponseDTO:
    """
    DTO for tax calculation response.
    """
    
    employee_id: str
    tax_year: str
    regime: TaxRegime
    gross_annual_salary: Money
    taxable_income: Optional[Money]
    calculated_tax: Optional[Money]
    surcharge_amount: Optional[Money]
    cess_amount: Optional[Money]
    rebate_87a: Money
    total_tax_liability: Optional[Money]
    effective_tax_rate: float
    deductions: Dict[str, Money]
    optimization_suggestions: List[Dict[str, Any]]
    calculated_at: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary for API response"""
        
        def money_to_float(money_obj):
            return float(money_obj.amount) if money_obj else None
        
        return {
            'employee_id': self.employee_id,
            'tax_year': self.tax_year,
            'regime': str(self.regime),
            'gross_annual_salary': money_to_float(self.gross_annual_salary),
            'taxable_income': money_to_float(self.taxable_income),
            'calculated_tax': money_to_float(self.calculated_tax),
            'surcharge_amount': money_to_float(self.surcharge_amount),
            'cess_amount': money_to_float(self.cess_amount),
            'rebate_87a': money_to_float(self.rebate_87a),
            'total_tax_liability': money_to_float(self.total_tax_liability),
            'effective_tax_rate': self.effective_tax_rate,
            'deductions': {k: money_to_float(v) for k, v in self.deductions.items()},
            'optimization_suggestions': self.optimization_suggestions,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }
    
    def get_tax_breakdown(self) -> Dict[str, float]:
        """Get detailed tax breakdown"""
        return {
            'gross_annual_salary': float(self.gross_annual_salary.amount),
            'taxable_income': float(self.taxable_income.amount) if self.taxable_income else 0.0,
            'income_tax': float(self.calculated_tax.amount) if self.calculated_tax else 0.0,
            'surcharge': float(self.surcharge_amount.amount) if self.surcharge_amount else 0.0,
            'cess': float(self.cess_amount.amount) if self.cess_amount else 0.0,
            'rebate_87a': float(self.rebate_87a.amount),
            'total_tax_liability': float(self.total_tax_liability.amount) if self.total_tax_liability else 0.0,
            'effective_tax_rate': self.effective_tax_rate
        }


@dataclass
class TaxDeductionDTO:
    """
    DTO for tax deduction information.
    """
    
    section: str
    amount: float
    description: Optional[str] = None
    supporting_documents: List[str] = None
    
    def __post_init__(self):
        if self.supporting_documents is None:
            self.supporting_documents = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxDeductionDTO':
        """Create DTO from dictionary"""
        return cls(
            section=data['section'],
            amount=float(data['amount']),
            description=data.get('description'),
            supporting_documents=data.get('supporting_documents', [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'section': self.section,
            'amount': self.amount,
            'description': self.description,
            'supporting_documents': self.supporting_documents
        }
    
    def validate(self) -> List[str]:
        """Validate deduction data"""
        errors = []
        
        if not self.section or not self.section.strip():
            errors.append("Deduction section is required")
        
        if self.amount < 0:
            errors.append("Deduction amount cannot be negative")
        
        return errors


@dataclass
class TaxRegimeComparisonDTO:
    """
    DTO for tax regime comparison.
    """
    
    employee_id: str
    gross_annual_salary: float
    deductions: Dict[str, float]
    old_regime_tax: Dict[str, float]
    new_regime_tax: Dict[str, float]
    recommendation: str
    savings_amount: float
    better_regime: str
    
    @classmethod
    def from_comparison_result(
        cls, 
        employee_id: str,
        gross_annual_salary: float,
        deductions: Dict[str, float],
        comparison_result: Dict[str, Any]
    ) -> 'TaxRegimeComparisonDTO':
        """Create DTO from comparison result"""
        
        old_regime = comparison_result['old_regime']
        new_regime = comparison_result['new_regime']
        
        old_total = old_regime['tax_breakdown']['total_liability']
        new_total = new_regime['tax_breakdown']['total_liability']
        
        if old_total < new_total:
            savings_amount = new_total - old_total
            better_regime = 'old'
        elif new_total < old_total:
            savings_amount = old_total - new_total
            better_regime = 'new'
        else:
            savings_amount = 0.0
            better_regime = 'equal'
        
        return cls(
            employee_id=employee_id,
            gross_annual_salary=gross_annual_salary,
            deductions=deductions,
            old_regime_tax=old_regime['tax_breakdown'],
            new_regime_tax=new_regime['tax_breakdown'],
            recommendation=comparison_result['recommendation'],
            savings_amount=savings_amount,
            better_regime=better_regime
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'employee_id': self.employee_id,
            'gross_annual_salary': self.gross_annual_salary,
            'deductions': self.deductions,
            'comparison': {
                'old_regime': self.old_regime_tax,
                'new_regime': self.new_regime_tax,
                'recommendation': self.recommendation,
                'savings_amount': self.savings_amount,
                'better_regime': self.better_regime
            }
        }


@dataclass
class TaxOptimizationSuggestionDTO:
    """
    DTO for tax optimization suggestions.
    """
    
    suggestion_type: str  # 'deduction', 'regime_change', 'investment', etc.
    title: str
    description: str
    potential_savings: float
    required_action: str
    priority: str  # 'high', 'medium', 'low'
    deadline: Optional[str] = None
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxOptimizationSuggestionDTO':
        """Create DTO from dictionary"""
        return cls(
            suggestion_type=data['suggestion_type'],
            title=data['title'],
            description=data['description'],
            potential_savings=float(data['potential_savings']),
            required_action=data['required_action'],
            priority=data.get('priority', 'medium'),
            deadline=data.get('deadline'),
            additional_info=data.get('additional_info', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'suggestion_type': self.suggestion_type,
            'title': self.title,
            'description': self.description,
            'potential_savings': self.potential_savings,
            'required_action': self.required_action,
            'priority': self.priority,
            'deadline': self.deadline,
            'additional_info': self.additional_info
        }


@dataclass
class TaxProjectionDTO:
    """
    DTO for tax projection calculations.
    """
    
    employee_id: str
    projection_year: str
    projected_income: float
    projected_deductions: Dict[str, float]
    regime: str
    projected_tax_liability: float
    assumptions: Dict[str, Any]
    confidence_level: str  # 'high', 'medium', 'low'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxProjectionDTO':
        """Create DTO from dictionary"""
        return cls(
            employee_id=data['employee_id'],
            projection_year=data['projection_year'],
            projected_income=float(data['projected_income']),
            projected_deductions=data.get('projected_deductions', {}),
            regime=data['regime'],
            projected_tax_liability=float(data['projected_tax_liability']),
            assumptions=data.get('assumptions', {}),
            confidence_level=data.get('confidence_level', 'medium')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'employee_id': self.employee_id,
            'projection_year': self.projection_year,
            'projected_income': self.projected_income,
            'projected_deductions': self.projected_deductions,
            'regime': self.regime,
            'projected_tax_liability': self.projected_tax_liability,
            'assumptions': self.assumptions,
            'confidence_level': self.confidence_level
        }


# Validation utilities
def validate_tax_year(tax_year: str) -> bool:
    """Validate tax year format"""
    import re
    pattern = r'^\d{4}-\d{2}$'
    return bool(re.match(pattern, tax_year))


def validate_deduction_section(section: str) -> bool:
    """Validate deduction section format"""
    valid_sections = [
        '80C', '80D', '80E', '80G', '80TTA', '80TTB', 
        '24B', 'HRA', 'LTA', 'Medical'
    ]
    return section in valid_sections


def validate_employee_id_format(employee_id: str) -> bool:
    """Validate employee ID format"""
    import re
    # Assuming format like EMP001, EMP002, etc.
    pattern = r'^EMP\d{3,}$'
    return bool(re.match(pattern, employee_id))


class TaxationDTOError(Exception):
    """Base exception for taxation DTO operations"""
    pass


class InvalidTaxationDataError(TaxationDTOError):
    """Exception raised when taxation data is invalid"""
    
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field} '{value}': {reason}")


class TaxationDTOValidationError(TaxationDTOError):
    """Exception raised when DTO validation fails"""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}") 