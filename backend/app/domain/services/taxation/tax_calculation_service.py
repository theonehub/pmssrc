"""
Tax Calculation Service
Handles all tax calculations for Indian taxation
"""

from decimal import Decimal
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.money import Money
from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits


@dataclass
class TaxCalculationInput:
    """Input for tax calculation."""
    salary_income: SalaryIncome
    perquisites: Perquisites
    house_property_income: HousePropertyIncome
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
    
    def __init__(self, taxation_repository=None):
        """
        Initialize the service.
        
        Args:
            taxation_repository: Optional taxation repository for updating records
        """
        self.taxation_repository = taxation_repository
    
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
        
        # Calculate tax liability
        tax_liability = self._calculate_tax_liability(
            taxable_income,
            regime,
            age,
            is_senior_citizen,
            is_super_senior_citizen
        )
        
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
                "regime": regime.regime_type.value,
                "age_category": "super_senior" if is_super_senior_citizen else "senior" if is_senior_citizen else "regular",
                "basic_tax": tax_liability.to_float(),
                "total_tax_liability": tax_liability.to_float()
            },
            "summary": {
                "effective_tax_rate": (tax_liability.to_float() / gross_income.to_float() * 100) if not gross_income.is_zero() else 0.0,
                "monthly_tax": tax_liability.divide(Decimal('12')).to_float()
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

    async def calculate_and_update_taxation_record(self, 
                                                 taxation_record, 
                                                 organization_id: str) -> TaxCalculationResult:
        """
        Calculate tax for a taxation record and update it with results in the database.
        
        Args:
            taxation_record: TaxationRecord to calculate and update
            organization_id: Organization ID for database operations
            
        Returns:
            TaxCalculationResult: Tax calculation result
            
        Raises:
            ValueError: If taxation repository is not configured
            RuntimeError: If database update fails
        """
        if not self.taxation_repository:
            raise ValueError("Taxation repository not configured for this service")
        
        # Calculate tax using the record's built-in method
        calculation_result = taxation_record.calculate_tax(self)
        
        try:
            # Update the record in the database
            await self.taxation_repository.update_taxation_record(taxation_record, organization_id)
            
            return calculation_result
            
        except Exception as e:
            # Reset calculation state on update failure
            taxation_record._invalidate_calculation()
            raise RuntimeError(f"Failed to update taxation record in database: {e}")
    
    def _calculate_total_income(self, input_data: TaxCalculationInput) -> Money:
        """Calculate total income from all sources."""
        # Salary income - use the actual method from SalaryIncome entity
        salary_total = input_data.salary_income.calculate_gross_salary()
        
        # Perquisites - use the actual method from Perquisites entity
        perquisites_total = input_data.perquisites.calculate_total_perquisites(input_data.regime)
        
        # House property income - use the actual method from HousePropertyIncome entity
        house_property_total = input_data.house_property_income.get_income_from_house_property()
        
        # Capital gains income - use the actual method from CapitalGainsIncome entity
        capital_gains_total = input_data.capital_gains_income.calculate_total_capital_gains_income()
        
        # Retirement benefits - use the actual method from RetirementBenefits entity
        retirement_total = input_data.retirement_benefits.calculate_total_retirement_income(input_data.regime)
        
        # Other income - use the actual method from OtherIncome entity
        other_income_total = input_data.other_income.calculate_total_other_income(input_data.regime)
        
        return (
            salary_total
            .add(perquisites_total)
            .add(house_property_total)
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
                               is_senior_citizen: bool,
                               is_super_senior_citizen: bool) -> Money:
        """Calculate tax liability based on tax slabs."""
        # Get tax slabs
        if regime.regime_type == TaxRegimeType.OLD:
            slabs = self._get_old_regime_slabs(age, is_senior_citizen, is_super_senior_citizen)
        else:
            slabs = self._get_new_regime_slabs()
        
        # Calculate tax for each slab
        tax_amount = Money(Decimal('0'))
        remaining_income = taxable_income
        
        for slab in slabs:
            if remaining_income <= Money(Decimal('0')):
                break
            
            slab_min = Money(slab["min"])
            slab_max = Money(slab["max"]) if slab["max"] is not None else remaining_income
            slab_rate = Decimal(str(slab["rate"])) / Decimal('100')
            
            if remaining_income > slab_min:
                # Calculate taxable amount in this slab using Money methods
                income_above_slab_min = remaining_income.subtract(slab_min)
                slab_range = slab_max.subtract(slab_min) if slab_max != remaining_income else income_above_slab_min
                taxable_in_slab = income_above_slab_min.min(slab_range)
                tax_amount = tax_amount.add(taxable_in_slab.multiply(slab_rate))
                remaining_income = remaining_income.subtract(taxable_in_slab) if remaining_income.is_greater_than(taxable_in_slab) else Money.zero()
        
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
                    "hra_received": input_data.salary_income.hra_received.to_float(),
                    "special_allowance": input_data.salary_income.special_allowance.to_float(),
                    "conveyance_allowance": input_data.salary_income.conveyance_allowance.to_float(),
                    "medical_allowance": input_data.salary_income.medical_allowance.to_float(),
                    "bonus": input_data.salary_income.bonus.to_float(),
                    "commission": input_data.salary_income.commission.to_float(),
                    #"overtime": input_data.salary_income.overtime.to_float(),
                    #"arrears": input_data.salary_income.arrears.to_float(),
                    #"gratuity": input_data.salary_income.gratuity.to_float(),
                    #"leave_encashment": input_data.salary_income.leave_encashment.to_float(),
                    "other_allowances": input_data.salary_income.other_allowances.to_float()
                },
                "perquisites": {
                    "rent_free_accommodation": input_data.perquisites.rent_free_accommodation.to_float(),
                    "concessional_accommodation": input_data.perquisites.concessional_accommodation.to_float(),
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
                "house_property_income": {
                    "property_type": input_data.house_property_income.property_type.value,
                    #"municipal_value": input_data.house_property_income.municipal_value.to_float(),
                    "fair_rental_value": input_data.house_property_income.fair_rental_value.to_float(),
                    "standard_rent": input_data.house_property_income.standard_rent.to_float(),
                    "actual_rent": input_data.house_property_income.actual_rent.to_float(),
                    "municipal_tax": input_data.house_property_income.municipal_tax.to_float(),
                    "interest_on_loan": input_data.house_property_income.interest_on_loan.to_float(),
                    "pre_construction_interest": input_data.house_property_income.pre_construction_interest.to_float(),
                    "other_deductions": input_data.house_property_income.other_deductions.to_float()
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
                    "post_office_interest": input_data.other_income.post_office_interest.to_float(),
                    "other_interest": input_data.other_income.other_interest.to_float(),
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
                    input_data.salary_income.hra_received,
                    input_data.house_property_income.actual_rent
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
            house_property_income=input_data.house_property_income,
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