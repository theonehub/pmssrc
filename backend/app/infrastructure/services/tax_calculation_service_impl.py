"""
Tax Calculation Service Implementation
Infrastructure implementation of the tax calculation service
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal

from app.domain.services.taxation.tax_calculation_service import (
    TaxCalculationService,
    TaxCalculationInput,
    TaxCalculationResult
)
from app.domain.value_objects.money import Money
from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits


class TaxCalculationServiceImpl(TaxCalculationService):
    """Infrastructure implementation of the tax calculation service."""
    
    def __init__(self, salary_package_repository=None, user_repository=None):
        """Initialize the service with repositories."""
        super().__init__(
            salary_package_repository=salary_package_repository,
            user_repository=user_repository
        )
    