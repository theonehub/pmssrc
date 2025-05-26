"""
Taxation Domain Events
Events that represent important business occurrences in the taxation domain
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from abc import ABC

from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.money import Money
from domain.value_objects.tax_regime import TaxRegime
from domain.events.employee_events import DomainEvent


@dataclass
class TaxCalculated(DomainEvent):
    """
    Event raised when tax calculation is completed.
    
    This event can trigger:
    - Payroll system updates
    - Form 16 generation
    - Tax liability notifications
    - Compliance reporting
    - Analytics updates
    """
    
    employee_id: EmployeeId
    tax_year: str
    regime: TaxRegime
    taxable_income: Money
    calculated_tax: Money
    total_tax_liability: Money
    
    def get_event_type(self) -> str:
        return "taxation.tax_calculated"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"
    
    def get_calculation_summary(self) -> dict:
        """Get tax calculation summary"""
        return {
            "employee_id": str(self.employee_id),
            "tax_year": self.tax_year,
            "regime": str(self.regime),
            "taxable_income": self.taxable_income.format(),
            "calculated_tax": self.calculated_tax.format(),
            "total_tax_liability": self.total_tax_liability.format(),
            "effective_tax_rate": self._calculate_effective_rate()
        }
    
    def _calculate_effective_rate(self) -> float:
        """Calculate effective tax rate"""
        if self.taxable_income.is_zero():
            return 0.0
        return float((self.total_tax_liability.amount / self.taxable_income.amount) * 100)


@dataclass
class TaxRegimeChanged(DomainEvent):
    """
    Event raised when an employee's tax regime is changed.
    
    This event can trigger:
    - Deduction validation and cleanup
    - Tax recalculation
    - Notification to employee
    - Compliance updates
    - Audit logging
    """
    
    employee_id: EmployeeId
    tax_year: str
    old_regime: TaxRegime
    new_regime: TaxRegime
    reason: str
    
    def get_event_type(self) -> str:
        return "taxation.regime_changed"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"
    
    def get_regime_change_details(self) -> dict:
        """Get regime change details"""
        return {
            "employee_id": str(self.employee_id),
            "tax_year": self.tax_year,
            "regime_change": {
                "from": str(self.old_regime),
                "to": str(self.new_regime)
            },
            "reason": self.reason,
            "impact": self._get_regime_impact()
        }
    
    def _get_regime_impact(self) -> dict:
        """Get impact of regime change"""
        return {
            "deductions_allowed_before": self.old_regime.allows_deductions(),
            "deductions_allowed_after": self.new_regime.allows_deductions(),
            "exemption_limit_change": {
                "old": float(self.old_regime.get_basic_exemption_limit()),
                "new": float(self.new_regime.get_basic_exemption_limit())
            }
        }


@dataclass
class DeductionAdded(DomainEvent):
    """
    Event raised when a tax deduction is added.
    
    This event can trigger:
    - Tax recalculation
    - Validation of supporting documents
    - Notification to employee
    - Compliance checks
    """
    
    employee_id: EmployeeId
    tax_year: str
    section: str
    amount: Money
    old_amount: Money
    description: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "taxation.deduction_added"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"
    
    def is_new_deduction(self) -> bool:
        """Check if this is a new deduction (not an update)"""
        return self.old_amount.is_zero()
    
    def is_deduction_update(self) -> bool:
        """Check if this is an update to existing deduction"""
        return not self.old_amount.is_zero()
    
    def get_amount_change(self) -> Money:
        """Get the change in deduction amount"""
        return self.amount.subtract(self.old_amount)
    
    def get_deduction_details(self) -> dict:
        """Get deduction details"""
        return {
            "employee_id": str(self.employee_id),
            "tax_year": self.tax_year,
            "section": self.section,
            "amount": self.amount.format(),
            "old_amount": self.old_amount.format(),
            "change": self.get_amount_change().format(),
            "description": self.description,
            "is_new": self.is_new_deduction()
        }


@dataclass
class DeductionRemoved(DomainEvent):
    """
    Event raised when a tax deduction is removed.
    
    This event can trigger:
    - Tax recalculation
    - Notification to employee
    - Audit logging
    - Compliance updates
    """
    
    employee_id: EmployeeId
    tax_year: str
    section: str
    amount: Money
    
    def get_event_type(self) -> str:
        return "taxation.deduction_removed"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"
    
    def get_removal_details(self) -> dict:
        """Get deduction removal details"""
        return {
            "employee_id": str(self.employee_id),
            "tax_year": self.tax_year,
            "section": self.section,
            "removed_amount": self.amount.format()
        }


@dataclass
class TaxProjectionCalculated(DomainEvent):
    """
    Event raised when tax projection is calculated for future periods.
    
    This event can trigger:
    - Investment planning recommendations
    - Salary optimization suggestions
    - Financial planning notifications
    """
    
    employee_id: EmployeeId
    projection_year: str
    projected_income: Money
    projected_tax: Money
    regime: TaxRegime
    assumptions: dict
    
    def get_event_type(self) -> str:
        return "taxation.projection_calculated"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.projection_year}"


@dataclass
class TaxComplianceAlert(DomainEvent):
    """
    Event raised when tax compliance issues are detected.
    
    This event can trigger:
    - Compliance notifications
    - Document requests
    - Audit alerts
    - Corrective action workflows
    """
    
    employee_id: EmployeeId
    tax_year: str
    alert_type: str  # "missing_documents", "limit_exceeded", "invalid_deduction", etc.
    message: str
    severity: str  # "low", "medium", "high", "critical"
    
    def get_event_type(self) -> str:
        return "taxation.compliance_alert"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"
    
    def is_critical(self) -> bool:
        """Check if this is a critical compliance alert"""
        return self.severity == "critical"
    
    def requires_immediate_action(self) -> bool:
        """Check if alert requires immediate action"""
        return self.severity in ["high", "critical"]


@dataclass
class Form16Generated(DomainEvent):
    """
    Event raised when Form 16 is generated for an employee.
    
    This event can trigger:
    - Document delivery to employee
    - Digital signature workflows
    - Archive storage
    - Notification systems
    """
    
    employee_id: EmployeeId
    tax_year: str
    form16_id: str
    file_path: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "taxation.form16_generated"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"


@dataclass
class TaxOptimizationSuggested(DomainEvent):
    """
    Event raised when tax optimization suggestions are generated.
    
    This event can trigger:
    - Employee notifications
    - Financial advisor consultations
    - Investment recommendations
    - Planning session scheduling
    """
    
    employee_id: EmployeeId
    tax_year: str
    suggestions: list
    potential_savings: Money
    
    def get_event_type(self) -> str:
        return "taxation.optimization_suggested"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.tax_year}"
    
    def has_significant_savings(self, threshold: Money) -> bool:
        """Check if potential savings exceed threshold"""
        return self.potential_savings.amount >= threshold.amount


# Event type registry for taxation events
TAXATION_EVENT_TYPE_REGISTRY = {
    "taxation.tax_calculated": TaxCalculated,
    "taxation.regime_changed": TaxRegimeChanged,
    "taxation.deduction_added": DeductionAdded,
    "taxation.deduction_removed": DeductionRemoved,
    "taxation.projection_calculated": TaxProjectionCalculated,
    "taxation.compliance_alert": TaxComplianceAlert,
    "taxation.form16_generated": Form16Generated,
    "taxation.optimization_suggested": TaxOptimizationSuggested,
}


def get_taxation_event_class(event_type: str) -> type:
    """Get taxation event class by event type string"""
    return TAXATION_EVENT_TYPE_REGISTRY.get(event_type)


def is_valid_taxation_event_type(event_type: str) -> bool:
    """Check if taxation event type is valid"""
    return event_type in TAXATION_EVENT_TYPE_REGISTRY 