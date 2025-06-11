"""
Tax Calculation Service
Comprehensive domain service for all Indian taxation components
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Optional

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.salary_income import SalaryIncome
from app.domain.entities.tax_deductions import TaxDeductions
from app.domain.entities.perquisites import Perquisites
from app.domain.entities.other_income import OtherIncome
from app.domain.entities.house_property_income import HousePropertyIncome
from app.domain.entities.capital_gains import CapitalGainsIncome
from app.domain.entities.retirement_benefits import RetirementBenefits


@dataclass
class TaxCalculationInput:
    """Complete tax input including all income sources and deductions."""
    
    # Income sources
    salary_income: Optional[SalaryIncome] = None
    perquisites: Optional[Perquisites] = None
    house_property_income: Optional[HousePropertyIncome] = None
    capital_gains_income: Optional[CapitalGainsIncome] = None
    retirement_benefits: Optional[RetirementBenefits] = None
    other_income: Optional[OtherIncome] = None
    
    # Deductions
    tax_deductions: Optional[TaxDeductions] = None
    
    # Taxpayer details
    age: int = 25
    regime: TaxRegime = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.regime is None:
            self.regime = TaxRegime(TaxRegimeType.OLD)


@dataclass
class TaxCalculationResult:
    """Complete tax calculation result with all income breakdowns."""
    
    # Income breakdown
    total_salary_income: Money
    total_perquisites: Money
    total_house_property_income: Money
    total_capital_gains_income: Money
    total_retirement_benefits: Money
    total_other_income: Money
    gross_total_income: Money
    
    # Separate capital gains tax
    capital_gains_tax: Money
    
    # Exemptions and deductions
    total_exemptions: Money
    total_deductions: Money
    interest_exemptions: Money
    
    # Tax calculation
    taxable_income: Money
    tax_before_rebate: Money
    rebate_87a: Money
    tax_after_rebate: Money
    surcharge: Money
    cess: Money
    total_tax_liability: Money
    comprehensive_tax_liability: Money
    effective_tax_rate: Decimal
    
    # Metadata
    regime_used: TaxRegime
    taxpayer_age: int
    
    # Detailed breakdowns
    income_breakdown: Dict[str, Any]
    exemptions_breakdown: Dict[str, Any]
    deductions_breakdown: Dict[str, Any]
    calculation_breakdown: Dict[str, Any]
    
    # Derived fields
    monthly_tax_liability: Money = None
    
    def __post_init__(self):
        """Calculate derived fields."""
        if self.monthly_tax_liability is None:
            self.monthly_tax_liability = self.comprehensive_tax_liability.divide(12)


@dataclass
class SurchargeBreakdown:
    """Detailed surcharge breakdown."""
    
    applicable: bool
    rate: Decimal
    rate_description: str
    base_amount: Money
    surcharge_amount: Money
    income_slab: str
    marginal_relief_applicable: bool
    marginal_relief_amount: Money
    effective_surcharge: Money


class TaxCalculationService:
    """
    Comprehensive tax calculation service for all Indian taxation components.
    
    Integrates all income sources, perquisites, deductions, and exemptions
    for complete tax calculation and regime comparison.
    """
    
    def calculate_comprehensive_tax(self, tax_input: TaxCalculationInput) -> TaxCalculationResult:
        """
        Calculate comprehensive tax including all income sources and deductions.
        
        Args:
            tax_input: Complete tax input data
            
        Returns:
            TaxCalculationResult: Complete tax calculation result
        """
        
        # Step 1: Calculate income from all sources
        income_breakdown = self._calculate_all_income_sources(tax_input)
        
        # Step 2: Calculate exemptions and deductions
        exemptions_breakdown = self._calculate_all_exemptions(tax_input)
        deductions_breakdown = self._calculate_all_deductions(tax_input)
        
        # Step 3: Calculate interest exemptions separately
        interest_exemptions = self._calculate_interest_exemptions(tax_input)
        
        # Step 4: Calculate final tax
        gross_income = income_breakdown['gross_total_income']
        total_exemptions = exemptions_breakdown['total_exemptions']
        total_deductions = deductions_breakdown['total_deductions']
        
        # Interest exemptions are applied to reduce other income, not as general exemptions
        adjusted_gross_income = gross_income.subtract(interest_exemptions)
        
        # Calculate taxable income
        income_after_exemptions = adjusted_gross_income.subtract(total_exemptions)
        
        # Apply standard deduction
        standard_deduction = tax_input.regime.get_standard_deduction()
        income_after_standard = income_after_exemptions.subtract(standard_deduction)
        
        # Apply other deductions (only in old regime)
        if tax_input.regime.allows_deductions():
            taxable_income = income_after_standard.subtract(total_deductions)
        else:
            taxable_income = income_after_standard
        
        # Ensure taxable income is not negative
        if not taxable_income.is_positive():
            taxable_income = Money.zero()
        
        # Calculate tax on slabs
        tax_before_rebate = self._calculate_slab_tax(taxable_income, tax_input.regime, tax_input.age)
        
        # Calculate rebate under Section 87A
        rebate_87a = self._calculate_rebate_87a(tax_before_rebate, taxable_income, tax_input.regime)
        
        # Tax after rebate
        if tax_before_rebate.is_greater_than(rebate_87a):
            tax_after_rebate = tax_before_rebate.subtract(rebate_87a)
        else:
            tax_after_rebate = Money.zero()
        
        # Calculate surcharge
        surcharge = self._calculate_surcharge(tax_after_rebate, taxable_income)
        
        # Calculate cess (4% on tax + surcharge)
        tax_plus_surcharge = tax_after_rebate.add(surcharge)
        cess = tax_plus_surcharge.percentage(Decimal('4'))
        
        # Total regular tax liability
        total_tax = tax_after_rebate.add(surcharge).add(cess)
        
        # Add capital gains tax
        capital_gains_tax = income_breakdown.get('capital_gains_tax', Money.zero())
        comprehensive_tax_liability = total_tax.add(capital_gains_tax)
        
        # Effective tax rate
        if taxable_income.is_positive():
            effective_rate = (comprehensive_tax_liability.amount / adjusted_gross_income.amount * Decimal('100'))
        else:
            effective_rate = Decimal('0')
        
        # Create detailed breakdown
        calculation_breakdown = self._create_calculation_breakdown(
            adjusted_gross_income, total_exemptions.add(standard_deduction), total_deductions, 
            taxable_income, tax_before_rebate, rebate_87a, tax_after_rebate, 
            surcharge, cess, tax_input.regime, tax_input.age
        )
        
        return TaxCalculationResult(
            total_salary_income=income_breakdown['total_salary'],
            total_perquisites=income_breakdown['total_perquisites'],
            total_house_property_income=income_breakdown['total_house_property'],
            total_capital_gains_income=income_breakdown.get('total_capital_gains_slab', Money.zero()),
            total_retirement_benefits=income_breakdown['total_retirement_benefits'],
            total_other_income=income_breakdown['total_other_income'],
            gross_total_income=adjusted_gross_income,
            capital_gains_tax=capital_gains_tax,
            total_exemptions=total_exemptions.add(standard_deduction),
            total_deductions=total_deductions if tax_input.regime.allows_deductions() else Money.zero(),
            interest_exemptions=interest_exemptions,
            taxable_income=taxable_income,
            tax_before_rebate=tax_before_rebate,
            rebate_87a=rebate_87a,
            tax_after_rebate=tax_after_rebate,
            surcharge=surcharge,
            cess=cess,
            total_tax_liability=total_tax,
            comprehensive_tax_liability=comprehensive_tax_liability,
            effective_tax_rate=effective_rate,
            regime_used=tax_input.regime,
            taxpayer_age=tax_input.age,
            income_breakdown=income_breakdown,
            exemptions_breakdown=exemptions_breakdown,
            deductions_breakdown=deductions_breakdown,
            calculation_breakdown=calculation_breakdown
        )
    
    def calculate_income_tax(self, 
                           gross_income: Money,
                           total_exemptions: Money,
                           total_deductions: Money,
                           regime: TaxRegime,
                           age: int) -> TaxCalculationResult:
        """
        Calculate comprehensive income tax.
        
        Args:
            gross_income: Total gross income
            total_exemptions: Total exemptions (HRA, LTA, etc.)
            total_deductions: Total deductions (80C, 80D, etc.)
            regime: Tax regime (old/new)
            age: Taxpayer's age
            
        Returns:
            TaxCalculationResult: Complete tax calculation result
        """
        
        # Step 1: Calculate taxable income
        income_after_exemptions = gross_income.subtract(total_exemptions)
        
        # Apply standard deduction
        standard_deduction = regime.get_standard_deduction()
        income_after_standard = income_after_exemptions.subtract(standard_deduction)
        
        # Apply other deductions (only in old regime)
        if regime.allows_deductions():
            taxable_income = income_after_standard.subtract(total_deductions)
        else:
            taxable_income = income_after_standard
        
        # Ensure taxable income is not negative
        if not taxable_income.is_positive():
            taxable_income = Money.zero()
        
        # Step 2: Calculate tax on slabs
        tax_on_slabs = self._calculate_slab_tax(taxable_income, regime, age)
        
        # Step 3: Calculate rebate under Section 87A
        rebate_87a = self._calculate_rebate_87a(tax_on_slabs, taxable_income, regime)
        
        # Step 4: Tax after rebate
        if tax_on_slabs.is_greater_than(rebate_87a):
            tax_after_rebate = tax_on_slabs.subtract(rebate_87a)
        else:
            tax_after_rebate = Money.zero()
        
        # Step 5: Calculate surcharge
        surcharge = self._calculate_surcharge(tax_after_rebate, taxable_income)
        
        # Step 6: Calculate cess (4% on tax + surcharge)
        tax_plus_surcharge = tax_after_rebate.add(surcharge)
        cess = tax_plus_surcharge.percentage(Decimal('4'))
        
        # Step 7: Total tax liability
        total_tax = tax_after_rebate.add(surcharge).add(cess)
        
        # Step 8: Effective tax rate
        if taxable_income.is_positive():
            effective_rate = (total_tax.amount / taxable_income.amount * Decimal('100'))
        else:
            effective_rate = Decimal('0')
        
        # Step 9: Create detailed breakdown
        breakdown = self._create_calculation_breakdown(
            gross_income, total_exemptions, total_deductions, taxable_income,
            tax_on_slabs, rebate_87a, tax_after_rebate, surcharge, cess,
            regime, age
        )
        
        return TaxCalculationResult(
            gross_income=gross_income,
            total_exemptions=total_exemptions.add(standard_deduction),
            total_deductions=total_deductions if regime.allows_deductions() else Money.zero(),
            taxable_income=taxable_income,
            tax_before_rebate=tax_on_slabs,
            rebate_87a=rebate_87a,
            tax_after_rebate=tax_after_rebate,
            surcharge=surcharge,
            cess=cess,
            total_tax_liability=total_tax,
            effective_tax_rate=effective_rate,
            regime_used=regime,
            taxpayer_age=age,
            calculation_breakdown=breakdown
        )
    
    def calculate_comprehensive_tax(self,
                                   gross_income: Money,
                                   exemptions: Money,
                                   deductions: Money,
                                   taxable_income: Money,
                                   regime: TaxRegime,
                                   age: int) -> TaxCalculationResult:
        """
        Calculate comprehensive tax with pre-calculated taxable income.
        
        Args:
            gross_income: Total gross income
            exemptions: Total exemptions
            deductions: Total deductions
            taxable_income: Pre-calculated taxable income
            regime: Tax regime
            age: Taxpayer's age
            
        Returns:
            TaxCalculationResult: Complete tax calculation result
        """
        
        # Calculate tax on slabs
        tax_on_slabs = self.calculate_tax_on_slabs(taxable_income, regime, age)
        
        # Calculate rebate under Section 87A
        rebate_87a = self.calculate_rebate_87a(taxable_income, tax_on_slabs, regime)
        
        # Tax after rebate
        tax_after_rebate = tax_on_slabs.subtract(rebate_87a).max(Money.zero())
        
        # Calculate surcharge
        surcharge = self.calculate_surcharge(taxable_income, tax_after_rebate, regime)
        
        # Calculate cess
        cess = self.calculate_cess(tax_after_rebate.add(surcharge))
        
        # Total tax liability
        total_tax = tax_after_rebate.add(surcharge).add(cess)
        
        # Effective tax rate
        effective_rate = Decimal('0')
        if taxable_income.is_positive():
            effective_rate = (total_tax.amount / taxable_income.amount) * Decimal('100')
        
        # Create breakdown
        breakdown = self._create_calculation_breakdown(
            gross_income, exemptions, deductions, taxable_income,
            tax_on_slabs, rebate_87a, tax_after_rebate, surcharge, cess,
            regime, age
        )
        
        return TaxCalculationResult(
            gross_income=gross_income,
            total_exemptions=exemptions,
            total_deductions=deductions,
            taxable_income=taxable_income,
            tax_before_rebate=tax_on_slabs,
            rebate_87a=rebate_87a,
            tax_after_rebate=tax_after_rebate,
            surcharge=surcharge,
            cess=cess,
            total_tax_liability=total_tax,
            effective_tax_rate=effective_rate,
            regime_used=regime,
            taxpayer_age=age,
            calculation_breakdown=breakdown
        )
    
    def calculate_tax_on_slabs(self, taxable_income: Money, regime: TaxRegime, age: int) -> Money:
        """
        Public method to calculate tax based on slabs.
        
        Args:
            taxable_income: Taxable income amount
            regime: Tax regime
            age: Taxpayer's age
            
        Returns:
            Money: Tax amount based on slabs
        """
        return self._calculate_slab_tax(taxable_income, regime, age)
    
    def calculate_rebate_87a(self, taxable_income: Money, tax_amount: Money, regime: TaxRegime) -> Money:
        """
        Public method to calculate rebate under Section 87A.
        
        Args:
            taxable_income: Taxable income
            tax_amount: Calculated tax amount
            regime: Tax regime
            
        Returns:
            Money: Rebate amount
        """
        return self._calculate_rebate_87a(tax_amount, taxable_income, regime)
    
    def calculate_surcharge(self, taxable_income: Money, tax_amount: Money, regime: TaxRegime) -> Money:
        """
        Public method to calculate surcharge.
        
        Args:
            taxable_income: Taxable income
            tax_amount: Tax amount after rebate
            regime: Tax regime
            
        Returns:
            Money: Surcharge amount
        """
        return self._calculate_surcharge(tax_amount, taxable_income)
    
    def calculate_cess(self, tax_plus_surcharge: Money) -> Money:
        """
        Public method to calculate cess.
        
        Args:
            tax_plus_surcharge: Tax amount plus surcharge
            
        Returns:
            Money: Cess amount (4% of tax + surcharge)
        """
        return tax_plus_surcharge.percentage(Decimal('4'))
    
    def _calculate_slab_tax(self, taxable_income: Money, regime: TaxRegime, age: int) -> Money:
        """
        Calculate tax based on income tax slabs.
        
        Args:
            taxable_income: Taxable income amount
            regime: Tax regime
            age: Taxpayer's age
            
        Returns:
            Money: Tax amount based on slabs
        """
        tax_slabs = regime.get_tax_slabs(age)
        total_tax = Money.zero()
        remaining_income = taxable_income.amount
        
        for slab in tax_slabs:
            if remaining_income <= 0:
                break
            
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            # Skip if income is below slab minimum
            if remaining_income <= slab_min:
                continue
            
            # Calculate taxable amount in this slab
            if slab_max is None:
                # Highest slab (no upper limit)
                taxable_in_slab = remaining_income - slab_min
            else:
                # Limited slab
                taxable_in_slab = min(remaining_income, slab_max) - slab_min
            
            if taxable_in_slab > 0:
                slab_tax = Money((taxable_in_slab * slab_rate) / Decimal('100'))
                total_tax = total_tax.add(slab_tax)
        
        return total_tax
    
    def _calculate_rebate_87a(self, tax_amount: Money, taxable_income: Money, regime: TaxRegime) -> Money:
        """
        Calculate rebate under Section 87A.
        
        Args:
            tax_amount: Calculated tax amount
            taxable_income: Taxable income
            regime: Tax regime
            
        Returns:
            Money: Rebate amount
        """
        rebate_limit = regime.get_rebate_87a_limit()
        max_rebate = regime.get_max_rebate_87a()
        
        if taxable_income.is_less_than(rebate_limit) or taxable_income.is_equal_to(rebate_limit):
            return tax_amount.min(max_rebate)
        
        return Money.zero()
    
    def _calculate_surcharge(self, tax_amount: Money, taxable_income: Money) -> Money:
        """
        Calculate surcharge based on income level.
        
        Args:
            tax_amount: Tax amount after rebate
            taxable_income: Taxable income
            
        Returns:
            Money: Surcharge amount
        """
        if not tax_amount.is_positive():
            return Money.zero()
        
        income = taxable_income.amount
        
        # Surcharge slabs (same for both regimes)
        if income <= Decimal('5000000'):  # Up to ₹50 lakh
            return Money.zero()
        elif income <= Decimal('10000000'):  # ₹50 lakh to ₹1 crore
            return tax_amount.percentage(Decimal('10'))
        elif income <= Decimal('20000000'):  # ₹1 crore to ₹2 crore
            return tax_amount.percentage(Decimal('15'))
        elif income <= Decimal('50000000'):  # ₹2 crore to ₹5 crore
            return tax_amount.percentage(Decimal('25'))
        else:  # Above ₹5 crore
            return tax_amount.percentage(Decimal('37'))
    
    def _create_calculation_breakdown(self, 
                                    gross_income: Money,
                                    total_exemptions: Money,
                                    total_deductions: Money,
                                    taxable_income: Money,
                                    tax_on_slabs: Money,
                                    rebate_87a: Money,
                                    tax_after_rebate: Money,
                                    surcharge: Money,
                                    cess: Money,
                                    regime: TaxRegime,
                                    age: int) -> Dict[str, Any]:
        """
        Create detailed calculation breakdown.
        
        Returns:
            Dict: Detailed breakdown of tax calculation
        """
        # Calculate slab-wise breakdown
        slab_breakdown = self._get_slab_wise_breakdown(taxable_income, regime, age)
        
        return {
            "regime_details": {
                "regime_type": regime.regime_type.value,
                "regime_description": regime.get_regime_description(),
                "deductions_allowed": regime.allows_deductions()
            },
            "taxpayer_details": {
                "age": age,
                "age_category": self._get_age_category(age)
            },
            "income_computation": {
                "gross_income": gross_income.to_float(),
                "total_exemptions": total_exemptions.to_float(),
                "income_after_exemptions": gross_income.subtract(total_exemptions).to_float(),
                "total_deductions": total_deductions.to_float() if regime.allows_deductions() else 0.0,
                "taxable_income": taxable_income.to_float()
            },
            "tax_calculation": {
                "tax_slabs_applied": regime.get_tax_slabs(age),
                "slab_wise_tax": slab_breakdown,
                "tax_before_rebate": tax_on_slabs.to_float(),
                "rebate_87a": {
                    "eligible": rebate_87a.is_positive(),
                    "amount": rebate_87a.to_float(),
                    "income_limit": regime.get_rebate_87a_limit().to_float(),
                    "max_rebate": regime.get_max_rebate_87a().to_float()
                },
                "tax_after_rebate": tax_after_rebate.to_float()
            },
            "additional_charges": {
                "surcharge": {
                    "amount": surcharge.to_float(),
                    "applicable": surcharge.is_positive(),
                    "rate": self._get_surcharge_rate(taxable_income)
                },
                "health_education_cess": {
                    "amount": cess.to_float(),
                    "rate": "4%",
                    "base_amount": tax_after_rebate.add(surcharge).to_float()
                }
            },
            "final_computation": {
                "total_tax_liability": tax_after_rebate.add(surcharge).add(cess).to_float(),
                "effective_tax_rate": f"{(tax_after_rebate.add(surcharge).add(cess).amount / taxable_income.amount * Decimal('100')):.2f}%" if taxable_income.is_positive() else "0.00%",
                "monthly_tax_liability": (tax_after_rebate.add(surcharge).add(cess).divide(12)).to_float(),
                "average_tax_rate": f"{(tax_after_rebate.add(surcharge).add(cess).amount / gross_income.amount * Decimal('100')):.2f}%" if gross_income.is_positive() else "0.00%"
            }
        }
    
    def _get_slab_wise_breakdown(self, taxable_income: Money, regime: TaxRegime, age: int) -> List[Dict[str, Any]]:
        """Get detailed slab-wise tax breakdown."""
        tax_slabs = regime.get_tax_slabs(age)
        breakdown = []
        remaining_income = taxable_income.amount
        
        for i, slab in enumerate(tax_slabs):
            if remaining_income <= 0:
                break
            
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            # Skip if income is below slab minimum
            if remaining_income <= slab_min:
                continue
            
            # Calculate taxable amount in this slab
            if slab_max is None:
                taxable_in_slab = remaining_income - slab_min
                slab_description = f"Above ₹{slab_min:,.0f}"
            else:
                taxable_in_slab = min(remaining_income, slab_max) - slab_min
                slab_description = f"₹{slab_min:,.0f} - ₹{slab_max:,.0f}"
            
            if taxable_in_slab > 0:
                slab_tax = (taxable_in_slab * slab_rate) / Decimal('100')
                
                breakdown.append({
                    "slab": i + 1,
                    "income_range": slab_description,
                    "rate": f"{slab_rate}%",
                    "taxable_amount": float(taxable_in_slab),
                    "tax_amount": float(slab_tax)
                })
        
        return breakdown
    
    def _get_age_category(self, age: int) -> str:
        """Get age category for display."""
        if age < 60:
            return "Individual (below 60 years)"
        elif age < 80:
            return "Senior Citizen (60-80 years)"
        else:
            return "Super Senior Citizen (above 80 years)"
    
    def _get_surcharge_rate(self, taxable_income: Money) -> str:
        """Get applicable surcharge rate."""
        income = taxable_income.amount
        
        if income <= Decimal('5000000'):
            return "0%"
        elif income <= Decimal('10000000'):
            return "10%"
        elif income <= Decimal('20000000'):
            return "15%"
        elif income <= Decimal('50000000'):
            return "25%"
        else:
            return "37%"


class RegimeComparisonService:
    """Service to compare tax liability across different regimes."""
    
    def __init__(self, tax_calculation_service: TaxCalculationService):
        self.tax_calculation_service = tax_calculation_service
    
    def compare_regimes(self, 
                       gross_income: Money,
                       total_exemptions: Money,
                       total_deductions: Money,
                       age: int) -> Dict[str, Any]:
        """
        Compare tax liability under both old and new regimes.
        
        Args:
            gross_income: Total gross income
            total_exemptions: Total exemptions
            total_deductions: Total deductions (applicable only in old regime)
            age: Taxpayer's age
            
        Returns:
            Dict: Comprehensive comparison between regimes
        """
        
        # Calculate tax under old regime (with deductions)
        old_regime_result = self.tax_calculation_service.calculate_income_tax(
            gross_income, total_exemptions, total_deductions, TaxRegime.old_regime(), age
        )
        
        # Calculate tax under new regime (without deductions)
        new_regime_result = self.tax_calculation_service.calculate_income_tax(
            gross_income, total_exemptions, Money.zero(), TaxRegime.new_regime(), age
        )
        
        # Determine optimal regime
        recommendation = self._get_regime_recommendation(old_regime_result, new_regime_result)
        
        # Calculate savings analysis
        savings_analysis = self._calculate_savings_analysis(old_regime_result, new_regime_result)
        
        return {
            "comparison_summary": {
                "old_regime": {
                    "total_tax": old_regime_result.total_tax_liability.to_float(),
                    "effective_rate": f"{old_regime_result.effective_tax_rate:.2f}%",
                    "monthly_tax": old_regime_result.monthly_tax_liability.to_float(),
                    "taxable_income": old_regime_result.taxable_income.to_float()
                },
                "new_regime": {
                    "total_tax": new_regime_result.total_tax_liability.to_float(),
                    "effective_rate": f"{new_regime_result.effective_tax_rate:.2f}%",
                    "monthly_tax": new_regime_result.monthly_tax_liability.to_float(),
                    "taxable_income": new_regime_result.taxable_income.to_float()
                }
            },
            "detailed_calculations": {
                "old_regime": old_regime_result.calculation_breakdown,
                "new_regime": new_regime_result.calculation_breakdown
            },
            "recommendation": recommendation,
            "savings_analysis": savings_analysis,
            "key_differences": self._get_key_differences(old_regime_result, new_regime_result, total_deductions)
        }
    
    def _get_regime_recommendation(self, old_result: TaxCalculationResult, 
                                 new_result: TaxCalculationResult) -> Dict[str, Any]:
        """Recommend optimal tax regime."""
        if new_result.total_tax_liability.is_less_than(old_result.total_tax_liability):
            savings = old_result.total_tax_liability.subtract(new_result.total_tax_liability)
            return {
                "recommended_regime": "new",
                "reason": "Lower tax liability in new regime",
                "annual_savings": savings.to_float(),
                "monthly_savings": savings.divide(12).to_float(),
                "percentage_savings": f"{(savings.amount / old_result.total_tax_liability.amount * Decimal('100')):.1f}%"
            }
        elif old_result.total_tax_liability.is_less_than(new_result.total_tax_liability):
            savings = new_result.total_tax_liability.subtract(old_result.total_tax_liability)
            return {
                "recommended_regime": "old",
                "reason": "Lower tax liability in old regime",
                "annual_savings": savings.to_float(),
                "monthly_savings": savings.divide(12).to_float(),
                "percentage_savings": f"{(savings.amount / new_result.total_tax_liability.amount * Decimal('100')):.1f}%"
            }
        else:
            return {
                "recommended_regime": "either",
                "reason": "Both regimes result in same tax liability",
                "annual_savings": 0.0,
                "monthly_savings": 0.0,
                "percentage_savings": "0.0%"
            }
    
    def _calculate_savings_analysis(self, old_result: TaxCalculationResult,
                                  new_result: TaxCalculationResult) -> Dict[str, Any]:
        """Calculate detailed savings analysis."""
        tax_difference = abs(old_result.total_tax_liability.amount - new_result.total_tax_liability.amount)
        
        return {
            "absolute_difference": float(tax_difference),
            "old_regime_tax": old_result.total_tax_liability.to_float(),
            "new_regime_tax": new_result.total_tax_liability.to_float(),
            "difference_percentage": f"{(tax_difference / max(old_result.total_tax_liability.amount, new_result.total_tax_liability.amount) * Decimal('100')):.2f}%",
            "break_even_deductions": self._calculate_break_even_deductions(old_result, new_result)
        }
    
    def _calculate_break_even_deductions(self, old_result: TaxCalculationResult,
                                       new_result: TaxCalculationResult) -> float:
        """Calculate minimum deductions needed for old regime to be beneficial."""
        # Simplified calculation - in practice, this would be more complex
        # due to non-linear tax slabs
        if new_result.total_tax_liability.is_less_than(old_result.total_tax_liability):
            return 0.0  # New regime is already better
        
        # Approximate calculation
        tax_difference = old_result.total_tax_liability.subtract(new_result.total_tax_liability)
        # Assuming 30% tax bracket for simplification
        return tax_difference.divide(0.3).to_float()
    
    def _get_key_differences(self, old_result: TaxCalculationResult,
                           new_result: TaxCalculationResult,
                           total_deductions: Money) -> List[str]:
        """Get key differences between the regimes."""
        differences = []
        
        # Deductions impact
        if total_deductions.is_positive():
            differences.append(f"Old regime utilizes ₹{total_deductions.to_float():,.0f} in deductions")
            differences.append("New regime doesn't allow traditional deductions")
        
        # Tax rates
        differences.append(f"Old regime effective rate: {old_result.effective_tax_rate:.2f}%")
        differences.append(f"New regime effective rate: {new_result.effective_tax_rate:.2f}%")
        
        # Rebate differences
        if old_result.rebate_87a.is_positive() or new_result.rebate_87a.is_positive():
            differences.append(f"Old regime rebate: ₹{old_result.rebate_87a.to_float():,.0f}")
            differences.append(f"New regime rebate: ₹{new_result.rebate_87a.to_float():,.0f}")
        
        return differences
    
    def _calculate_all_income_sources(self, tax_input: TaxCalculationInput) -> Dict[str, Any]:
        """Calculate income from all sources."""
        
        # Salary income
        total_salary = Money.zero()
        salary_breakdown = {}
        if tax_input.salary_income:
            total_salary = tax_input.salary_income.calculate_gross_salary()
            salary_breakdown = tax_input.salary_income.get_salary_breakdown(tax_input.regime)
        
        # Perquisites
        total_perquisites = Money.zero()
        perquisites_breakdown = {}
        if tax_input.perquisites:
            total_perquisites = tax_input.perquisites.calculate_total_perquisites(tax_input.regime)
            perquisites_breakdown = tax_input.perquisites.get_perquisites_breakdown(tax_input.regime)
        
        # House property income
        total_house_property = Money.zero()
        house_property_breakdown = {}
        if tax_input.house_property_income:
            total_house_property = tax_input.house_property_income.calculate_net_income_from_house_property(tax_input.regime)
            house_property_breakdown = tax_input.house_property_income.get_house_property_breakdown(tax_input.regime)
        
        # Capital gains income (only STCG that goes to regular income)
        total_capital_gains_slab = Money.zero()
        capital_gains_breakdown = {}
        capital_gains_tax = Money.zero()
        if tax_input.capital_gains_income:
            total_capital_gains_slab = tax_input.capital_gains_income.calculate_stcg_for_slab_rates()
            capital_gains_tax = tax_input.capital_gains_income.calculate_total_capital_gains_tax()
            capital_gains_breakdown = tax_input.capital_gains_income.get_capital_gains_breakdown(tax_input.regime)
        
        # Retirement benefits
        total_retirement_benefits = Money.zero()
        retirement_benefits_breakdown = {}
        if tax_input.retirement_benefits:
            total_retirement_benefits = tax_input.retirement_benefits.calculate_total_retirement_income(tax_input.regime)
            retirement_benefits_breakdown = tax_input.retirement_benefits.get_retirement_benefits_breakdown(tax_input.regime)
        
        # Other income
        total_other_income = Money.zero()
        other_income_breakdown = {}
        if tax_input.other_income:
            total_other_income = tax_input.other_income.calculate_total_other_income(tax_input.regime)
            other_income_breakdown = tax_input.other_income.get_other_income_breakdown(tax_input.regime)
        
        # Calculate gross total income (for regular tax calculation)
        gross_total = (total_salary
                      .add(total_perquisites)
                      .add(total_house_property)
                      .add(total_capital_gains_slab)  # Only STCG for slab rates
                      .add(total_retirement_benefits)
                      .add(total_other_income))
        
        return {
            "total_salary": total_salary,
            "total_perquisites": total_perquisites,
            "total_house_property": total_house_property,
            "total_capital_gains_slab": total_capital_gains_slab,
            "capital_gains_tax": capital_gains_tax,
            "total_retirement_benefits": total_retirement_benefits,
            "total_other_income": total_other_income,
            "gross_total_income": gross_total,
            "salary_details": salary_breakdown,
            "perquisites_details": perquisites_breakdown,
            "house_property_details": house_property_breakdown,
            "capital_gains_details": capital_gains_breakdown,
            "retirement_benefits_details": retirement_benefits_breakdown,
            "other_income_details": other_income_breakdown
        }
    
    def _calculate_all_exemptions(self, tax_input: TaxCalculationInput) -> Dict[str, Any]:
        """Calculate all exemptions."""
        
        total_exemptions = Money.zero()
        exemptions_details = {}
        
        # Salary exemptions
        if tax_input.salary_income:
            salary_exemptions = tax_input.salary_income.calculate_total_exemptions(tax_input.regime)
            total_exemptions = total_exemptions.add(salary_exemptions)
            exemptions_details["salary_exemptions"] = salary_exemptions.to_float()
        
        return {
            "total_exemptions": total_exemptions,
            "details": exemptions_details
        }
    
    def _calculate_all_deductions(self, tax_input: TaxCalculationInput) -> Dict[str, Any]:
        """Calculate all deductions."""
        
        total_deductions = Money.zero()
        deductions_breakdown = {}
        
        if tax_input.tax_deductions:
            total_deductions = tax_input.tax_deductions.calculate_total_deductions(tax_input.regime)
            deductions_breakdown = tax_input.tax_deductions.get_comprehensive_breakdown(tax_input.regime)
        
        return {
            "total_deductions": total_deductions,
            "breakdown": deductions_breakdown
        }
    
    def _calculate_interest_exemptions(self, tax_input: TaxCalculationInput) -> Money:
        """Calculate interest income exemptions (80TTA/80TTB)."""
        
        interest_exemptions = Money.zero()
        
        if tax_input.tax_deductions and tax_input.tax_deductions.section_80tta_ttb:
            interest_exemptions = tax_input.tax_deductions.calculate_interest_exemptions(tax_input.regime)
        
        return interest_exemptions
    
    def compare_regimes_comprehensive(self, tax_input: TaxCalculationInput) -> Dict[str, Any]:
        """
        Compare tax liability between old and new regimes comprehensively.
        
        Args:
            tax_input: Complete tax input data
            
        Returns:
            Dict: Complete regime comparison analysis
        """
        
        # Calculate for old regime
        old_input = TaxCalculationInput(
            salary_income=tax_input.salary_income,
            perquisites=tax_input.perquisites,
            house_property_income=tax_input.house_property_income,
            capital_gains_income=tax_input.capital_gains_income,
            retirement_benefits=tax_input.retirement_benefits,
            other_income=tax_input.other_income,
            tax_deductions=tax_input.tax_deductions,
            age=tax_input.age,
            regime=TaxRegime(TaxRegimeType.OLD)
        )
        old_result = self.calculate_comprehensive_tax(old_input)
        
        # Calculate for new regime
        new_input = TaxCalculationInput(
            salary_income=tax_input.salary_income,
            perquisites=tax_input.perquisites,
            house_property_income=tax_input.house_property_income,
            capital_gains_income=tax_input.capital_gains_income,
            retirement_benefits=tax_input.retirement_benefits,
            other_income=tax_input.other_income,
            tax_deductions=tax_input.tax_deductions,
            age=tax_input.age,
            regime=TaxRegime(TaxRegimeType.NEW)
        )
        new_result = self.calculate_comprehensive_tax(new_input)
        
        # Calculate comparison metrics
        old_tax = old_result.comprehensive_tax_liability
        new_tax = new_result.comprehensive_tax_liability
        
        # Calculate tax difference safely
        if old_tax.is_greater_than(new_tax):
            tax_difference = old_tax.subtract(new_tax)
            savings_amount = tax_difference
        elif new_tax.is_greater_than(old_tax):
            tax_difference = new_tax.subtract(old_tax)
            savings_amount = tax_difference
        else:
            tax_difference = Money.zero()
            savings_amount = Money.zero()
        
        savings_percentage = self._calculate_savings_percentage(old_result, new_result)
        
        # Determine recommendation
        if old_result.comprehensive_tax_liability.is_less_than(
            new_result.comprehensive_tax_liability
        ):
            recommended_regime = "Old Regime"
            recommendation_reason = "Lower tax liability with deductions and exemptions"
        elif new_result.comprehensive_tax_liability.is_less_than(
            old_result.comprehensive_tax_liability
        ):
            recommended_regime = "New Regime"
            recommendation_reason = "Lower tax liability with simplified structure"
        else:
            recommended_regime = "Either Regime"
            recommendation_reason = "Both regimes result in same tax liability"
        
        return {
            "old_regime": {
                "gross_income": old_result.gross_total_income.to_float(),
                "total_exemptions": old_result.total_exemptions.to_float(),
                "total_deductions": old_result.total_deductions.to_float(),
                "interest_exemptions": old_result.interest_exemptions.to_float(),
                "taxable_income": old_result.taxable_income.to_float(),
                "tax_liability": old_result.comprehensive_tax_liability.to_float(),
                "effective_rate": float(old_result.effective_tax_rate)
            },
            "new_regime": {
                "gross_income": new_result.gross_total_income.to_float(),
                "total_exemptions": new_result.total_exemptions.to_float(),
                "total_deductions": new_result.total_deductions.to_float(),
                "interest_exemptions": new_result.interest_exemptions.to_float(),
                "taxable_income": new_result.taxable_income.to_float(),
                "tax_liability": new_result.comprehensive_tax_liability.to_float(),
                "effective_rate": float(new_result.effective_tax_rate)
            },
            "comparison": {
                "tax_difference": tax_difference.to_float() if old_tax.is_greater_than(new_tax) else -tax_difference.to_float(),
                "savings_amount": savings_amount.to_float(),
                "savings_percentage": float(savings_percentage),
                "recommended_regime": recommended_regime,
                "recommendation_reason": recommendation_reason
            },
            "detailed_analysis": {
                "exemptions_lost_in_new_regime": (
                    old_result.total_exemptions.subtract(new_result.total_exemptions).to_float()
                    if old_result.total_exemptions.is_greater_than(new_result.total_exemptions)
                    else 0.0
                ),
                "deductions_lost_in_new_regime": old_result.total_deductions.to_float(),
                "perquisites_benefit_old_regime": (
                    old_result.total_perquisites.to_float() 
                    if old_result.regime_used.regime_type == TaxRegimeType.OLD 
                    else 0
                ),
                "break_even_deductions": self._calculate_break_even_deductions_comprehensive(old_result, new_result)
            }
        }
    
    def _calculate_savings_percentage(self, old_result: TaxCalculationResult, 
                                    new_result: TaxCalculationResult) -> Decimal:
        """Calculate savings percentage between regimes."""
        
        old_tax = old_result.comprehensive_tax_liability
        new_tax = new_result.comprehensive_tax_liability
        
        if old_tax.is_zero():
            return Decimal('0')
        
        # Calculate difference safely
        if old_tax.is_greater_than(new_tax):
            difference = old_tax.subtract(new_tax)
            percentage = (difference.amount / old_tax.amount) * Decimal('100')
        elif new_tax.is_greater_than(old_tax):
            difference = new_tax.subtract(old_tax)
            percentage = -(difference.amount / old_tax.amount) * Decimal('100')
        else:
            percentage = Decimal('0')
        
        return percentage if percentage.is_finite() else Decimal('0')
    
    def _calculate_break_even_deductions_comprehensive(self, old_result: TaxCalculationResult,
                                                     new_result: TaxCalculationResult) -> float:
        """Calculate break-even deduction amount."""
        
        old_tax = old_result.comprehensive_tax_liability
        new_tax = new_result.comprehensive_tax_liability
        
        # This is the amount of deductions needed in old regime to match new regime tax
        if new_tax.is_greater_than(old_tax):
            tax_difference = new_tax.subtract(old_tax)
            # Assuming 30% tax bracket for approximation
            break_even = tax_difference.amount / Decimal('0.30')
            return float(break_even)
        
        return 0.0
    
    def get_tax_optimization_suggestions(self, tax_input: TaxCalculationInput) -> Dict[str, Any]:
        """
        Get comprehensive tax optimization suggestions.
        
        Args:
            tax_input: Complete tax input data
            
        Returns:
            Dict: Tax optimization suggestions
        """
        
        suggestions = []
        
        # Calculate current tax for both regimes
        old_input = TaxCalculationInput(
            salary_income=tax_input.salary_income,
            perquisites=tax_input.perquisites,
            house_property_income=tax_input.house_property_income,
            capital_gains_income=tax_input.capital_gains_income,
            retirement_benefits=tax_input.retirement_benefits,
            other_income=tax_input.other_income,
            tax_deductions=tax_input.tax_deductions,
            age=tax_input.age,
            regime=TaxRegime(TaxRegimeType.OLD)
        )
        old_result = self.calculate_comprehensive_tax(old_input)
        
        new_input = TaxCalculationInput(
            salary_income=tax_input.salary_income,
            perquisites=tax_input.perquisites,
            house_property_income=tax_input.house_property_income,
            capital_gains_income=tax_input.capital_gains_income,
            retirement_benefits=tax_input.retirement_benefits,
            other_income=tax_input.other_income,
            tax_deductions=tax_input.tax_deductions,
            age=tax_input.age,
            regime=TaxRegime(TaxRegimeType.NEW)
        )
        new_result = self.calculate_comprehensive_tax(new_input)
        
        # Regime selection suggestion
        if old_result.comprehensive_tax_liability.is_less_than(
            new_result.comprehensive_tax_liability
        ):
            suggestions.append({
                "category": "Regime Selection",
                "suggestion": "Choose Old Tax Regime",
                "potential_saving": new_result.comprehensive_tax_liability.subtract(
                    old_result.comprehensive_tax_liability
                ).to_float(),
                "action": "Opt for old regime to maximize deductions and exemptions"
            })
        
        # Deduction optimization suggestions
        if tax_input.tax_deductions:
            deduction_suggestions = tax_input.tax_deductions.get_tax_saving_suggestions(
                tax_input.regime, 
                old_result.gross_total_income
            )
            
            for suggestion in deduction_suggestions.get("suggestions", []):
                suggestions.append({
                    "category": "Deduction Optimization",
                    "suggestion": f"Invest in {suggestion['section']}",
                    "potential_saving": suggestion.get("potential_tax_saving", 0),
                    "action": f"Consider investing remaining ₹{suggestion.get('remaining_limit', 0)}"
                })
        
        # Salary structure optimization
        if tax_input.salary_income:
            salary_warnings = tax_input.salary_income.validate_hra_details()
            for warning_type, message in salary_warnings.items():
                suggestions.append({
                    "category": "Salary Structure",
                    "suggestion": "Optimize HRA structure",
                    "potential_saving": "Variable",
                    "action": message
                })
        
        return {
            "current_tax_liability": {
                "old_regime": old_result.comprehensive_tax_liability.to_float(),
                "new_regime": new_result.comprehensive_tax_liability.to_float()
            },
            "optimization_suggestions": suggestions,
            "overall_recommendation": {
                "regime": "Old Regime" if old_result.comprehensive_tax_liability.is_less_than(
                    new_result.comprehensive_tax_liability
                ) else "New Regime",
                "reason": "Based on current income and deduction profile"
            }
        } 