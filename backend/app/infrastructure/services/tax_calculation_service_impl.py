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
from app.domain.entities.taxation.taxation_record import TaxationRecord
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.tax_deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits


class TaxCalculationServiceImpl(TaxCalculationService):
    """Infrastructure implementation of the tax calculation service."""
    
    def __init__(self):
        """Initialize the service."""
        super().__init__()
    
    def calculate_tax(self, input_data: TaxCalculationInput) -> TaxCalculationResult:
        """
        Calculate tax based on input data.
        
        Args:
            input_data: Tax calculation input data
            
        Returns:
            TaxCalculationResult: Tax calculation result
        """
        return super().calculate_tax(input_data)
    
    def calculate_tax_for_record(self, record: TaxationRecord) -> TaxCalculationResult:
        """
        Calculate tax for a taxation record.
        
        Args:
            record: Taxation record
            
        Returns:
            TaxCalculationResult: Tax calculation result
        """
        # Convert record to input data
        input_data = self._convert_record_to_input(record)
        
        # Calculate tax
        return self.calculate_tax(input_data)
    
    def _convert_record_to_input(self, record: TaxationRecord) -> TaxCalculationInput:
        """
        Convert taxation record to tax calculation input.
        
        Args:
            record: Taxation record
            
        Returns:
            TaxCalculationInput: Tax calculation input
        """
        return TaxCalculationInput(
            salary_income=record.salary_income,
            perquisites=record.perquisites,
            house_property_income=record.house_property_income,
            capital_gains_income=record.capital_gains_income,
            retirement_benefits=record.retirement_benefits,
            other_income=record.other_income,
            tax_deductions=record.tax_deductions,
            regime=record.regime,
            age=record.age,
            is_senior_citizen=record.is_senior_citizen,
            is_super_senior_citizen=record.is_super_senior_citizen,
            is_government_employee=record.is_government_employee
        ) 