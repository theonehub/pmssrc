"""Domain Services Module."""

from app.domain.services.tax_calculation_service import (
    TaxCalculationService, 
    TaxCalculationResult,
    RegimeComparisonService
)
from app.domain.services.payroll_tax_service import (
    PayrollTaxService,
    MonthlyTaxResult,
    AnnualPayrollTaxResult
)

__all__ = [
    "TaxCalculationService",
    "TaxCalculationResult", 
    "RegimeComparisonService",
    "PayrollTaxService",
    "MonthlyTaxResult",
    "AnnualPayrollTaxResult"
] 