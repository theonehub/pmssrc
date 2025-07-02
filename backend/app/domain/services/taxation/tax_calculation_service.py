"""
Tax Calculation Service
Handles all tax calculations for Indian taxation
"""

import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.value_objects.employee_id import EmployeeId
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TaxCalculationInput:
    """Input for tax calculation."""
    salary_income: SalaryIncome
    perquisites: Perquisites
    capital_gains_income: CapitalGainsIncome
    retirement_benefits: RetirementBenefits
    other_income: OtherIncome
    deductions: TaxDeductions
    regime: TaxRegime
    age: int
    is_senior_citizen: bool
    is_super_senior_citizen: bool
    is_government_employee: bool


@dataclass
class TaxCalculationResult:
    """Result of tax calculation."""
    total_income: Money
    total_exemptions: Money
    total_deductions: Money
    taxable_income: Money
    tax_liability: Money
    tax_breakdown: Dict[str, Any]
    regime_comparison: Optional[Dict[str, Any]] = None
    monthly_payroll: Optional[Any] = None  # Add monthly payroll projection
    
    def __post_init__(self):
        """Validate that all monetary fields are Money objects."""
        from app.domain.value_objects.money import Money
        
        # Check that all monetary fields are Money objects
        if not isinstance(self.total_income, Money):
            raise ValueError(f"total_income must be a Money object, got {type(self.total_income)}")
        if not isinstance(self.total_exemptions, Money):
            raise ValueError(f"total_exemptions must be a Money object, got {type(self.total_exemptions)}")
        if not isinstance(self.total_deductions, Money):
            raise ValueError(f"total_deductions must be a Money object, got {type(self.total_deductions)}")
        if not isinstance(self.taxable_income, Money):
            raise ValueError(f"taxable_income must be a Money object, got {type(self.taxable_income)}")
        if not isinstance(self.tax_liability, Money):
            raise ValueError(f"tax_liability must be a Money object, got {type(self.tax_liability)}")

    # Additional convenience properties
    @property
    def gross_income(self) -> Money:
        """Alias for total_income for backward compatibility."""
        return self.total_income
    
    @property
    def total_tax_liability(self) -> Money:
        """Alias for tax_liability for backward compatibility."""
        return self.tax_liability
    
    @property
    def monthly_tax_liability(self) -> Money:
        """Calculate monthly tax liability."""
        return self.tax_liability.divide(Decimal('12'))
    
    @property
    def effective_tax_rate(self) -> float:
        """Calculate effective tax rate as percentage."""
        if self.total_income.is_zero():
            return 0.0
        return (self.tax_liability.to_float() / self.total_income.to_float()) * 100
    
    @property
    def calculation_breakdown(self) -> Dict[str, Any]:
        """Alias for tax_breakdown for backward compatibility."""
        return self.tax_breakdown


