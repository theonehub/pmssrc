"""
Payroll Tax Service
Domain service for calculating taxes on monthly payroll with LWP considerations
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.monthly_payroll import MonthlyPayroll, AnnualPayrollWithLWP, LWPDetails
from app.domain.entities.salary_income import SalaryIncome
from app.domain.services.tax_calculation_service import TaxCalculationService, TaxCalculationResult


@dataclass
class MonthlyTaxResult:
    """Result of monthly tax calculation with LWP impact."""
    
    month: int
    year: int
    lwp_days: int
    base_monthly_gross: Money
    adjusted_monthly_gross: Money
    lwp_deduction: Money
    monthly_taxable: Money
    projected_annual_tax: Money
    monthly_tax_liability: Money
    effective_monthly_rate: Decimal
    lwp_tax_savings: Money
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "month": self.month,
            "year": self.year,
            "lwp_days": self.lwp_days,
            "base_monthly_gross": self.base_monthly_gross.to_float(),
            "adjusted_monthly_gross": self.adjusted_monthly_gross.to_float(),
            "lwp_deduction": self.lwp_deduction.to_float(),
            "monthly_taxable": self.monthly_taxable.to_float(),
            "projected_annual_tax": self.projected_annual_tax.to_float(),
            "monthly_tax_liability": self.monthly_tax_liability.to_float(),
            "effective_monthly_rate": float(self.effective_monthly_rate),
            "lwp_tax_savings": self.lwp_tax_savings.to_float()
        }


@dataclass
class AnnualPayrollTaxResult:
    """Comprehensive result of annual payroll tax calculation with LWP."""
    
    base_scenario: TaxCalculationResult  # Without LWP
    lwp_scenario: TaxCalculationResult   # With LWP
    lwp_tax_savings: Money
    monthly_results: List[MonthlyTaxResult]
    lwp_impact_summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "base_scenario": {
                "total_tax_liability": self.base_scenario.total_tax_liability.to_float(),
                "taxable_income": self.base_scenario.taxable_income.to_float(),
                "effective_tax_rate": float(self.base_scenario.effective_tax_rate)
            },
            "lwp_scenario": {
                "total_tax_liability": self.lwp_scenario.total_tax_liability.to_float(),
                "taxable_income": self.lwp_scenario.taxable_income.to_float(),
                "effective_tax_rate": float(self.lwp_scenario.effective_tax_rate)
            },
            "lwp_tax_savings": self.lwp_tax_savings.to_float(),
            "monthly_results": [result.to_dict() for result in self.monthly_results],
            "lwp_impact_summary": self.lwp_impact_summary
        }


class PayrollTaxService:
    """Service for calculating payroll taxes with LWP considerations."""
    
    def __init__(self):
        self.tax_service = TaxCalculationService()
    
    def calculate_monthly_tax_with_lwp(
        self,
        monthly_payroll: MonthlyPayroll,
        regime: TaxRegime,
        age: int = 30
    ) -> MonthlyTaxResult:
        """
        Calculate monthly tax liability considering LWP.
        
        Args:
            monthly_payroll: Monthly payroll with LWP details
            regime: Tax regime
            age: Taxpayer age
            
        Returns:
            MonthlyTaxResult: Monthly tax calculation result
        """
        # Calculate base monthly amounts
        base_monthly_gross = monthly_payroll.calculate_monthly_gross_without_lwp()
        adjusted_monthly_gross = monthly_payroll.calculate_monthly_gross_with_lwp()
        lwp_deduction = monthly_payroll.calculate_lwp_deduction()
        monthly_taxable = monthly_payroll.calculate_monthly_taxable_salary_with_lwp(regime)
        
        # Project annual taxable income based on current month
        projected_annual_taxable = monthly_taxable.multiply(12)
        
        # Calculate projected annual tax
        projected_annual_tax = self.tax_service.calculate_tax_on_slabs(
            projected_annual_taxable, regime, age
        )
        
        # Calculate rebate (if applicable)
        rebate_87a = self.tax_service.calculate_rebate_87a(
            projected_annual_taxable, projected_annual_tax, regime
        )
        tax_after_rebate = projected_annual_tax.subtract(rebate_87a)
        
        # Calculate surcharge and cess
        surcharge = self.tax_service.calculate_surcharge(
            projected_annual_taxable, tax_after_rebate, regime
        )
        cess = self.tax_service.calculate_cess(tax_after_rebate.add(surcharge))
        
        # Final projected annual tax
        final_projected_annual_tax = tax_after_rebate.add(surcharge).add(cess)
        
        # Monthly tax liability (1/12th of annual)
        monthly_tax_liability = final_projected_annual_tax.divide(12)
        
        # Calculate effective monthly rate
        effective_monthly_rate = Decimal('0')
        if adjusted_monthly_gross.is_positive():
            effective_monthly_rate = (monthly_tax_liability.amount / adjusted_monthly_gross.amount) * Decimal('100')
        
        # Calculate tax savings due to LWP (can be positive or negative)
        # Base monthly taxable (without LWP)
        base_monthly_taxable = monthly_payroll.base_salary_income.calculate_taxable_salary(regime).divide(12)
        base_annual_taxable = base_monthly_taxable.multiply(12)
        
        base_annual_tax = self.tax_service.calculate_tax_on_slabs(base_annual_taxable, regime, age)
        base_rebate = self.tax_service.calculate_rebate_87a(base_annual_taxable, base_annual_tax, regime)
        base_tax_after_rebate = base_annual_tax.subtract(base_rebate)
        base_surcharge = self.tax_service.calculate_surcharge(base_annual_taxable, base_tax_after_rebate, regime)
        base_cess = self.tax_service.calculate_cess(base_tax_after_rebate.add(base_surcharge))
        base_final_tax = base_tax_after_rebate.add(base_surcharge).add(base_cess)
        
        # Calculate tax impact (savings or penalty)
        base_monthly_tax = base_final_tax.divide(12).to_float()
        lwp_monthly_tax = monthly_tax_liability.to_float()
        monthly_tax_impact = base_monthly_tax - lwp_monthly_tax  # Positive = savings
        
        lwp_tax_savings = Money.from_float(abs(monthly_tax_impact))
        
        return MonthlyTaxResult(
            month=monthly_payroll.lwp_details.month,
            year=monthly_payroll.lwp_details.year,
            lwp_days=monthly_payroll.lwp_details.lwp_days,
            base_monthly_gross=base_monthly_gross,
            adjusted_monthly_gross=adjusted_monthly_gross,
            lwp_deduction=lwp_deduction,
            monthly_taxable=monthly_taxable,
            projected_annual_tax=final_projected_annual_tax,
            monthly_tax_liability=monthly_tax_liability,
            effective_monthly_rate=effective_monthly_rate,
            lwp_tax_savings=lwp_tax_savings
        )
    
    def calculate_annual_payroll_tax_with_lwp(
        self,
        annual_payroll: AnnualPayrollWithLWP,
        regime: TaxRegime,
        age: int = 30,
        deductions: Money = None,
        other_income: Money = None
    ) -> AnnualPayrollTaxResult:
        """
        Calculate comprehensive annual tax with LWP impact.
        
        Args:
            annual_payroll: Annual payroll with LWP details
            regime: Tax regime
            age: Taxpayer age
            deductions: Additional deductions (optional)
            other_income: Other income sources (optional)
            
        Returns:
            AnnualPayrollTaxResult: Comprehensive tax calculation result
        """
        if deductions is None:
            deductions = Money.zero()
        if other_income is None:
            other_income = Money.zero()
        
        # Calculate base scenario (without LWP)
        base_gross_income = annual_payroll.base_salary_income.calculate_gross_salary().add(other_income)
        base_exemptions = annual_payroll.base_salary_income.calculate_total_exemptions(regime)
        base_taxable_income = annual_payroll.base_salary_income.calculate_taxable_salary(regime)
        base_taxable_income = base_taxable_income.add(other_income).subtract(deductions)
        
        base_scenario = self.tax_service.calculate_comprehensive_tax(
            gross_income=base_gross_income,
            exemptions=base_exemptions.add(regime.get_standard_deduction()),
            deductions=deductions,
            taxable_income=base_taxable_income,
            regime=regime,
            age=age
        )
        
        # Calculate LWP scenario
        lwp_gross_income = annual_payroll.calculate_annual_gross_with_lwp().add(other_income)
        lwp_exemptions = annual_payroll.calculate_annual_exemptions_with_lwp(regime)
        lwp_taxable_income = annual_payroll.calculate_annual_taxable_with_lwp(regime)
        lwp_taxable_income = lwp_taxable_income.add(other_income).subtract(deductions)
        
        lwp_scenario = self.tax_service.calculate_comprehensive_tax(
            gross_income=lwp_gross_income,
            exemptions=lwp_exemptions.add(regime.get_standard_deduction()),
            deductions=deductions,
            taxable_income=lwp_taxable_income,
            regime=regime,
            age=age
        )
        
        # Calculate LWP tax impact (can be savings or penalty)
        base_tax = base_scenario.total_tax_liability.to_float()
        lwp_tax = lwp_scenario.total_tax_liability.to_float()
        tax_impact_amount = base_tax - lwp_tax  # Positive = savings, Negative = penalty
        
        # Convert back to Money object (always positive amount)
        lwp_tax_savings = Money.from_float(abs(tax_impact_amount))
        
        # Calculate monthly results
        monthly_results = []
        monthly_payrolls = annual_payroll.get_monthly_payrolls()
        
        for monthly_payroll in monthly_payrolls:
            monthly_result = self.calculate_monthly_tax_with_lwp(monthly_payroll, regime, age)
            monthly_results.append(monthly_result)
        
        # Create LWP impact summary
        lwp_impact_summary = self._create_lwp_impact_summary(
            annual_payroll, base_scenario, lwp_scenario, monthly_results, regime
        )
        
        return AnnualPayrollTaxResult(
            base_scenario=base_scenario,
            lwp_scenario=lwp_scenario,
            lwp_tax_savings=lwp_tax_savings,
            monthly_results=monthly_results,
            lwp_impact_summary=lwp_impact_summary
        )
    
    def _create_lwp_impact_summary(
        self,
        annual_payroll: AnnualPayrollWithLWP,
        base_scenario: TaxCalculationResult,
        lwp_scenario: TaxCalculationResult,
        monthly_results: List[MonthlyTaxResult],
        regime: TaxRegime
    ) -> Dict[str, Any]:
        """Create comprehensive LWP impact summary."""
        
        total_lwp_days = annual_payroll.calculate_total_lwp_days()
        total_working_days = annual_payroll.calculate_total_working_days()
        annual_lwp_deduction = annual_payroll.calculate_annual_lwp_deduction()
        
        # Calculate signed tax impact
        base_tax = base_scenario.total_tax_liability.to_float()
        lwp_tax = lwp_scenario.total_tax_liability.to_float()
        annual_tax_impact = base_tax - lwp_tax  # Positive = savings, Negative = penalty
        
        # Calculate monthly variations
        monthly_lwp_days = [result.lwp_days for result in monthly_results]
        monthly_tax_liabilities = [result.monthly_tax_liability.to_float() for result in monthly_results]
        monthly_tax_savings = [result.lwp_tax_savings.to_float() for result in monthly_results]
        
        # Calculate net income impact (salary loss - tax savings)
        net_income_impact = -annual_lwp_deduction.to_float() + annual_tax_impact
        
        return {
            "lwp_overview": {
                "total_lwp_days": total_lwp_days,
                "total_working_days": total_working_days,
                "lwp_percentage": float((total_lwp_days / total_working_days) * 100) if total_working_days > 0 else 0,
                "months_with_lwp": len([result for result in monthly_results if result.lwp_days > 0]),
                "average_monthly_lwp": total_lwp_days / 12
            },
            "financial_impact": {
                "annual_salary_reduction": annual_lwp_deduction.to_float(),
                "annual_tax_savings": annual_tax_impact,  # Can be negative (penalty)
                "effective_tax_rate_reduction": float(base_scenario.effective_tax_rate - lwp_scenario.effective_tax_rate),
                "net_income_impact": net_income_impact  # Overall impact on take-home
            },
            "monthly_variations": {
                "lwp_days_by_month": monthly_lwp_days,
                "tax_liability_by_month": monthly_tax_liabilities,
                "tax_savings_by_month": monthly_tax_savings,
                "highest_lwp_month": max(enumerate(monthly_lwp_days), key=lambda x: x[1])[0] + 1 if monthly_lwp_days else 0,
                "total_monthly_tax_savings": sum(monthly_tax_savings)
            },
            "tax_comparison": {
                "base_scenario": {
                    "taxable_income": base_scenario.taxable_income.to_float(),
                    "total_tax": base_scenario.total_tax_liability.to_float(),
                    "effective_rate": float(base_scenario.effective_tax_rate)
                },
                "lwp_scenario": {
                    "taxable_income": lwp_scenario.taxable_income.to_float(),
                    "total_tax": lwp_scenario.total_tax_liability.to_float(),
                    "effective_rate": float(lwp_scenario.effective_tax_rate)
                }
            },
            "regime_used": regime.regime_type.value
        }
    
    def calculate_lwp_tax_optimization(
        self,
        base_salary: SalaryIncome,
        target_lwp_days: int,
        regime: TaxRegime,
        age: int = 30,
        distribute_evenly: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate tax optimization scenarios with different LWP distributions.
        
        Args:
            base_salary: Base salary income
            target_lwp_days: Total LWP days to optimize
            regime: Tax regime
            age: Taxpayer age
            distribute_evenly: Whether to distribute LWP evenly across months
            
        Returns:
            Dict: Optimization analysis results
        """
        scenarios = []
        
        # Scenario 1: No LWP
        no_lwp_details = [LWPDetails(lwp_days=0, month=i+1, year=2024) for i in range(12)]
        no_lwp_payroll = AnnualPayrollWithLWP(base_salary, no_lwp_details)
        no_lwp_result = self.calculate_annual_payroll_tax_with_lwp(no_lwp_payroll, regime, age)
        
        # Store base tax for comparison
        no_lwp_tax = no_lwp_result.lwp_scenario.total_tax_liability.to_float()
        
        scenarios.append({
            "scenario": "No LWP",
            "distribution": "None",
            "total_tax": no_lwp_tax,
            "tax_savings": 0,
            "monthly_distribution": [0] * 12
        })
        
        # Scenario 2: Even distribution
        if distribute_evenly and target_lwp_days > 0:
            lwp_per_month = target_lwp_days // 12
            remaining_lwp = target_lwp_days % 12
            
            even_lwp_details = []
            for i in range(12):
                lwp_days = lwp_per_month + (1 if i < remaining_lwp else 0)
                even_lwp_details.append(LWPDetails(lwp_days=lwp_days, month=i+1, year=2024))
            
            even_lwp_payroll = AnnualPayrollWithLWP(base_salary, even_lwp_details)
            even_lwp_result = self.calculate_annual_payroll_tax_with_lwp(even_lwp_payroll, regime, age)
            
            # Calculate tax savings properly
            no_lwp_tax = no_lwp_result.lwp_scenario.total_tax_liability.to_float()
            even_lwp_tax = even_lwp_result.lwp_scenario.total_tax_liability.to_float()
            tax_savings = no_lwp_tax - even_lwp_tax
            
            scenarios.append({
                "scenario": "Even Distribution",
                "distribution": f"{lwp_per_month}-{lwp_per_month + (1 if remaining_lwp > 0 else 0)} days per month",
                "total_tax": even_lwp_result.lwp_scenario.total_tax_liability.to_float(),
                "tax_savings": tax_savings,
                "monthly_distribution": [detail.lwp_days for detail in even_lwp_details]
            })
        
        # Scenario 3: Front-loaded (higher LWP in early months)
        if target_lwp_days > 0:
            front_loaded_details = []
            remaining_days = target_lwp_days
            
            for i in range(12):
                if remaining_days > 0:
                    # Take more days in earlier months (max 25 days per month)
                    lwp_days = min(remaining_days, min(25, remaining_days // (12 - i) + 5))
                    remaining_days -= lwp_days
                else:
                    lwp_days = 0
                front_loaded_details.append(LWPDetails(lwp_days=lwp_days, month=i+1, year=2024))
            
            front_loaded_payroll = AnnualPayrollWithLWP(base_salary, front_loaded_details)
            front_loaded_result = self.calculate_annual_payroll_tax_with_lwp(front_loaded_payroll, regime, age)
            
            # Calculate tax savings properly
            front_loaded_tax = front_loaded_result.lwp_scenario.total_tax_liability.to_float()
            front_tax_savings = no_lwp_tax - front_loaded_tax
            
            scenarios.append({
                "scenario": "Front-loaded",
                "distribution": "Higher LWP in early months",
                "total_tax": front_loaded_result.lwp_scenario.total_tax_liability.to_float(),
                "tax_savings": front_tax_savings,
                "monthly_distribution": [detail.lwp_days for detail in front_loaded_details]
            })
        
        # Scenario 4: Back-loaded (higher LWP in later months)
        if target_lwp_days > 0:
            back_loaded_details = []
            remaining_days = target_lwp_days
            
            # Start from the end and work backwards
            monthly_lwp = [0] * 12
            for i in range(11, -1, -1):
                if remaining_days > 0:
                    lwp_days = min(remaining_days, min(25, remaining_days // (i + 1) + 5))
                    monthly_lwp[i] = lwp_days
                    remaining_days -= lwp_days
            
            for i in range(12):
                back_loaded_details.append(LWPDetails(lwp_days=monthly_lwp[i], month=i+1, year=2024))
            
            back_loaded_payroll = AnnualPayrollWithLWP(base_salary, back_loaded_details)
            back_loaded_result = self.calculate_annual_payroll_tax_with_lwp(back_loaded_payroll, regime, age)
            
            # Calculate tax savings properly
            back_loaded_tax = back_loaded_result.lwp_scenario.total_tax_liability.to_float()
            back_tax_savings = no_lwp_tax - back_loaded_tax
            
            scenarios.append({
                "scenario": "Back-loaded",
                "distribution": "Higher LWP in later months",
                "total_tax": back_loaded_result.lwp_scenario.total_tax_liability.to_float(),
                "tax_savings": back_tax_savings,
                "monthly_distribution": [detail.lwp_days for detail in back_loaded_details]
            })
        
        # Find optimal scenario
        tax_scenarios = [s for s in scenarios if s["scenario"] != "No LWP"]
        optimal_scenario = max(tax_scenarios, key=lambda x: x["tax_savings"]) if tax_scenarios else None
        
        return {
            "target_lwp_days": target_lwp_days,
            "scenarios": scenarios,
            "optimal_scenario": optimal_scenario,
            "optimization_summary": {
                "max_tax_savings": optimal_scenario["tax_savings"] if optimal_scenario else 0,
                "optimal_distribution": optimal_scenario["scenario"] if optimal_scenario else "No optimization possible",
                "savings_range": {
                    "min": min([s["tax_savings"] for s in tax_scenarios]) if tax_scenarios else 0,
                    "max": max([s["tax_savings"] for s in tax_scenarios]) if tax_scenarios else 0
                }
            },
            "regime_used": regime.regime_type.value
        }