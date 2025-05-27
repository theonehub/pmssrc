"""
Tax Calculation Strategies - Strategy Pattern Implementation
Modular, reusable tax calculation strategies for different regimes and scenarios
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import date, datetime
import logging

from models.taxation.legacy_taxation_model import Taxation
from domain.entities.taxation_models.salary_components import SalaryComponents
from domain.entities.taxation_models.income_sources import IncomeFromOtherSources
from domain.entities.taxation_models.deductions import DeductionComponents
from domain.entities.salary_management import SalaryProjection, LWPAdjustment

logger = logging.getLogger(__name__)


@dataclass
class TaxSlab:
    """Tax slab definition"""
    min_income: float
    max_income: float
    rate: float
    description: str = ""
    
    def is_applicable(self, income: float) -> bool:
        """Check if income falls in this slab"""
        return self.min_income <= income <= self.max_income
    
    def calculate_tax(self, income: float) -> float:
        """Calculate tax for this slab"""
        if not self.is_applicable(income):
            return 0.0
        
        taxable_in_slab = min(self.max_income, income) - self.min_income
        return taxable_in_slab * self.rate


@dataclass
class TaxCalculationContext:
    """Context for tax calculation containing all required data"""
    employee_id: str
    tax_year: str
    calculation_date: datetime
    regime: str
    age: int
    is_govt_employee: bool
    
    # Income components
    salary_projection: Optional[SalaryProjection] = None
    lwp_adjustment: Optional[Dict[str, Any]] = None
    other_sources: Optional[IncomeFromOtherSources] = None
    house_property_income: float = 0.0
    capital_gains: Dict[str, float] = None
    leave_encashment_income: float = 0.0
    pension_income: float = 0.0
    gratuity_income: float = 0.0
    
    # Deductions
    deductions: Optional[DeductionComponents] = None
    standard_deduction: float = 0.0
    
    # Previous tax information
    previous_tax_paid: float = 0.0
    tds_deducted: float = 0.0
    
    def __post_init__(self):
        if self.capital_gains is None:
            self.capital_gains = {
                "stcg_111a": 0.0,
                "stcg_other": 0.0,
                "ltcg_112a": 0.0,
                "ltcg_other": 0.0
            }


@dataclass
class TaxCalculationResult:
    """Result of tax calculation"""
    employee_id: str
    regime: str
    gross_income: float
    taxable_income: float
    total_deductions: float
    tax_before_rebate: float
    rebate_87a: float
    tax_after_rebate: float
    surcharge: float
    cess: float
    total_tax: float
    effective_tax_rate: float
    marginal_tax_rate: float
    
    # Detailed breakdown
    income_breakdown: Dict[str, float]
    deduction_breakdown: Dict[str, float]
    tax_slab_breakdown: List[Dict[str, Any]]
    
    calculation_date: datetime
    calculation_method: str = "strategy_pattern"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "regime": self.regime,
            "gross_income": self.gross_income,
            "taxable_income": self.taxable_income,
            "total_deductions": self.total_deductions,
            "tax_before_rebate": self.tax_before_rebate,
            "rebate_87a": self.rebate_87a,
            "tax_after_rebate": self.tax_after_rebate,
            "surcharge": self.surcharge,
            "cess": self.cess,
            "total_tax": self.total_tax,
            "effective_tax_rate": self.effective_tax_rate,
            "marginal_tax_rate": self.marginal_tax_rate,
            "income_breakdown": self.income_breakdown,
            "deduction_breakdown": self.deduction_breakdown,
            "tax_slab_breakdown": self.tax_slab_breakdown,
            "calculation_date": self.calculation_date.isoformat(),
            "calculation_method": self.calculation_method
        }


class TaxCalculationStrategy(ABC):
    """Abstract base class for tax calculation strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"TaxStrategy.{name}")
    
    @abstractmethod
    def get_tax_slabs(self, age: int) -> List[TaxSlab]:
        """Get tax slabs for the regime"""
        pass
    
    @abstractmethod
    def calculate_standard_deduction(self, gross_salary: float) -> float:
        """Calculate standard deduction"""
        pass
    
    @abstractmethod
    def apply_deductions(self, context: TaxCalculationContext) -> float:
        """Apply deductions and return total deduction amount"""
        pass
    
    @abstractmethod
    def calculate_rebate_87a(self, tax: float, income: float) -> float:
        """Calculate Section 87A rebate"""
        pass
    
    def calculate_income_tax(self, taxable_income: float, age: int) -> Dict[str, Any]:
        """Calculate income tax using tax slabs"""
        slabs = self.get_tax_slabs(age)
        total_tax = 0.0
        slab_breakdown = []
        
        for slab in slabs:
            if taxable_income > slab.min_income:
                taxable_in_slab = min(slab.max_income, taxable_income) - slab.min_income
                if taxable_in_slab > 0:
                    tax_in_slab = taxable_in_slab * slab.rate
                    total_tax += tax_in_slab
                    
                    slab_breakdown.append({
                        "slab_range": f"{slab.min_income:,.0f} - {slab.max_income:,.0f}",
                        "rate": f"{slab.rate * 100:.1f}%",
                        "taxable_amount": taxable_in_slab,
                        "tax_amount": tax_in_slab
                    })
        
        return {
            "total_tax": total_tax,
            "slab_breakdown": slab_breakdown
        }
    
    def calculate_surcharge(self, base_tax: float, net_income: float) -> float:
        """Calculate surcharge with marginal relief"""
        if net_income <= 5000000:  # 50 lakh
            return 0.0
        elif net_income <= 10000000:  # 1 crore
            surcharge_rate = 0.10
        elif net_income <= 20000000:  # 2 crore
            surcharge_rate = 0.15
        elif net_income <= 50000000:  # 5 crore
            surcharge_rate = 0.25
        else:
            surcharge_rate = 0.37
        
        # Calculate surcharge
        surcharge = base_tax * surcharge_rate
        
        # Apply marginal relief
        if net_income > 5000000:
            threshold = 5000000 if net_income <= 10000000 else (
                10000000 if net_income <= 20000000 else (
                    20000000 if net_income <= 50000000 else 50000000
                )
            )
            income_above_threshold = net_income - threshold
            relief = max(0, surcharge - income_above_threshold)
            surcharge = max(0, surcharge - relief)
        
        return surcharge
    
    def calculate_cess(self, tax_with_surcharge: float) -> float:
        """Calculate Health and Education Cess (4%)"""
        return tax_with_surcharge * 0.04
    
    def calculate(self, context: TaxCalculationContext) -> TaxCalculationResult:
        """Main calculation method - template method pattern"""
        self.logger.info(f"Starting tax calculation for {context.employee_id} using {self.name}")
        
        # 1. Calculate gross income
        gross_income = self._calculate_gross_income(context)
        
        # 2. Apply standard deduction
        standard_deduction = self.calculate_standard_deduction(
            context.salary_projection.projected_annual_gross if context.salary_projection else 0.0
        )
        
        # 3. Apply other deductions
        total_deductions = self.apply_deductions(context) + standard_deduction
        
        # 4. Calculate taxable income
        taxable_income = max(0, gross_income - total_deductions)
        
        # 5. Calculate income tax
        tax_result = self.calculate_income_tax(taxable_income, context.age)
        tax_before_rebate = tax_result["total_tax"]
        
        # 6. Apply rebate
        rebate_87a = self.calculate_rebate_87a(tax_before_rebate, taxable_income)
        tax_after_rebate = max(0, tax_before_rebate - rebate_87a)
        
        # 7. Calculate surcharge
        surcharge = self.calculate_surcharge(tax_after_rebate, taxable_income)
        
        # 8. Calculate cess
        cess = self.calculate_cess(tax_after_rebate + surcharge)
        
        # 9. Calculate total tax
        total_tax = tax_after_rebate + surcharge + cess
        
        # 10. Calculate rates
        effective_tax_rate = (total_tax / gross_income * 100) if gross_income > 0 else 0
        marginal_tax_rate = self._calculate_marginal_rate(taxable_income, context.age)
        
        # 11. Prepare breakdown
        income_breakdown = self._prepare_income_breakdown(context, gross_income)
        deduction_breakdown = self._prepare_deduction_breakdown(context, total_deductions, standard_deduction)
        
        result = TaxCalculationResult(
            employee_id=context.employee_id,
            regime=context.regime,
            gross_income=gross_income,
            taxable_income=taxable_income,
            total_deductions=total_deductions,
            tax_before_rebate=tax_before_rebate,
            rebate_87a=rebate_87a,
            tax_after_rebate=tax_after_rebate,
            surcharge=surcharge,
            cess=cess,
            total_tax=total_tax,
            effective_tax_rate=effective_tax_rate,
            marginal_tax_rate=marginal_tax_rate,
            income_breakdown=income_breakdown,
            deduction_breakdown=deduction_breakdown,
            tax_slab_breakdown=tax_result["slab_breakdown"],
            calculation_date=datetime.now()
        )
        
        self.logger.info(f"Tax calculation completed for {context.employee_id}: Total tax = {total_tax}")
        return result
    
    def _calculate_gross_income(self, context: TaxCalculationContext) -> float:
        """Calculate total gross income from all sources"""
        gross_income = 0.0
        
        # Salary income (with LWP adjustment)
        if context.salary_projection:
            gross_income += context.salary_projection.projected_annual_gross
        
        # Other income sources
        if context.other_sources:
            gross_income += context.other_sources.total_taxable_income_per_slab(context.regime, context.age)
        
        # House property income
        gross_income += context.house_property_income
        
        # Capital gains (only STCG at slab rates)
        gross_income += context.capital_gains.get("stcg_other", 0.0)
        
        # Other income
        gross_income += context.leave_encashment_income
        gross_income += context.pension_income
        gross_income += context.gratuity_income
        
        return gross_income
    
    def _calculate_marginal_rate(self, taxable_income: float, age: int) -> float:
        """Calculate marginal tax rate"""
        slabs = self.get_tax_slabs(age)
        
        for slab in reversed(slabs):
            if taxable_income > slab.min_income:
                return slab.rate * 100
        
        return 0.0
    
    def _prepare_income_breakdown(self, context: TaxCalculationContext, gross_income: float) -> Dict[str, float]:
        """Prepare detailed income breakdown"""
        breakdown = {}
        
        if context.salary_projection:
            breakdown["salary"] = context.salary_projection.projected_annual_gross
        
        if context.other_sources:
            breakdown["other_sources"] = context.other_sources.total_taxable_income_per_slab(context.regime, context.age)
        
        if context.house_property_income > 0:
            breakdown["house_property"] = context.house_property_income
        
        if context.capital_gains.get("stcg_other", 0) > 0:
            breakdown["stcg_slab_rate"] = context.capital_gains["stcg_other"]
        
        if context.leave_encashment_income > 0:
            breakdown["leave_encashment"] = context.leave_encashment_income
        
        if context.pension_income > 0:
            breakdown["pension"] = context.pension_income
        
        if context.gratuity_income > 0:
            breakdown["gratuity"] = context.gratuity_income
        
        return breakdown
    
    def _prepare_deduction_breakdown(self, context: TaxCalculationContext, 
                                   total_deductions: float, standard_deduction: float) -> Dict[str, float]:
        """Prepare detailed deduction breakdown"""
        breakdown = {"standard_deduction": standard_deduction}
        
        if context.deductions and context.regime == "old":
            # Add specific deduction breakdowns
            breakdown.update({
                "section_80c": context.deductions.total_80c_deduction(),
                "section_80d": context.deductions.total_80d_deduction(context.age),
                "section_80g": context.deductions.total_80g_deduction(),
                "other_deductions": context.deductions.total_other_deductions(context.age)
            })
        
        return breakdown


