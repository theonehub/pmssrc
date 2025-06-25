"""
Regime Comparison Service Implementation
Infrastructure implementation of the regime comparison service
"""

from typing import Dict, Any, Optional
from decimal import Decimal

from app.domain.services.taxation.regime_comparison_service import (
    RegimeComparisonService,
    RegimeComparisonInput,
    RegimeComparisonResult
)
from app.domain.value_objects.money import Money
from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.taxation_record import TaxationRecord
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits


class RegimeComparisonServiceImpl(RegimeComparisonService):
    """Infrastructure implementation of the regime comparison service."""
    
    def __init__(self):
        """Initialize the service."""
        super().__init__()
    
    def compare_regimes(self, input_data: RegimeComparisonInput) -> RegimeComparisonResult:
        """
        Compare old and new tax regimes.
        
        Args:
            input_data: Regime comparison input data
            
        Returns:
            RegimeComparisonResult: Regime comparison result
        """
        return super().compare_regimes(input_data)
    
    def compare_regimes_for_record(self, record: TaxationRecord) -> RegimeComparisonResult:
        """
        Compare regimes for a taxation record.
        
        Args:
            record: Taxation record
            
        Returns:
            RegimeComparisonResult: Regime comparison result
        """
        # Convert record to input data
        input_data = self._convert_record_to_input(record)
        
        # Compare regimes
        return self.compare_regimes(input_data)
    
    def _convert_record_to_input(self, record: TaxationRecord) -> RegimeComparisonInput:
        """
        Convert taxation record to regime comparison input.
        
        Args:
            record: Taxation record
            
        Returns:
            RegimeComparisonInput: Regime comparison input
        """
        return RegimeComparisonInput(
            salary_income=record.salary_income,
            perquisites=record.perquisites,
            capital_gains_income=record.other_income.capital_gains_income if record.other_income else None,
            retirement_benefits=record.retirement_benefits,
            other_income=record.other_income,
            deductions=record.deductions,
            age=record.age,
            is_senior_citizen=record.age >= 60,
            is_super_senior_citizen=record.age >= 80,
            is_government_employee=record.is_government_employee
        ) 