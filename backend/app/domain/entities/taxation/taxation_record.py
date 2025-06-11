"""
Taxation Record Entity
Represents a complete tax record for an employee
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import date

from app.domain.value_objects.money import Money
from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.tax_deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits


@dataclass
class TaxationRecord:
    """Taxation record entity containing complete tax information."""
    
    # Employee details
    employee_id: str
    financial_year: int
    assessment_year: int
    
    # Income sources
    salary_income: SalaryIncome
    perquisites: Perquisites
    house_property_income: HousePropertyIncome
    capital_gains_income: CapitalGainsIncome
    retirement_benefits: RetirementBenefits
    other_income: OtherIncome
    
    # Deductions
    tax_deductions: TaxDeductions
    
    # Tax regime
    regime: TaxRegime
    
    # Additional details
    age: int
    is_senior_citizen: bool = False
    is_super_senior_citizen: bool = False
    is_government_employee: bool = False
    
    def get_total_income(self) -> Money:
        """Get total income from all sources."""
        return (
            self.salary_income.get_total_salary()
            .add(self.perquisites.get_total_perquisites())
            .add(self.house_property_income.get_income_from_house_property())
            .add(self.capital_gains_income.get_net_taxable_capital_gain())
            .add(self.retirement_benefits.get_taxable_retirement_benefits())
            .add(self.other_income.get_total_taxable_income())
        )
    
    def get_total_exemptions(self) -> Money:
        """Get total exemptions from all sources."""
        return (
            self.salary_income.get_total_exemptions()
            .add(self.retirement_benefits.get_total_exemptions())
            .add(self.other_income.get_total_exempt_income())
        )
    
    def get_total_deductions(self) -> Money:
        """Get total deductions."""
        return self.tax_deductions.get_total_deductions()
    
    def get_taxable_income(self) -> Money:
        """
        Calculate taxable income.
        
        Taxable income = Total income - Total exemptions - Total deductions
        """
        return (
            self.get_total_income()
            .subtract(self.get_total_exemptions())
            .subtract(self.get_total_deductions())
        )
    
    def get_tax_liability(self) -> Money:
        """
        Calculate total tax liability.
        
        Tax liability = Tax on taxable income + Tax on special income
        """
        # Calculate tax on taxable income
        taxable_income = self.get_taxable_income()
        
        # Calculate tax on special income (capital gains, etc.)
        special_income_tax = (
            self.capital_gains_income.get_taxable_capital_gain()
            .add(self.other_income.calculate_tax_on_speculative_income())
            .add(self.other_income.calculate_tax_on_short_term_capital_gains())
            .add(self.other_income.calculate_tax_on_long_term_capital_gains())
            .add(self.other_income.calculate_tax_on_dividend_income())
        )
        
        return taxable_income.add(special_income_tax)
    
    def get_regime_comparison(self) -> dict:
        """
        Compare tax liability under both regimes.
        
        Returns:
            dict: Comparison of tax liability under old and new regimes
        """
        # Create a copy with old regime
        old_regime_record = TaxationRecord(
            employee_id=self.employee_id,
            financial_year=self.financial_year,
            assessment_year=self.assessment_year,
            salary_income=self.salary_income,
            perquisites=self.perquisites,
            house_property_income=self.house_property_income,
            capital_gains_income=self.capital_gains_income,
            retirement_benefits=self.retirement_benefits,
            other_income=self.other_income,
            tax_deductions=self.tax_deductions,
            regime=TaxRegime(TaxRegimeType.OLD),
            age=self.age,
            is_senior_citizen=self.is_senior_citizen,
            is_super_senior_citizen=self.is_super_senior_citizen,
            is_government_employee=self.is_government_employee
        )
        
        # Create a copy with new regime
        new_regime_record = TaxationRecord(
            employee_id=self.employee_id,
            financial_year=self.financial_year,
            assessment_year=self.assessment_year,
            salary_income=self.salary_income,
            perquisites=self.perquisites,
            house_property_income=self.house_property_income,
            capital_gains_income=self.capital_gains_income,
            retirement_benefits=self.retirement_benefits,
            other_income=self.other_income,
            tax_deductions=self.tax_deductions,
            regime=TaxRegime(TaxRegimeType.NEW),
            age=self.age,
            is_senior_citizen=self.is_senior_citizen,
            is_super_senior_citizen=self.is_super_senior_citizen,
            is_government_employee=self.is_government_employee
        )
        
        old_regime_tax = old_regime_record.get_tax_liability()
        new_regime_tax = new_regime_record.get_tax_liability()
        
        return {
            "old_regime": {
                "tax_liability": old_regime_tax.to_float(),
                "effective_tax_rate": f"{(old_regime_tax.amount / self.get_total_income().amount * Decimal('100')):.2f}%",
                "deductions_available": True
            },
            "new_regime": {
                "tax_liability": new_regime_tax.to_float(),
                "effective_tax_rate": f"{(new_regime_tax.amount / self.get_total_income().amount * Decimal('100')):.2f}%",
                "deductions_available": False
            },
            "comparison": {
                "tax_difference": (old_regime_tax.subtract(new_regime_tax)).to_float(),
                "percentage_difference": f"{((old_regime_tax.amount - new_regime_tax.amount) / old_regime_tax.amount * Decimal('100')):.2f}%",
                "recommended_regime": "old" if old_regime_tax.is_less_than(new_regime_tax) else "new"
            }
        }
    
    def get_tax_breakdown(self) -> dict:
        """
        Get detailed tax breakdown.
        
        Returns:
            dict: Detailed breakdown of tax calculation
        """
        return {
            "employee_details": {
                "employee_id": self.employee_id,
                "financial_year": self.financial_year,
                "assessment_year": self.assessment_year,
                "age": self.age,
                "is_senior_citizen": self.is_senior_citizen,
                "is_super_senior_citizen": self.is_super_senior_citizen,
                "is_government_employee": self.is_government_employee
            },
            "income_breakdown": {
                "salary_income": self.salary_income.get_total_salary().to_float(),
                "perquisites": self.perquisites.get_total_perquisites().to_float(),
                "house_property_income": self.house_property_income.get_income_from_house_property().to_float(),
                "capital_gains": self.capital_gains_income.get_net_taxable_capital_gain().to_float(),
                "retirement_benefits": self.retirement_benefits.get_taxable_retirement_benefits().to_float(),
                "other_income": self.other_income.get_total_taxable_income().to_float(),
                "total_income": self.get_total_income().to_float()
            },
            "exemptions_breakdown": {
                "salary_exemptions": self.salary_income.get_total_exemptions().to_float(),
                "retirement_exemptions": self.retirement_benefits.get_total_exemptions().to_float(),
                "other_exemptions": self.other_income.get_total_exempt_income().to_float(),
                "total_exemptions": self.get_total_exemptions().to_float()
            },
            "deductions_breakdown": {
                "section_80c": self.tax_deductions.get_total_80c_deductions().to_float(),
                "section_80d": self.tax_deductions.get_total_80d_deductions().to_float(),
                "other_deductions": self.tax_deductions.get_total_deductions().to_float(),
                "total_deductions": self.get_total_deductions().to_float()
            },
            "tax_calculation": {
                "taxable_income": self.get_taxable_income().to_float(),
                "tax_liability": self.get_tax_liability().to_float(),
                "effective_tax_rate": f"{(self.get_tax_liability().amount / self.get_total_income().amount * Decimal('100')):.2f}%",
                "regime_used": self.regime.regime_type.value
            }
        } 