"""
Tax Calculator Domain Service
Implements tax calculation strategies for different regimes
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from decimal import Decimal

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, RegimeType
from app.domain.value_objects.employee_id import EmployeeId


class TaxCalculator(ABC):
    """
    Abstract tax calculator following Strategy pattern.
    
    Follows SOLID principles:
    - SRP: Only handles tax calculation logic
    - OCP: Can be extended with new calculation strategies
    - LSP: All implementations can be substituted
    - ISP: Provides focused tax calculation interface
    - DIP: Depends on abstractions (value objects)
    """
    
    @abstractmethod
    def calculate_income_tax(
        self, 
        taxable_income: Money, 
        regime: TaxRegime,
        employee_age: Optional[int] = None
    ) -> Money:
        """Calculate income tax based on taxable income and regime"""
        pass
    
    @abstractmethod
    def calculate_surcharge(
        self, 
        income_tax: Money, 
        taxable_income: Money, 
        regime: TaxRegime
    ) -> Money:
        """Calculate surcharge on income tax"""
        pass
    
    @abstractmethod
    def calculate_cess(
        self, 
        tax_plus_surcharge: Money, 
        regime: TaxRegime
    ) -> Money:
        """Calculate health and education cess"""
        pass
    
    @abstractmethod
    def calculate_rebate_87a(
        self, 
        income_tax: Money, 
        taxable_income: Money, 
        regime: TaxRegime
    ) -> Money:
        """Calculate rebate under section 87A"""
        pass


class IndianTaxCalculator(TaxCalculator):
    """
    Indian tax calculator implementation.
    
    Implements Indian Income Tax Act provisions for both old and new regimes.
    """
    
    def calculate_income_tax(
        self, 
        taxable_income: Money, 
        regime: TaxRegime,
        employee_age: Optional[int] = None
    ) -> Money:
        """Calculate income tax based on Indian tax slabs"""
        
        if not taxable_income.is_positive():
            return Money.zero()
        
        # Get exemption limit based on age and regime
        exemption_limit = self._get_exemption_limit(regime, employee_age)
        
        # If income is below exemption limit, no tax
        if taxable_income.amount <= exemption_limit.amount:
            return Money.zero()
        
        # Calculate tax using slabs
        tax_slabs = regime.get_tax_slabs()
        return self._calculate_slab_wise_tax(taxable_income, tax_slabs)
    
    def calculate_surcharge(
        self, 
        income_tax: Money, 
        taxable_income: Money, 
        regime: TaxRegime
    ) -> Money:
        """Calculate surcharge based on income levels"""
        
        if not income_tax.is_positive():
            return Money.zero()
        
        surcharge_slabs = regime.get_surcharge_slabs()
        income_amount = taxable_income.amount
        
        for slab in surcharge_slabs:
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            if slab_max is None:
                # Last slab (no upper limit)
                if income_amount > slab_min:
                    return income_tax.multiply(slab_rate / 100)
            else:
                if slab_min < income_amount <= slab_max:
                    return income_tax.multiply(slab_rate / 100)
        
        return Money.zero()
    
    def calculate_cess(
        self, 
        tax_plus_surcharge: Money, 
        regime: TaxRegime
    ) -> Money:
        """Calculate health and education cess (4% on tax + surcharge)"""
        
        if not tax_plus_surcharge.is_positive():
            return Money.zero()
        
        cess_rate = regime.get_cess_rate()
        return tax_plus_surcharge.multiply(cess_rate / 100)
    
    def calculate_rebate_87a(
        self, 
        income_tax: Money, 
        taxable_income: Money, 
        regime: TaxRegime
    ) -> Money:
        """Calculate rebate under section 87A"""
        
        if not regime.supports_rebate_87a() or not income_tax.is_positive():
            return Money.zero()
        
        rebate_limit = Money.from_float(regime.get_rebate_87a_limit())
        rebate_amount = Money.from_float(regime.get_rebate_87a_amount())
        
        # Rebate is available only if taxable income is within limit
        if taxable_income.amount <= rebate_limit.amount:
            # Rebate is minimum of income tax and maximum rebate amount
            return income_tax.min(rebate_amount)
        
        return Money.zero()
    
    def calculate_total_tax_liability(
        self,
        taxable_income: Money,
        regime: TaxRegime,
        employee_age: Optional[int] = None
    ) -> Dict[str, Money]:
        """
        Calculate complete tax liability breakdown.
        
        Returns:
            Dictionary with tax components: income_tax, surcharge, cess, rebate, total
        """
        
        # Calculate income tax
        income_tax = self.calculate_income_tax(taxable_income, regime, employee_age)
        
        # Calculate surcharge
        surcharge = self.calculate_surcharge(income_tax, taxable_income, regime)
        
        # Calculate cess on (tax + surcharge)
        tax_plus_surcharge = income_tax.add(surcharge)
        cess = self.calculate_cess(tax_plus_surcharge, regime)
        
        # Calculate rebate
        rebate = self.calculate_rebate_87a(income_tax, taxable_income, regime)
        
        # Calculate total liability
        total_before_rebate = income_tax.add(surcharge).add(cess)
        total_liability = total_before_rebate.subtract(rebate)
        
        return {
            'income_tax': income_tax,
            'surcharge': surcharge,
            'cess': cess,
            'rebate_87a': rebate,
            'total_liability': total_liability
        }
    
    def _get_exemption_limit(self, regime: TaxRegime, employee_age: Optional[int]) -> Money:
        """Get exemption limit based on regime and age"""
        
        if employee_age is None:
            return Money.from_float(regime.get_basic_exemption_limit())
        
        if employee_age >= 80:
            return Money.from_float(regime.get_super_senior_citizen_exemption_limit())
        elif employee_age >= 60:
            return Money.from_float(regime.get_senior_citizen_exemption_limit())
        else:
            return Money.from_float(regime.get_basic_exemption_limit())
    
    def _calculate_slab_wise_tax(self, taxable_income: Money, tax_slabs: List[Dict]) -> Money:
        """Calculate tax using slab-wise rates"""
        
        total_tax = Money.zero()
        remaining_income = taxable_income.amount
        
        for slab in tax_slabs:
            if remaining_income <= 0:
                break
            
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            # Skip if income is below this slab
            if remaining_income <= slab_min:
                continue
            
            # Calculate taxable amount in this slab
            if slab_max is None:
                # Last slab (no upper limit)
                taxable_in_slab = remaining_income - slab_min
            else:
                taxable_in_slab = min(remaining_income, slab_max) - slab_min
            
            # Calculate tax for this slab
            if taxable_in_slab > 0:
                slab_tax = Money(taxable_in_slab * (slab_rate / 100))
                total_tax = total_tax.add(slab_tax)
        
        return total_tax


class TaxCalculatorFactory:
    """
    Factory for creating tax calculator instances.
    
    Follows SOLID principles:
    - SRP: Only responsible for creating tax calculators
    - OCP: Can be extended with new calculator types
    - DIP: Returns abstractions, not concrete implementations
    """
    
    def __init__(self):
        self._calculators = {
            'indian': IndianTaxCalculator()
        }
    
    def create_calculator(self, country: str = 'indian') -> TaxCalculator:
        """Create tax calculator for specified country"""
        
        calculator = self._calculators.get(country.lower())
        if not calculator:
            raise ValueError(f"Tax calculator not available for country: {country}")
        
        return calculator
    
    def get_available_calculators(self) -> List[str]:
        """Get list of available calculator types"""
        return list(self._calculators.keys())


class TaxOptimizationService:
    """
    Domain service for tax optimization recommendations.
    
    Provides suggestions for minimizing tax liability through legal means.
    """
    
    def __init__(self, tax_calculator: TaxCalculator):
        self.tax_calculator = tax_calculator
    
    def suggest_optimizations(
        self,
        current_income: Money,
        current_deductions: Dict[str, Money],
        regime: TaxRegime,
        employee_age: Optional[int] = None
    ) -> List[Dict]:
        """
        Suggest tax optimization strategies.
        
        Returns list of optimization suggestions with potential savings.
        """
        
        suggestions = []
        
        # Calculate current tax liability
        current_taxable = self._calculate_taxable_income(current_income, current_deductions, regime)
        current_tax = self.tax_calculator.calculate_total_tax_liability(
            current_taxable, regime, employee_age
        )
        
        # Suggest Section 80C optimizations
        if regime.allows_section_80c():
            section_80c_suggestion = self._suggest_section_80c_optimization(
                current_income, current_deductions, regime, employee_age
            )
            if section_80c_suggestion:
                suggestions.append(section_80c_suggestion)
        
        # Suggest Section 80D optimizations
        if regime.allows_section_80d():
            section_80d_suggestion = self._suggest_section_80d_optimization(
                current_income, current_deductions, regime, employee_age
            )
            if section_80d_suggestion:
                suggestions.append(section_80d_suggestion)
        
        # Suggest regime comparison
        regime_comparison = self._suggest_regime_comparison(
            current_income, current_deductions, employee_age
        )
        if regime_comparison:
            suggestions.append(regime_comparison)
        
        return suggestions
    
    def compare_regimes(
        self,
        income: Money,
        deductions: Dict[str, Money],
        employee_age: Optional[int] = None
    ) -> Dict[str, Dict]:
        """Compare tax liability under both regimes"""
        
        old_regime = TaxRegime.old_regime()
        new_regime = TaxRegime.new_regime()
        
        # Calculate for old regime (with deductions)
        old_taxable = self._calculate_taxable_income(income, deductions, old_regime)
        old_tax = self.tax_calculator.calculate_total_tax_liability(
            old_taxable, old_regime, employee_age
        )
        
        # Calculate for new regime (without most deductions)
        new_taxable = self._calculate_taxable_income(income, {}, new_regime)
        new_tax = self.tax_calculator.calculate_total_tax_liability(
            new_taxable, new_regime, employee_age
        )
        
        return {
            'old_regime': {
                'taxable_income': old_taxable,
                'tax_breakdown': old_tax,
                'regime': old_regime
            },
            'new_regime': {
                'taxable_income': new_taxable,
                'tax_breakdown': new_tax,
                'regime': new_regime
            },
            'recommendation': self._get_regime_recommendation(old_tax, new_tax)
        }
    
    def _calculate_taxable_income(
        self, 
        income: Money, 
        deductions: Dict[str, Money], 
        regime: TaxRegime
    ) -> Money:
        """Calculate taxable income after applying deductions"""
        
        taxable = income
        
        # Apply standard deduction
        standard_deduction = Money.from_float(regime.get_standard_deduction_limit())
        taxable = taxable.subtract(standard_deduction)
        
        # Apply other deductions if allowed by regime
        if regime.allows_deductions():
            for section, amount in deductions.items():
                if section in regime.get_allowed_deduction_sections():
                    taxable = taxable.subtract(amount)
        
        return taxable
    
    def _suggest_section_80c_optimization(
        self,
        income: Money,
        current_deductions: Dict[str, Money],
        regime: TaxRegime,
        employee_age: Optional[int]
    ) -> Optional[Dict]:
        """Suggest Section 80C optimization"""
        
        current_80c = current_deductions.get('80C', Money.zero())
        max_80c = Money.from_float(150000)  # Rs. 1.5 lakhs limit
        
        if current_80c.amount < max_80c.amount:
            additional_investment = max_80c.subtract(current_80c)
            
            # Calculate tax savings
            tax_rate = self._estimate_marginal_tax_rate(income, regime, employee_age)
            potential_savings = additional_investment.multiply(Decimal(str(tax_rate / 100)))
            
            return {
                'section': '80C',
                'current_investment': current_80c,
                'recommended_additional': additional_investment,
                'potential_savings': potential_savings,
                'suggestion': f"Invest additional {additional_investment.format()} in 80C instruments to save {potential_savings.format()} in taxes"
            }
        
        return None
    
    def _suggest_section_80d_optimization(
        self,
        income: Money,
        current_deductions: Dict[str, Money],
        regime: TaxRegime,
        employee_age: Optional[int]
    ) -> Optional[Dict]:
        """Suggest Section 80D optimization"""
        
        current_80d = current_deductions.get('80D', Money.zero())
        
        # Determine 80D limit based on age
        if employee_age and employee_age >= 60:
            max_80d = Money.from_float(50000)  # Rs. 50,000 for senior citizens
        else:
            max_80d = Money.from_float(25000)  # Rs. 25,000 for others
        
        if current_80d.amount < max_80d.amount:
            additional_premium = max_80d.subtract(current_80d)
            
            # Calculate tax savings
            tax_rate = self._estimate_marginal_tax_rate(income, regime, employee_age)
            potential_savings = additional_premium.multiply(Decimal(str(tax_rate / 100)))
            
            return {
                'section': '80D',
                'current_premium': current_80d,
                'recommended_additional': additional_premium,
                'potential_savings': potential_savings,
                'suggestion': f"Increase health insurance premium by {additional_premium.format()} to save {potential_savings.format()} in taxes"
            }
        
        return None
    
    def _suggest_regime_comparison(
        self,
        income: Money,
        deductions: Dict[str, Money],
        employee_age: Optional[int]
    ) -> Optional[Dict]:
        """Suggest regime comparison if beneficial"""
        
        comparison = self.compare_regimes(income, deductions, employee_age)
        
        old_total = comparison['old_regime']['tax_breakdown']['total_liability']
        new_total = comparison['new_regime']['tax_breakdown']['total_liability']
        
        if old_total.amount != new_total.amount:
            savings = old_total.subtract(new_total) if old_total.amount > new_total.amount else new_total.subtract(old_total)
            better_regime = 'new_regime' if new_total.amount < old_total.amount else 'old_regime'
            
            return {
                'type': 'regime_comparison',
                'current_regime_tax': old_total,
                'alternative_regime_tax': new_total,
                'potential_savings': savings,
                'recommended_regime': better_regime,
                'suggestion': f"Consider switching to {better_regime.replace('_', ' ')} to save {savings.format()}"
            }
        
        return None
    
    def _estimate_marginal_tax_rate(
        self, 
        income: Money, 
        regime: TaxRegime, 
        employee_age: Optional[int]
    ) -> float:
        """Estimate marginal tax rate for the income level"""
        
        tax_slabs = regime.get_tax_slabs()
        income_amount = income.amount
        
        # Find the applicable tax slab
        for slab in tax_slabs:
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            if slab_max is None:
                # Last slab
                if income_amount > slab_min:
                    return float(slab_rate)
            else:
                if slab_min < income_amount <= slab_max:
                    return float(slab_rate)
        
        return 0.0
    
    def _get_regime_recommendation(
        self, 
        old_regime_tax: Dict[str, Money], 
        new_regime_tax: Dict[str, Money]
    ) -> str:
        """Get regime recommendation based on tax comparison"""
        
        old_total = old_regime_tax['total_liability']
        new_total = new_regime_tax['total_liability']
        
        if old_total.amount < new_total.amount:
            savings = new_total.subtract(old_total)
            return f"Old regime is better by {savings.format()}"
        elif new_total.amount < old_total.amount:
            savings = old_total.subtract(new_total)
            return f"New regime is better by {savings.format()}"
        else:
            return "Both regimes result in same tax liability" 