class TaxCalculationService:
    """Service for calculating taxes."""
    
    def __init__(self, salary_package_repository=None, user_repository=None):
        """
        Initialize the service.
        
        Args:
            salary_package_repository: Optional salary package repository for monthly computation
            user_repository: Optional user repository for employee info
        """
        self.salary_package_repository = salary_package_repository
        self.user_repository = user_repository
        self.logger = get_logger(__name__)


    async def compute_monthly_tax(self, employee_id: str, organization_id: str) -> Dict[str, Any]:
        """
        Compute monthly tax for an employee based on their salary package record.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID for database segregation
            
        Returns:
            Dict[str, Any]: Monthly tax computation result
            
        Raises:
            ValueError: If required data is not found or invalid
            RuntimeError: If computation fails
        """
        
        try:
            # Get current month and year for computation
            from datetime import datetime
            now = datetime.now()
            month = now.month
            year = now.year
            
            self.logger.debug(f"compute_monthly_tax: Using current month={month}, year={year}")
            
            # Validate inputs
            from app.domain.value_objects.tax_year import TaxYear
            current_tax_year = TaxYear.current()
            tax_year = str(current_tax_year)
            
            self.logger.debug(f"compute_monthly_tax: Current tax year: {tax_year}")
            
            # Check if required repositories are configured
            if not self.salary_package_repository:
                self.logger.error("compute_monthly_tax: Salary package repository not configured")
                raise ValueError("Salary package repository not configured for monthly tax computation")
            
            self.logger.debug("compute_monthly_tax: Salary package repository is configured")
            
            # Get salary package record for the employee and tax year
            self.logger.debug(f"compute_monthly_tax: Fetching salary package record for employee {employee_id}, tax_year {tax_year}")

            salary_package_record = await self.salary_package_repository.get_salary_package_record(
                employee_id, tax_year, organization_id
            )
            
            if not salary_package_record:
                self.logger.error(f"compute_monthly_tax: No salary package record found for employee {employee_id} in tax year {tax_year}")
                raise ValueError(
                    f"Salary package record not found for employee {employee_id} "
                    f"in tax year {tax_year}. Please ensure salary data is configured."
                )
            
            self.logger.debug(f"compute_monthly_tax: Found salary package record. Salary incomes count: {len(salary_package_record.salary_incomes)}")
            self.logger.debug(f"compute_monthly_tax: Record has perquisites: {salary_package_record.perquisites is not None}")
            self.logger.debug(f"compute_monthly_tax: Record has other_income: {salary_package_record.other_income is not None}")
            self.logger.debug(f"compute_monthly_tax: Record has retirement_benefits: {salary_package_record.retirement_benefits is not None}")
            
            # Compute monthly tax using the salary package record
            self.logger.debug("compute_monthly_tax: Computing monthly tax from salary package record")
            logger.info(f"*********************************************************************************************************")
            calculation_result = salary_package_record.calculate_tax(self)
            
            # Save the updated salary package record with calculation result to database
            self.logger.debug("compute_monthly_tax: Saving updated salary package record to database")
            try:
                await self.salary_package_repository.save(salary_package_record, organization_id)
                self.logger.debug("compute_monthly_tax: Successfully saved updated salary package record to database")
            except Exception as save_error:
                self.logger.error(f"compute_monthly_tax: Failed to save updated salary package record to database: {str(save_error)}")
                # Continue with computation even if save fails
                self.logger.warning("compute_monthly_tax: Continuing with computation despite save failure")
            
            # Extract monthly tax amount from calculation result
            monthly_tax_amount = calculation_result.monthly_tax_liability.to_float()
            self.logger.debug(f"compute_monthly_tax: Monthly tax amount: {monthly_tax_amount}")
            
            # Get additional details from the calculation result
            calculation_details = {}
            if calculation_result:
                self.logger.debug("compute_monthly_tax: Extracting calculation details from salary package record")
                calculation_details = {
                    "annual_gross_income": calculation_result.total_income.to_float(),
                    "annual_exemptions": calculation_result.total_exemptions.to_float(),
                    "annual_deductions": calculation_result.total_deductions.to_float(),
                    "annual_taxable_income": calculation_result.taxable_income.to_float(),
                    "annual_tax_liability": calculation_result.tax_liability.to_float(),
                    "effective_tax_rate": calculation_result.effective_tax_rate,
                    "tax_regime": salary_package_record.regime.regime_type.value,
                    "last_calculated_at": salary_package_record.last_calculated_at.isoformat() if salary_package_record.last_calculated_at else None
                }
                self.logger.debug(f"compute_monthly_tax: Annual gross income: {calculation_details['annual_gross_income']}")
                self.logger.debug(f"compute_monthly_tax: Annual tax liability: {calculation_details['annual_tax_liability']}")
                self.logger.debug(f"compute_monthly_tax: Tax regime: {calculation_details['tax_regime']}")
            else:
                self.logger.warning("compute_monthly_tax: No calculation result available")
            
            # Build comprehensive response
            response = {
                "employee_id": employee_id,
                "computation_month": month,
                "computation_year": year,
                "tax_year": tax_year,
                "monthly_tax_liability": monthly_tax_amount,
                "monthly_tax_formatted": f"₹{monthly_tax_amount:,.2f}",
                "salary_package_info": {
                    "salary_incomes_count": len(salary_package_record.salary_incomes),
                    "has_perquisites": salary_package_record.perquisites is not None,
                    "has_other_income": salary_package_record.other_income is not None,
                    "has_retirement_benefits": salary_package_record.retirement_benefits is not None,
                    "is_comprehensive": salary_package_record.has_comprehensive_income(),
                    "age": salary_package_record.age,
                    "regime": salary_package_record.regime.regime_type.value,
                    "is_government_employee": salary_package_record.is_government_employee
                },
                "calculation_details": calculation_details,
                "status": "computed",
                "computed_at": datetime.utcnow().isoformat()
            }
            
            self.logger.debug("compute_monthly_tax: Built response object with salary package info")
            
            # Add latest salary breakdown
            if salary_package_record.salary_incomes:
                self.logger.debug("compute_monthly_tax: Adding latest salary breakdown")
                latest_salary = salary_package_record.get_latest_salary_income()
                response["latest_salary_info"] = {
                    "basic_salary": latest_salary.basic_salary.to_float(),
                    "hra_provided": latest_salary.hra_provided.to_float(),
                    "special_allowance": latest_salary.special_allowance.to_float(),
                    "bonus": latest_salary.bonus.to_float(),
                    "commission": latest_salary.commission.to_float(),
                    "gross_salary": latest_salary.calculate_gross_salary().to_float()
                }
                self.logger.debug(f"compute_monthly_tax: Latest salary basic: {response['latest_salary_info']['basic_salary']}")
                self.logger.debug(f"compute_monthly_tax: Latest salary gross: {response['latest_salary_info']['gross_salary']}")
            else:
                self.logger.warning("compute_monthly_tax: No salary incomes found in salary package record")
            
            self.logger.debug(f"compute_monthly_tax: Successfully computed monthly tax for employee {employee_id}")
            return response
            
        except ValueError as e:
            self.logger.error(f"compute_monthly_tax: Validation error for employee {employee_id}: {str(e)}")
            # Re-raise validation errors
            raise e
        except Exception as e:
            self.logger.error(f"compute_monthly_tax: Unexpected error for employee {employee_id}: {str(e)}", exc_info=True)
            # Wrap other errors in RuntimeError
            raise RuntimeError(f"Failed to compute monthly tax for employee {employee_id}: {str(e)}")
    
    async def compute_monthly_tax_with_details(self, employee_id: str, organization_id: str) -> Dict[str, Any]:
        """
        Compute monthly tax with detailed breakdown for frontend display.
        
        This is an enhanced version that provides more detailed information
        suitable for frontend tax overview components.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID
            
        Returns:
            Dict[str, Any]: Detailed monthly tax computation result
        """
        
        try:
            # Get basic computation
            basic_result = await self.compute_monthly_tax(employee_id, organization_id)
            
            # Get salary package record for additional details
            tax_year = basic_result["tax_year"]

            self.logger.debug(f"compute_monthly_tax_with_details: Fetching salary package record for additional details - employee {employee_id}, tax_year {tax_year}")
            
            salary_package_record = await self.salary_package_repository.get_salary_package_record(
                employee_id, tax_year, organization_id
            )
            
            if not salary_package_record:
                self.logger.warning(f"compute_monthly_tax_with_details: No salary package record found for detailed breakdown - returning basic result")
                return basic_result
            
            self.logger.debug("compute_monthly_tax_with_details: Building detailed result with additional breakdown")
            
            # Add detailed breakdown
            detailed_result = basic_result.copy()
            
            # Note: The salary package record has already been saved to database in compute_monthly_tax method
            # No additional save needed here as the calculation result is already persisted
            
            # # Add component status
            # self.logger.debug("compute_monthly_tax_with_details: Building component status")
            # detailed_result["component_status"] = {
            #     "salary": {
            #         "configured": len(salary_package_record.salary_incomes) > 0,
            #         "count": len(salary_package_record.salary_incomes)
            #     },
            #     "perquisites": {
            #         "configured": salary_package_record.perquisites is not None,
            #         "value": salary_package_record.perquisites.calculate_total_perquisites(salary_package_record.regime).to_float() if salary_package_record.perquisites else 0.0
            #     },
            #     "deductions": {
            #         "configured": True,  # Always have default deductions
            #         "value": salary_package_record.deductions.calculate_total_deductions(salary_package_record.regime).to_float()
            #     },
            #     "other_income": {
            #         "configured": salary_package_record.other_income is not None,
            #         "value": salary_package_record.other_income.calculate_total_other_income_slab_rates(salary_package_record.regime, salary_package_record.age).to_float() if salary_package_record.other_income else 0.0
            #     },
            #     "retirement_benefits": {
            #         "configured": salary_package_record.retirement_benefits is not None,
            #         "value": salary_package_record.retirement_benefits.calculate_total_retirement_income(salary_package_record.regime).to_float() if salary_package_record.retirement_benefits else 0.0
            #     }
            # }
            
            # self.logger.debug(f"compute_monthly_tax_with_details: Component status - Salary configured: {detailed_result['component_status']['salary']['configured']}")
            # self.logger.debug(f"compute_monthly_tax_with_details: Component status - Perquisites configured: {detailed_result['component_status']['perquisites']['configured']}")
            # self.logger.debug(f"compute_monthly_tax_with_details: Component status - Deductions value: {detailed_result['component_status']['deductions']['value']}")
            
            # Add recommendation - compute fresh calculation result
            # fresh_calculation_result = salary_package_record.calculate_tax(self)
            # if fresh_calculation_result:
            #     self.logger.debug("compute_monthly_tax_with_details: Generating tax recommendation")
            #     monthly_tax = fresh_calculation_result.monthly_tax_liability.to_float()
            #     annual_income = fresh_calculation_result.total_income.to_float()
                
            #     if monthly_tax == 0:
            #         detailed_result["recommendation"] = "No tax liability"
            #         self.logger.debug("compute_monthly_tax_with_details: Recommendation - No tax liability")
            #     elif annual_income > 0:
            #         tax_rate = (monthly_tax * 12 / annual_income) * 100
            #         if tax_rate < 5:
            #             detailed_result["recommendation"] = "Low tax rate - consider new regime"
            #             self.logger.debug(f"compute_monthly_tax_with_details: Recommendation - Low tax rate ({tax_rate:.2f}%)")
            #         elif tax_rate > 20:
            #             detailed_result["recommendation"] = "High tax rate - review deductions"
            #             self.logger.debug(f"compute_monthly_tax_with_details: Recommendation - High tax rate ({tax_rate:.2f}%)")
            #         else:
            #             detailed_result["recommendation"] = "Moderate tax rate"
            #             self.logger.debug(f"compute_monthly_tax_with_details: Recommendation - Moderate tax rate ({tax_rate:.2f}%)")
            #     else:
            #         detailed_result["recommendation"] = "Review income configuration"
            #         self.logger.debug("compute_monthly_tax_with_details: Recommendation - Review income configuration")
            # else:
            #     self.logger.warning("compute_monthly_tax_with_details: No fresh calculation result available for recommendation")
            
            self.logger.debug(f"compute_monthly_tax_with_details: Successfully completed detailed computation for employee {employee_id}")
            return detailed_result
            
        except Exception as e:
            self.logger.error(f"compute_monthly_tax_with_details: Error in detailed computation for employee {employee_id}: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to compute detailed monthly tax for employee {employee_id}: {str(e)}")
    
    def calculate_tax(self, input_data: TaxCalculationInput) -> TaxCalculationResult:
        """
        Calculate tax based on input data.
        
        Args:
            input_data: Tax calculation input data
            
        Returns:
            TaxCalculationResult: Tax calculation result
        """
        # Calculate total income
        total_income = self._calculate_total_income(input_data)
        
        # Calculate total exemptions
        total_exemptions = self._calculate_total_exemptions(input_data)
        
        # Calculate total deductions
        total_deductions = self._calculate_total_deductions(input_data)
        
        # Calculate taxable income
        # First subtract exemptions, then deductions, ensuring we don't go negative
        income_after_exemptions = total_income.subtract(total_exemptions) if total_income.is_greater_than(total_exemptions) else Money.zero()
        taxable_income = income_after_exemptions.subtract(total_deductions) if income_after_exemptions.is_greater_than(total_deductions) else Money.zero()
        
        # Calculate tax liability
        tax_liability = self._calculate_tax_liability(
            taxable_income,
            input_data.regime,
            input_data.age,
            input_data.capital_gains_income.calculate_stcg_111a_tax(),
            input_data.capital_gains_income.calculate_ltcg_112a_tax(),
            input_data.is_senior_citizen,
            input_data.is_super_senior_citizen
        )
        
        # Get tax breakdown
        tax_breakdown = self._get_tax_breakdown(
            total_income,
            total_exemptions,
            total_deductions,
            taxable_income,
            tax_liability,
            input_data
        )
        
        # Skip regime comparison to avoid infinite recursion
        regime_comparison = None
        
        return TaxCalculationResult(
            total_income=total_income,
            total_exemptions=total_exemptions,
            total_deductions=total_deductions,
            taxable_income=taxable_income,
            tax_liability=tax_liability,
            tax_breakdown=tax_breakdown,
            regime_comparison=regime_comparison
        )

    def calculate_income_tax(self, 
                           gross_income: Money,
                           total_exemptions: Money, 
                           total_deductions: Money,
                           stcg_tax: Money,
                           ltcg_tax: Money,
                           regime: TaxRegime, 
                           age: int) -> TaxCalculationResult:
        """
        Calculate income tax with provided totals - method expected by TaxationRecord.
        
        Args:
            gross_income: Total gross income
            total_exemptions: Total exemptions amount
            total_deductions: Total deductions amount
            regime: Tax regime
            age: Employee age
            
        Returns:
            TaxCalculationResult: Tax calculation result
        """
        # Determine citizen categories based on age
        is_senior_citizen = age >= 60
        is_super_senior_citizen = age >= 80
        
        # Calculate taxable income
        income_after_exemptions = gross_income.subtract(total_exemptions) if gross_income.is_greater_than(total_exemptions) else Money.zero()
        taxable_income = income_after_exemptions.subtract(total_deductions) if income_after_exemptions.is_greater_than(total_deductions) else Money.zero()
        logger.info(f"TheOne: Taxable income: {taxable_income.to_float()}")
        
        # Calculate tax liability
        tax_liability = self._calculate_tax_liability(
            taxable_income,
            regime,
            age,
            stcg_tax,
            ltcg_tax,
            is_senior_citizen,
            is_super_senior_citizen
        )
        
        # Create tax breakdown
        tax_breakdown = {
            "income_details": {
                "gross_income": gross_income.to_float(),
                "total_exemptions": total_exemptions.to_float(),
                "income_after_exemptions": income_after_exemptions.to_float(),
                "total_deductions": total_deductions.to_float(),
                "taxable_income": taxable_income.to_float(),
                "tax_liability": tax_liability.to_float()
            }
        }
        
        return TaxCalculationResult(
            total_income=gross_income,
            total_exemptions=total_exemptions,
            total_deductions=total_deductions,
            taxable_income=taxable_income,
            tax_liability=tax_liability,
            tax_breakdown=tax_breakdown,
            regime_comparison=None
        )
  
    def _calculate_total_income(self, input_data: TaxCalculationInput) -> Money:
        """Calculate total income from all sources."""
        # Salary income - use the actual method from SalaryIncome entity
        salary_total = input_data.salary_income.calculate_gross_salary()
        
        # Perquisites - use the actual method from Perquisites entity
        perquisites_total = input_data.perquisites.calculate_total_perquisites(input_data.regime)
        
        # Capital gains income - use the actual method from CapitalGainsIncome entity
        capital_gains_total = input_data.capital_gains_income.calculate_total_capital_gains_income()
        
        # Retirement benefits - use the actual method from RetirementBenefits entity
        retirement_total = input_data.retirement_benefits.calculate_total_retirement_income(input_data.regime)
        
        # Other income - use the actual method from OtherIncome entity (now includes house property income)
        other_income_total = input_data.other_income.calculate_total_other_income_slab_rates(input_data.regime, input_data.age)
        
        return (
            salary_total
            .add(perquisites_total)
            .add(capital_gains_total)
            .add(retirement_total)
            .add(other_income_total)
        )
    
    def _calculate_total_exemptions(self, input_data: TaxCalculationInput) -> Money:
        """Calculate total exemptions."""
        # Use the actual exemption methods from entities
        salary_exemptions = input_data.salary_income.calculate_total_exemptions(input_data.regime)
        
        # For now, return salary exemptions only (can be enhanced later)
        return salary_exemptions
    
    def _calculate_total_deductions(self, input_data: TaxCalculationInput) -> Money:
        """Calculate total deductions."""
        if input_data.regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()  # No deductions in new regime
        
        # Use the actual deduction methods from TaxDeductions entity
        return Money.zero() #input_data.deductions.get_total_deductions()
    
    def _calculate_tax_liability(self,
                               taxable_income: Money,
                               regime: TaxRegime,
                               age: int,
                               additional_tax_liability: Money,
                               is_senior_citizen: bool,
                               is_super_senior_citizen: bool) -> Money:
        """Calculate tax liability based on tax slabs."""
        # Get tax slabs
        if regime.regime_type == TaxRegimeType.OLD:
            slabs = self._get_old_regime_slabs(age, is_senior_citizen, is_super_senior_citizen)
        else:
            slabs = self._get_new_regime_slabs()

        print(f"TheOne: Slabs: {slabs}")
        
        # Calculate tax for each slab using progressive taxation
        tax_amount = Money(Decimal('0'))
        
        for slab in slabs:
            slab_min = Money(slab["min"])
            slab_max = Money(slab["max"]) if slab["max"] is not None else taxable_income
            slab_rate = Decimal(str(slab["rate"])) / Decimal('100')
            
            # Calculate taxable amount in this slab
            if taxable_income > slab_min:
                # Amount of income that falls in this slab
                if slab["max"] is not None:
                    # For slabs with upper limit: min(taxable_income, slab_max) - slab_min
                    income_in_slab = taxable_income.min(slab_max).subtract(slab_min)
                else:
                    # For highest slab (no upper limit): taxable_income - slab_min
                    income_in_slab = taxable_income.subtract(slab_min)
                
                # Ensure we don't have negative income in slab
                if income_in_slab.is_greater_than(Money.zero()):
                    tax_for_slab = income_in_slab.multiply(slab_rate)
                    tax_amount = tax_amount.add(tax_for_slab)
                    
                    logger.info(f"TheOne: Slab ({slab_min.to_float()}-{slab_max.to_float() if slab['max'] else 'unlimited'}): "
                               f"income_in_slab={income_in_slab.to_float()}, rate={slab_rate}, "
                               f"tax_for_slab={tax_for_slab.to_float()}, total_tax={tax_amount.to_float()}")
            else:
                logger.info(f"TheOne: Skipping slab ({slab_min.to_float()}-{slab_max.to_float() if slab['max'] else 'unlimited'}): "
                           f"taxable_income {taxable_income.to_float()} <= slab_min {slab_min.to_float()}")
        
        # Add STCG tax
        tax_amount = tax_amount.add(additional_tax_liability)
        
        # Add surcharge if applicable
        if taxable_income > Money(Decimal('5000000')):  # Above ₹50 lakh
            surcharge_rate = Decimal('0.10')  # 10% surcharge
            if taxable_income > Money(Decimal('10000000')):  # Above ₹1 crore
                surcharge_rate = Decimal('0.15')  # 15% surcharge
            if taxable_income > Money(Decimal('20000000')):  # Above ₹2 crore
                surcharge_rate = Decimal('0.25')  # 25% surcharge
            if taxable_income > Money(Decimal('50000000')):  # Above ₹5 crore
                surcharge_rate = Decimal('0.37')  # 37% surcharge
            
            surcharge = tax_amount.multiply(surcharge_rate)
            tax_amount = tax_amount.add(surcharge)
        
        # Add health and education cess
        cess_rate = Decimal('0.04')  # 4% cess
        cess = tax_amount.multiply(cess_rate)
        tax_amount = tax_amount.add(cess)
        logger.info(f"TheOne: Tax amount: {tax_amount.to_float()}")
        
        return tax_amount
    
    def _get_tax_breakdown(self,
                          total_income: Money,
                          total_exemptions: Money,
                          total_deductions: Money,
                          taxable_income: Money,
                          tax_liability: Money,
                          input_data: TaxCalculationInput) -> Dict[str, Any]:
        """Get detailed tax calculation breakdown."""
        return {
            "income_breakdown": {
                "salary_income": {
                    "basic_salary": input_data.salary_income.basic_salary.to_float(),
                    "dearness_allowance": input_data.salary_income.dearness_allowance.to_float(),
                    "hra_provided": input_data.salary_income.hra_provided.to_float(),
                    "special_allowance": input_data.salary_income.special_allowance.to_float(),
                    "bonus": input_data.salary_income.bonus.to_float(),
                    "commission": input_data.salary_income.commission.to_float(),
                    "overtime": input_data.salary_income.specific_allowances.overtime_allowance.to_float() if input_data.salary_income.specific_allowances else 0.0,
                    "arrears": input_data.salary_income.arrears.to_float(),

                },
                "perquisites": {
                    "car_perquisite": input_data.perquisites.car_perquisite.to_float(),
                    "driver_perquisite": input_data.perquisites.driver_perquisite.to_float(),
                    "fuel_perquisite": input_data.perquisites.fuel_perquisite.to_float(),
                    "education_perquisite": input_data.perquisites.education_perquisite.to_float(),
                    "domestic_servant_perquisite": input_data.perquisites.domestic_servant_perquisite.to_float(),
                    "utility_perquisite": input_data.perquisites.utility_perquisite.to_float(),
                    "loan_perquisite": input_data.perquisites.loan_perquisite.to_float(),
                    "esop_perquisite": input_data.perquisites.esop_perquisite.to_float(),
                    "club_membership_perquisite": input_data.perquisites.club_membership_perquisite.to_float(),
                    "other_perquisites": input_data.perquisites.other_perquisites.to_float()
                },

                "capital_gains_income": {
                    "stcg_111a_equity_stt": input_data.capital_gains_income.stcg_111a_equity_stt.to_float(),
                    "stcg_other_assets": input_data.capital_gains_income.stcg_other_assets.to_float(),
                    "stcg_debt_mf": input_data.capital_gains_income.stcg_debt_mf.to_float(),
                    
                    "ltcg_112a_equity_stt": input_data.capital_gains_income.ltcg_112a_equity_stt.to_float(),
                    "ltcg_other_assets": input_data.capital_gains_income.ltcg_other_assets.to_float(),
                    "ltcg_debt_mf": input_data.capital_gains_income.ltcg_debt_mf.to_float(),
                },
                "retirement_benefits": {
                    "gratuity_amount": input_data.retirement_benefits.gratuity_amount.to_float(),
                    "years_of_service": input_data.retirement_benefits.years_of_service,
                    "is_government_employee": input_data.retirement_benefits.is_government_employee,
                    "leave_encashment_amount": input_data.retirement_benefits.leave_encashment_amount.to_float(),
                    "leave_balance": input_data.retirement_benefits.leave_balance,
                    "pension_amount": input_data.retirement_benefits.pension_amount.to_float(),
                    "is_commuted_pension": input_data.retirement_benefits.is_commuted_pension,
                    "commutation_percentage": float(input_data.retirement_benefits.commutation_percentage),
                    "vrs_compensation": input_data.retirement_benefits.vrs_compensation.to_float(),
                    "other_retirement_benefits": input_data.retirement_benefits.other_retirement_benefits.to_float()
                },
                "other_income": {
                    "bank_interest": input_data.other_income.bank_interest.to_float(),
                    "fixed_deposit_interest": input_data.other_income.fixed_deposit_interest.to_float(),
                    "recurring_deposit_interest": input_data.other_income.recurring_deposit_interest.to_float(),
                    "post_office_interest": input_data.other_income.other_interest.to_float(),
                    "equity_dividend": input_data.other_income.equity_dividend.to_float(),
                    "mutual_fund_dividend": input_data.other_income.mutual_fund_dividend.to_float(),
                    "other_dividend": input_data.other_income.other_dividend.to_float(),
                    "house_property_rent": input_data.other_income.house_property_rent.to_float(),
                    "commercial_property_rent": input_data.other_income.commercial_property_rent.to_float(),
                    "other_rental": input_data.other_income.other_rental.to_float(),
                    "business_income": input_data.other_income.business_income.to_float(),
                    "professional_income": input_data.other_income.professional_income.to_float(),
                    "short_term_capital_gains": input_data.other_income.short_term_capital_gains.to_float(),
                    "long_term_capital_gains": input_data.other_income.long_term_capital_gains.to_float(),
                    "lottery_winnings": input_data.other_income.lottery_winnings.to_float(),
                    "horse_race_winnings": input_data.other_income.horse_race_winnings.to_float(),
                    "crossword_puzzle_winnings": input_data.other_income.crossword_puzzle_winnings.to_float(),
                    "card_game_winnings": input_data.other_income.card_game_winnings.to_float(),
                    "other_speculative_income": input_data.other_income.other_speculative_income.to_float(),
                    "agricultural_income": input_data.other_income.agricultural_income.to_float(),
                    "share_of_profit_partnership": input_data.other_income.share_of_profit_partnership.to_float(),
                    "interest_on_tax_free_bonds": input_data.other_income.interest_on_tax_free_bonds.to_float(),
                    "other_exempt_income": input_data.other_income.other_exempt_income.to_float()
                }
            },
            "exemptions_breakdown": {
                "hra_exemption": self._calculate_hra_exemption(
                    input_data.salary_income.basic_salary,
                    input_data.salary_income.dearness_allowance,
                    input_data.salary_income.hra_provided,
                    (input_data.other_income.house_property_income.annual_rent_received 
                     if input_data.other_income.house_property_income else Money.zero())
                ).to_float(),
                "gratuity_exemption": self._calculate_gratuity_exemption(
                    input_data.retirement_benefits.gratuity_amount,
                    input_data.retirement_benefits.years_of_service,
                    input_data.retirement_benefits.is_government_employee
                ).to_float(),
                "leave_encashment_exemption": self._calculate_leave_encashment_exemption(
                    input_data.retirement_benefits.leave_encashment_amount,
                    input_data.retirement_benefits.leave_balance,
                    input_data.retirement_benefits.is_government_employee
                ).to_float(),
                "pension_exemption": self._calculate_pension_exemption(
                    input_data.retirement_benefits.pension_amount,
                    input_data.retirement_benefits.is_commuted_pension,
                    input_data.retirement_benefits.commutation_percentage,
                    input_data.retirement_benefits.is_government_employee
                ).to_float(),
                "vrs_exemption": self._calculate_vrs_exemption(
                    input_data.retirement_benefits.vrs_compensation
                ).to_float(),
                "other_exemptions": (
                    input_data.other_income.interest_on_tax_free_bonds.add(
                        input_data.other_income.other_exempt_income
                    )
                ).to_float()
            },
            "deductions_breakdown": {
                "section_80c": min(
                    (
                        input_data.deductions.life_insurance_premium
                        .add(input_data.deductions.elss_investments)
                        .add(input_data.deductions.public_provident_fund)
                        .add(input_data.deductions.employee_provident_fund)
                        .add(input_data.deductions.sukanya_samriddhi)
                        .add(input_data.deductions.national_savings_certificate)
                        .add(input_data.deductions.tax_saving_fixed_deposits)
                        .add(input_data.deductions.principal_repayment_home_loan)
                        .add(input_data.deductions.tuition_fees)
                        .add(input_data.deductions.other_80c_deductions)
                    ).to_float(),
                    150000.0  # Max ₹1.5 lakh
                ),
                "section_80d": min(
                    (
                        input_data.deductions.health_insurance_self
                        .add(input_data.deductions.health_insurance_parents)
                        .add(input_data.deductions.preventive_health_checkup)
                    ).to_float(),
                    25000.0  # Max ₹25,000
                ),
                "section_80e": input_data.deductions.education_loan_interest.to_float(),
                "section_80g": input_data.deductions.donations_80g.to_float(),
                "section_80tta": min(
                    input_data.deductions.savings_account_interest.to_float(),
                    10000.0  # Max ₹10,000
                ),
                "section_80ttb": min(
                    input_data.deductions.senior_citizen_interest.to_float(),
                    50000.0  # Max ₹50,000
                ) if input_data.is_senior_citizen else 0.0,
                "section_80u": (
                    input_data.deductions.disability_deduction
                    .add(input_data.deductions.medical_treatment_deduction)
                ).to_float(),
                "other_deductions": (
                    input_data.deductions.scientific_research_donation
                    .add(input_data.deductions.political_donation)
                    .add(input_data.deductions.infrastructure_deduction)
                    .add(input_data.deductions.industrial_undertaking_deduction)
                    .add(input_data.deductions.special_category_state_deduction)
                    .add(input_data.deductions.hotel_deduction)
                    .add(input_data.deductions.north_eastern_state_deduction)
                    .add(input_data.deductions.employment_deduction)
                    .add(input_data.deductions.employment_generation_deduction)
                    .add(input_data.deductions.offshore_banking_deduction)
                    .add(input_data.deductions.co_operative_society_deduction)
                    .add(input_data.deductions.royalty_deduction)
                    .add(input_data.deductions.patent_deduction)
                    .add(input_data.deductions.interest_on_savings_deduction)
                    .add(input_data.deductions.disability_deduction_amount)
                ).to_float()
            },
            "tax_summary": {
                "total_income": total_income.to_float(),
                "total_exemptions": total_exemptions.to_float(),
                "total_deductions": total_deductions.to_float(),
                "taxable_income": taxable_income.to_float(),
                "tax_liability": tax_liability.to_float(),
                "regime": input_data.regime.regime_type.value
            }
        }
    
    def _get_regime_comparison(self, input_data: TaxCalculationInput) -> Dict[str, Any]:
        """Compare tax liability under old and new regimes."""
        # Calculate tax under old regime
        old_regime_result = self.calculate_tax(input_data)
        
        # Calculate tax under new regime
        new_regime_input = TaxCalculationInput(
            salary_income=input_data.salary_income,
            perquisites=input_data.perquisites,
            capital_gains_income=input_data.capital_gains_income,
            retirement_benefits=input_data.retirement_benefits,
            other_income=input_data.other_income,
            deductions=input_data.deductions,
            regime=TaxRegime(TaxRegimeType.NEW),
            age=input_data.age,
            is_senior_citizen=input_data.is_senior_citizen,
            is_super_senior_citizen=input_data.is_super_senior_citizen,
            is_government_employee=input_data.is_government_employee
        )
        new_regime_result = self.calculate_tax(new_regime_input)
        
        return {
            "old_regime": {
                "taxable_income": old_regime_result.taxable_income.to_float(),
                "tax_liability": old_regime_result.tax_liability.to_float(),
                "total_deductions": old_regime_result.total_deductions.to_float()
            },
            "new_regime": {
                "taxable_income": new_regime_result.taxable_income.to_float(),
                "tax_liability": new_regime_result.tax_liability.to_float(),
                "total_deductions": new_regime_result.total_deductions.to_float()
            },
            "difference": {
                "tax_liability": (
                    new_regime_result.tax_liability.subtract(old_regime_result.tax_liability) 
                    if new_regime_result.tax_liability.is_greater_than(old_regime_result.tax_liability)
                    else old_regime_result.tax_liability.subtract(new_regime_result.tax_liability).multiply(Decimal('-1'))
                ).to_float(),
                "percentage": float(
                    (new_regime_result.tax_liability.subtract(old_regime_result.tax_liability) 
                     if new_regime_result.tax_liability.is_greater_than(old_regime_result.tax_liability)
                     else old_regime_result.tax_liability.subtract(new_regime_result.tax_liability).multiply(Decimal('-1')))
                    .divide(old_regime_result.tax_liability).multiply(Decimal('100'))
                ) if old_regime_result.tax_liability.is_greater_than(Money(Decimal('0'))) else 0.0
            },
            "recommended_regime": (
                "new" if new_regime_result.tax_liability.is_less_than(old_regime_result.tax_liability)
                else "old"
            )
        }
    
    def _calculate_hra_exemption(self,
                               basic_salary: Money,
                               dearness_allowance: Money,
                               hra: Money,
                               rent_paid: Money) -> Money:
        """Calculate HRA exemption."""
        # HRA exemption is least of:
        # 1. Actual HRA received
        # 2. Rent paid - 10% of (Basic + DA)
        # 3. 50% of (Basic + DA) for metro cities, 40% for others
        basic_plus_da = basic_salary.add(dearness_allowance)
        ten_percent_basic_da = basic_plus_da.multiply(Decimal('0.10'))
        rent_minus_10_percent = rent_paid.subtract(ten_percent_basic_da) if rent_paid.is_greater_than(ten_percent_basic_da) else Money.zero()
        hra_percentage = Decimal('0.50')  # Assuming metro city
        fifty_percent_basic_da = basic_plus_da.multiply(hra_percentage)
        
        return hra.min(rent_minus_10_percent).min(fifty_percent_basic_da)
    
    def _calculate_gratuity_exemption(self,
                                    gratuity_amount: Money,
                                    years_of_service: int,
                                    is_government_employee: bool) -> Money:
        """Calculate gratuity exemption."""
        if is_government_employee:
            return gratuity_amount  # Fully exempt for government employees
        
        # For private employees, exemption is least of:
        # 1. Actual gratuity received
        # 2. ₹20 lakh
        # 3. 15 days' salary × years of service
        twenty_lakh = Money(Decimal('2000000'))  # ₹20 lakh
        fifteen_days_salary = Money(Decimal(str(years_of_service * 15)))  # 15 days' salary × years
        return gratuity_amount.min(twenty_lakh).min(fifteen_days_salary)
    
    def _calculate_leave_encashment_exemption(self,
                                            leave_encashment: Money,
                                            leave_balance: int,
                                            is_government_employee: bool) -> Money:
        """Calculate leave encashment exemption."""
        if is_government_employee:
            return leave_encashment  # Fully exempt for government employees
        
        # For private employees, exemption is least of:
        # 1. Actual leave encashment
        # 2. ₹3 lakh
        # 3. 10 months' average salary
        three_lakh = Money(Decimal('300000'))  # ₹3 lakh
        ten_months_salary = Money(Decimal(str(leave_balance * 10)))  # 10 months' salary
        return leave_encashment.min(three_lakh).min(ten_months_salary)
    
    def _calculate_pension_exemption(self,
                                   pension_amount: Money,
                                   is_commuted_pension: bool,
                                   commutation_percentage: Decimal,
                                   is_government_employee: bool) -> Money:
        """Calculate pension exemption."""
        if not is_commuted_pension:
            return Money(Decimal('0'))  # No exemption for uncommuted pension
        
        if is_government_employee:
            return pension_amount  # Fully exempt for government employees
        
        # For private employees, exemption is:
        # 1/3 of commuted pension if gratuity is received
        # 1/2 of commuted pension if gratuity is not received
        if commutation_percentage > Decimal('0'):
            exemption_percentage = Decimal('0.33')  # Assuming gratuity is received
            return pension_amount.multiply(exemption_percentage)
        
        return Money(Decimal('0'))
    
    def _calculate_vrs_exemption(self, vrs_compensation: Money) -> Money:
        """Calculate VRS compensation exemption."""
        # VRS compensation is exempt up to ₹5 lakh
        five_lakh = Money(Decimal('500000'))
        return vrs_compensation.min(five_lakh)
    
    def _get_old_regime_slabs(self,
                             age: int,
                             is_senior_citizen: bool,
                             is_super_senior_citizen: bool) -> List[Dict[str, Any]]:
        """Get tax slabs for old regime."""
        if is_super_senior_citizen:
            # Super Senior Citizen (above 80 years)
            return [
                {"min": Decimal('0'), "max": Decimal('500000'), "rate": Decimal('0')},
                {"min": Decimal('500000'), "max": Decimal('1000000'), "rate": Decimal('20')},
                {"min": Decimal('1000000'), "max": None, "rate": Decimal('30')}
            ]
        elif is_senior_citizen:
            # Senior Citizen (60-80 years)
            return [
                {"min": Decimal('0'), "max": Decimal('300000'), "rate": Decimal('0')},
                {"min": Decimal('300000'), "max": Decimal('500000'), "rate": Decimal('5')},
                {"min": Decimal('500000'), "max": Decimal('1000000'), "rate": Decimal('20')},
                {"min": Decimal('1000000'), "max": None, "rate": Decimal('30')}
            ]
        else:
            # Individual (below 60 years)
            return [
                {"min": Decimal('0'), "max": Decimal('250000'), "rate": Decimal('0')},
                {"min": Decimal('250000'), "max": Decimal('500000'), "rate": Decimal('5')},
                {"min": Decimal('500000'), "max": Decimal('1000000'), "rate": Decimal('20')},
                {"min": Decimal('1000000'), "max": None, "rate": Decimal('30')}
            ]
    
    def _get_new_regime_slabs(self) -> List[Dict[str, Any]]:
        """Get tax slabs for new regime."""
        # New regime slabs are same for all age groups
        return [
            {"min": Decimal('0'), "max": Decimal('300000'), "rate": Decimal('0')},
            {"min": Decimal('300000'), "max": Decimal('600000'), "rate": Decimal('5')},
            {"min": Decimal('600000'), "max": Decimal('900000'), "rate": Decimal('10')},
            {"min": Decimal('900000'), "max": Decimal('1200000'), "rate": Decimal('15')},
            {"min": Decimal('1200000'), "max": Decimal('1500000'), "rate": Decimal('20')},
            {"min": Decimal('1500000'), "max": None, "rate": Decimal('30')}
        ] 

    def _create_monthly_payout_from_taxation_record(self, 
                                                   taxation_record, 
                                                   calculation_result: TaxCalculationResult) -> 'PayoutBase':
        """
        Create a monthly payout record based on taxation record and calculation result.
        
        This method calculates monthly salary components by dividing annual amounts by 12,
        and includes TDS calculation based on the annual tax liability.
        
        Args:
            taxation_record: The taxation record containing salary and other details
            calculation_result: The tax calculation result
            
        Returns:
            PayoutBase: Monthly payout record with calculated values
        """
        from datetime import date
        from app.domain.entities.taxation.payout import PayoutBase, PayoutFrequency, PayoutStatus
        
        # Get current year for payout dates
        current_year = date.today().year
        current_month = date.today().month
        
        # Calculate monthly salary components from annual salary
        annual_gross = calculation_result.total_income
        monthly_gross = annual_gross.divide(Decimal('12'))
        
        # Extract salary components from the salary income entity
        salary_income = taxation_record.salary_income
        
        # Calculate monthly components
        monthly_basic = salary_income.basic_salary.divide(Decimal('12'))
        monthly_da = salary_income.dearness_allowance.divide(Decimal('12'))
        monthly_hra = salary_income.hra_provided.divide(Decimal('12'))
        monthly_special = salary_income.special_allowance.divide(Decimal('12'))
        monthly_bonus = salary_income.bonus.divide(Decimal('12'))
        monthly_commission = salary_income.commission.divide(Decimal('12'))
        monthly_overtime = salary_income.specific_allowances.overtime_allowance.divide(Decimal('12')) if salary_income.specific_allowances else Money.zero()
        monthly_arrears = salary_income.arrears.divide(Decimal('12'))
        
        # Calculate monthly TDS (Tax Deducted at Source)
        annual_tax = calculation_result.tax_liability
        monthly_tds = annual_tax.divide(Decimal('12'))
        
        # Calculate statutory deductions (EPF, ESI, Professional Tax)
        monthly_epf_employee = self._calculate_monthly_epf_employee(monthly_basic, monthly_da)
        monthly_epf_employer = self._calculate_monthly_epf_employer(monthly_basic, monthly_da)
        monthly_esi_employee = self._calculate_monthly_esi_employee(monthly_gross)
        monthly_esi_employer = self._calculate_monthly_esi_employer(monthly_gross)
        monthly_professional_tax = self._calculate_monthly_professional_tax(monthly_gross)
        
        # Calculate total monthly deductions
        total_monthly_deductions = (
            monthly_epf_employee
            .add(monthly_esi_employee)
            .add(monthly_professional_tax)
            .add(monthly_tds)
        )
        
        # Calculate net monthly salary
        net_monthly_salary = monthly_gross.subtract(total_monthly_deductions)
        
        # Create payout record
        return PayoutBase(
            employee_id=str(taxation_record.employee_id),
            pay_period_start=date(current_year, current_month, 1),
            pay_period_end=date(current_year, current_month, 28),  # Approximate month end
            payout_date=date(current_year, current_month, 30),  # Assumed payout on 30th
            frequency=PayoutFrequency.MONTHLY,
            
            # Monthly salary components
            basic_salary=monthly_basic.to_float(),
            da=monthly_da.to_float(),
            hra=monthly_hra.to_float(),
            special_allowance=monthly_special.to_float(),
            bonus=monthly_bonus.to_float(),
            commission=monthly_commission.to_float(),
            overtime=monthly_overtime.to_float(),
            arrears=monthly_arrears.to_float(),
            
            # Monthly deductions
            epf_employee=monthly_epf_employee.to_float(),
            epf_employer=monthly_epf_employer.to_float(),
            esi_employee=monthly_esi_employee.to_float(),
            esi_employer=monthly_esi_employer.to_float(),
            professional_tax=monthly_professional_tax.to_float(),
            tds=monthly_tds.to_float(),
            advance_deduction=0.0,
            loan_deduction=0.0,
            other_deductions=0.0,
            
            # Calculated totals
            gross_salary=monthly_gross.to_float(),
            total_deductions=total_monthly_deductions.to_float(),
            net_salary=net_monthly_salary.to_float(),
            
            # Annual projections
            annual_gross_salary=annual_gross.to_float(),
            annual_tax_liability=annual_tax.to_float(),
            monthly_tds=monthly_tds.to_float(),
            
            # Tax details
            tax_regime=taxation_record.regime.regime_type.value,
            tax_exemptions=calculation_result.total_exemptions.to_float(),
            standard_deduction=50000.0 if taxation_record.regime.regime_type.value == "new" else 0.0,
            section_80c_claimed=0.0,  # Can be enhanced later
            
            # Reimbursements
            reimbursements=0.0,
            
            # Working days (default values - can be enhanced)
            total_days_in_month=30,
            working_days_in_period=22,
            lwp_days=0,
            effective_working_days=22,
            
            # Status
            status=PayoutStatus.PENDING,
            notes=f"Auto-generated monthly payout for tax year {taxation_record.tax_year}",
            remarks=f"Based on {taxation_record.regime.regime_type.value} tax regime calculation"
        )

    def _calculate_monthly_epf_employee(self, monthly_basic: Money, monthly_da: Money) -> Money:
        """Calculate monthly EPF employee contribution (12% of basic + DA, capped at ₹1,800)."""
        epf_eligible_salary = monthly_basic.add(monthly_da)
        epf_contribution = epf_eligible_salary.multiply(Decimal('0.12'))
        epf_cap = Money(Decimal('1800'))  # Current EPF cap is ₹1,800 per month
        return epf_contribution.min(epf_cap)

    def _calculate_monthly_epf_employer(self, monthly_basic: Money, monthly_da: Money) -> Money:
        """Calculate monthly EPF employer contribution (12% of basic + DA, capped at ₹1,800)."""
        return self._calculate_monthly_epf_employee(monthly_basic, monthly_da)

    def _calculate_monthly_esi_employee(self, monthly_gross: Money) -> Money:
        """Calculate monthly ESI employee contribution (0.75% of gross, applicable if gross ≤ ₹21,000)."""
        esi_threshold = Money(Decimal('21000'))
        if monthly_gross.is_greater_than(esi_threshold):
            return Money.zero()
        return monthly_gross.multiply(Decimal('0.0075'))

    def _calculate_monthly_esi_employer(self, monthly_gross: Money) -> Money:
        """Calculate monthly ESI employer contribution (3.25% of gross, applicable if gross ≤ ₹21,000)."""
        esi_threshold = Money(Decimal('21000'))
        if monthly_gross.is_greater_than(esi_threshold):
            return Money.zero()
        return monthly_gross.multiply(Decimal('0.0325'))

    def _calculate_monthly_professional_tax(self, monthly_gross: Money) -> Money:
        """Calculate monthly professional tax based on gross salary slabs."""
        # Professional tax varies by state. Using Maharashtra rates as example:
        if monthly_gross.is_less_than(Money(Decimal('15000'))) or monthly_gross.is_equal_to(Money(Decimal('15000'))):
            return Money.zero()
        elif monthly_gross.is_less_than(Money(Decimal('25000'))) or monthly_gross.is_equal_to(Money(Decimal('25000'))):
            return Money(Decimal('175'))
        else:
            return Money(Decimal('200')) 