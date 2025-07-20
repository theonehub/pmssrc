"""
Taxation Record Entity
Main aggregate root for taxation domain
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import uuid4
from decimal import Decimal

from app.utils.logger import get_detailed_logger
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService, TaxCalculationResult
from app.domain.value_objects.taxation.tax_regime import TaxRegimeType
from app.domain.entities.taxation.monthly_salary import MonthlySalary
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.domain.entities.taxation.monthly_salary_status import TDSStatus

logger = get_detailed_logger()

@dataclass
class SalaryPackageRecord:
    """
    Main salary package aggregate root.
    
    Represents a complete salary components, values provided for a month, which can be used to calculate the tax for the month.
    Contains all income types, deductions, and calculation information.
    
    Enhanced to support comprehensive Indian taxation:
    - Salary income (simple and periodic)  
    - Perquisites (all 15+ types)
    - House property income (now under other_income)
    - Capital gains
    - Retirement benefits
    - Other income sources
    - Monthly payroll with LWP
    """
    
    # Identifiers
    employee_id: EmployeeId
    tax_year: TaxYear
    age: int
    regime: TaxRegime
    deductions: TaxDeductions
    
    # Optional components
    salary_incomes: List[SalaryIncome]
    annual_salary_income: Optional[SalaryIncome] = None
    capital_gains_income: Optional[CapitalGainsIncome] = None
    perquisites: Optional[Perquisites] = None
    retirement_benefits: Optional[RetirementBenefits] = None
    other_income: Optional[OtherIncome] = None
    is_regime_update_allowed: Optional[bool] = True
    
    is_government_employee: bool = False
    
    # Identifiers
    salary_package_id: Optional[str] = None
    
    # Calculated fields
    calculation_result: Optional[TaxCalculationResult] = None
    last_calculated_at: Optional[datetime] = None
    monthly_salary_records: List[MonthlySalary] = field(default_factory=list)
    
    # Metadata
    is_final: bool = False
    submitted_at: Optional[datetime] = None
    
    # Audit fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    
    # Domain events (not persisted)
    _domain_events: List[Dict[str, Any]] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate the salary package record after initialization."""
        if self.age < 18 or self.age > 100:
            raise ValueError("Invalid age for taxation")
        if not self.salary_incomes:
            raise ValueError("At least one salary income is required")
        if not self.salary_package_id:
            self.salary_package_id = str(uuid4())
        
        # Initialize annual_salary_income if not already set
        if not hasattr(self, 'annual_salary_income') or self.annual_salary_income is None:
            self._update_annual_salary_income()     #Logically Correct
    
    def add_salary_income(self, salary_income: SalaryIncome) -> None:
        """
        Add a new salary income to the list.
        Automatically updates the effective_till of the previous salary income.
        Updates the annual_salary_income field based on effective months calculation.
        
        Args:
            salary_income: New salary income to add
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        # If there are existing salary incomes and the new one has effective_from date
        if self.salary_incomes and salary_income.effective_from:
            latest_salary = self.salary_incomes[-1]
            # Ensure the new salary's effective_from is after the latest salary's effective_from
            if salary_income.effective_from <= latest_salary.effective_from:
                raise ValueError("New salary income's effective_from date must be after the latest salary's effective_from date")
            # Ensure increments only start from the 1st of the month
            if len(self.salary_incomes) > 0 and salary_income.effective_from.day != 1:
                raise ValueError("New salary income's effective_from date must be the 1st of the month for increments")
            # Calculate one day before the new effective_from date
            from datetime import timedelta
            new_effective_till = salary_income.effective_from - timedelta(days=1)
            # Update the effective_till of the previous salary income
            # Create a new SalaryIncome instance with updated effective_till
            from copy import deepcopy
            updated_previous_salary = deepcopy(latest_salary)
            updated_previous_salary.effective_till = new_effective_till
            # Replace the last salary income with the updated one
            self.salary_incomes[-1] = updated_previous_salary
        
        # Add the new salary income
        self.salary_incomes.append(salary_income)
        
        # Update annual_salary_income based on all salary incomes and their effective months
        self._update_annual_salary_income()
        
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryIncomeAdded",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "new_salary_gross": salary_income.calculate_gross_salary().to_float(),
            "total_salary_incomes": len(self.salary_incomes),
            "effective_from": salary_income.effective_from.isoformat() if salary_income.effective_from else None,
            "effective_till": salary_income.effective_till.isoformat() if salary_income.effective_till else None,
            "annual_salary_gross": self.annual_salary_income.calculate_gross_salary().to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_latest_salary_income(self, new_salary_income: SalaryIncome) -> None:
        """
        Update the latest salary income in the list.
        Updates the annual_salary_income field based on effective months calculation.
        
        Args:
            new_salary_income: New salary income to replace the latest one
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        if not self.salary_incomes:
            raise ValueError("No salary incomes to update")
        
        old_gross = self.salary_incomes[-1].calculate_gross_salary()
        self.salary_incomes[-1] = new_salary_income
        new_gross = new_salary_income.calculate_gross_salary()
        
        # Update annual_salary_income based on all salary incomes and their effective months
        self._update_annual_salary_income()
        
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "LatestSalaryIncomeUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_gross_salary": old_gross.to_float(),
            "new_gross_salary": new_gross.to_float(),
            "annual_salary_gross": self.annual_salary_income.calculate_gross_salary().to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def get_latest_salary_income(self) -> SalaryIncome:
        """
        Get the latest salary income from the list.
        
        Returns:
            SalaryIncome: Latest salary income
        """
        if not self.salary_incomes:
            raise ValueError("No salary incomes available")
        return self.salary_incomes[-1]
    
    def get_annual_salary_income(self) -> SalaryIncome:
        """
        Get the annual salary income which represents the weighted total of all salary incomes
        based on their effective months. This contains ANNUAL TOTAL amounts, not monthly amounts.
        
        For example: If you have 3 months at ₹100K basic + 9 months at ₹150K basic,
        this returns a SalaryIncome with basic_salary = ₹300K + ₹1350K = ₹1650K (annual total).
        
        Returns:
            SalaryIncome: Annual salary income with weighted annual totals
        """
        if not hasattr(self, 'annual_salary_income') or self.annual_salary_income is None:
            self._update_annual_salary_income()
        return self.annual_salary_income
    
    def get_salary_income_history(self) -> List[SalaryIncome]:
        """
        Get all salary incomes in chronological order.
        
        Returns:
            List[SalaryIncome]: List of all salary incomes
        """
        return self.salary_incomes.copy()
    
    def compute_annual_salary_income(self) -> Money:
        """
        Compute gross annual salary from all salary components applicable in the current financial year.
        This includes actual salary earned from different periods and projected salary for remaining period.
        
        Returns:
            Money: Total gross annual salary for the financial year
        """
        from datetime import timedelta
        from decimal import Decimal
        
        # Get financial year boundaries
        financial_year_start = self.tax_year.get_start_date()
        financial_year_end = self.tax_year.get_end_date()
        current_date = datetime.now().date()
        
        total_gross_salary = Money.zero()
        

        logger.info(f"Computing gross annual salary for {self.employee_id} in {self.tax_year}")
        logger.info(f"Salary incomes Length: {len(self.salary_incomes)}")
        logger.info(f"Financial year start: {financial_year_start}, Financial year end: {financial_year_end}")
        logger.info(f"Current date: {current_date}")
        
        # Process all salary incomes that fall within the financial year
        for salary_income in self.salary_incomes:
            logger.info(f"**************************************************")
            logger.info(f"Salary income effective from: {salary_income.effective_from}")
            logger.info(f"Salary income effective till: {salary_income.effective_till}")

            # Determine the effective period for this salary income within the financial year
            salary_start = max(
                salary_income.effective_from.date() if salary_income.effective_from else financial_year_start,
                financial_year_start
            )
            salary_end = min(
                salary_income.effective_till.date() if salary_income.effective_till else financial_year_end,
                financial_year_end
            )
            logger.info(f"Salary start: {salary_start}, Salary end: {salary_end}")
            
            # Skip if salary period doesn't overlap with financial year
            if salary_start > financial_year_end or salary_end < financial_year_start:
                continue
            
            # Calculate the number of months this salary is applicable
            months_applicable = self._calculate_months_between_dates(salary_start, salary_end)
            
            if months_applicable > 0:
                logger.info(f"**************************************************")
                logger.info(f"Salary income basic salary: {salary_income.basic_salary}")
                logger.info(f"Months applicable: {months_applicable}")
                logger.info(f"**************************************************")
                # Calculate proportional salary for this period
                monthly_gross = salary_income.calculate_gross_salary()  # This is monthly amount
                logger.info(f"Monthly gross: {monthly_gross}")
                period_gross = monthly_gross.multiply(Decimal(str(months_applicable)))
                logger.info(f"Period gross: {period_gross}")
                total_gross_salary = total_gross_salary.add(period_gross)
                logger.info(f"Total gross salary: {total_gross_salary}")
                logger.info(f"**************************************************")
                
        return total_gross_salary
    
    def get_annual_salary_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of how gross annual salary is computed.
        Shows contribution from each salary component and projections.
        
        Returns:
            Dict: Detailed breakdown of annual salary computation
        """
        from datetime import timedelta
        from decimal import Decimal
        
        # Get financial year boundaries
        financial_year_start = self.tax_year.get_start_date()
        financial_year_end = self.tax_year.get_end_date()
        current_date = datetime.now().date()
        
        breakdown = {
            "financial_year": str(self.tax_year),
            "financial_year_start": financial_year_start.isoformat(),
            "financial_year_end": financial_year_end.isoformat(),
            "current_date": current_date.isoformat(),
            "salary_periods": [],
            "projections": [],
            "summary": {
                "total_salary_periods": 0,
                "total_from_actual_periods": 0.0,
                "total_from_projections": 0.0,
                "total_gross_annual_salary": 0.0
            }
        }
        
        total_gross_salary = Money.zero()
        covered_periods = []
        
        # Process all salary incomes that fall within the financial year
        for i, salary_income in enumerate(self.salary_incomes):
            # Determine the effective period for this salary income within the financial year
            salary_start = max(
                salary_income.effective_from.date() if salary_income.effective_from else financial_year_start,
                financial_year_start
            )
            salary_end = min(
                salary_income.effective_till.date() if salary_income.effective_till else financial_year_end,
                financial_year_end
            )
            
            # Skip if salary period doesn't overlap with financial year
            if salary_start > financial_year_end or salary_end < financial_year_start:
                continue
            
            # Calculate the number of months this salary is applicable
            months_applicable = self._calculate_months_between_dates(salary_start, salary_end)
            
            if months_applicable > 0:
                # Calculate proportional salary for this period
                monthly_gross = salary_income.calculate_gross_salary()  # This is monthly amount
                period_gross = monthly_gross.multiply(Decimal(str(months_applicable)))
                total_gross_salary = total_gross_salary.add(period_gross)
                
                # Track covered periods
                covered_periods.append({
                    'start': salary_start,
                    'end': salary_end,
                    'months': months_applicable,
                    'monthly_gross': monthly_gross.to_float()
                })
                
                # Add to breakdown
                breakdown["salary_periods"].append({
                    "period_index": i + 1,
                    "effective_from": salary_income.effective_from.isoformat() if salary_income.effective_from else None,
                    "effective_till": salary_income.effective_till.isoformat() if salary_income.effective_till else None,
                    "period_start_in_fy": salary_start.isoformat(),
                    "period_end_in_fy": salary_end.isoformat(),
                    "months_applicable": round(months_applicable, 2),
                    "monthly_gross_salary": monthly_gross.to_float(),
                    "total_for_period": period_gross.to_float(),
                    "salary_components": {
                        "basic_salary": salary_income.basic_salary.to_float(),
                        "dearness_allowance": salary_income.dearness_allowance.to_float(),
                        "hra_provided": salary_income.hra_provided.to_float(),
                        "special_allowance": salary_income.special_allowance.to_float(),
                        "commission": salary_income.commission.to_float(),
                        "specific_allowances_total": salary_income.specific_allowances.calculate_total_specific_allowances().to_float() if salary_income.specific_allowances else 0.0,
                        "specific_allowances_breakdown": {
                            "hills_allowance": salary_income.specific_allowances.hills_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "border_allowance": salary_income.specific_allowances.border_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "transport_employee_allowance": salary_income.specific_allowances.transport_employee_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "children_education_allowance": salary_income.specific_allowances.children_education_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "hostel_allowance": salary_income.specific_allowances.hostel_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "disabled_transport_allowance": salary_income.specific_allowances.disabled_transport_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "underground_mines_allowance": salary_income.specific_allowances.underground_mines_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "government_entertainment_allowance": salary_income.specific_allowances.government_entertainment_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "city_compensatory_allowance": salary_income.specific_allowances.city_compensatory_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "rural_allowance": salary_income.specific_allowances.rural_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "project_allowance": salary_income.specific_allowances.project_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "deputation_allowance": salary_income.specific_allowances.deputation_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "overtime_allowance": salary_income.specific_allowances.overtime_allowance.to_float() if salary_income.specific_allowances else 0.0,
                            "any_other_allowance": salary_income.specific_allowances.any_other_allowance.to_float() if salary_income.specific_allowances else 0.0
                        }
                    }
                })
        
        # Calculate projections for uncovered periods
        if current_date < financial_year_end:
            # Find the latest salary income for projection
            latest_salary = self.get_latest_salary_income()
            
            # Calculate uncovered period from current date to financial year end
            projection_start = max(current_date, financial_year_start)
            projection_end = financial_year_end
            
            # Check if there's any uncovered period that needs projection
            uncovered_months = self._get_uncovered_months(covered_periods, projection_start, projection_end)
            
            if uncovered_months > 0:
                # Project salary for uncovered period using latest salary
                monthly_gross = latest_salary.calculate_gross_salary()
                projected_gross = monthly_gross.multiply(Decimal(str(uncovered_months)))
                total_gross_salary = total_gross_salary.add(projected_gross)
                
                # Add to breakdown
                breakdown["projections"].append({
                    "projection_start": projection_start.isoformat(),
                    "projection_end": projection_end.isoformat(),
                    "uncovered_months": round(uncovered_months, 2),
                    "monthly_gross_salary": monthly_gross.to_float(),
                    "projected_amount": projected_gross.to_float(),
                    "based_on_latest_salary": True,
                    "latest_salary_effective_from": latest_salary.effective_from.isoformat() if latest_salary.effective_from else None
                })
                
                breakdown["summary"]["total_from_projections"] = projected_gross.to_float()
        
        # Update summary
        breakdown["summary"]["total_salary_periods"] = len(breakdown["salary_periods"])
        breakdown["summary"]["total_from_actual_periods"] = sum(period["total_for_period"] for period in breakdown["salary_periods"])
        breakdown["summary"]["total_gross_annual_salary"] = total_gross_salary.to_float()
        
        return breakdown
    
    def _calculate_months_between_dates(self, start_date: date, end_date: date) -> float:
        """
        Calculate the number of months between two dates (including fractional months).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            float: Number of months (including fractional months)
        """
        if start_date > end_date:
            return 0.0
        
        # Get financial year boundaries for special handling
        financial_year_start = self.tax_year.get_start_date()
        financial_year_end = self.tax_year.get_end_date()
        
        # Special handling for complete financial year
        if start_date <= financial_year_start and end_date >= financial_year_end:
            logger.debug(f"Complete financial year detected: {start_date} to {end_date} covers {financial_year_start} to {financial_year_end}")
            return 12.0
        
        # Special handling for exact financial year period
        if start_date == financial_year_start and end_date == financial_year_end:
            logger.debug(f"Exact financial year period: {start_date} to {end_date}")
            return 12.0
        
        # Calculate months using a more accurate approach
        # Step 1: Calculate the number of complete months
        start_year, start_month, start_day = start_date.year, start_date.month, start_date.day
        end_year, end_month, end_day = end_date.year, end_date.month, end_date.day
        
        # Calculate total months difference (this gives us the base number of months)
        months_diff = (end_year - start_year) * 12 + (end_month - start_month)
        
        # Now we need to handle the day calculation properly
        # If we're on the same day or the end day is later, we get a full month plus fraction
        # If the end day is earlier, we're still in the previous month
        
        if end_day >= start_day:
            # We have completed the month and possibly some additional days
            if start_day == 1 and end_day == self._get_last_day_of_month(end_year, end_month):
                # Complete month: from 1st to last day of month
                months_diff += 1.0
            elif start_day == 1:
                # Started from 1st, calculate fraction based on days covered
                days_in_month = self._get_last_day_of_month(end_year, end_month)
                fraction = end_day / days_in_month
                months_diff += fraction
            else:
                # Started mid-month, calculate fraction
                days_in_month = self._get_last_day_of_month(end_year, end_month)
                days_covered = end_day - start_day + 1  # +1 to include both start and end dates
                fraction = days_covered / days_in_month
                months_diff += fraction
        else:
            # The end day is before the start day, so we haven't completed the month
            # We're still in the previous month
            if months_diff > 0:
                months_diff -= 1
                # Calculate the fraction for the incomplete month
                days_in_prev_month = self._get_last_day_of_month(
                    end_year if end_month > 1 else end_year - 1,
                    end_month - 1 if end_month > 1 else 12
                )
                # Days from start_day to end of previous month + days from 1 to end_day
                days_covered = (days_in_prev_month - start_day + 1) + end_day
                fraction = days_covered / 30.0  # Use 30 as average for cross-month calculation
                months_diff += fraction
        
        # Special case: For periods that should be exactly whole months
        # (e.g., July 1 to March 31 should be exactly 9 months)
        if self._is_period_exact_months(start_date, end_date):
            exact_months = self._calculate_exact_months(start_date, end_date)
            logger.debug(f"Period {start_date} to {end_date} is exact months: {exact_months}")
            return exact_months
        
        # Ensure we don't exceed 12 months for a financial year period
        if (start_date >= financial_year_start and end_date <= financial_year_end and 
            months_diff > 12.0):
            logger.debug(f"Capping months at 12.0 for financial year period: {start_date} to {end_date}")
            return 12.0
        
        result = max(0.0, months_diff)
        logger.debug(f"Calculated months between {start_date} and {end_date}: {result}")
        return result
    
    def _get_last_day_of_month(self, year: int, month: int) -> int:
        """Get the last day of a given month and year."""
        from calendar import monthrange
        return monthrange(year, month)[1]
    
    def _is_period_exact_months(self, start_date: date, end_date: date) -> bool:
        """
        Check if a period represents exact months (e.g., July 1 to March 31).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            bool: True if the period represents exact months
        """
        # Check if start is the 1st of a month and end is the last day of a month
        start_is_first = start_date.day == 1
        end_is_last = end_date.day == self._get_last_day_of_month(end_date.year, end_date.month)
        
        return start_is_first and end_is_last
    
    def _calculate_exact_months(self, start_date: date, end_date: date) -> float:
        """
        Calculate exact months for periods that start on 1st and end on last day of month.
        
        Args:
            start_date: Start date (should be 1st of month)
            end_date: End date (should be last day of month)
            
        Returns:
            float: Exact number of months
        """
        start_year, start_month = start_date.year, start_date.month
        end_year, end_month = end_date.year, end_date.month
        
        # Calculate total months between the two dates
        # For example: July 2025 to March 2026
        # July (7) to December (12) = 6 months (Jul, Aug, Sep, Oct, Nov, Dec)
        # January (1) to March (3) = 3 months (Jan, Feb, Mar)
        # Total = 6 + 3 = 9 months
        
        if end_year == start_year:
            # Same year: just count months from start_month to end_month (inclusive)
            months_diff = end_month - start_month + 1
        else:
            # Different years: months from start_month to December + months from January to end_month
            months_from_start_year = 12 - start_month + 1  # Months from start_month to December (inclusive)
            months_from_end_year = end_month  # Months from January to end_month (inclusive)
            months_from_intermediate_years = max(0, (end_year - start_year - 1) * 12)  # Complete years in between
            
            months_diff = months_from_start_year + months_from_intermediate_years + months_from_end_year
        
        return float(months_diff)
    
    def _update_annual_salary_income(self) -> None:
        """
        Update the annual_salary_income field based on all salary incomes and their effective months.
        This creates a weighted average salary income that represents the annual equivalent.
        """
        from decimal import Decimal
        from copy import deepcopy
        
        # Get financial year boundaries
        financial_year_start = self.tax_year.get_start_date()
        financial_year_end = self.tax_year.get_end_date()
        
        # Calculate total months and weighted components
        total_months = Decimal('0')
        weighted_basic_salary = Money.zero()
        weighted_dearness_allowance = Money.zero()
        weighted_hra_provided = Money.zero()
        weighted_special_allowance = Money.zero()
        weighted_commission = Money.zero()
        weighted_pf_employee_contribution = Money.zero()
        weighted_pf_employer_contribution = Money.zero()
        weighted_pf_voluntary_contribution = Money.zero()
        weighted_esi_contribution = Money.zero()
        
        # Track weighted specific allowances
        weighted_specific_allowances = {}
        
        # Process each salary income to calculate weighted averages
        for salary_income in self.salary_incomes:
            # Determine the effective period for this salary income within the financial year
            salary_start = max(
                salary_income.effective_from.date() if salary_income.effective_from else financial_year_start,
                financial_year_start
            )
            salary_end = min(
                salary_income.effective_till.date() if salary_income.effective_till else financial_year_end,
                financial_year_end
            )
            
            # Skip if salary period doesn't overlap with financial year
            if salary_start > financial_year_end or salary_end < financial_year_start:
                continue
            # Calculate the number of months this salary is applicable
            months_applicable = Decimal(str(self._calculate_months_between_dates(salary_start, salary_end)))
            
            if months_applicable > 0:
                # Add weighted components
                total_months += months_applicable
                weighted_basic_salary = weighted_basic_salary.add(
                    salary_income.basic_salary.multiply(months_applicable)
                )
                weighted_dearness_allowance = weighted_dearness_allowance.add(
                    salary_income.dearness_allowance.multiply(months_applicable)
                )
                weighted_hra_provided = weighted_hra_provided.add(
                    salary_income.hra_provided.multiply(months_applicable)
                )
                weighted_special_allowance = weighted_special_allowance.add(
                    salary_income.special_allowance.multiply(months_applicable)
                )
                weighted_commission = weighted_commission.add(
                    salary_income.commission.multiply(months_applicable)
                )
                weighted_pf_employee_contribution = weighted_pf_employee_contribution.add(
                    salary_income.epf_employee.multiply(months_applicable)
                )
                weighted_pf_employer_contribution = weighted_pf_employer_contribution.add(
                    salary_income.epf_employer.multiply(months_applicable)
                )
                weighted_pf_voluntary_contribution = weighted_pf_voluntary_contribution.add(
                    salary_income.vps_employee.multiply(months_applicable)
                )
                weighted_esi_contribution = weighted_esi_contribution.add(
                    salary_income.esi_contribution.multiply(months_applicable)
                )
                
                # Log salary income summary using salary summary table logger
                from app.utils.table_logger import log_salary_summary

                summary_data = {
                    'Start': str(salary_start),
                    'Till': str(salary_end),
                    'Months': str(months_applicable),
                    'Basic': str(salary_income.basic_salary),
                    'DA': str(salary_income.dearness_allowance),
                    'HRA': str(salary_income.hra_provided),
                    'Special': str(salary_income.special_allowance),
                    'Commission': str(salary_income.commission),
                    'EPF Employee': str(salary_income.epf_employee),
                    'EPF Employer': str(salary_income.epf_employer),
                    'VPS Employee': str(salary_income.vps_employee),
                    'ESI': str(salary_income.esi_contribution)
                }

                log_salary_summary("SALARY INCOME SUMMARY", summary_data)
                
                # Handle specific allowances if present
                if salary_income.specific_allowances:
                    self._add_weighted_specific_allowances(
                        weighted_specific_allowances, 
                        salary_income.specific_allowances, 
                        months_applicable
                    )
        
        # Calculate annual totals (do NOT divide by total_months - store actual annual amounts)
        if total_months > 0:
            # Create the annual salary income as weighted total
            # Get the latest salary income as a template
            latest_salary = self.get_latest_salary_income()
            annual_salary = deepcopy(latest_salary)
            
            # Update components with weighted totals (these represent annual amounts)
            # The weighted values already represent total amounts across applicable months
            # Store them as annual amounts, not monthly equivalents
            
            annual_salary.basic_salary = weighted_basic_salary
            annual_salary.dearness_allowance = weighted_dearness_allowance
            annual_salary.hra_provided = weighted_hra_provided
            annual_salary.special_allowance = weighted_special_allowance
            annual_salary.commission = weighted_commission
            annual_salary.epf_employee = weighted_pf_employee_contribution
            annual_salary.epf_employer = weighted_pf_employer_contribution
            annual_salary.vps_employee = weighted_pf_voluntary_contribution
            annual_salary.esi_contribution = weighted_esi_contribution
            
            # Update specific allowances with weighted totals
            if weighted_specific_allowances:
                annual_salary.specific_allowances = self._create_weighted_specific_allowances_annual(
                    weighted_specific_allowances, 
                    latest_salary.specific_allowances
                )
            
            # Set effective dates to cover the entire financial year
            annual_salary.effective_from = datetime.combine(financial_year_start, datetime.min.time())
            annual_salary.effective_till = datetime.combine(financial_year_end, datetime.min.time())
            
            self.annual_salary_income = annual_salary
            
            logger.info(f"Updated annual_salary_income - Total applicable months: {total_months}, Annual gross: {annual_salary.calculate_gross_salary()}")
            
            # Log specific allowances if present
            if annual_salary.specific_allowances:
                total_specific_allowances = annual_salary.specific_allowances.calculate_total_specific_allowances()
                logger.info(f"Annual specific allowances included: {total_specific_allowances}")
        else:
            # If no applicable periods, use the latest salary as fallback
            latest_salary = self.get_latest_salary_income()
            self.annual_salary_income = deepcopy(latest_salary)
            logger.info(f"No applicable periods found, using latest salary as annual_salary_income")
    
    def _add_weighted_specific_allowances(self, weighted_allowances: dict, specific_allowances, months_applicable: Decimal) -> None:
        """
        Add weighted specific allowances to the accumulator dictionary.
        
        Args:
            weighted_allowances: Dictionary to accumulate weighted allowances
            specific_allowances: SpecificAllowances object from salary income
            months_applicable: Number of months this salary is applicable
        """
        # List of all specific allowance fields
        allowance_fields = [
            'hills_allowance', 'hills_exemption_limit', 'border_allowance', 'border_exemption_limit',
            'transport_employee_allowance', 'children_education_allowance', 'hostel_allowance',
            'disabled_transport_allowance', 'underground_mines_allowance', 'government_entertainment_allowance',
            'city_compensatory_allowance', 'rural_allowance', 'proctorship_allowance', 'wardenship_allowance',
            'project_allowance', 'deputation_allowance', 'overtime_allowance', 'interim_relief',
            'tiffin_allowance', 'fixed_medical_allowance', 'servant_allowance', 'any_other_allowance',
            'any_other_allowance_exemption', 'govt_employees_outside_india_allowance',
            'supreme_high_court_judges_allowance', 'judge_compensatory_allowance',
            'section_10_14_special_allowances', 'travel_on_tour_allowance', 'tour_daily_charge_allowance',
            'conveyance_in_performace_of_duties', 'helper_in_performace_of_duties', 'academic_research',
            'uniform_allowance'
        ]
        
        # Integer fields that need special handling
        integer_fields = [
            'children_education_count', 'children_hostel_count'
        ]
        
        # Boolean fields that need special handling
        boolean_fields = ['is_disabled']
        
        # Accumulate weighted money values
        for field in allowance_fields:
            if hasattr(specific_allowances, field):
                field_value = getattr(specific_allowances, field)
                if field_value and hasattr(field_value, 'multiply'):  # Money object
                    if field not in weighted_allowances:
                        weighted_allowances[field] = Money.zero()
                    weighted_allowances[field] = weighted_allowances[field].add(
                        field_value.multiply(months_applicable)
                    )
        
        # Handle integer fields (use latest values, don't weight them)
        for field in integer_fields:
            if hasattr(specific_allowances, field):
                weighted_allowances[field] = getattr(specific_allowances, field)
        
        # Handle boolean fields (use latest values, don't weight them)
        for field in boolean_fields:
            if hasattr(specific_allowances, field):
                weighted_allowances[field] = getattr(specific_allowances, field)
    
    def _create_weighted_specific_allowances_annual(self, weighted_allowances: dict, template_allowances) -> 'SpecificAllowances':
        """
        Create a SpecificAllowances object with weighted annual total values.
        
        Args:
            weighted_allowances: Dictionary with accumulated weighted allowances (already annual totals)
            template_allowances: Template SpecificAllowances object to copy structure from
            
        Returns:
            SpecificAllowances: New object with weighted annual total values
        """
        from copy import deepcopy
        from app.domain.entities.taxation.salary_income import SpecificAllowances
        
        # Create a new SpecificAllowances object
        if template_allowances:
            annual_allowances = deepcopy(template_allowances)
        else:
            annual_allowances = SpecificAllowances()
        
        # List of money fields to update with weighted annual totals
        money_fields = [
            'hills_allowance', 'hills_exemption_limit', 'border_allowance', 'border_exemption_limit',
            'transport_employee_allowance', 'children_education_allowance', 'hostel_allowance',
            'disabled_transport_allowance', 'underground_mines_allowance', 'government_entertainment_allowance',
            'city_compensatory_allowance', 'rural_allowance', 'proctorship_allowance', 'wardenship_allowance',
            'project_allowance', 'deputation_allowance', 'overtime_allowance', 'interim_relief',
            'tiffin_allowance', 'fixed_medical_allowance', 'servant_allowance', 'any_other_allowance',
            'any_other_allowance_exemption', 'govt_employees_outside_india_allowance',
            'supreme_high_court_judges_allowance', 'judge_compensatory_allowance',
            'section_10_14_special_allowances', 'travel_on_tour_allowance', 'tour_daily_charge_allowance',
            'conveyance_in_performace_of_duties', 'helper_in_performace_of_duties', 'academic_research',
            'uniform_allowance'
        ]
        
        # Update money fields with annual totals (do NOT divide by total_months)
        for field in money_fields:
            if field in weighted_allowances:
                annual_total = weighted_allowances[field]  # Already represents annual total
                setattr(annual_allowances, field, annual_total)
        
        # Update integer and boolean fields (these were set to latest values)
        integer_and_boolean_fields = [
            'children_education_count', 'children_hostel_count'
        ]
        
        for field in integer_and_boolean_fields:
            if field in weighted_allowances:
                setattr(annual_allowances, field, weighted_allowances[field])
        
        return annual_allowances
    
    def _create_weighted_specific_allowances(self, weighted_allowances: dict, total_months: Decimal, template_allowances) -> 'SpecificAllowances':
        """
        Create a SpecificAllowances object with weighted average values.
        
        Args:
            weighted_allowances: Dictionary with accumulated weighted allowances
            total_months: Total months across all salary periods
            template_allowances: Template SpecificAllowances object to copy structure from
            
        Returns:
            SpecificAllowances: New object with weighted average values
        """
        from copy import deepcopy
        from app.domain.entities.taxation.salary_income import SpecificAllowances
        
        # Create a new SpecificAllowances object
        if template_allowances:
            annual_allowances = deepcopy(template_allowances)
        else:
            annual_allowances = SpecificAllowances()
        
        # List of money fields to update with weighted averages
        money_fields = [
            'hills_allowance', 'hills_exemption_limit', 'border_allowance', 'border_exemption_limit',
            'transport_employee_allowance', 'children_education_allowance', 'hostel_allowance',
            'disabled_transport_allowance', 'underground_mines_allowance', 'government_entertainment_allowance',
            'city_compensatory_allowance', 'rural_allowance', 'proctorship_allowance', 'wardenship_allowance',
            'project_allowance', 'deputation_allowance', 'overtime_allowance', 'interim_relief',
            'tiffin_allowance', 'fixed_medical_allowance', 'servant_allowance', 'any_other_allowance',
            'any_other_allowance_exemption', 'govt_employees_outside_india_allowance',
            'supreme_high_court_judges_allowance', 'judge_compensatory_allowance',
            'section_10_14_special_allowances', 'travel_on_tour_allowance', 'tour_daily_charge_allowance',
            'conveyance_in_performace_of_duties', 'helper_in_performace_of_duties', 'academic_research',
            'uniform_allowance'
        ]
        
        # Update money fields with weighted averages
        for field in money_fields:
            if field in weighted_allowances:
                weighted_value = weighted_allowances[field].divide(total_months)
                setattr(annual_allowances, field, weighted_value)
        
        # Update integer and boolean fields (these were set to latest values)
        integer_and_boolean_fields = [
            'children_education_count', 'children_hostel_count'
        ]
        
        for field in integer_and_boolean_fields:
            if field in weighted_allowances:
                setattr(annual_allowances, field, weighted_allowances[field])
        
        return annual_allowances
    
    def _get_uncovered_months(self, covered_periods: list, projection_start: date, projection_end: date) -> float:
        """
        Calculate uncovered months that need salary projection.
        
        Args:
            covered_periods: List of periods already covered by salary incomes
            projection_start: Start date for projection period
            projection_end: End date for projection period
            
        Returns:
            float: Number of uncovered months
        """
        if projection_start >= projection_end:
            return 0.0
        
        # For simplicity, calculate the projection period months
        # This assumes that existing salary incomes cover the past periods completely
        # and we need to project for the remaining future period
        
        total_projection_months = self._calculate_months_between_dates(projection_start, projection_end)
        
        # Check if current date is after all covered periods
        latest_covered_end = None
        for period in covered_periods:
            if latest_covered_end is None or period['end'] > latest_covered_end:
                latest_covered_end = period['end']
        
        if latest_covered_end and latest_covered_end >= projection_start:
            # Calculate only the period after the latest covered end
            actual_projection_start = max(latest_covered_end + timedelta(days=1), projection_start)
            if actual_projection_start <= projection_end:
                return self._calculate_months_between_dates(actual_projection_start, projection_end)
            else:
                return 0.0
        else:
            return total_projection_months
        

    def _get_gross_salary_income(self) -> Money:
        """
        Get the gross salary of the employee.
        
        Returns:
            Money: Gross salary of the employee
        """
        total = self.get_annual_salary_income().calculate_gross_salary()
        logger.info(f"TheOne: Annual Salary Income: {total}")
        ##compute one time arrear and one time bonus for all the MonthlySalary records
        for monthly_salary in self.monthly_salary_records:
            # Log monthly salary data using table logger
            from app.utils.table_logger import log_simple_table
            
            headers = ['Month', 'Bonus', 'Arrear']
            data = [[
                str(monthly_salary.month),
                str(monthly_salary.one_time_bonus),
                str(monthly_salary.one_time_arrear)
            ]]
            
            log_simple_table("MONTHLY SALARY BONUS & ARREAR", data, headers)
            total = total.add(monthly_salary.one_time_arrear).add(monthly_salary.one_time_bonus)
        logger.info(f"*********************************************************************************************************")
        logger.info(f"Total: {total}")
        logger.info(f"*********************************************************************************************************")
        return total
    
    def get_pf_employee_contribution(self) -> Money:
        """
        Get the PF employee contribution.
        """
        return self.get_annual_salary_income().get_pf_employee_contribution()
    
    def additional_tax_liability(self) -> Money:
        """
        Calculate additional tax liability from all sources.
        
        Returns:
            Money: Additional tax liability from all sources
        """
        if self.capital_gains_income:
            return self.capital_gains_income.calculate_stcg_111a_tax().add(self.capital_gains_income.calculate_ltcg_112a_tax())
        return Money.zero()

    def calculate_professional_tax(self, gross_salary: Money) -> Money:
        """
        Calculate professional tax.
        """
        if gross_salary > Money(10000):
            return Money(150).multiply(12)
        elif gross_salary > Money(15000):
            return Money(200).multiply(12)
        
        return Money.zero()


    def calculate_tds_deducted_till_date(self) -> Money:
        """
        Calculate TDS deducted till date.
        """
        tds_deducted_till_date = Money.zero()
        for monthly_salary in self.monthly_salary_records:
            # Log TDS status data using table logger
            from app.utils.table_logger import log_simple_table
            
            headers = ['Month', 'TDS Status', 'TDS Amount']
            data = [[
                str(monthly_salary.month),
                str(monthly_salary.tds_status.status),
                str(monthly_salary.tds_status.total_tax_liability)
            ]]
            
            log_simple_table("TDS STATUS DETAILS", data, headers)
            if monthly_salary.tds_status.status == 'paid':
                tds_deducted_till_date = tds_deducted_till_date.add(monthly_salary.tds_status.total_tax_liability)
            else:
                break
        return tds_deducted_till_date

    def calculate_tax(self, calculation_service: TaxCalculationService, computing_month: int = datetime.now().month) -> TaxCalculationResult:
        """
        Calculate tax using domain service and update SalaryPackageRecord with results.
        
        Args:
            calculation_service: Tax calculation service
            
        Returns:
            TaxCalculationResult: Complete calculation result
        """
        gross_income = self.calculate_gross_income()
        logger.info(f"TheOne: Total income: {gross_income}")
        
        # Calculate total exemptions
        total_exemptions = self.calculate_exemptions()
        logger.info(f"TheOne: Total exemptions: {total_exemptions}")

        # Calculate total deductions
        total_deductions = self.deductions.calculate_total_deductions(self.regime, self.age, 
                                gross_income, self.get_pf_employee_contribution())
        
        logger.info(f"TheOne: Total deductions: {total_deductions}")

        income_after_exemptions = gross_income.subtract(total_exemptions)
        logger.info(f"TheOne: Income after exemptions: {income_after_exemptions}")

        taxable_income = income_after_exemptions.subtract(total_deductions)
        logger.info(f"TheOne: Taxable income: {taxable_income}")
        
        # Perform tax calculation
        tax_amount, surcharge, cess, total_tax = calculation_service._calculate_tax_liability(
            taxable_income,
            self.regime,
            self.age,
            self.additional_tax_liability()
        )
        #Keeping professional tax here not with additional tax liability as Cess is not applicable on professional tax
        professional_tax = self.calculate_professional_tax(gross_income)

        tds_deducted_till_date = self.calculate_tds_deducted_till_date()
        tds_remaining = total_tax.subtract(tds_deducted_till_date)
        #get remaing months in current year
        months_passed = computing_month - 4#(april is 4th month)
        remaining_months = 12 - months_passed
        if remaining_months == 0:
            monthly_tax = total_tax.divide(Decimal('12')) 
        else:
            monthly_tax = tds_remaining.divide(remaining_months)

        monthly_tax = monthly_tax.add(professional_tax.divide(Decimal('12')))   
        
        # Create simplified tax breakdown
        tax_breakdown = {
            "income_details": {
                "gross_income": gross_income.to_float(),
                "total_exemptions": total_exemptions.to_float(),
                "income_after_exemptions": income_after_exemptions.to_float(),
                "total_deductions": total_deductions.to_float(),
                "taxable_income": taxable_income.to_float()
            },
            "tax_calculation": {
                "regime": self.regime.regime_type.value,
                "basic_tax": tax_amount.to_float(),
                "professional_tax": professional_tax.to_float(),
                "surcharge": surcharge.to_float(),
                "cess": cess.to_float(),
                "total_tax": total_tax.to_float() + professional_tax.to_float()
            },
            "summary": {
                "effective_tax_rate": ((total_tax.to_float() + professional_tax.to_float()) / gross_income.to_float() * 100) if not gross_income.is_zero() else 0.0,
                "monthly_tax": monthly_tax.to_float()
            }
        }
        
        # Create TaxCalculationResult
        self.calculation_result = TaxCalculationResult(
            total_income=gross_income,
            total_exemptions=total_exemptions,
            total_deductions=total_deductions,
            taxable_income=taxable_income,
            professional_tax=professional_tax,
            tax_amount=tax_amount,
            surcharge=surcharge,
            cess=cess,
            tax_liability=total_tax,
            tax_breakdown=tax_breakdown,
            regime_comparison=None
        )
        
        print(f"**************************************************")
        print(f"TheOne: Result: {self.calculation_result}")
        print(f"**************************************************")
        
        # Update metadata
        self.last_calculated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "TaxCalculated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "tax_amount": self.calculation_result.total_tax_liability.to_float(),
            "regime": self.regime.regime_type.value,
            "calculated_at": self.last_calculated_at.isoformat()
        })
        
        return self.calculation_result

    def get_calculation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the calculation results stored in the SalaryPackageRecord.
        
        Returns:
            Dict[str, Any]: Summary of calculation results
        """
        if not self.calculation_result:
            return {
                "status": "no_calculation",
                "message": "No calculation result available"
            }
        
        return {
            "status": "calculated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "regime": self.regime.regime_type.value,
            "gross_income": getattr(self, '_calculated_gross_income', Money.zero()).to_float(),
            "total_exemptions": getattr(self, '_calculated_total_exemptions', Money.zero()).to_float(),
            "total_deductions": getattr(self, '_calculated_total_deductions', Money.zero()).to_float(),
            "taxable_income": getattr(self, '_calculated_taxable_income', Money.zero()).to_float(),
            "tax_liability": getattr(self, '_calculated_tax_liability', Money.zero()).to_float(),
            "monthly_tax": getattr(self, '_calculated_monthly_tax', Money.zero()).to_float(),
            "effective_tax_rate": getattr(self, '_calculated_effective_tax_rate', 0.0),
            "last_calculated": self.last_calculated_at.isoformat() if self.last_calculated_at else None,
            "calculation_valid": self.is_calculation_valid()
        }
    
    def calculate_basic_plus_da(self) -> Money:
        """
        Calculate basic plus DA from all sources.
        
        Returns:
            Money: Total basic plus DA from all sources
        """
        basic_plus_da = self.annual_salary_income.calculate_basic_plus_da()
        return basic_plus_da
    
    def calculate_gross_income(self) -> Money:
        """
        Calculate comprehensive gross income from all sources.
        
        Returns:
            Money: Total gross income from all sources
        """
        total_income = Money.zero()
        # Calculate comprehensive gross income
        gross_salary_income = self._get_gross_salary_income()
        total_income = total_income.add(gross_salary_income)
        summary_data = {
            'gross_salary_income': gross_salary_income
        }

        # Other income (if any) - now includes house property income and capital gains
        if self.other_income:
            other_income_slab_amount = self.other_income.calculate_total_other_income_slab_rates(self.regime, self.age)
            total_income = total_income.add(other_income_slab_amount)
            summary_data['other_income_slab_amount'] = other_income_slab_amount
            adjustments_less = Money.zero()
            # Fix: Check if house_property_income is not None before calling get_house_property_loss
            if self.other_income.house_property_income is not None:
                adjustments_less = self.other_income.house_property_income.get_house_property_loss(self.regime)
                summary_data['adjustments_less (-) House Property Loss'] = adjustments_less
            total_income = total_income.subtract(adjustments_less)
                    
        # Perquisites (if any)
        if self.perquisites:
            total_income = total_income.add(self.perquisites.calculate_total_perquisites(self.regime, self.calculate_basic_plus_da()))
        
        # Retirement benefits (if any)
        if self.retirement_benefits:
            total_income = total_income.add(self.retirement_benefits.calculate_total_retirement_income(self.regime, self.is_government_employee, self.age))
        
        # Log the summary table
        summary_data['Total_Gross_Income'] = total_income
        from app.utils.table_logger import log_salary_summary
        log_salary_summary("GROSS INCOME SUMMARY", summary_data)

        return total_income

    def calculate_exemptions(self) -> Money:
        """
        Calculate comprehensive exemptions from all sources.
        
        Returns:
            Money: Total exemptions from all sources
        """
        total_exemptions = Money.zero()
        summary_data = {}
        # Salary exemptions (core) - use latest salary income
        core_salary_exemptions = self.annual_salary_income.calculate_total_exemptions(self.regime, self.is_government_employee)
        summary_data['core_salary_exemptions'] = core_salary_exemptions

        salary_standard_deduction = self.regime.get_standard_deduction()
        total_exemptions = total_exemptions.add(core_salary_exemptions).add(salary_standard_deduction)
        summary_data['salary_standard_deduction'] = salary_standard_deduction

        # Retirement benefits exemptions
        if self.retirement_benefits:
            retirement_benefits_exemptions = self.retirement_benefits.calculate_total_exemptions(self.regime, self.age)
            total_exemptions = total_exemptions.add(retirement_benefits_exemptions)
            summary_data['retirement_benefits_exemptions'] = retirement_benefits_exemptions
        # Other income exemptions (interest exemptions)
        if self.other_income:
            other_income_exemptions = self.other_income.calculate_interest_exemptions(self.regime, self.age)
            total_exemptions = total_exemptions.add(other_income_exemptions)
            summary_data['other_income_exemptions'] = other_income_exemptions
        
        summary_data['Total Exemptions'] = total_exemptions

        # Log the summary table
        from app.utils.table_logger import log_salary_summary
        log_salary_summary("EXEMPTIONS SUMMARY", summary_data)

        return total_exemptions
    
    def update_perquisites(self, new_perquisites: Optional[Perquisites]) -> None:
        """
        Update perquisites information.
        
        Args:
            new_perquisites: New perquisites details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_value = Money.zero()
        if self.perquisites:
            old_value = self.perquisites.calculate_total_perquisites(self.regime)
        
        self.perquisites = new_perquisites
        
        new_value = Money.zero()
        if new_perquisites:
            new_value = new_perquisites.calculate_total_perquisites(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "PerquisitesUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_perquisites_value": old_value.to_float(),
            "new_perquisites_value": new_value.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_house_property_income(self, new_house_property: Optional[HousePropertyIncome]) -> None:
        """
        Update house property income information.
        
        Args:
            new_house_property: New house property income details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_income = Money.zero()
        if self.other_income and self.other_income.house_property_income:
            old_income = self.other_income.house_property_income.calculate_net_income_from_house_property(self.regime)
        
        # Ensure other_income exists
        if not self.other_income:
            from app.domain.entities.taxation.other_income import OtherIncome
            self.other_income = OtherIncome()
        
        self.other_income.house_property_income = new_house_property
        
        new_income = Money.zero()
        if new_house_property:
            new_income = new_house_property.calculate_net_income_from_house_property(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "HousePropertyIncomeUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_house_property_income": old_income.to_float(),
            "new_house_property_income": new_income.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_retirement_benefits(self, new_retirement_benefits: Optional[RetirementBenefits]) -> None:
        """
        Update retirement benefits information.
        
        Args:
            new_retirement_benefits: New retirement benefits details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_benefits = Money.zero()
        if self.retirement_benefits:
            old_benefits = self.retirement_benefits.calculate_total_retirement_income(self.regime, self.is_government_employee, self.age)
        
        self.retirement_benefits = new_retirement_benefits
        
        new_benefits = Money.zero()
        if new_retirement_benefits:
            new_benefits = new_retirement_benefits.calculate_total_retirement_income(self.regime, self.is_government_employee, self.age)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "RetirementBenefitsUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_retirement_benefits": old_benefits.to_float(),
            "new_retirement_benefits": new_benefits.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_other_income(self, new_other_income: Optional[OtherIncome]) -> None:
        """
        Update other income information.
        
        Args:
            new_other_income: New other income details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_income = Money.zero()
        if self.other_income:
            old_income = self.other_income.calculate_total_other_income(self.regime, self.age)
        
        self.other_income = new_other_income
        
        new_income = Money.zero()
        if new_other_income:
            new_income = new_other_income.calculate_total_other_income(self.regime, self.age)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "OtherIncomeUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_other_income": old_income.to_float(),
            "new_other_income": new_income.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_deductions(self, new_deductions: TaxDeductions) -> None:
        """
        Update deduction information.
        
        Args:
            new_deductions: New deduction details
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        # Calculate gross income for deduction calculations
        gross_income = self.calculate_gross_income()
        old_deductions = self.deductions.calculate_total_deductions(self.regime, self.age, gross_income, self.get_pf_employee_contribution())
        self.deductions = new_deductions
        new_deductions_total = new_deductions.calculate_total_deductions(self.regime, self.age, gross_income, self.get_pf_employee_contribution())
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "DeductionsUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_deductions": old_deductions.to_float(),
            "new_deductions": new_deductions_total.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def finalize_record(self) -> None:
        """
        Finalize the salary package record (no further changes allowed).
        """
        if not self.is_calculation_valid():
            raise ValueError("Cannot finalize record without valid calculation")
        
        self.is_final = True
        self.submitted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryPackageRecordFinalized",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "total_tax": self.calculation_result.total_tax_liability.to_float() if self.calculation_result else 0.0,
            "finalized_at": self.submitted_at.isoformat()
        })
    
    def reopen_record(self) -> None:
        """
        Reopen a finalized record for modifications.
        """
        if not self.is_final:
            return  # Already open
        
        self.is_final = False
        self.submitted_at = None
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryPackageRecordReopened",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "reopened_at": self.updated_at.isoformat()
        })
    
    def _invalidate_calculation(self) -> None:
        """Invalidate current calculation and update metadata."""
        self.calculation_result = None
        self.last_calculated_at = None
        self.updated_at = datetime.utcnow()
        self.version += 1
    
    def _add_domain_event(self, event: Dict[str, Any]) -> None:
        """Add a domain event."""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Dict[str, Any]]:
        """Get all domain events."""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after processing."""
        self._domain_events.clear()
    
    def is_calculation_valid(self) -> bool:
        """
        Check if current calculation is valid.
        
        Returns:
            bool: True if calculation is current and valid
        """
        return (self.calculation_result is not None and 
                self.last_calculated_at is not None and
                self.last_calculated_at >= self.updated_at)
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """
        Get tax summary for display.
        
        Returns:
            Dict: Tax summary information
        """
        if not self.is_calculation_valid():
            return {
                "status": "calculation_required",
                "employee_id": str(self.employee_id),
                "tax_year": str(self.tax_year),
                "regime": self.regime.regime_type.value,
                "is_final": self.is_final,
                "salary_incomes_count": len(self.salary_incomes)
            }
        
        return {
            "status": "calculated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "regime": self.regime.regime_type.value,
            "is_final": self.is_final,
            "gross_income": self.calculation_result.gross_income.to_float(),
            "taxable_income": self.calculation_result.taxable_income.to_float(),
            "total_tax_liability": self.calculation_result.total_tax_liability.to_float(),
            "monthly_tax": self.calculation_result.monthly_tax_liability.to_float(),
            "effective_tax_rate": f"{self.calculation_result.effective_tax_rate:.2f}%",
            "last_calculated": self.last_calculated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "salary_incomes_count": len(self.salary_incomes)
        }
    
    def get_detailed_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed tax breakdown.
        
        Returns:
            Dict: Complete tax calculation breakdown
        """
        if not self.is_calculation_valid():
            raise ValueError("No valid calculation available")
        
        result = {
            "salary_package_record": {
                "employee_id": str(self.employee_id),
                "tax_year": str(self.tax_year),
                "age": self.age,
                "regime": self.regime.regime_type.value,
                "is_final": self.is_final,
                "last_calculated": self.last_calculated_at.isoformat(),
                "salary_incomes_count": len(self.salary_incomes),
                "has_comprehensive_income": self.has_comprehensive_income()
            },
            "income_breakdown": self.get_comprehensive_income_breakdown(),
            "deduction_breakdown": self.deductions.get_deduction_breakdown(self.regime),
            "tax_calculation": self.calculation_result.calculation_breakdown,
            "validation_warnings": self._get_validation_warnings()
        }
        
        # Add separate capital gains tax if applicable
        if self.other_income and self.other_income.capital_gains_income:
            result["separate_capital_gains_tax"] = self.calculate_separate_capital_gains_tax().to_float()
        
        return result
    
    def has_comprehensive_income(self) -> bool:
        """
        Check if the record has any comprehensive income components beyond basic salary.
        
        Returns:
            bool: True if has any comprehensive income components
        """
        return any([
            self.perquisites is not None,
            self.other_income is not None and (
                self.other_income.house_property_income is not None or
                not self.other_income.dividend_income.is_zero() or
                not self.other_income.business_professional_income.is_zero() or
                not self.other_income.other_miscellaneous_income.is_zero() or
                not self.other_income.gifts_received.is_zero()
            ),
            self.other_income and self.other_income.capital_gains_income is not None,
            self.retirement_benefits is not None
        ])
    
    def calculate_separate_capital_gains_tax(self) -> Money:
        """
        Calculate capital gains tax that's charged separately (not at slab rates).
        
        Returns:
            Money: Separate capital gains tax
        """
        if not self.other_income or not self.other_income.capital_gains_income:
            return Money.zero()
        
        return self.other_income.capital_gains_income.calculate_total_capital_gains_tax()
    
    def get_comprehensive_income_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of all income sources.
        
        Returns:
            Dict: Comprehensive income breakdown
        """
        latest_salary = self.get_latest_salary_income()
        
        breakdown = {
            "salary_income": {
                "gross_salary": latest_salary.calculate_gross_salary().to_float(),
                "exemptions": latest_salary.calculate_total_exemptions(self.regime, self.is_government_employee).to_float(),
                "breakdown": latest_salary.get_salary_breakdown(self.regime, self.is_government_employee),
                "salary_incomes_count": len(self.salary_incomes),
                "salary_history": [
                    {
                        "index": i,
                        "gross_salary": salary.calculate_gross_salary().to_float(),
                        "basic_salary": salary.basic_salary.to_float(),
                        "special_allowance": salary.special_allowance.to_float()
                    }
                    for i, salary in enumerate(self.salary_incomes)
                ]
            }
        }
        
        if self.perquisites:
            breakdown["perquisites"] = {
                "total_value": self.perquisites.calculate_total_perquisites(self.regime).to_float(),
                "breakdown": self.perquisites.get_perquisites_breakdown(self.regime)
            }
        
        if self.other_income and self.other_income.capital_gains_income:
            breakdown["capital_gains_income"] = {
                "slab_rate_income": self.other_income.capital_gains_income.calculate_stcg_for_slab_rates().to_float(),
                "separate_tax": self.other_income.capital_gains_income.calculate_total_capital_gains_tax().to_float(),
                "breakdown": self.other_income.capital_gains_income.get_capital_gains_breakdown(self.regime)
            }
        
        if self.retirement_benefits:
            breakdown["retirement_benefits"] = {
                "taxable_amount": self.retirement_benefits.calculate_total_retirement_income(self.regime, self.is_government_employee, self.age).to_float(),
                "exemptions": self.retirement_benefits.calculate_total_exemptions(self.regime, self.age).to_float(),
                "breakdown": self.retirement_benefits.get_retirement_benefits_breakdown(self.regime, self.age)
            }
        
        if self.other_income:
            breakdown["other_income"] = {
                "taxable_amount": self.other_income.calculate_total_other_income(self.regime, self.age).to_float(),
                "exemptions": self.other_income.calculate_interest_exemptions(self.regime, self.age).to_float(),
                "breakdown": self.other_income.get_other_income_breakdown(self.regime, self.age)
            }
        
        return breakdown
    
    def _get_validation_warnings(self) -> List[str]:
        """Get validation warnings for the salary package record."""
        warnings = []
        
        # HRA validation warnings
        latest_salary = self.get_latest_salary_income()
        hra_warnings = latest_salary.validate_hra_details()
        warnings.extend(hra_warnings.values())
        
        # Deduction warnings
        if self.regime.allows_deductions():
            # Check if deductions are underutilized
            gross_income = self.calculate_gross_income()
            total_deductions = self.deductions.calculate_total_deductions(self.regime, self.age, gross_income, self.get_pf_employee_contribution())
            if total_deductions.is_less_than(Money.from_int(100000)):  # Less than 1 lakh
                warnings.append("Consider maximizing tax-saving investments under Section 80C")
            
            # 80D warnings
            current_80d = self.deductions.section_80d.calculate_eligible_deduction(self.regime)
            if current_80d.is_zero():
                warnings.append("Consider health insurance for additional tax savings under Section 80D")
        
        # Age-based warnings
        if self.age >= 60 and self.regime.regime_type.value == "new":
            warnings.append("Senior citizens may benefit more from the old tax regime")
        
        # Salary history warnings
        if len(self.salary_incomes) > 1:
            warnings.append(f"Multiple salary revisions detected ({len(self.salary_incomes)} versions)")
        
        return warnings