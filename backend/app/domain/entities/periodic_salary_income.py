"""
Periodic Salary Income Entity
Handles salary income across multiple periods for mid-year scenarios
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Any, List
from datetime import date

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.employment_period import EmploymentPeriod
from app.domain.entities.taxation.salary_income import SalaryIncome


@dataclass
class PeriodicSalaryData:
    """
    Salary data for a specific period.
    """
    
    period: EmploymentPeriod
    salary_income: SalaryIncome
    
    def calculate_annualized_gross(self, tax_year: TaxYear) -> Money:
        """
        Calculate what the annual gross would be if this salary was paid for full year.
        
        Args:
            tax_year: Tax year for calculation
            
        Returns:
            Money: Annualized gross salary
        """
        monthly_gross = self.salary_income.calculate_gross_salary().divide(12)
        return monthly_gross.multiply(12)
    
    def calculate_prorated_gross(self, tax_year: TaxYear) -> Money:
        """
        Calculate prorated gross salary for this period.
        
        Args:
            tax_year: Tax year for calculation
            
        Returns:
            Money: Prorated gross salary
        """
        period_months = self.period.get_period_months(tax_year)
        monthly_gross = self.salary_income.calculate_gross_salary().divide(12)
        return monthly_gross.multiply(period_months)
    
    def calculate_prorated_exemptions(self, regime: TaxRegime, tax_year: TaxYear) -> Money:
        """
        Calculate prorated exemptions for this period.
        
        Args:
            regime: Tax regime
            tax_year: Tax year for calculation
            
        Returns:
            Money: Prorated exemptions
        """
        if self.period.is_full_year(tax_year):
            return self.salary_income.calculate_total_exemptions(regime)
        
        # For partial periods, some exemptions need special handling
        period_factor = self.period.get_proration_factor(tax_year)
        
        # HRA exemption - calculate based on actual period
        hra_exemption = self._calculate_period_hra_exemption(regime, tax_year)
        
        # Other exemptions - prorate normally
        lta_exemption = self.salary_income.calculate_lta_exemption(regime).multiply(period_factor)
        medical_exemption = self.salary_income.calculate_medical_allowance_exemption(regime).multiply(period_factor)
        conveyance_exemption = self.salary_income.calculate_conveyance_exemption(regime).multiply(period_factor)
        
        return hra_exemption.add(lta_exemption).add(medical_exemption).add(conveyance_exemption)
    
    def _calculate_period_hra_exemption(self, regime: TaxRegime, tax_year: TaxYear) -> Money:
        """
        Calculate HRA exemption for the specific period.
        
        Args:
            regime: Tax regime
            tax_year: Tax year
            
        Returns:
            Money: Period-specific HRA exemption
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        period_months = self.period.get_period_months(tax_year)
        monthly_basic_da = self.salary_income.basic_salary.add(self.salary_income.dearness_allowance).divide(12)
        monthly_hra = self.salary_income.hra_received.divide(12)
        monthly_rent = self.salary_income.actual_rent_paid.divide(12)
        
        # Calculate for each month and sum up
        total_exemption = Money.zero()
        
        for _ in range(int(period_months)):
            # Three calculations - minimum is exempt
            actual_hra = monthly_hra
            
            # 50% for metro, 40% for non-metro
            percentage = Decimal('50') if self.salary_income.hra_city_type == "metro" else Decimal('40')
            percent_of_salary = monthly_basic_da.percentage(percentage)
            
            # Rent paid minus 10% of salary
            ten_percent_salary = monthly_basic_da.percentage(Decimal('10'))
            
            if monthly_rent.is_greater_than(ten_percent_salary):
                rent_minus_ten_percent = monthly_rent.subtract(ten_percent_salary)
            else:
                rent_minus_ten_percent = Money.zero()
            
            # Minimum of the three amounts
            monthly_exemption = Money.zero()
            if actual_hra.is_positive():
                monthly_exemption = actual_hra.min(percent_of_salary).min(rent_minus_ten_percent)
            
            total_exemption = total_exemption.add(monthly_exemption)
        
        # Handle fractional month
        fractional_part = period_months % 1
        if fractional_part > 0:
            actual_hra = monthly_hra.multiply(fractional_part)
            percent_of_salary = monthly_basic_da.percentage(percentage).multiply(fractional_part)
            rent_minus_ten_percent = monthly_rent.subtract(ten_percent_salary).multiply(fractional_part)
            
            if rent_minus_ten_percent.amount < 0:
                rent_minus_ten_percent = Money.zero()
            
            fractional_exemption = Money.zero()
            if actual_hra.is_positive():
                fractional_exemption = actual_hra.min(percent_of_salary).min(rent_minus_ten_percent)
            
            total_exemption = total_exemption.add(fractional_exemption)
        
        return total_exemption