class OldRegimeTaxStrategy(TaxCalculationStrategy):
    """Tax calculation strategy for old regime"""
    
    def __init__(self):
        super().__init__("OldRegime")
    
    def get_tax_slabs(self, age: int) -> List[TaxSlab]:
        """Get old regime tax slabs based on age"""
        if age >= 80:  # Super Senior Citizens
            basic_exemption = 500000
        elif age >= 60:  # Senior Citizens
            basic_exemption = 300000
        else:
            basic_exemption = 250000
        
        slabs = [
            TaxSlab(0, basic_exemption, 0.0, "Basic Exemption"),
            TaxSlab(basic_exemption, 500000, 0.05, "5% Slab"),
            TaxSlab(500000, 1000000, 0.20, "20% Slab"),
            TaxSlab(1000000, float('inf'), 0.30, "30% Slab")
        ]
        
        # Remove overlapping slabs for senior citizens
        if basic_exemption >= 500000:
            slabs = [s for s in slabs if not (s.min_income == 250000 and s.max_income == 500000)]
        
        return slabs
    
    def calculate_standard_deduction(self, gross_salary: float) -> float:
        """Old regime standard deduction: Rs. 50,000"""
        return min(50000, gross_salary) if gross_salary > 0 else 0
    
    def apply_deductions(self, context: TaxCalculationContext) -> float:
        """Apply all deductions available in old regime"""
        if not context.deductions:
            return 0.0
        
        return context.deductions.total_deduction_per_slab(
            salary=context.salary_projection,
            income_from_other_sources=context.other_sources,
            regime=context.regime,
            is_govt_employee=context.is_govt_employee,
            age=context.age,
            parent_age=context.age  # Assuming same age if not provided
        )
    
    def calculate_rebate_87a(self, tax: float, income: float) -> float:
        """Old regime rebate: Rs. 12,500 for income up to Rs. 5 lakh"""
        if income <= 500000:
            return min(12500, tax)
        return 0.0


