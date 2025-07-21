"""
Tax Calculation Service
Handles all tax calculations for Indian taxation
"""

import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
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
    is_government_employee: bool


@dataclass
class TaxCalculationResult:
    """Result of tax calculation."""
    total_income: Money
    professional_tax: Money
    total_exemptions: Money
    total_deductions: Money
    taxable_income: Money
    tax_amount: Money
    surcharge: Money
    cess: Money
    tax_liability: Money
    tax_breakdown: Dict[str, Any]
    regime_comparison: Optional[Dict[str, Any]] = None
    
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


    async def compute_monthly_tax(self, employee_id: str, current_user, computing_month: int = datetime.now().month) -> Dict[str, Any]:
        """
        Compute monthly tax for an employee based on their salary package record.
        
        Args:
            employee_id: Employee ID
            current_user: Current authenticated user with organisation context
            
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
            month = computing_month
            year = now.year
            
            logger.info(f"compute_monthly_tax: Using Computation month={month}, year={year}")
            
            # Validate inputs
            from app.domain.value_objects.tax_year import TaxYear
            current_tax_year = TaxYear.current()
            tax_year = str(current_tax_year)
            
            logger.debug(f"compute_monthly_tax: Current Financial year: {tax_year}")
            
            # Check if required repositories are configured
            if not self.salary_package_repository:
                logger.error("compute_monthly_tax: Salary package repository not configured")
                raise ValueError("Salary package repository not configured for monthly tax computation")
            
            logger.debug("compute_monthly_tax: Salary package repository is configured")
            
            # Get salary package record for the employee and tax year
            logger.debug(f"compute_monthly_tax: Fetching salary package record for employee {employee_id}, tax_year {tax_year}")

            salary_package_record = await self.salary_package_repository.get_salary_package_record(
                employee_id, tax_year, current_user.hostname
            )
            
            if not salary_package_record:
                logger.error(f"compute_monthly_tax: No salary package record found for employee {employee_id} in tax year {tax_year}")
                raise ValueError(
                    f"Salary package record not found for employee {employee_id} "
                    f"in tax year {tax_year}. Please ensure salary data is configured."
                )
            
            # Compute monthly tax using the salary package record
            logger.info("compute_monthly_tax: Computing monthly tax from salary package record")
            calculation_result = salary_package_record.calculate_tax(self, computing_month)

            salary_package_record.last_calculated_at = datetime.utcnow()
            salary_package_record.calculation_result = calculation_result
            
            # Save the updated salary package record with calculation result to database
            logger.debug("compute_monthly_tax: Saving updated salary package record to database")
            try:
                await self.salary_package_repository.save(salary_package_record, current_user.hostname)
                logger.debug("compute_monthly_tax: Successfully saved updated salary package record to database")
            except Exception as save_error:
                logger.error(f"compute_monthly_tax: Failed to save updated salary package record to database: {str(save_error)}")
                # Continue with computation even if save fails
                logger.warning("compute_monthly_tax: Continuing with computation despite save failure")
            
            # Extract monthly tax amount from calculation result
            monthly_tax_amount = calculation_result.monthly_tax_liability.to_float()
            logger.debug(f"compute_monthly_tax: Monthly tax amount: {monthly_tax_amount}")
            
            # Get additional details from the calculation result
            calculation_details = {}
            if calculation_result:
                logger.debug("compute_monthly_tax: Extracting calculation details from salary package record")
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
                logger.debug(f"compute_monthly_tax: Annual gross income: {calculation_details['annual_gross_income']}")
                logger.debug(f"compute_monthly_tax: Annual tax liability: {calculation_details['annual_tax_liability']}")
                logger.debug(f"compute_monthly_tax: Tax regime: {calculation_details['tax_regime']}")
            else:
                logger.warning("compute_monthly_tax: No calculation result available")
            
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
            
            logger.debug("compute_monthly_tax: Built response object with salary package info")
            
            # Add latest salary breakdown
            if salary_package_record.salary_incomes:
                logger.debug("compute_monthly_tax: Adding latest salary breakdown")
                latest_salary = salary_package_record.get_latest_salary_income()
                response["latest_salary_info"] = {
                    "basic_salary": latest_salary.basic_salary.to_float(),
                    "dearness_allowance": latest_salary.dearness_allowance.to_float(),
                    "hra_provided": latest_salary.hra_provided.to_float(),
                    "eps_employee": latest_salary.eps_employee.to_float(),
                    "eps_employer": latest_salary.eps_employer.to_float(),
                    "esi_contribution": latest_salary.esi_contribution.to_float(),
                    "vps_employee": latest_salary.vps_employee.to_float(),
                    "special_allowance": latest_salary.special_allowance.to_float(),
                    "commission": latest_salary.commission.to_float(),
                    "gross_salary": latest_salary.calculate_gross_salary().to_float()
                }
                logger.debug(f"compute_monthly_tax: Latest salary basic: {response['latest_salary_info']['basic_salary']}")
                logger.debug(f"compute_monthly_tax: Latest salary gross: {response['latest_salary_info']['gross_salary']}")
            else:
                logger.warning("compute_monthly_tax: No salary incomes found in salary package record")
            
            logger.debug(f"compute_monthly_tax: Successfully computed monthly tax for employee {employee_id}")
            return response
            
        except ValueError as e:
            logger.error(f"compute_monthly_tax: Validation error for employee {employee_id}: {str(e)}")
            # Re-raise validation errors
            raise e
        except Exception as e:
            logger.error(f"compute_monthly_tax: Unexpected error for employee {employee_id}: {str(e)}", exc_info=True)
            # Wrap other errors in RuntimeError
            raise RuntimeError(f"Failed to compute monthly tax for employee {employee_id}: {str(e)}")
    
    async def compute_monthly_tax_with_details(self, employee_id: str, current_user) -> Dict[str, Any]:
        """
        Compute monthly tax with detailed breakdown for frontend display.
        
        This is an enhanced version that provides more detailed information
        suitable for frontend tax overview components.
        
        Args:
            employee_id: Employee ID
            current_user: Current authenticated user with organisation context
            
        Returns:
            Dict[str, Any]: Detailed monthly tax computation result
        """
        
        try:
            # Get basic computation
            basic_result = await self.compute_monthly_tax(employee_id, current_user)
            
            # Get salary package record for additional details
            tax_year = basic_result["tax_year"]

            logger.debug(f"compute_monthly_tax_with_details: Fetching salary package record for additional details - employee {employee_id}, tax_year {tax_year}")
            
            salary_package_record = await self.salary_package_repository.get_salary_package_record(
                employee_id, tax_year, current_user.hostname
            )
            
            if not salary_package_record:
                logger.warning(f"compute_monthly_tax_with_details: No salary package record found for detailed breakdown - returning basic result")
                return basic_result
            
            logger.debug("compute_monthly_tax_with_details: Building detailed result with additional breakdown")
            
            # Add detailed breakdown
            detailed_result = basic_result.copy()
            
            logger.debug(f"compute_monthly_tax_with_details: Successfully completed detailed computation for employee {employee_id}")
            return detailed_result
            
        except Exception as e:
            logger.error(f"compute_monthly_tax_with_details: Error in detailed computation for employee {employee_id}: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to compute detailed monthly tax for employee {employee_id}: {str(e)}")
    
    # def calculate_tax(self, input_data: TaxCalculationInput) -> TaxCalculationResult:
    #     """
    #     Calculate tax based on input data.
        
    #     Args:
    #         input_data: Tax calculation input data
            
    #     Returns:
    #         TaxCalculationResult: Tax calculation result
    #     """

    #     summary_data = {
    #         'regime': input_data.regime.regime_type.value,
    #         'age': input_data.age
    #     }

    #     # Calculate total income
    #     total_income = self._calculate_total_income(input_data, summary_data)
        
    #     # Calculate total exemptions
    #     total_exemptions = self._calculate_total_exemptions(input_data, summary_data)
        
    #     # Calculate total deductions
    #     total_deductions = self._calculate_total_deductions(input_data, summary_data)
        
    #     # Calculate taxable income
    #     # First subtract exemptions, then deductions, ensuring we don't go negative
    #     income_after_exemptions = total_income.subtract(total_exemptions) if total_income > total_exemptions else Money.zero()
    #     taxable_income = income_after_exemptions.subtract(total_deductions) if income_after_exemptions > total_deductions else Money.zero()
        
    #     # Calculate tax liability
    #     tax_amount, surcharge, cess, total_tax = self._calculate_tax_liability(
    #         taxable_income,
    #         input_data.regime,
    #         input_data.age,
    #         input_data.capital_gains_income.calculate_stcg_111a_tax(),
    #         input_data.capital_gains_income.calculate_ltcg_112a_tax(),
    #     )
        
    #     # Log the summary table
    #     from app.utils.table_logger import log_salary_summary
    #     log_salary_summary("TAX CALCULATION SUMMARY", summary_data)

    #     # Get tax breakdown
    #     tax_breakdown = self._get_tax_breakdown(
    #         total_income,
    #         total_exemptions,
    #         total_deductions,
    #         taxable_income,
    #         total_tax,
    #         input_data
    #     )
        
    #     # Skip regime comparison to avoid infinite recursion
    #     regime_comparison = None
        
    #     return TaxCalculationResult(
    #         total_income=total_income,
    #         total_exemptions=total_exemptions,
    #         total_deductions=total_deductions,
    #         taxable_income=taxable_income,
    #         tax_liability=total_tax,
    #         tax_breakdown=tax_breakdown,
    #         regime_comparison=regime_comparison
    #     )

    def _calculate_total_income(self, input_data: TaxCalculationInput, summary_data: Dict[str, Any]) -> Money:
        """Calculate total income from all sources."""
        summary_data['calculate_total_income'] = 'start'
        # Salary income - use the actual method from SalaryIncome entity
        salary_total = input_data.salary_income.calculate_gross_salary(summary_data)
        
        # Perquisites - use the actual method from Perquisites entity
        perquisites_total = input_data.perquisites.calculate_total_perquisites(input_data.regime, summary_data)
        
        # Capital gains income - use the actual method from CapitalGainsIncome entity
        capital_gains_total = input_data.capital_gains_income.calculate_total_capital_gains_income(summary_data)
        
        # Retirement benefits - use the actual method from RetirementBenefits entity
        retirement_total = input_data.retirement_benefits.calculate_total_retirement_income(input_data.regime, summary_data)
        
        # Other income - use the actual method from OtherIncome entity (now includes house property income)
        other_income_total = input_data.other_income.calculate_total_other_income_slab_rates(input_data.regime, input_data.age, summary_data)
        total_income = (
            salary_total
            .add(perquisites_total)
            .add(capital_gains_total)
            .add(retirement_total)
            .add(other_income_total)
        )
        summary_data['final_total_income'] = total_income
        summary_data['calculate_total_income'] = 'end'
        return total_income
    
    def _calculate_total_exemptions(self, input_data: TaxCalculationInput, summary_data: Dict[str, Any]) -> Money:
        """Calculate total exemptions."""
        summary_data['calculate_total_exemptions'] = 'start'
        # Use the actual exemption methods from entities
        salary_exemptions = input_data.salary_income.calculate_total_exemptions(input_data.regime, summary_data)
        
        # For now, return salary exemptions only (can be enhanced later)
        summary_data['calculate_total_exemptions'] = 'end'
        return salary_exemptions
    
    def _calculate_total_deductions(self, input_data: TaxCalculationInput) -> Money:
        """Calculate total deductions."""
        if input_data.regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()  # No deductions in new regime
        
        # Use the actual deduction methods from TaxDeductions entity
        return input_data.deductions.get_total_deductions()
    
    def _calculate_tax_liability(self,
                               taxable_income: Money,
                               regime: TaxRegime,
                               age: int,
                               additional_tax_liability: Money,
                               summary_data: Dict[str, Any] = None
                               ) -> Tuple[Money, Money, Money, Money]:
        """Calculate tax liability based on tax slabs."""
        # Get tax slabs
        slabs = regime.get_tax_slabs(age)
        rebate_limit = regime.get_rebate_87a_limit()
        max_rebate = regime.get_max_rebate_87a()

        if summary_data:
            summary_data['calculate_tax_liability'] = 'start'
            summary_data['rebate_limit'] = rebate_limit.to_float()
            summary_data['max_rebate'] = max_rebate.to_float()
        
        # Calculate tax for each slab using progressive taxation
        tax_amount = Money(Decimal('0'))
        surcharge = Money(Decimal('0'))  # Ensure always defined
        cess = Money(Decimal('0'))  # Ensure always defined
        if taxable_income > rebate_limit:
            loop_counter = 0
            for slab in slabs:
                loop_counter += 1
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
                    if income_in_slab > Money.zero():
                        tax_for_slab = income_in_slab.multiply(slab_rate)
                        tax_amount = tax_amount.add(tax_for_slab)
                        if summary_data:
                            summary_data[f'slab_{loop_counter}'] = f'{slab_min.to_float()}-{slab_max.to_float() if slab["max"] else "unlimited"}'
                            summary_data[f'slab_{loop_counter}_rate'] = slab_rate
                            summary_data[f'slab_{loop_counter}_taxable_income'] = taxable_income.to_float()
                            summary_data[f'slab_{loop_counter}_income_in_slab'] = income_in_slab.to_float()
                            summary_data[f'slab_{loop_counter}_tax_for_slab'] = tax_for_slab.to_float()
                            summary_data[f'slab_{loop_counter}_tax_amount'] = tax_amount.to_float()

                        logger.debug(f"TheOne: Slab ({slab_min.to_float()}-{slab_max.to_float() if slab['max'] else 'unlimited'}): "
                                f"income_in_slab={income_in_slab.to_float()}, rate={slab_rate}, "
                                f"tax_for_slab={tax_for_slab.to_float()}, total_tax={tax_amount.to_float()}")
                else:
                    logger.debug(f"TheOne: Skipping slab ({slab_min.to_float()}-{slab_max.to_float() if slab['max'] else 'unlimited'}): "
                            f"taxable_income {taxable_income.to_float()} <= slab_min {slab_min.to_float()}")
            
        # Add STCG tax
        tax_amount = tax_amount.add(additional_tax_liability)
        if summary_data:
            summary_data['additional_tax_liability'] = additional_tax_liability.to_float()
            summary_data['tax_amount'] = tax_amount.to_float()
        
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
            if summary_data:
                summary_data['surcharge_rate'] = surcharge_rate
                summary_data['surcharge'] = surcharge.to_float()
                summary_data['tax_amount'] = tax_amount.to_float()
        
        # Add health and education cess
        cess_rate = Decimal('0.04')  # 4% cess
        cess = tax_amount.multiply(cess_rate)
        total_tax = tax_amount.add(cess)
        if summary_data:
            summary_data['cess_rate'] = cess_rate
            summary_data['cess'] = cess.to_float()
            summary_data['total_tax'] = total_tax.to_float()
        logger.debug(f"TheOne: Tax amount: {tax_amount.to_float(), surcharge.to_float(), cess.to_float()} => {total_tax.to_float()}")
        
        return tax_amount, surcharge, cess, total_tax
    
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
                    "commission": input_data.salary_income.commission.to_float(),
                    "overtime": input_data.salary_income.specific_allowances.overtime_allowance.to_float() if input_data.salary_income.specific_allowances else 0.0
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
                ),
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
    
    # def _get_regime_comparison(self, input_data: TaxCalculationInput) -> Dict[str, Any]:
    #     """Compare tax liability under old and new regimes."""
    #     # Calculate tax under old regime
    #     old_regime_result = self.calculate_tax(input_data)
        
    #     # Calculate tax under new regime
    #     new_regime_input = TaxCalculationInput(
    #         salary_income=input_data.salary_income,
    #         perquisites=input_data.perquisites,
    #         capital_gains_income=input_data.capital_gains_income,
    #         retirement_benefits=input_data.retirement_benefits,
    #         other_income=input_data.other_income,
    #         deductions=input_data.deductions,
    #         regime=TaxRegime(TaxRegimeType.NEW),
    #         age=input_data.age,
    #         is_government_employee=input_data.is_government_employee
    #     )
    #     new_regime_result = self.calculate_tax(new_regime_input)
        
    #     return {
    #         "old_regime": {
    #             "taxable_income": old_regime_result.taxable_income.to_float(),
    #             "tax_liability": old_regime_result.tax_liability.to_float(),
    #             "total_deductions": old_regime_result.total_deductions.to_float()
    #         },
    #         "new_regime": {
    #             "taxable_income": new_regime_result.taxable_income.to_float(),
    #             "tax_liability": new_regime_result.tax_liability.to_float(),
    #             "total_deductions": new_regime_result.total_deductions.to_float()
    #         },
    #         "difference": {
    #             "tax_liability": (
    #                 new_regime_result.tax_liability.subtract(old_regime_result.tax_liability) 
    #                 if new_regime_result.tax_liability > old_regime_result.tax_liability
    #                 else old_regime_result.tax_liability.subtract(new_regime_result.tax_liability).multiply(Decimal('-1'))
    #             ).to_float(),
    #             "percentage": float(
    #                 (new_regime_result.tax_liability.subtract(old_regime_result.tax_liability) 
    #                  if new_regime_result.tax_liability > old_regime_result.tax_liability
    #                  else old_regime_result.tax_liability.subtract(new_regime_result.tax_liability).multiply(Decimal('-1')))
    #                 .divide(old_regime_result.tax_liability).multiply(Decimal('100'))
    #             ) if old_regime_result.tax_liability > Money(Decimal('0')) else 0.0
    #         },
    #         "recommended_regime": (
    #             "new" if new_regime_result.tax_liability < old_regime_result.tax_liability
    #             else "old"
    #         )
    #     }
    
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
        rent_minus_10_percent = rent_paid.subtract(ten_percent_basic_da) if rent_paid > ten_percent_basic_da else Money.zero()
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