"""
Perquisites model for taxation calculations.

Represents all perquisites as per Indian Income Tax Act including:
- Accommodation benefits
- Car & transport
- Medical reimbursement
- Leave travel allowance
- Education benefits
- ESOPs & Stock options
- And other perquisites
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Perquisites:
    """
    Represents all perquisites as per Indian Income Tax Act.
    Each perquisite has its own exemption/taxability logic.
    """

    # Accommodation perquisites
    accommodation_provided: str = 'Employer-Owned'  # Employer-Owned, Govt, Employer-Leased, Hotel provided for 15 days or above
    accommodation_govt_lic_fees: float = 0
    accommodation_city_population: str = 'Exceeding 40 lakhs in 2011 Census'
    accommodation_rent: float = 0
    is_furniture_owned: bool = False
    furniture_actual_cost: float = 0
    furniture_cost_to_employer: float = 0
    furniture_cost_paid_by_employee: float = 0

    #Gross Salary : Basic + DA
    def total_accommodation_value(self, gross_salary: float, regime: str = 'new') -> float:
        """Calculate taxable value of accommodation perquisite."""
        if regime == 'new':
            return 0
        
        logger.info(f"Calculating total accommodation value for regime: {regime}")
        logger.info(f"Gross salary: {gross_salary}")
        logger.info(f"Furniture owned: {self.is_furniture_owned}")
        logger.info(f"Furniture cost to employer: {self.furniture_cost_to_employer}")
        logger.info(f"Furniture cost paid by employee: {self.furniture_cost_paid_by_employee}")
        logger.info(f"Accommodation provided: {self.accommodation_provided}")
        logger.info(f"Accommodation rent: {self.accommodation_rent}")
        logger.info(f"Accommodation city population: {self.accommodation_city_population}")
        logger.info(f"Accommodation gov lic fees: {self.accommodation_govt_lic_fees}")
        
        if self.is_furniture_owned:
            furniture_value = (self.furniture_cost_to_employer * 0.1) - self.furniture_cost_paid_by_employee
        else:
            furniture_value = self.furniture_cost_to_employer - self.furniture_cost_paid_by_employee

        logger.info(f"Furniture value: {furniture_value}")
        if self.accommodation_provided == 'Govt':
            logger.info(f"Govt accommodation value: {self.accommodation_govt_lic_fees - self.accommodation_rent + furniture_value}")
            return self.accommodation_govt_lic_fees - self.accommodation_rent + furniture_value
        elif self.accommodation_provided == 'Employer-Owned':
            if self.accommodation_city_population == 'Exceeding 40 lakhs in 2011 Census':
                logger.info(f"Exceeding 40 lakhs in 2011 Census: {(gross_salary * 0.1) + furniture_value}")
                return (gross_salary * 0.1) + furniture_value
            elif self.accommodation_city_population == 'Between 15 lakhs and 40 lakhs in 2011 Census':
                logger.info(f"Between 15 lakhs and 40 lakhs in 2011 Census: {(gross_salary * 0.075) + furniture_value}")
                return (gross_salary * 0.075) + furniture_value
            elif self.accommodation_city_population == 'Below 15 lakhs in 2011 Census':
                logger.info(f"Below 15 lakhs in 2011 Census: {gross_salary * 0.05}")
                return gross_salary * 0.05
        elif self.accommodation_provided == 'Employer-Leased':
            logger.info(f"Employer-Leased: {(min(self.accommodation_rent, (gross_salary * 0.10))) + furniture_value}")
            return ((min(self.accommodation_rent, (gross_salary * 0.10))) + furniture_value)
        elif self.accommodation_provided == 'Hotel provided for 15 days or above':
            logger.info(f"Hotel provided for 15 days or above: {min(self.accommodation_rent, (gross_salary * 0.24))}")
            return min(self.accommodation_rent, (gross_salary * 0.24))
        else:
            logger.info(f"No accommodation provided: 0")
            return 0


    # Car perquisites
    is_car_rating_higher: bool = False  # True if engine capacity > 1.6L
    is_car_employer_owned: bool = False
    is_expenses_reimbursed: bool = False
    is_driver_provided: bool = False
    car_use: str = 'Personal'  # Personal, Business, Mixed
    car_cost_to_employer: float = 0     # expense incurred by employer
    month_counts: int = 0
    other_vehicle_cost_to_employer: float = 0
    other_vehicle_month_counts: int = 0

    def total_car_value(self, regime: str = 'new') -> float:
        """
        Calculate taxable value of car perquisite.
        
        FIXED CRITICAL ERRORS:
        1. Car rating logic was inverted - higher capacity (>1.6L) gets HIGHER rates, not lower
        2. Personal use should use actual costs, not predefined rates
        3. Mixed use calculation was incorrect
        """
        if regime == 'new':
            return 0
        logger.info(f"Calculating total car value for regime: {regime}")
        logger.info(f"Car use: {self.car_use}")
        logger.info(f"Car cost to employer: {self.car_cost_to_employer}")
        logger.info(f"Month counts: {self.month_counts}")
        logger.info(f"Other vehicle cost to employer: {self.other_vehicle_cost_to_employer}")
        logger.info(f"Other vehicle month counts: {self.other_vehicle_month_counts}")
        logger.info(f"Is expenses reimbursed: {self.is_expenses_reimbursed}")
        logger.info(f"Is car rating higher: {self.is_car_rating_higher}")
        logger.info(f"Is driver provided: {self.is_driver_provided}")
        
        if self.car_use == 'Personal':
            # FIXED: For personal use, full cost is taxable
            return (self.car_cost_to_employer * self.month_counts) + \
                   max(0, (self.other_vehicle_cost_to_employer * self.other_vehicle_month_counts))
        elif self.car_use == 'Mixed':
            if self.is_expenses_reimbursed:
                # FIXED: Higher capacity (>1.6L) gets HIGHER rates
                value = 2400 if self.is_car_rating_higher else 1800
                logger.info(f"Mixed use with expenses reimbursed: Higher capacity gets Rs. 2,400, lower gets Rs. 1,800")
            else:
                # FIXED: Higher capacity (>1.6L) gets HIGHER rates
                value = 900 if self.is_car_rating_higher else 600
                logger.info(f"Mixed use without expenses reimbursed: Higher capacity gets Rs. 900, lower gets Rs. 600")
            
            if self.is_driver_provided:
                value += 900  # Additional Rs. 900 for driver
                
            return (value * self.month_counts) + max(0, (self.other_vehicle_cost_to_employer * self.other_vehicle_month_counts))
        elif self.car_use == 'Business':
            # Business use is generally not taxable
            logger.info(f"Business use: No perquisite value")
            return 0
        else:
            return 0

    # Medical Reimbursement -- ToDo: OpenEnded for now as not able to figureout components for Gross Salary
    is_treated_in_India: bool = False
    medical_reimbursement_by_employer: float = 0
    travelling_allowance_for_treatment: float = 0
    rbi_limit_for_illness: float = 0

    def total_medical_reimbursement(self, gross_salary: float, regime: str = 'new') -> float:
        """
        Taxable value of medical reimbursement.
        
        FIXED CRITICAL ERRORS:
        1. Overseas treatment calculation was wrong
        2. Travel allowance logic was unclear
        3. RBI limit application was incorrect
        """
        if regime == 'new':
            return 0
        logger.info(f"Calculating total medical reimbursement for regime: {regime}")
        logger.info(f"Is treated in India: {self.is_treated_in_India}")
        logger.info(f"Medical reimbursement by employer: {self.medical_reimbursement_by_employer}")
        logger.info(f"Travelling allowance for treatment: {self.travelling_allowance_for_treatment}")
        logger.info(f"RBI limit for illness: {self.rbi_limit_for_illness}")
        
        if self.is_treated_in_India:
            # FIXED: For treatment in India, Rs. 15,000 exemption applies
            return max(0, self.medical_reimbursement_by_employer - 15000)
        else:
            # FIXED: For overseas treatment
            # 1. Travel allowance is taxable if gross salary > Rs. 2 lakh
            # 2. Medical expenses beyond RBI limit are taxable
            travel_value = 0
            if gross_salary > 200000:  # Rs. 2 lakh
                travel_value = self.travelling_allowance_for_treatment
                
            # Medical reimbursement beyond RBI limit is taxable
            medical_value = max(0, self.medical_reimbursement_by_employer - self.rbi_limit_for_illness)
            
            logger.info(f"Overseas treatment: Travel value: {travel_value}, Medical value: {medical_value}")
            return travel_value + medical_value

    # Leave Travel Allowance
    lta_amount_claimed: float = 0
    lta_claimed_count: int = 0
    travel_through: str = 'Air'  # Railway, Air, Public Transport 
    public_transport_travel_amount_for_same_distance: float = 0

    def total_lta_value(self, regime: str = 'new') -> float:
        """
        Taxable value of Leave Travel Allowance (LTA).
        
        FIXED CRITICAL ERRORS:
        1. LTA exemption logic was incomplete
        2. Should compare actual vs eligible amount, not just count
        3. Travel mode restrictions were not properly implemented
        """
        if regime == 'new':
            return 0
        logger.info(f"Calculating total LTA value for regime: {regime}")
        logger.info(f"LTA amount claimed: {self.lta_amount_claimed}")
        logger.info(f"LTA claimed count: {self.lta_claimed_count}")
        logger.info(f"Travel through: {self.travel_through}")
        logger.info(f"Public transport travel amount for same distance: {self.public_transport_travel_amount_for_same_distance}")
        
        # FIXED: LTA exemption rules
        # 1. Limited to 2 journeys in a block of 4 years
        # 2. Exemption is limited to actual cost or economy class airfare/AC first class railway fare
        
        if self.lta_claimed_count > 2:
            logger.info(f"LTA claimed more than 2 times in 4-year block, fully taxable")
            return self.lta_amount_claimed
            
        # FIXED: Calculate eligible exemption based on travel mode
        if self.travel_through == 'Railway':
            # For railway, generally AC First Class fare is the limit
            eligible_exemption = self.public_transport_travel_amount_for_same_distance
        elif self.travel_through == 'Air':
            # For air travel, economy class fare is the limit
            eligible_exemption = self.public_transport_travel_amount_for_same_distance
        else:
            # For other modes, actual public transport cost
            eligible_exemption = self.public_transport_travel_amount_for_same_distance
            
        # Taxable amount is excess of claimed over eligible
        taxable_amount = max(0, self.lta_amount_claimed - eligible_exemption)
        logger.info(f"LTA calculation: Claimed: {self.lta_amount_claimed}, Eligible: {eligible_exemption}, Taxable: {taxable_amount}")
        return taxable_amount

    # Gas, Electricity, Water
    is_gas_manufactured_by_employer: bool = False
    gas_amount_paid_by_employer: float = 0
    gas_amount_paid_by_employee: float = 0

    is_electricity_manufactured_by_employer: bool = False
    electricity_amount_paid_by_employer: float = 0
    electricity_amount_paid_by_employee: float = 0

    is_water_manufactured_by_employer: bool = False
    water_amount_paid_by_employer: float = 0
    water_amount_paid_by_employee: float = 0

    def total_gas_electricity_water_value(self, regime: str = 'new') -> float:
        """Taxable value of gas, electricity, and water perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total gas, electricity, and water value for regime: {regime}")
        logger.info(f"Is gas manufactured by employer: {self.is_gas_manufactured_by_employer}")
        logger.info(f"Gas amount paid by employer: {self.gas_amount_paid_by_employer}")
        logger.info(f"Gas amount paid by employee: {self.gas_amount_paid_by_employee}")
        logger.info(f"Is electricity manufactured by employer: {self.is_electricity_manufactured_by_employer}")
        logger.info(f"Electricity amount paid by employer: {self.electricity_amount_paid_by_employer}")
        logger.info(f"Electricity amount paid by employee: {self.electricity_amount_paid_by_employee}")
        logger.info(f"Is water manufactured by employer: {self.is_water_manufactured_by_employer}")
        logger.info(f"Water amount paid by employer: {self.water_amount_paid_by_employer}")
        logger.info(f"Water amount paid by employee: {self.water_amount_paid_by_employee}")
        
        paid_by_employer_sum = self.gas_amount_paid_by_employer + self.electricity_amount_paid_by_employer + self.water_amount_paid_by_employer
        paid_by_employee_sum = self.gas_amount_paid_by_employee + self.electricity_amount_paid_by_employee + self.water_amount_paid_by_employee
        return max(0, paid_by_employer_sum - paid_by_employee_sum)

    # Free Education
    employer_maintained_1st_child: bool = False
    monthly_count_1st_child: int = 0
    employer_monthly_expenses_1st_child: float = 0

    employer_maintained_2nd_child: bool = False
    monthly_count_2nd_child: int = 0
    employer_monthly_expenses_2nd_child: float = 0

    def total_free_education_value(self, regime: str = 'new') -> float:
        """Taxable value of free education perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total free education value for regime: {regime}")
        logger.info(f"Employer maintained 1st child: {self.employer_maintained_1st_child}")
        logger.info(f"Monthly count 1st child: {self.monthly_count_1st_child}")
        logger.info(f"Employer monthly expenses 1st child: {self.employer_monthly_expenses_1st_child}")
        logger.info(f"Employer maintained 2nd child: {self.employer_maintained_2nd_child}")
        logger.info(f"Monthly count 2nd child: {self.monthly_count_2nd_child}")
        logger.info(f"Employer monthly expenses 2nd child: {self.employer_monthly_expenses_2nd_child}")

        monthly_exemption = 1000  # Rs. 1,000 per month
        value = 0
        if (self.monthly_count_1st_child > 0):
            value = max(0, self.employer_monthly_expenses_1st_child - monthly_exemption) * self.monthly_count_1st_child
        if (self.monthly_count_2nd_child > 0):
            value += max(0, self.employer_monthly_expenses_2nd_child - monthly_exemption) * self.monthly_count_2nd_child
        return value

    # Interest-free/concessional loan
    loan_type: str = 'Personal'
    loan_amount: float = 0
    outstanding_loan_amount: float = 0 
    loan_interest_rate_company: float = 0
    loan_interest_rate_sbi: float = 0
    loan_month_count: int = 0
    loan_emi_amount: float = 0
    loan_start_date: str = ''
    loan_end_date: str = ''


    #TODO: Prepayment of loan need to be worked on.

    def total_interest_amount(self, regime: str = 'new') -> float:
        """
        Taxable value of interest-free/concessional loan perquisite.
        
        FIXED CRITICAL ERROR: 
        - Previous calculation was returning annual value incorrectly
        - Should return the actual interest differential for the fiscal year
        """
        if regime == 'new':
            return 0

        logger.info(f"Calculating total interest amount for regime: {regime}")
        logger.info(f"Loan type: {self.loan_type}")
        logger.info(f"Loan amount: {self.loan_amount}")
        logger.info(f"Outstanding loan amount: {self.outstanding_loan_amount}")
        logger.info(f"Loan interest rate company: {self.loan_interest_rate_company}")
        logger.info(f"Loan interest rate SBI: {self.loan_interest_rate_sbi}")
        logger.info(f"Loan EMI amount: {self.loan_emi_amount}")
        logger.info(f"Loan start date: {self.loan_start_date}")
        logger.info(f"Loan end date: {self.loan_end_date}")
        
        # Early return for exempt loans
        if self.loan_type == 'Medical' or self.loan_amount <= 20000:
            logger.info(f"Loan exempt: Type={self.loan_type}, Amount={self.loan_amount}")
            return 0
        
        # Calculate interest rate differential
        interest_rate_diff = self.loan_interest_rate_sbi - self.loan_interest_rate_company
        if interest_rate_diff <= 0:
            logger.info(f"No interest benefit: SBI rate ({self.loan_interest_rate_sbi}%) <= Company rate ({self.loan_interest_rate_company}%)")
            return 0
        
        # Use outstanding amount if provided, otherwise use loan amount
        principal_amount = self.outstanding_loan_amount if self.outstanding_loan_amount > 0 else self.loan_amount
        
        # FIXED: Calculate annual interest differential correctly
        annual_interest_differential = principal_amount * (interest_rate_diff / 100)
        
        logger.info(f"Interest calculation: Principal: {principal_amount}, Rate diff: {interest_rate_diff}%, Annual differential: {annual_interest_differential}")
        
        # If specific months are provided, prorate the amount
        if self.loan_month_count > 0 and self.loan_month_count < 12:
            prorated_amount = annual_interest_differential * (self.loan_month_count / 12)
            logger.info(f"Prorated for {self.loan_month_count} months: {prorated_amount}")
            return prorated_amount
        
        return annual_interest_differential

    
    # ESOP
    number_of_esop_shares_exercised: float = 0
    esop_exercise_price_per_share: float = 0
    esop_allotment_price_per_share: float = 0

    def allocation_gain(self, regime: str = 'new') -> float:
        """Taxable value of ESOP allocation gain."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating allocation gain for regime: {regime}")
        logger.info(f"ESOP allotment price per share: {self.esop_allotment_price_per_share}")
        logger.info(f"ESOP exercise price per share: {self.esop_exercise_price_per_share}")
        logger.info(f"Number of ESOP shares Exercised: {self.number_of_esop_shares_exercised}")
        
        return max(0, (self.esop_exercise_price_per_share - self.esop_allotment_price_per_share) * self.number_of_esop_shares_exercised)


    mau_ownership: str = 'Employer-Owned'  # 'Employer-Owned', 'Employer-Hired'
    mau_value_to_employer: float = 0
    mau_value_to_employee: float = 0

    def total_mau_value(self, regime: str = 'new') -> float:
        """Calculate total value of movable assets."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total MAU value for regime: {regime}")
        logger.info(f"MAU ownership: {self.mau_ownership}")
        logger.info(f"MAU value to employer: {self.mau_value_to_employer}")
        logger.info(f"MAU value to employee: {self.mau_value_to_employee}")
        
        employer_cost = 0
        if self.mau_ownership == 'Employer-Owned':
            employer_cost = (self.mau_value_to_employer * 0.1)
        else:
            employer_cost = self.mau_value_to_employer
        
        return max(0, employer_cost - self.mau_value_to_employee)
    
    mat_type: str = 'Electronics'  # 'Electronics', 'Motor Vehicle', 'Other'
    mat_value_to_employer: float = 0
    mat_value_to_employee: float = 0
    mat_number_of_completed_years_of_use: int = 0

    def total_mat_value(self, regime: str = 'new') -> float:
        """Taxable value of transfer of movable assets perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total MAT value for regime: {regime}")
        logger.info(f"MAT type: {self.mat_type}")
        logger.info(f"MAT value to employer: {self.mat_value_to_employer}")
        logger.info(f"MAT value to employee: {self.mat_value_to_employee}")
        logger.info(f"MAT number of completed years of use: {self.mat_number_of_completed_years_of_use}")
        
        # Ensure mat_number_of_completed_years_of_use is an integer
        try:
            years_of_use = int(self.mat_number_of_completed_years_of_use)
        except (ValueError, TypeError):
            logger.error(f"Invalid value for mat_number_of_completed_years_of_use: {self.mat_number_of_completed_years_of_use}, using 0")
            years_of_use = 0
        
        if self.mat_type == 'Electronics':
            depreciated_value = (self.mat_value_to_employer * 0.5) * years_of_use
        elif self.mat_type == 'Motor Vehicle':
            depreciated_value = (self.mat_value_to_employer * 0.2) * years_of_use
        else:
            depreciated_value = (self.mat_value_to_employer * 0.1) * years_of_use
        
        return max(0, (self.mat_value_to_employer - depreciated_value) - self.mat_value_to_employee)

    # Lunch/Refreshment
    lunch_amount_paid_by_employer: float = 0
    lunch_amount_paid_by_employee: float = 0
    lunch_amount_days_per_year: int = 0

    def total_lunch_value(self, regime: str = 'new') -> float:
        """Taxable value of lunch/refreshment perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total lunch value for regime: {regime}")
        logger.info(f"Lunch amount paid by employer: {self.lunch_amount_paid_by_employer}")
        logger.info(f"Lunch amount paid by employee: {self.lunch_amount_paid_by_employee}")
        # Apply the exemption of Rs. 50 per meal
        exemption_per_meal = 50
        annual_exemption = exemption_per_meal * self.lunch_amount_days_per_year
        return max(0, self.lunch_amount_paid_by_employer - 
                    self.lunch_amount_paid_by_employee - 
                    annual_exemption)
        
    # Monetary benefits
    monetary_amount_paid_by_employer: float = 0
    expenditure_for_offical_purpose: float = 0
    monetary_benefits_amount_paid_by_employee: float = 0

    def total_monetary_benefits_value(self, regime: str = 'new') -> float:
        """Taxable value of monetary benefits perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total monetary benefits value for regime: {regime}")
        logger.info(f"Monetary amount paid by employer: {self.monetary_amount_paid_by_employer}")
        logger.info(f"Expenditure for offical purpose: {self.expenditure_for_offical_purpose}")
        logger.info(f"Monetary benefits amount paid by employee: {self.monetary_benefits_amount_paid_by_employee}")
        return max(0, self.monetary_amount_paid_by_employer - 
                       self.expenditure_for_offical_purpose - 
                       self.monetary_benefits_amount_paid_by_employee)

    # Gift Vouchers (new field for partial exemption)
    gift_vouchers_amount_paid_by_employer: float = 0

    def total_gift_vouchers_value(self, regime: str = 'new') -> float:
        """
        Taxable value of gift vouchers.
        
        FIXED CRITICAL ERROR: 
        - Gift vouchers up to Rs. 5,000 are exempt
        - Only amount ABOVE Rs. 5,000 is taxable
        """
        if regime == 'new':
            return 0
        logger.info(f"Calculating total gift vouchers value for regime: {regime}")
        logger.info(f"Gift vouchers amount paid by employer: {self.gift_vouchers_amount_paid_by_employer}")
        
        # FIXED: Only the amount above Rs. 5,000 is taxable
        if self.gift_vouchers_amount_paid_by_employer <= 5000:
            logger.info(f"Gift vouchers within Rs. 5,000 exemption limit: No tax")
            return 0
        else:
            taxable_amount = self.gift_vouchers_amount_paid_by_employer - 5000
            logger.info(f"Gift vouchers exceeding Rs. 5,000 limit: Taxable amount = {taxable_amount}")
            return taxable_amount

    # Club Expenses
    club_expenses_amount_paid_by_employer: float = 0
    club_expenses_amount_paid_by_employee: float = 0
    club_expenses_amount_paid_for_offical_purpose: float = 0

    def total_club_expenses_value(self, regime: str = 'new') -> float:
        """Taxable value of club expenses perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total club expenses value for regime: {regime}")
        logger.info(f"Club expenses amount paid by employer: {self.club_expenses_amount_paid_by_employer}")
        logger.info(f"Club expenses amount paid by employee: {self.club_expenses_amount_paid_by_employee}")
        logger.info(f"Club expenses amount paid for offical purpose: {self.club_expenses_amount_paid_for_offical_purpose}")
        return max(0, self.club_expenses_amount_paid_by_employer - 
                       self.club_expenses_amount_paid_by_employee - 
                       self.club_expenses_amount_paid_for_offical_purpose)

    # Domestic help
    domestic_help_amount_paid_by_employer: float = 0
    domestic_help_amount_paid_by_employee: float = 0

    def total_domestic_help_value(self, regime: str = 'new') -> float:
        """Taxable value of domestic help perquisite."""
        if regime == 'new':
            return 0
        logger.info(f"Calculating total domestic help value for regime: {regime}")
        logger.info(f"Domestic help amount paid by employer: {self.domestic_help_amount_paid_by_employer}")
        logger.info(f"Domestic help amount paid by employee: {self.domestic_help_amount_paid_by_employee}")
        return max(0, self.domestic_help_amount_paid_by_employer - self.domestic_help_amount_paid_by_employee)

    
    def total_taxable_income_per_slab(self, gross_salary: float, regime: str = 'new') -> float:
        """
        Calculate total taxable value of all perquisites for the given regime.
        Includes all perquisite types as per Indian tax rules.
        
        FIXED: Added missing medical reimbursement calculation.
        """
        if regime == 'new':
            return 0
        total_value = 0.0
        # Add all perquisite calculations
        total_value += self.total_accommodation_value(gross_salary=gross_salary, regime=regime)
        total_value += self.total_car_value(regime=regime)
        total_value += self.total_medical_reimbursement(gross_salary=gross_salary, regime=regime)  # FIXED: Added missing medical reimbursement
        total_value += self.total_lta_value(regime)
        total_value += self.total_free_education_value(regime)
        total_value += self.total_gas_electricity_water_value(regime)
        total_value += self.total_domestic_help_value(regime)
        total_value += self.total_interest_amount(regime)
        total_value += self.total_lunch_value(regime)
        total_value += self.allocation_gain(regime)
        total_value += self.total_mau_value(regime)
        total_value += self.total_mat_value(regime)
        total_value += self.total_monetary_benefits_value(regime)
        total_value += self.total_gift_vouchers_value(regime)
        total_value += self.total_club_expenses_value(regime)
        
        logger.info(f"Total perquisites value: {total_value}")
        return total_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return { 
            "accommodation_provided": self.accommodation_provided,
            "accommodation_govt_lic_fees": self.accommodation_govt_lic_fees,
            "accommodation_city_population": self.accommodation_city_population,
            "accommodation_rent": self.accommodation_rent,
            "is_furniture_owned": self.is_furniture_owned,
            "furniture_actual_cost": self.furniture_actual_cost,
            "furniture_cost_to_employer": self.furniture_cost_to_employer,
            "furniture_cost_paid_by_employee": self.furniture_cost_paid_by_employee,
            "is_car_rating_higher": self.is_car_rating_higher,
            "is_car_employer_owned": self.is_car_employer_owned,
            "is_expenses_reimbursed": self.is_expenses_reimbursed,
            "is_driver_provided": self.is_driver_provided,
            "car_use": self.car_use,
            "car_cost_to_employer": self.car_cost_to_employer,
            "month_counts": self.month_counts,
            "other_vehicle_cost_to_employer": self.other_vehicle_cost_to_employer,
            "other_vehicle_month_counts": self.other_vehicle_month_counts,
            "is_treated_in_India": self.is_treated_in_India,
            "medical_reimbursement_by_employer": self.medical_reimbursement_by_employer,
            "travelling_allowance_for_treatment": self.travelling_allowance_for_treatment,
            "rbi_limit_for_illness": self.rbi_limit_for_illness,
            "lta_amount_claimed": self.lta_amount_claimed,
            "lta_claimed_count": self.lta_claimed_count,
            "travel_through": self.travel_through,
            "public_transport_travel_amount_for_same_distance": self.public_transport_travel_amount_for_same_distance,
            
            # Education fields
            "employer_maintained_1st_child": self.employer_maintained_1st_child,
            "monthly_count_1st_child": self.monthly_count_1st_child,
            "employer_monthly_expenses_1st_child": self.employer_monthly_expenses_1st_child,
            "employer_maintained_2nd_child": self.employer_maintained_2nd_child,
            "monthly_count_2nd_child": self.monthly_count_2nd_child,
            "employer_monthly_expenses_2nd_child": self.employer_monthly_expenses_2nd_child,
            
            # Gas, Electricity, Water
            "is_gas_manufactured_by_employer": self.is_gas_manufactured_by_employer,
            "gas_amount_paid_by_employer": self.gas_amount_paid_by_employer,
            "gas_amount_paid_by_employee": self.gas_amount_paid_by_employee,

            "is_electricity_manufactured_by_employer": self.is_electricity_manufactured_by_employer,
            "electricity_amount_paid_by_employer": self.electricity_amount_paid_by_employer,
            "electricity_amount_paid_by_employee": self.electricity_amount_paid_by_employee,

            "is_water_manufactured_by_employer": self.is_water_manufactured_by_employer,
            "water_amount_paid_by_employer": self.water_amount_paid_by_employer,
            "water_amount_paid_by_employee": self.water_amount_paid_by_employee,
            
            # Domestic help
            "domestic_help_amount_paid_by_employer": self.domestic_help_amount_paid_by_employer,
            "domestic_help_amount_paid_by_employee": self.domestic_help_amount_paid_by_employee,
            
            # Loan details
            "loan_type": self.loan_type,
            "loan_amount": self.loan_amount,
            "outstanding_loan_amount": self.outstanding_loan_amount,
            "loan_interest_rate_company": self.loan_interest_rate_company,
            "loan_interest_rate_sbi": self.loan_interest_rate_sbi,
            "loan_month_count": self.loan_month_count,
            "loan_emi_amount": self.loan_emi_amount,
            "loan_start_date": self.loan_start_date,
            "loan_end_date": self.loan_end_date,
            
            # Lunch
            "lunch_amount_paid_by_employer": self.lunch_amount_paid_by_employer,
            "lunch_amount_paid_by_employee": self.lunch_amount_paid_by_employee,
            
            # ESOP
            "number_of_esop_shares_exercised": self.number_of_esop_shares_exercised,
            "esop_exercise_price_per_share": self.esop_exercise_price_per_share,
            "esop_allotment_price_per_share": self.esop_allotment_price_per_share,
            
            # Movable assets
            "mau_ownership": self.mau_ownership,
            "mau_value_to_employer": self.mau_value_to_employer,
            "mau_value_to_employee": self.mau_value_to_employee,
            "mat_type": self.mat_type,
            "mat_value_to_employer": self.mat_value_to_employer,
            "mat_value_to_employee": self.mat_value_to_employee,
            "mat_number_of_completed_years_of_use": self.mat_number_of_completed_years_of_use,
            
            # Monetary benefits
            "monetary_amount_paid_by_employer": self.monetary_amount_paid_by_employer,
            "expenditure_for_offical_purpose": self.expenditure_for_offical_purpose,
            "monetary_benefits_amount_paid_by_employee": self.monetary_benefits_amount_paid_by_employee,
            
            # Gift vouchers and club expenses
            "gift_vouchers_amount_paid_by_employer": self.gift_vouchers_amount_paid_by_employer,
            "club_expenses_amount_paid_by_employer": self.club_expenses_amount_paid_by_employer,
            "club_expenses_amount_paid_by_employee": self.club_expenses_amount_paid_by_employee,
            "club_expenses_amount_paid_for_offical_purpose": self.club_expenses_amount_paid_for_offical_purpose
        } 