class NewRegimeTaxStrategy(TaxCalculationStrategy):
    """Tax calculation strategy for new regime"""
    
    def __init__(self):
        super().__init__("NewRegime")
    
    def get_tax_slabs(self, age: int) -> List[TaxSlab]:
        """Get new regime tax slabs (Budget 2025 rates)"""
        return [
            TaxSlab(0, 400000, 0.0, "Basic Exemption"),
            TaxSlab(400000, 800000, 0.05, "5% Slab"),
            TaxSlab(800000, 1200000, 0.10, "10% Slab"),
            TaxSlab(1200000, 1600000, 0.15, "15% Slab"),
            TaxSlab(1600000, 2000000, 0.20, "20% Slab"),
            TaxSlab(2000000, 2400000, 0.25, "25% Slab"),
            TaxSlab(2400000, float('inf'), 0.30, "30% Slab")
        ]
    
    def calculate_standard_deduction(self, gross_salary: float) -> float:
        """New regime standard deduction: Rs. 75,000"""
        return min(75000, gross_salary) if gross_salary > 0 else 0
    
    def apply_deductions(self, context: TaxCalculationContext) -> float:
        """New regime has limited deductions"""
        # Only specific deductions allowed in new regime
        total_deductions = 0.0
        
        if context.deductions:
            # Only employer NPS contribution (80CCD(2)) allowed
            total_deductions += context.deductions.section_80ccd_2_enps
        
        return total_deductions
    
    def calculate_rebate_87a(self, tax: float, income: float) -> float:
        """New regime rebate: Rs. 60,000 for income up to Rs. 12 lakh (Budget 2025)"""
        if income <= 1200000:
            return min(60000, tax)
        return 0.0


