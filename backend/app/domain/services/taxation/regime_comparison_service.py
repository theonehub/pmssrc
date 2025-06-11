"""
Regime Comparison Service
Domain service for comparing old and new tax regimes
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.domain.value_objects.money import Money
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.tax_deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits


@dataclass
class RegimeComparisonInput:
    """Input for regime comparison."""
    salary_income: SalaryIncome
    perquisites: Perquisites
    house_property_income: HousePropertyIncome
    capital_gains_income: CapitalGainsIncome
    retirement_benefits: RetirementBenefits
    other_income: OtherIncome
    tax_deductions: TaxDeductions
    age: int
    is_senior_citizen: bool
    is_super_senior_citizen: bool
    is_government_employee: bool


@dataclass
class RegimeComparisonResult:
    """Result of regime comparison."""
    old_regime_tax: Money
    new_regime_tax: Money
    tax_difference: Money
    percentage_difference: Decimal
    recommended_regime: str
    comparison_breakdown: Dict[str, Any]
    savings_breakdown: Dict[str, Any]


class RegimeComparisonService:
    """Service for comparing tax regimes."""
    
    def compare_regimes(self, input_data: RegimeComparisonInput) -> RegimeComparisonResult:
        """
        Compare old and new tax regimes.
        
        Args:
            input_data: Regime comparison input data
            
        Returns:
            RegimeComparisonResult: Regime comparison result
        """
        # Calculate tax under old regime
        old_regime_tax = self._calculate_old_regime_tax(input_data)
        
        # Calculate tax under new regime
        new_regime_tax = self._calculate_new_regime_tax(input_data)
        
        # Calculate difference
        tax_difference = old_regime_tax - new_regime_tax
        percentage_difference = (tax_difference / old_regime_tax) * Decimal('100')
        
        # Determine recommended regime
        recommended_regime = "new" if tax_difference > Money(0) else "old"
        
        # Get comparison breakdown
        comparison_breakdown = self._get_comparison_breakdown(
            input_data, old_regime_tax, new_regime_tax
        )
        
        # Get savings breakdown
        savings_breakdown = self._get_savings_breakdown(
            input_data, old_regime_tax, new_regime_tax
        )
        
        return RegimeComparisonResult(
            old_regime_tax=old_regime_tax,
            new_regime_tax=new_regime_tax,
            tax_difference=tax_difference,
            percentage_difference=percentage_difference,
            recommended_regime=recommended_regime,
            comparison_breakdown=comparison_breakdown,
            savings_breakdown=savings_breakdown
        )
    
    def _calculate_old_regime_tax(self, input_data: RegimeComparisonInput) -> Money:
        """Calculate tax under old regime."""
        # Calculate total income
        total_income = (
            input_data.salary_income.basic_salary +
            input_data.salary_income.dearness_allowance +
            input_data.salary_income.house_rent_allowance +
            input_data.salary_income.special_allowance +
            input_data.salary_income.conveyance_allowance +
            input_data.salary_income.medical_allowance +
            input_data.salary_income.bonus +
            input_data.salary_income.commission +
            input_data.salary_income.overtime +
            input_data.salary_income.arrears +
            input_data.salary_income.gratuity +
            input_data.salary_income.leave_encashment +
            input_data.salary_income.other_allowances
        )
        
        # Calculate total deductions
        total_deductions = (
            input_data.tax_deductions.section_80c +
            input_data.tax_deductions.section_80d +
            input_data.tax_deductions.section_80e +
            input_data.tax_deductions.section_80g +
            input_data.tax_deductions.section_80gg +
            input_data.tax_deductions.section_80gga +
            input_data.tax_deductions.section_80ggc +
            input_data.tax_deductions.section_80tta +
            input_data.tax_deductions.section_80ttb +
            input_data.tax_deductions.section_80u +
            input_data.tax_deductions.standard_deduction +
            input_data.tax_deductions.hra_exemption +
            input_data.tax_deductions.lta_exemption +
            input_data.tax_deductions.other_deductions
        )
        
        # Calculate taxable income
        taxable_income = total_income - total_deductions
        
        # Calculate tax using old regime slabs
        return self._calculate_tax_using_slabs(
            taxable_income,
            input_data.age,
            input_data.is_senior_citizen,
            input_data.is_super_senior_citizen,
            is_old_regime=True
        )
    
    def _calculate_new_regime_tax(self, input_data: RegimeComparisonInput) -> Money:
        """Calculate tax under new regime."""
        # Calculate total income (same as old regime)
        total_income = (
            input_data.salary_income.basic_salary +
            input_data.salary_income.dearness_allowance +
            input_data.salary_income.house_rent_allowance +
            input_data.salary_income.special_allowance +
            input_data.salary_income.conveyance_allowance +
            input_data.salary_income.medical_allowance +
            input_data.salary_income.bonus +
            input_data.salary_income.commission +
            input_data.salary_income.overtime +
            input_data.salary_income.arrears +
            input_data.salary_income.gratuity +
            input_data.salary_income.leave_encashment +
            input_data.salary_income.other_allowances
        )
        
        # Calculate taxable income (no deductions in new regime)
        taxable_income = total_income
        
        # Calculate tax using new regime slabs
        return self._calculate_tax_using_slabs(
            taxable_income,
            input_data.age,
            input_data.is_senior_citizen,
            input_data.is_super_senior_citizen,
            is_old_regime=False
        )
    
    def _calculate_tax_using_slabs(
        self,
        taxable_income: Money,
        age: int,
        is_senior_citizen: bool,
        is_super_senior_citizen: bool,
        is_old_regime: bool
    ) -> Money:
        """Calculate tax using tax slabs."""
        # Get appropriate tax slabs
        if is_old_regime:
            slabs = self._get_old_regime_slabs(age, is_senior_citizen, is_super_senior_citizen)
        else:
            slabs = self._get_new_regime_slabs()
        
        # Calculate tax for each slab
        total_tax = Money(0)
        remaining_income = taxable_income
        
        for slab in slabs:
            if remaining_income <= Money(0):
                break
                
            slab_amount = min(remaining_income, Money(slab['amount']))
            tax_for_slab = slab_amount * Decimal(str(slab['rate'])) / Decimal('100')
            total_tax += tax_for_slab
            remaining_income -= slab_amount
        
        return total_tax
    
    def _get_old_regime_slabs(
        self,
        age: int,
        is_senior_citizen: bool,
        is_super_senior_citizen: bool
    ) -> List[Dict[str, Any]]:
        """Get old regime tax slabs."""
        if is_super_senior_citizen:
            return [
                {'amount': 500000, 'rate': 0},
                {'amount': 1000000, 'rate': 20},
                {'amount': float('inf'), 'rate': 30}
            ]
        elif is_senior_citizen:
            return [
                {'amount': 300000, 'rate': 0},
                {'amount': 500000, 'rate': 5},
                {'amount': 1000000, 'rate': 20},
                {'amount': float('inf'), 'rate': 30}
            ]
        else:
            return [
                {'amount': 250000, 'rate': 0},
                {'amount': 500000, 'rate': 5},
                {'amount': 1000000, 'rate': 20},
                {'amount': float('inf'), 'rate': 30}
            ]
    
    def _get_new_regime_slabs(self) -> List[Dict[str, Any]]:
        """Get new regime tax slabs."""
        return [
            {'amount': 300000, 'rate': 0},
            {'amount': 600000, 'rate': 5},
            {'amount': 900000, 'rate': 10},
            {'amount': 1200000, 'rate': 15},
            {'amount': 1500000, 'rate': 20},
            {'amount': float('inf'), 'rate': 30}
        ]
    
    def _get_comparison_breakdown(
        self,
        input_data: RegimeComparisonInput,
        old_regime_tax: Money,
        new_regime_tax: Money
    ) -> Dict[str, Any]:
        """Get detailed comparison breakdown."""
        return {
            'income_breakdown': {
                'salary_income': {
                    'basic_salary': input_data.salary_income.basic_salary,
                    'dearness_allowance': input_data.salary_income.dearness_allowance,
                    'house_rent_allowance': input_data.salary_income.house_rent_allowance,
                    'special_allowance': input_data.salary_income.special_allowance,
                    'other_allowances': input_data.salary_income.other_allowances
                },
                'perquisites': {
                    'rent_free_accommodation': input_data.perquisites.rent_free_accommodation,
                    'car_perquisite': input_data.perquisites.car_perquisite,
                    'other_perquisites': input_data.perquisites.other_perquisites
                },
                'other_income': {
                    'house_property': input_data.house_property_income.municipal_value,
                    'capital_gains': input_data.capital_gains_income.sale_price,
                    'other_sources': input_data.other_income.bank_interest
                }
            },
            'deductions_breakdown': {
                'section_80c': input_data.tax_deductions.section_80c,
                'section_80d': input_data.tax_deductions.section_80d,
                'standard_deduction': input_data.tax_deductions.standard_deduction,
                'hra_exemption': input_data.tax_deductions.hra_exemption,
                'other_deductions': input_data.tax_deductions.other_deductions
            },
            'tax_breakdown': {
                'old_regime': {
                    'total_tax': old_regime_tax,
                    'effective_rate': (old_regime_tax / input_data.salary_income.basic_salary) * Decimal('100')
                },
                'new_regime': {
                    'total_tax': new_regime_tax,
                    'effective_rate': (new_regime_tax / input_data.salary_income.basic_salary) * Decimal('100')
                }
            }
        }
    
    def _get_savings_breakdown(
        self,
        input_data: RegimeComparisonInput,
        old_regime_tax: Money,
        new_regime_tax: Money
    ) -> Dict[str, Any]:
        """Get savings breakdown."""
        tax_difference = old_regime_tax - new_regime_tax
        percentage_difference = (tax_difference / old_regime_tax) * Decimal('100')
        
        return {
            'absolute_savings': tax_difference,
            'percentage_savings': percentage_difference,
            'monthly_savings': tax_difference / Decimal('12'),
            'annual_savings': tax_difference,
            'savings_by_component': {
                'deductions_savings': input_data.tax_deductions.section_80c * Decimal('0.3'),
                'hra_savings': input_data.tax_deductions.hra_exemption * Decimal('0.3'),
                'other_savings': input_data.tax_deductions.other_deductions * Decimal('0.3')
            }
        } 