@dataclass
class PeriodicSalaryIncome:
    """
    Entity handling salary income across multiple periods.
    Supports mid-year increments, joiners, and complex scenarios.
    """
    
    periods: List[PeriodicSalaryData] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate periodic salary data."""
        if not self.periods:
            raise ValueError("At least one salary period is required")
        
        # Check for overlapping periods
        for i, period1 in enumerate(self.periods):
            for j, period2 in enumerate(self.periods[i+1:], i+1):
                if period1.period.overlaps_with(period2.period):
                    raise ValueError(f"Overlapping periods found: {period1.period.description} and {period2.period.description}")
    
    def add_period(self, period_data: PeriodicSalaryData):
        """
        Add a new salary period.
        
        Args:
            period_data: Periodic salary data to add
        """
        # Check for overlaps with existing periods
        for existing in self.periods:
            if existing.period.overlaps_with(period_data.period):
                raise ValueError(f"Period overlaps with existing period: {existing.period.description}")
        
        self.periods.append(period_data)
        # Sort periods by start date
        self.periods.sort(key=lambda p: p.period.start_date)
    
    def calculate_total_gross_salary(self, tax_year: TaxYear) -> Money:
        """
        Calculate total gross salary across all periods.
        
        Args:
            tax_year: Tax year for calculation
            
        Returns:
            Money: Total gross salary
        """
        total = Money.zero()
        for period_data in self.periods:
            total = total.add(period_data.calculate_prorated_gross(tax_year))
        return total
    
    def calculate_total_exemptions(self, regime: TaxRegime, tax_year: TaxYear) -> Money:
        """
        Calculate total exemptions across all periods.
        
        Args:
            regime: Tax regime
            tax_year: Tax year for calculation
            
        Returns:
            Money: Total exemptions
        """
        total = Money.zero()
        for period_data in self.periods:
            total = total.add(period_data.calculate_prorated_exemptions(regime, tax_year))
        return total
    
    def get_highest_salary_period(self) -> PeriodicSalaryData:
        """
        Get the period with highest salary.
        
        Returns:
            PeriodicSalaryData: Period with highest salary
        """
        return max(self.periods, key=lambda p: p.salary_income.calculate_gross_salary().amount)
    
    def get_current_period(self, as_of_date: date = None) -> PeriodicSalaryData:
        """
        Get the current active period.
        
        Args:
            as_of_date: Date to check against (defaults to today)
            
        Returns:
            PeriodicSalaryData: Current active period
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        for period_data in reversed(self.periods):  # Check from latest first
            if (period_data.period.start_date <= as_of_date and 
                (period_data.period.end_date is None or period_data.period.end_date >= as_of_date)):
                return period_data
        
        # If no current period found, return the latest one
        return self.periods[-1]
    
    def calculate_mid_year_impact(self, tax_year: TaxYear, regime: TaxRegime) -> Dict[str, Any]:
        """
        Calculate the impact of mid-year changes.
        
        Args:
            tax_year: Tax year
            regime: Tax regime
            
        Returns:
            Dict: Analysis of mid-year impact
        """
        if len(self.periods) == 1:
            return {"impact": "No mid-year changes", "analysis": "Single period employment"}
        
        # Compare if all periods were at highest salary vs actual
        highest_period = self.get_highest_salary_period()
        full_year_at_highest = highest_period.salary_income.calculate_gross_salary()
        
        actual_total = self.calculate_total_gross_salary(tax_year)
        difference = full_year_at_highest.subtract(actual_total)
        
        period_details = []
        for period_data in self.periods:
            period_details.append({
                "period": period_data.period.to_dict(),
                "monthly_gross": period_data.salary_income.calculate_gross_salary().divide(12).to_float(),
                "period_months": float(period_data.period.get_period_months(tax_year)),
                "period_gross": period_data.calculate_prorated_gross(tax_year).to_float(),
                "annualized_gross": period_data.calculate_annualized_gross(tax_year).to_float()
            })
        
        return {
            "periods_count": len(self.periods),
            "actual_gross_salary": actual_total.to_float(),
            "full_year_at_highest_salary": full_year_at_highest.to_float(),
            "salary_impact": difference.to_float(),
            "impact_percentage": float((difference.amount / full_year_at_highest.amount) * 100) if full_year_at_highest.is_positive() else 0,
            "period_details": period_details,
            "highest_salary_period": highest_period.period.description
        }
    
    def get_detailed_breakdown(self, regime: TaxRegime, tax_year: TaxYear) -> Dict[str, Any]:
        """
        Get detailed breakdown of periodic salary income.
        
        Args:
            regime: Tax regime
            tax_year: Tax year
            
        Returns:
            Dict: Detailed breakdown
        """
        period_breakdowns = []
        
        for period_data in self.periods:
            period_breakdown = period_data.salary_income.get_salary_breakdown(regime)
            period_breakdown.update({
                "employment_period": period_data.period.to_dict(),
                "period_months": float(period_data.period.get_period_months(tax_year)),
                "proration_factor": float(period_data.period.get_proration_factor(tax_year)),
                "prorated_gross": period_data.calculate_prorated_gross(tax_year).to_float(),
                "prorated_exemptions": period_data.calculate_prorated_exemptions(regime, tax_year).to_float()
            })
            period_breakdowns.append(period_breakdown)
        
        return {
            "total_periods": len(self.periods),
            "total_gross_salary": self.calculate_total_gross_salary(tax_year).to_float(),
            "total_exemptions": self.calculate_total_exemptions(regime, tax_year).to_float(),
            "regime_used": regime.regime_type.value,
            "tax_year": str(tax_year),
            "period_breakdowns": period_breakdowns,
            "mid_year_impact": self.calculate_mid_year_impact(tax_year, regime)
        }
    
    @classmethod
    def create_full_year(cls, salary_income: SalaryIncome, tax_year: TaxYear) -> 'PeriodicSalaryIncome':
        """
        Create periodic salary income for full year employment.
        
        Args:
            salary_income: Salary income details
            tax_year: Tax year
            
        Returns:
            PeriodicSalaryIncome: Full year periodic salary
        """
        period = EmploymentPeriod.full_year_period(tax_year)
        period_data = PeriodicSalaryData(period=period, salary_income=salary_income)
        return cls(periods=[period_data])
    
    @classmethod
    def create_mid_year_joiner(cls, salary_income: SalaryIncome, joining_date: date) -> 'PeriodicSalaryIncome':
        """
        Create periodic salary income for mid-year joiner.
        
        Args:
            salary_income: Salary income details
            joining_date: Date of joining
            
        Returns:
            PeriodicSalaryIncome: Mid-year joiner periodic salary
        """
        period = EmploymentPeriod.mid_year_joiner(joining_date)
        period_data = PeriodicSalaryData(period=period, salary_income=salary_income)
        return cls(periods=[period_data])
    
    @classmethod
    def create_with_increment(cls, initial_salary: SalaryIncome, increment_salary: SalaryIncome,
                             increment_date: date, tax_year: TaxYear) -> 'PeriodicSalaryIncome':
        """
        Create periodic salary income with mid-year increment.
        
        Args:
            initial_salary: Initial salary before increment
            increment_salary: Salary after increment
            increment_date: Date of increment
            tax_year: Tax year
            
        Returns:
            PeriodicSalaryIncome: Periodic salary with increment
        """
        # Pre-increment period (end date is day before increment)
        from datetime import timedelta
        pre_increment_end = increment_date - timedelta(days=1)
        pre_period = EmploymentPeriod(
            start_date=tax_year.get_start_date(),
            end_date=pre_increment_end,
            description="Pre-increment period"
        )
        
        # Post-increment period
        post_period = EmploymentPeriod(
            start_date=increment_date,
            end_date=tax_year.get_end_date(),
            description="Post-increment period"
        )
        
        periods = [
            PeriodicSalaryData(period=pre_period, salary_income=initial_salary),
            PeriodicSalaryData(period=post_period, salary_income=increment_salary)
        ]
        
        return cls(periods=periods) 