class SeniorCitizenTaxStrategy(OldRegimeTaxStrategy):
    """Specialized strategy for senior citizens (60-80 years)"""
    
    def __init__(self):
        super().__init__()
        self.name = "SeniorCitizenOldRegime"
    
    def apply_deductions(self, context: TaxCalculationContext) -> float:
        """Enhanced deductions for senior citizens"""
        base_deductions = super().apply_deductions(context)
        
        # Additional benefits for senior citizens
        if context.deductions:
            # Higher medical insurance deduction limit
            additional_medical = min(25000, context.deductions.section_80d_hi_parent)
            base_deductions += additional_medical
        
        return base_deductions


class SuperSeniorCitizenTaxStrategy(OldRegimeTaxStrategy):
    """Specialized strategy for super senior citizens (80+ years)"""
    
    def __init__(self):
        super().__init__()
        self.name = "SuperSeniorCitizenOldRegime"
    
    def apply_deductions(self, context: TaxCalculationContext) -> float:
        """Enhanced deductions for super senior citizens"""
        base_deductions = super().apply_deductions(context)
        
        # Additional benefits for super senior citizens
        if context.deductions:
            # Even higher medical insurance deduction
            additional_medical = min(50000, context.deductions.section_80d_hi_parent)
            base_deductions += additional_medical
        
        return base_deductions


