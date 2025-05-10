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

    # Medical Reimbursement
    is_treated_in_India: bool = False
    medical_reimbursement_by_employer: float = 0
    travelling_allowance_for_treatment: float = 0
    rbi_limit_for_illness: float = 0

    # Free Education
    employer_maintained_1st_child: bool = False
    monthly_count_1st_child: int = 0
    employer_monthly_expenses_1st_child: float = 0

    employer_maintained_2nd_child: bool = False
    monthly_count_2nd_child: int = 0
    employer_monthly_expenses_2nd_child: float = 0

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

    # Interest-free/concessional loan
    loan_type: str = 'Personal'
    loan_amount: float = 0
    loan_interest_rate_company: float = 0
    loan_interest_rate_sbi: float = 0
    loan_month_count: int = 0
    loan_start_date: str = ''
    loan_end_date: str = ''

    # Leave Travel Allowance
    lta_amount_claimed: float = 0
    lta_claimed_count: int = 0
    travel_through: str = 'Air'  # Railway, Air, Public Transport 
    public_transport_travel_amount_for_same_distance: float = 0

    # ESOP
    number_of_esop_shares_awarded: float = 0
    esop_exercise_price_per_share: float = 0
    esop_allotment_price_per_share: float = 0
    grant_date: Optional[date] = None
    vesting_date: Optional[date] = None
    exercise_date: Optional[date] = None
    vesting_period: int = 0
    exercise_period: int = 0
    exercise_price_per_share: float = 0

    mau_ownership: str = 'Employer-Owned'  # 'Employer-Owned', 'Employer-Hired'
    mau_value_to_employer: float = 0
    mau_value_to_employee: float = 0

    mat_type: str = 'Electronics'  # 'Electronics', 'Motor Vehicle', 'Other'
    mat_value_to_employer: float = 0
    mat_value_to_employee: float = 0
    mat_number_of_completed_years_of_use: int = 0
    # Lunch/Refreshment
    lunch_amount_paid_by_employer: float = 0
    lunch_amount_paid_by_employee: float = 0

    # Monetary benefits
    monetary_amount_paid_by_employer: float = 0
    expenditure_for_offical_purpose: float = 0
    monetary_benefits_amount_paid_by_employee: float = 0

    # Gift Vouchers (new field for partial exemption)
    gift_vouchers_amount_paid_by_employer: float = 0

    # Club Expenses
    club_expenses_amount_paid_by_employer: float = 0
    club_expenses_amount_paid_by_employee: float = 0
    club_expenses_amount_paid_for_offical_purpose: float = 0

    # Domestic help
    domestic_help_amount_paid_by_employer: float = 0
    domestic_help_amount_paid_by_employee: float = 0

    def total_accommodation_value(self, gross_salary: float, regime: str = 'new') -> float:
        """Calculate taxable value of accommodation perquisite."""
        if regime == 'new':
            return 0
        
        if self.is_furniture_owned:
            furniture_value = (self.furniture_cost_to_employer * 0.1) - self.furniture_cost_paid_by_employee
        else:
            furniture_value = self.furniture_cost_to_employer - self.furniture_cost_paid_by_employee

        if self.accommodation_provided == 'Govt':
            return self.accommodation_govt_lic_fees - self.accommodation_rent + furniture_value
        elif self.accommodation_provided == 'Employer-Owned':
            if self.accommodation_city_population == 'Exceeding 40 lakhs in 2011 Census':
                return (gross_salary * 0.1) + furniture_value
            elif self.accommodation_city_population == 'Between 15 lakhs and 40 lakhs in 2011 Census':
                return (gross_salary * 0.075) + furniture_value
            elif self.accommodation_city_population == 'Below 15 lakhs in 2011 Census':
                return gross_salary * 0.05
        elif self.accommodation_provided == 'Employer-Leased':
            return ((min(self.accommodation_rent, (gross_salary * 0.10))) + furniture_value)
        elif self.accommodation_provided == 'Hotel provided for 15 days or above':
            return min(self.accommodation_rent, (gross_salary * 0.24)) - self.furniture_cost_paid_by_employee
        else:
            return 0

    def total_car_value(self, gross_salary: float, regime: str = 'new') -> float:
        """Calculate taxable value of car perquisite."""
        if regime == 'new':
            return 0
        
        if self.car_use == 'Personal':
            return (self.car_cost_to_employer * self.month_counts) + \
                    (self.other_vehicle_cost_to_employer - 900) * self.other_vehicle_month_counts
        elif self.car_use == 'Mixed':
            if self.is_expenses_reimbursed:
                value = 1800 if self.is_car_rating_higher else 2400
                if self.is_driver_provided:
                    value += 900
                return (value * self.month_counts) + ((self.other_vehicle_cost_to_employer - 900) 
                                                    * self.other_vehicle_month_counts)
            else:
                value = 600 if self.is_car_rating_higher else 900
                if self.is_driver_provided:
                    value += 900
                return ((value * self.month_counts) + ((self.other_vehicle_cost_to_employer - 900) 
                                                    * self.other_vehicle_month_counts))
    
    def total_medical_reimbursement(self, gross_salary: float, regime: str = 'new') -> float:
        """Taxable value of medical reimbursement (exempt up to 15,000 if treated in India)."""
        if regime == 'new':
            return 0
        
        elif self.is_treated_in_India:
            return max(0, self.medical_reimbursement_by_employer - 15000)
        else:
            travel_value = 0
            if gross_salary < 200000:   # 2L
                travel_value = self.travelling_allowance_for_treatment
            return travel_value + min(0, self.medical_reimbursement_by_employer - self.rbi_limit_for_illness)

    def total_lta_value(self, regime: str = 'new') -> float:
        """Taxable value of Leave Travel Allowance (LTA)."""
        if regime == 'new':
            return 0
        else:
            # LTA exemption is limited to 2 journeys in a block of 4 years
            if self.lta_claimed_count <= 2:
                return max(0, self.lta_amount_claimed - self.public_transport_travel_amount_for_same_distance)
            else:
                return 0

    def total_free_education_value(self, regime: str = 'new') -> float:
        """Taxable value of free education perquisite."""
        if regime == 'new':
            return 0
        else:
            monthly_exemption = 1000  # Rs. 1,000 per month
            value = 0
            if (self.monthly_count_1st_child > 0):
                value = max(0, self.employer_monthly_expenses_1st_child - monthly_exemption) * self.monthly_count_1st_child
            if (self.monthly_count_2nd_child > 0):
                value += max(0, self.employer_monthly_expenses_2nd_child - monthly_exemption) * self.monthly_count_2nd_child
            return value

    def total_gas_electricity_water_value(self, regime: str = 'new') -> float:
        """Taxable value of gas, electricity, and water perquisite."""
        if regime == 'new':
            return 0
        else:
            paid_by_employer_sum = self.gas_amount_paid_by_employer + self.electricity_amount_paid_by_employer + self.water_amount_paid_by_employer
            paid_by_employee_sum = self.gas_amount_paid_by_employee + self.electricity_amount_paid_by_employee + self.water_amount_paid_by_employee
            return max(0, paid_by_employer_sum - paid_by_employee_sum)
        
    def total_domestic_help_value(self, regime: str = 'new') -> float:
        """Taxable value of domestic help perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.domestic_help_amount_paid_by_employer - self.domestic_help_amount_paid_by_employee)

    def total_interest_amount(self, regime: str = 'new') -> float:
        """Taxable value of interest-free/concessional loan perquisite."""
        if regime == 'new':
            return 0
        else:
            interest_rate_diff = self.loan_interest_rate_sbi - self.loan_interest_rate_company
            if interest_rate_diff > 0:
                return max(0, interest_rate_diff)/12 * self.loan_month_count
            else:
                return 0
    
    def allocation_gain(self, regime: str = 'new') -> float:
        """Taxable value of ESOP allocation gain."""
        if regime == 'new':
            return 0
        else:
            return max(0, (self.esop_allotment_price_per_share - self.esop_exercise_price_per_share) * self.number_of_esop_shares_awarded)
    
    def total_mau_value(self, regime: str = 'new') -> float:
        """Calculate total value of movable assets."""
        if regime == 'new':
            return 0
        
        employer_cost = 0
        if self.mau_ownership == 'Employer-Owned':
            employer_cost = (self.mau_value_to_employer * 0.1)
        else:
            employer_cost = self.mau_value_to_employer
        
        return max(0, employer_cost - self.mau_value_to_employee)
        

    def total_mat_value(self, regime: str = 'new') -> float:
        """Taxable value of transfer of movable assets perquisite."""
        if regime == 'new':
            return 0
        else:
            if self.mat_type == 'Electronics':
                depreciated_value = (self.mat_value_to_employer * 0.5) * (self.mat_number_of_completed_years_of_use)
            elif self.mat_type == 'Motor Vehicle':
                depreciated_value = (self.mat_value_to_employer * 0.2) * (self.mat_number_of_completed_years_of_use)
            else:
                depreciated_value = (self.mat_value_to_employer * 0.1) * (self.mat_number_of_completed_years_of_use)
        
        return max(0, (self.mat_value_to_employer - depreciated_value) - self.mat_value_to_employee)

    def total_monetary_benefits_value(self, regime: str = 'new') -> float:
        """Taxable value of monetary benefits perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.monetary_amount_paid_by_employer - 
                       self.expenditure_for_offical_purpose - 
                       self.monetary_benefits_amount_paid_by_employee)
        
    def total_gift_vouchers_value(self, regime: str = 'new') -> float:
        """Taxable value of gift vouchers (exempt up to Rs. 5,000)."""
        if regime == 'new':
            return 0
        else:
            # Only the amount above 5,000 is taxable
            return max(0, self.gift_vouchers_amount_paid_by_employer - 5000)
            
    def total_club_expenses_value(self, regime: str = 'new') -> float:
        """Taxable value of club expenses perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.club_expenses_amount_paid_by_employer - 
                       self.club_expenses_amount_paid_by_employee - 
                       self.club_expenses_amount_paid_for_offical_purpose)

    def total_lunch_value(self, regime: str = 'new') -> float:
        """Taxable value of lunch/refreshment perquisite."""
        if regime == 'new':
            return 0
        else:
            # Apply the exemption of Rs. 50 per meal
            exemption_per_meal = 50
            # Assume daily lunch for 22 working days per month
            annual_exemption = exemption_per_meal * 22 * 12
            return max(0, self.lunch_amount_paid_by_employer - 
                       self.lunch_amount_paid_by_employee - 
                       annual_exemption)

    def total(self, regime: str = 'new') -> float:
        """
        Calculate total taxable value of all perquisites for the given regime.
        Includes all perquisite types as per Indian tax rules.
        """
        if regime == 'new':
            return 0
        total_value = 0.0
        # Add all perquisite calculations
        total_value += self.total_accommodation_value(gross_salary=0, regime=regime)  # gross_salary to be passed if available
        total_value += self.total_car_value(gross_salary=0, regime=regime)
        total_value += self.total_medical_reimbursement(gross_salary=0, regime=regime)
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
            "loan_interest_rate_company": self.loan_interest_rate_company,
            "loan_interest_rate_sbi": self.loan_interest_rate_sbi,
            "loan_month_count": self.loan_month_count,
            "loan_start_date": self.loan_start_date,
            "loan_end_date": self.loan_end_date,
            
            # Lunch
            "lunch_amount_paid_by_employer": self.lunch_amount_paid_by_employer,
            "lunch_amount_paid_by_employee": self.lunch_amount_paid_by_employee,
            
            # ESOP
            "number_of_esop_shares_awarded": self.number_of_esop_shares_awarded,
            "esop_exercise_price_per_share": self.esop_exercise_price_per_share,
            "esop_allotment_price_per_share": self.esop_allotment_price_per_share,
            "grant_date": self.grant_date.isoformat() if self.grant_date else None,
            "vesting_date": self.vesting_date.isoformat() if self.vesting_date else None,
            "exercise_date": self.exercise_date.isoformat() if self.exercise_date else None,
            "vesting_period": self.vesting_period,
            "exercise_period": self.exercise_period,
            "exercise_price_per_share": self.exercise_price_per_share,
            
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