class TaxStrategyFactory:
    """Factory for creating appropriate tax calculation strategies"""
    
    @staticmethod
    def get_strategy(context: TaxCalculationContext) -> TaxCalculationStrategy:
        """Get appropriate strategy based on context"""
        
        if context.regime == "new":
            return NewRegimeTaxStrategy()
        else:  # old regime
            if context.age >= 80:
                return SuperSeniorCitizenTaxStrategy()
            elif context.age >= 60:
                return SeniorCitizenTaxStrategy()
            else:
                return OldRegimeTaxStrategy()
    
    @staticmethod
    def get_available_strategies() -> List[str]:
        """Get list of available strategies"""
        return [
            "OldRegime",
            "NewRegime", 
            "SeniorCitizenOldRegime",
            "SuperSeniorCitizenOldRegime"
        ]


class TaxCalculationEngine:
    """Main tax calculation engine using strategy pattern"""
    
    def __init__(self):
        self.strategy_factory = TaxStrategyFactory()
        self.logger = logging.getLogger("TaxCalculationEngine")
    
    def calculate_tax(self, context: TaxCalculationContext) -> TaxCalculationResult:
        """Calculate tax using appropriate strategy"""
        try:
            strategy = self.strategy_factory.get_strategy(context)
            self.logger.info(f"Using strategy: {strategy.name} for employee {context.employee_id}")
            
            result = strategy.calculate(context)
            
            self.logger.info(f"Tax calculation completed successfully for {context.employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in tax calculation for {context.employee_id}: {str(e)}")
            raise
    
    def compare_regimes(self, context: TaxCalculationContext) -> Dict[str, TaxCalculationResult]:
        """Compare tax liability between old and new regimes"""
        results = {}
        
        # Calculate for old regime
        old_context = context
        old_context.regime = "old"
        old_strategy = OldRegimeTaxStrategy()
        results["old"] = old_strategy.calculate(old_context)
        
        # Calculate for new regime
        new_context = context
        new_context.regime = "new"
        new_strategy = NewRegimeTaxStrategy()
        results["new"] = new_strategy.calculate(new_context)
        
        return results
    
    def calculate_catch_up_tax(self, employee_id: str, current_tax: float, 
                             new_annual_tax: float, remaining_months: int) -> Dict[str, float]:
        """Calculate catch-up tax for remaining months"""
        if remaining_months <= 0:
            return {"additional_monthly_tds": 0.0, "total_catch_up": 0.0}
        
        additional_annual_tax = new_annual_tax - current_tax
        additional_monthly_tds = additional_annual_tax / remaining_months
        
        return {
            "additional_annual_tax": additional_annual_tax,
            "additional_monthly_tds": additional_monthly_tds,
            "remaining_months": remaining_months,
            "total_catch_up": additional_annual_tax
        } 