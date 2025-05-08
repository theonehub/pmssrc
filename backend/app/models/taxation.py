from dataclasses import dataclass
from datetime import date
import json
from typing import Optional, Dict, Any, List
import logging
import datetime
logger = logging.getLogger(__name__)

section_80g_100_wo_ql_heads = [
    "National Defence Fund set up by Central Government",
    "Prime Minister national relief fund",
    "Approved university",
    "Any other eligible donations for 100% deduction"
]

section_80g_50_wo_ql_heads = ["Prime Minister's Drought Relief Fund"]

section_80g_100_ql_heads = [
    "Donations to government or any approved local authority to promote family planning",
    "Any other fund that satisfies the conditions"
]

section_80g_50_ql_heads = [
    "Donations to government or any approved local authority to except to promote family planning",
    "Any Corporation for promoting interest of minority community",
    "For repair or renovation of any notified temple, mosque, gurudwara, church or other places of worship",
    "Any other fund that satisfies the conditions"
]

@dataclass
class IncomeFromOtherSources:
    regime: str = 'new'
    age: int = 0
    interest_savings: float = 0
    interest_fd: float = 0
    interest_rd: float = 0
    dividend_income: float = 0
    gifts: float = 0
    other_interest: float = 0
    other_income: float = 0

    def get_section_80tt(self, age: int, regime: str = 'new'):
        if regime == 'old':
            if age >= 60:
                return "80TTB"
            else:
                return "80TTC"
        else:
            return "Not Applicable"

    def total_taxable_income_per_slab(self, regime: str = 'new', age: int = 0):
        deduction = 10000
        if regime == 'new':
            return 0
        
        elif regime == 'old':
            if age >= 60:
                deduction = 50000

        return max(0, sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.other_income
        ]) - deduction)

    def total(self) -> float:
        """Calculate total income from other sources"""
        return sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.other_income
        ])
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "regime": self.regime,
            "age": self.age,
            "interest_savings": self.interest_savings,
            "interest_fd": self.interest_fd,
            "interest_rd": self.interest_rd,
            "dividend_income": self.dividend_income,
            "gifts": self.gifts,
            "other_interest": self.other_interest,
            "other_income": self.other_income
        }

@dataclass
class IncomeFromHouseProperty:
    occupancy_status: str = ''  #LetOut, SelfOccupied, PerConstruction
    rent_income: float = 0
    property_tax: float = 0
    standard_deduction: float = 0
    interest_on_home_loan: float = 0

    def total_taxable_income_per_slab(self, regime: str = 'new'):
        self.standard_deduction = self.rent_income * 0.3
        if regime == 'New':
            if self.occupancy_status == 'LetOut':
                interest = self.interest_on_home_loan
            else:
                interest = 0
        elif self.occupancy_status == 'PerConstruction':
            interest = self.interest_on_home_loan * 0.2
        else:
            interest = self.interest_on_home_loan

        return self.rent_income - self.property_tax - self.standard_deduction - interest
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "occupancy_status": self.occupancy_status,
            "rent_income": self.rent_income,
            "property_tax": self.property_tax,
            "standard_deduction": self.standard_deduction,
            "interest_on_home_loan": self.interest_on_home_loan
        }

@dataclass
class CapitalGains:
    stcg_111a: float = 0    # Short Term Capital Gain from listed equity shares 
                            # and equity oriented mutual funds which are charged to STT
                            # (taxed at 20%)
    stcg_any_other_asset: float = 0     # Short Term Capital Gain from other assets 
                                        # (taxed at slab rates)
    stcg_debt_mutual_fund: float = 0    # Short Term Capital Gain from debt mutual funds 
                                        # (taxed at slab rates)
    
    ltcg_112a: float = 0    # Long Term Capital Gain from listed equity shares 
                            # and equity oriented mutual funds which are charged to STT 
                            # (12.5% above 1.25L)
    ltcg_any_other_asset: float = 0     # Long Term Capital Gain from other assets 
                                        # (taxed at 12.5%)
    ltcg_debt_mutual_fund: float = 0    # Long Term Capital Gain from debt mutual funds 
                                        # (taxed at 12.5%)
        
    def total_stcg_special_rate(self):
        """Total short-term capital gains charged at special rates"""
        return self.stcg_111a
    
    def total_stcg_slab_rate(self):
        """Total short-term capital gains taxed at slab rates"""
        return self.stcg_any_other_asset + self.stcg_debt_mutual_fund
    
    def total_ltcg_special_rate(self):
        """Total long-term capital gains charged at special rates"""
        return self.ltcg_112a + self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
    
    def total(self) -> float:
        """Calculate total capital gains"""
        return (
            self.total_stcg_special_rate() +
            self.total_stcg_slab_rate() +
            self.total_ltcg_special_rate()
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "stcg_111a": self.stcg_111a,
            "stcg_any_other_asset": self.stcg_any_other_asset,
            "stcg_debt_mutual_fund": self.stcg_debt_mutual_fund,
            "ltcg_112a": self.ltcg_112a,
            "ltcg_any_other_asset": self.ltcg_any_other_asset,
            "ltcg_debt_mutual_fund": self.ltcg_debt_mutual_fund
        }

@dataclass
class BusinessProfessionalIncome:
    business_income: float = 0
    professional_income: float = 0
    
    def total_taxable_income_per_slab(self):
        return self.business_income + self.professional_income
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "business_income": self.business_income,
            "professional_income": self.professional_income
        }

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
    monthly_count_1st_child:int = 0
    employer_monthly_expenses_1st_child: float = 0

    employer_maintained_2nd_child: bool = False
    monthly_count_2nd_child:int = 0
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
    travel_through: str = 'Air' #Railway, Air, Public Transport 
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

    # Movable assets - using single field structure for both types of movable assets
    movable_asset_type: str = 'Electronics'  # 'Electronics', 'Motor Vehicle', 'Other'
    movable_asset_value_to_employer: float = 0
    movable_asset_value_to_employee: float = 0
    number_of_completed_years_of_use: int = 0

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
        
        #if self.is_car_employer_owned_hired car its owned or not but computation is same - Discussed with Viral ji
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
            if gross_salary < 200000:   #2L
                travel_value = self.travelling_allowance_for_treatment ###TODO need to check in further discussions
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
        if self.movable_asset_type == 'Electronics':
            return (self.movable_asset_value_to_employer * 0.5) * (self.number_of_completed_years_of_use)
        elif self.movable_asset_type == 'Motor Vehicle':
            return (self.movable_asset_value_to_employer * 0.2) * (self.number_of_completed_years_of_use)
        else:
            return self.movable_asset_value_to_employer 

    def total_mat_value(self, regime: str = 'new') -> float:
        """Taxable value of transfer of movable assets perquisite."""
        if regime == 'new':
            return 0
        else:
            if self.movable_asset_type == 'Electronics':
                asset_current_value = (self.movable_asset_value_to_employer * 0.5) * (self.number_of_completed_years_of_use)
                return max(0, (self.movable_asset_value_to_employer - asset_current_value) - self.movable_asset_value_to_employee)
            elif self.movable_asset_type == 'Motor Vehicle':
                asset_current_value = (self.movable_asset_value_to_employer * 0.2) * (self.number_of_completed_years_of_use)
                return max(0, (self.movable_asset_value_to_employer - asset_current_value) - self.movable_asset_value_to_employee)
            else:
                asset_current_value = self.movable_asset_value_to_employer 
                asset_current_value = (self.movable_asset_value_to_employer * 0.1) * (self.number_of_completed_years_of_use)
                return max(0, (self.movable_asset_value_to_employer - asset_current_value) - self.movable_asset_value_to_employee)

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
        total_value += self.total_medical_reimbursement(regime)
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
            "movable_asset_type": self.movable_asset_type,
            "movable_asset_value_to_employer": self.movable_asset_value_to_employer,
            "movable_asset_value_to_employee": self.movable_asset_value_to_employee,
            "number_of_completed_years_of_use": self.number_of_completed_years_of_use,
            
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

@dataclass
class SalaryComponents:
    """
    Represents all salary components as per Indian Income Tax Act.
    Includes all allowances and perquisites.
    """
    basic: float = 0                                    #Basic Pay(Slab)
    dearness_allowance: float = 0                       #Dearness Allowance(Slab)
    hra_city: str = 'Others'                            #HRA_City_selected(Metadata)
    hra_percentage: float = 0                           #HRA_Percentage(Metadata)
    hra: float = 0                                      #HRA(Slab)
    special_allowance: float = 0                        #Special Allowance(Slab)
    bonus: float = 0                                    #Bonus(Slab)
    commission: float = 0                               #Commission(Slab)
    city_compensatory_allowance: float = 0              #City Compensatory Allowance(Slab)
    rural_allowance: float = 0                          #Rural Allowance(Slab)
    proctorship_allowance: float = 0                    #Proctorship Allowance(Slab)
    wardenship_allowance: float = 0                     #Wardenship Allowance(Slab)
    project_allowance: float = 0                        #Project Allowance(Slab)
    deputation_allowance: float = 0                     #Deputation Allowance(Slab)
    overtime_allowance: float = 0                       #Overtime Allowance(Slab)
    interim_relief: float = 0                           #Interim Relief(Slab)
    tiffin_allowance: float = 0                         #Tiffin Allowance(Slab)
    fixed_medical_allowance: float = 0                  #Fixed Medical Allowance(Slab)
    servant_allowance: float = 0                        #Servant Allowance(Slab)
    any_other_allowance: float = 0                      #Any Other Allowance(Slab)
    any_other_allowance_exemption: float = 0            #Any Other Allowance Exemption(Slab-Deduction)
    govt_employees_outside_india_allowance: float = 0   #Allowances to Government employees outside India(Exempted)
    supreme_high_court_judges_allowance: float = 0      #Allowance to High Court & Supreme Court Judges(Exempted)
    judge_compensatory_allowance: float = 0             #Compensatory Allowance received by a Judge(Exempted)
    section_10_14_special_allowances: float = 0         #Special Allowances exempt under Section 10(14)(Exempted)
    travel_on_tour_allowance: float = 0                 #Allowance granted to meet cost of travel on tour(Exempted)
    tour_daily_charge_allowance: float = 0              #Allowance granted to meet cost of daily charges incurred on tour(Exempted)
    conveyance_in_performace_of_duties: float = 0       #Allowance granted to meet expenditure incurred on conveyance in performace of duties(Exempted)
    helper_in_performace_of_duties: float = 0           #Allowance granted to meet expenditure incurred on helper in performace of duties(Exempted)      
    academic_research: float = 0                        #Allowance granted for encouraging the academic, research & training pursuits in educational & research institutions(Exempted)
    uniform_allowance: float = 0                        #Allowance granted for expenditure incurred on purchase or maintenance of uniform for wear during performace of duties(Exempted)

    perquisites: Optional[Perquisites] = None

    def total(self, regime: str = 'new') -> float:
        """
        Calculate total taxable salary including all components and perquisites.
        """
        if regime == 'old':
            hra = (self.basic + self.dearness_allowance) * self.hra_percentage
        else:
            hra = 0

        logger.info(f"Salary Components - {json.dumps(self.to_dict(), indent=2)}")

        base_total = (
            self.basic + self.dearness_allowance + max(0, self.hra - hra) + self.special_allowance +
            self.bonus + self.commission + self.city_compensatory_allowance + self.rural_allowance +
            self.proctorship_allowance + self.wardenship_allowance + self.project_allowance +
            self.deputation_allowance + self.overtime_allowance + self.interim_relief +
            self.tiffin_allowance + self.fixed_medical_allowance + self.servant_allowance
        )
        if self.perquisites:
            base_total += self.perquisites.total(regime)
        return base_total
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "basic": self.basic,
            "dearness_allowance": self.dearness_allowance,
            "hra_city": self.hra_city,
            "hra_percentage": self.hra_percentage,
            "hra": self.hra,
            "special_allowance": self.special_allowance,
            "bonus": self.bonus,
            "commission": self.commission,
            "city_compensatory_allowance": self.city_compensatory_allowance,
            "rural_allowance": self.rural_allowance,
            "proctorship_allowance": self.proctorship_allowance,
            "wardenship_allowance": self.wardenship_allowance,
            "project_allowance": self.project_allowance,
            "deputation_allowance": self.deputation_allowance,
            "overtime_allowance": self.overtime_allowance,
            "any_other_allowance": self.any_other_allowance,
            "any_other_allowance_exemption": self.any_other_allowance_exemption,
            "interim_relief": self.interim_relief,
            "tiffin_allowance": self.tiffin_allowance,
            "fixed_medical_allowance": self.fixed_medical_allowance,
            "servant_allowance": self.servant_allowance,
            "govt_employees_outside_india_allowance": self.govt_employees_outside_india_allowance,
            "supreme_high_court_judges_allowance": self.supreme_high_court_judges_allowance,
            "judge_compensatory_allowance": self.judge_compensatory_allowance,
            "section_10_14_special_allowances": self.section_10_14_special_allowances,
            "travel_on_tour_allowance": self.travel_on_tour_allowance,
            "tour_daily_charge_allowance": self.tour_daily_charge_allowance,
            "conveyance_in_performace_of_duties": self.conveyance_in_performace_of_duties,
            "helper_in_performace_of_duties": self.helper_in_performace_of_duties,
            "academic_research": self.academic_research,
            "uniform_allowance": self.uniform_allowance,
            "perquisites": self.perquisites.to_dict() if self.perquisites else None
        }

@dataclass
class DeductionComponents:
    regime: str = 'new'
    age: int = 0
    #section 80C
    section_80c_lic: float = 0  #Life Insurance Premium
    section_80c_epf: float = 0  #Employee Provident Fund
    section_80c_ssp: float = 0  #Sukanya Samridhi Account
    section_80c_nsc: float = 0  #National Savings Certificate
    section_80c_ulip: float = 0  #Unit Linked Insurance Plan
    section_80c_tsmf: float = 0  #Tax Saving Mutual Fund
    section_80c_tffte2c: float = 0  #Tuition Fees for full time education of upto 2 kids
    section_80c_paphl: float = 0  #Principal amount paid for housing loan installments
    section_80c_sdpphp: float = 0  #Stamp duty paid for purchase of residental property
    section_80c_tsfdsb: float = 0  #Tax saving fixed deposit in a scheduled bank
    section_80c_scss: float = 0  #Senior citizen savings scheme
    section_80c_others: float = 0  #Others  Max all above 1,50,000

    #section 80CCC
    section_80ccc_ppic: float = 0  #Pension Payment under section  Max 1,50,000

    #section 80CCD
    section_80ccd_1_nps: float = 0  #self-employed or employee contribution to NPS
    section_80ccd_1b_additional: float = 0  #additional contribution to NPS by self-employed 
                                            #or employee Max 50,000

    # Max deduction 1,50,000 for all the above elements


    def total_deductions_80c_80ccd_80ccd_1_1b(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            # Calculate Section 80C total (capped at 150,000)
            section_80c_total = (min(sum([
                self.section_80c_lic,
                self.section_80c_epf,
                self.section_80c_ssp,
                self.section_80c_nsc,
                self.section_80c_ulip,
                self.section_80c_tsmf,
                self.section_80c_tffte2c,
                self.section_80c_paphl,
                self.section_80c_sdpphp,
                self.section_80c_tsfdsb,
                self.section_80c_scss,
                self.section_80c_others,
                self.section_80ccc_ppic,
                self.section_80ccd_1_nps]), 150000) +
                min(self.section_80ccd_1b_additional, 50000))
            return section_80c_total
            
    section_80ccd_2_enps: float = 0  #contribution to NPS by employer 
                                     #14% of salary(govt employees) 
                                     # 10% of salary(private employees)

    def total_deductions_80ccd_2(self, regime: str = 'new', gross_income: float = 0, is_govt_employee: bool = False):
        if regime == 'new':
            return 0
        else:
            if is_govt_employee:
                max_cap = gross_income * 0.14
            else:
                max_cap = gross_income * 0.10
            return min(self.section_80ccd_2_enps, max_cap)
            

    #section 80D Health Insurance Premium
    section_80d_hisf: float = 0     #Health Insurance Premium for self and family
                                    #Max 25,000 if age is above 60 otherwise 50,000
    section_80d_phcs: float = 0     #Preventive health checkups max 5000 per year
                                    #its included in 25k or 50k limit

    def total_deductions_80d_self_family(self, regime: str = 'new', age: int = 0):
        if regime == 'new':
            return 0
        else:
            if age >= 60:
                return min(self.section_80d_hisf + min(self.section_80d_phcs, 5000), 50000)
            else:
                return min(self.section_80d_hisf + min(self.section_80d_phcs, 5000), 25000)

    #section 80D Health Insurance Premium for parents
    section_80d_hi_parent: float = 0  #Health Insurance Premium for parents
                                    #Max 25,000 if age is above 60 otherwise 50,000
    
    def total_deductions_80d_parent(self, regime: str = 'new', age: int = 0):
        if regime == 'new':
            return 0
        else:
            if age >= 60:
                return min(self.section_80d_hi_parent, 50000)
            else:
                return min(self.section_80d_hi_parent, 25000)

    #section 80DD Disability Deduction 
    relation_80dd: str = '' #Spouse, Child, Parents, Sibling
    disability_percentage: str = '' #Between 40%-80% - 75k, More than 80% - 125k
    section_80dd: float = 0

    def total_deductions_80dd(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            if self.relation_80dd in ['Spouse', 'Child', 'Parents', 'Sibling']:
                if self.disability_percentage == 'Between 40%-80%':
                    return min(self.section_80dd, 75000)
                else:
                    return min(self.section_80dd, 125000)
            else:
                return 0

    #section 80DDB Specific Diseases
    relation_80ddb: str = '' #Spouse, Child, Parents, Sibling
    age_80ddb: int = 0
    section_80ddb: float = 0 #if age < 60 - 40k else 100K

    def total_deductions_80ddb(self, regime: str = 'new', age: int = 0):
        if regime == 'new':
            return 0
        else:
            if self.relation_80ddb in ['Spouse', 'Child', 'Parents', 'Sibling']:
                if age < 60:
                    return min(self.section_80ddb, 40000)
                else:
                    return min(self.section_80ddb, 100000)
            else:
                return 0

    #section 80EEB interest on loan for EV vehicle purchased between 01.04.2019 & 31.03.2023
    section_80eeb: float = 0    #Max 150K
    ev_purchase_date: date = date.today()

    def total_deductions_80eeb(self, regime: str = 'new', ev_purchase_date: date = date.today()):
        if regime == 'new':
            return 0
        else:
            if ev_purchase_date >= date(2019, 4, 1) and ev_purchase_date <= date(2023, 3, 31):
                return min(self.section_80eeb, 150000)
            else:
                return 0

    #section 80G Donations to charitable institutions
    section_80g_100_wo_ql: float = 0    #Donations entitled to 100% deduction without qualifying limit 
    section_80g_100_head: str = ''

    def total_deductions_80g_100_wo_ql(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        elif self.section_80g_100_head in section_80g_100_wo_ql_heads:
            return self.section_80g_100_wo_ql
        else:
            return 0

    section_80g_50_wo_ql: float = 0    #Donations entitled to 50% deduction without qualifying limit 
    section_80g_50_head: str = ''

    def total_deductions_80g_50_wo_ql(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        elif self.section_80g_50_head in section_80g_50_wo_ql_heads:
            return (self.section_80g_50_wo_ql * 0.5)
        else:
            return 0

    section_80g_100_ql: float = 0   #Donations entitled to 100% deduction with 
                                    #qualifying limit of 10% of adjusted gross total income  
    section_80g_100_ql_head: str = ''

    def total_deductions_80g_100_ql(self, regime: str = 'new', gross_total_income: float = 0):
        if regime == 'new':
            return 0
        elif self.section_80g_100_ql_head in section_80g_100_ql_heads:
            return min(self.section_80g_100_ql, (gross_total_income * 0.1))
        else:
            return 0

    section_80g_50_ql: float = 0    #Donations entitled to 50% deduction with qualifying limit of 10% of adjusted gross total income  
    section_80g_50_ql_head: str = ''

    def total_deductions_80g_50_ql(self, regime: str = 'new', gross_total_income: float = 0):
        if regime == 'new':
            return 0
        elif self.section_80g_50_ql_head in section_80g_50_ql_heads:
            return min(self.section_80g_50_ql, (gross_total_income * 0.1))
        else:
            return 0


    #section 80GGC Interest on savings account
    section_80ggc: float = 0        #Deduction on Political parties contribution (No Deductions for payments made in Cash)

    def total_deductions_80ggc(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            return self.section_80ggc

    #section 80U
    section_80u: float = 0
    disability_percentage_80u: str = '' #Between 40%-80% - 75k, More than 80% - 125k

    def total_deductions_80u(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            if self.disability_percentage_80u == 'Between 40%-80%':
                return min(self.section_80u, 75000)
            else:
                return min(self.section_80u, 125000)
            

    def total_deduction(self, regime: str = 'new', 
                        is_govt_employee: bool = False,         
                        gross_income: float = 0, age: int = 0,             
                        ev_purchase_date: date = date.today()):
        return (self.total_deductions_80c_80ccd_80ccd_1_1b(regime) +
                self.total_deductions_80ccd_2(regime, gross_income, is_govt_employee) +
                self.total_deductions_80d_self_family(regime, age) +
                self.total_deductions_80d_parent(regime, age) +
                self.total_deductions_80dd(regime) +
                self.total_deductions_80ddb(regime, age) +
                self.total_deductions_80eeb(regime, ev_purchase_date) +
                self.total_deductions_80g_100_wo_ql(regime) +
                self.total_deductions_80g_50_wo_ql(regime) +
                self.total_deductions_80g_100_ql(regime, gross_income) +
                self.total_deductions_80g_50_ql(regime, gross_income) +
                self.total_deductions_80ggc(regime) +
                self.total_deductions_80u(regime))

    def total(self, regime: str = 'new', is_govt_employee: bool = False, gross_income: float = 0, age: int = 0, ev_purchase_date: date = date.today()) -> float:
        """Alias for total_deduction to maintain compatibility."""
        return self.total_deduction(regime, is_govt_employee, gross_income, age, ev_purchase_date)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "regime": self.regime,
            "age": self.age,
            "section_80c_lic": self.section_80c_lic,
            "section_80c_epf": self.section_80c_epf,
            "section_80c_ssp": self.section_80c_ssp,
            "section_80c_nsc": self.section_80c_nsc,
            "section_80c_ulip": self.section_80c_ulip,
            "section_80c_tsmf": self.section_80c_tsmf,
            "section_80c_tffte2c": self.section_80c_tffte2c,
            "section_80c_paphl": self.section_80c_paphl,
            "section_80c_sdpphp": self.section_80c_sdpphp,
            "section_80c_tsfdsb": self.section_80c_tsfdsb,
            "section_80c_scss": self.section_80c_scss,
            "section_80c_others": self.section_80c_others,
            "section_80ccc_ppic": self.section_80ccc_ppic,
            "section_80ccd_1_nps": self.section_80ccd_1_nps,
            "section_80ccd_1b_additional": self.section_80ccd_1b_additional,
            "section_80ccd_2_enps": self.section_80ccd_2_enps,
            "section_80d_hisf": self.section_80d_hisf,
            "section_80d_phcs": self.section_80d_phcs,
            "section_80d_hi_parent": self.section_80d_hi_parent,
            "relation_80dd": self.relation_80dd,
            "disability_percentage": self.disability_percentage,
            "section_80dd": self.section_80dd,
            "relation_80ddb": self.relation_80ddb,
            "age_80ddb": self.age_80ddb,
            "section_80ddb": self.section_80ddb,
            "section_80eeb": self.section_80eeb,
            "ev_purchase_date": self.ev_purchase_date.isoformat() if hasattr(self, 'ev_purchase_date') and self.ev_purchase_date else None,
            "section_80g_100_wo_ql": self.section_80g_100_wo_ql,
            "section_80g_100_head": self.section_80g_100_head,
            "section_80g_50_wo_ql": self.section_80g_50_wo_ql,
            "section_80g_50_head": self.section_80g_50_head,
            "section_80g_100_ql": self.section_80g_100_ql,
            "section_80g_100_ql_head": self.section_80g_100_ql_head,
            "section_80g_50_ql": self.section_80g_50_ql,
            "section_80g_50_ql_head": self.section_80g_50_ql_head,
            "section_80ggc": self.section_80ggc,
            "section_80u": self.section_80u,
            "disability_percentage_80u": self.disability_percentage_80u
        }

@dataclass
class Taxation:
    emp_id: str
    emp_age: int
    salary: SalaryComponents
    other_sources: IncomeFromOtherSources
    capital_gains: CapitalGains
    deductions: DeductionComponents
    regime: str
    total_tax: float
    tax_breakup: dict
    tax_year: str
    filing_status: str
    tax_payable: float
    tax_paid: float
    tax_due: float
    tax_refundable: float
    tax_pending: float
    is_govt_employee: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Taxation':
        """Create a Taxation object from a dictionary"""
        # Extract nested objects
        salary_data = data.get('salary', {})
        other_sources_data = data.get('other_sources', {})
        capital_gains_data = data.get('capital_gains', {})
        deductions_data = data.get('deductions', {})
        
        # Handle perquisites in salary data
        perquisites = None
        if 'perquisites' in salary_data and salary_data['perquisites']:
            perquisites_data = salary_data['perquisites']
            perquisites = Perquisites(
                # Accommodation perquisites
                accommodation_provided=perquisites_data.get('accommodation_provided', 'Employer-Owned'),
                accommodation_govt_lic_fees=perquisites_data.get('accommodation_govt_lic_fees', 0),
                accommodation_city_population=perquisites_data.get('accommodation_city_population', 'Exceeding 40 lakhs in 2011 Census'),
                accommodation_rent=perquisites_data.get('accommodation_rent', 0),
                is_furniture_owned=perquisites_data.get('is_furniture_owned', False),
                furniture_actual_cost=perquisites_data.get('furniture_actual_cost', 0),
                furniture_cost_to_employer=perquisites_data.get('furniture_cost_to_employer', 0),
                furniture_cost_paid_by_employee=perquisites_data.get('furniture_cost_paid_by_employee', 0),
                
                # Car perquisites
                is_car_rating_higher=perquisites_data.get('is_car_rating_higher', False),
                is_car_employer_owned=perquisites_data.get('is_car_employer_owned', False),
                is_expenses_reimbursed=perquisites_data.get('is_expenses_reimbursed', False),
                is_driver_provided=perquisites_data.get('is_driver_provided', False),
                car_use=perquisites_data.get('car_use', 'Personal'),
                car_cost_to_employer=perquisites_data.get('car_cost_to_employer', 0),
                month_counts=perquisites_data.get('month_counts', 0),
                other_vehicle_cost_to_employer=perquisites_data.get('other_vehicle_cost_to_employer', 0),
                other_vehicle_month_counts=perquisites_data.get('other_vehicle_month_counts', 0),
                
                # Medical Reimbursement
                is_treated_in_India=perquisites_data.get('is_treated_in_India', False),
                medical_reimbursement_by_employer=perquisites_data.get('medical_reimbursement_by_employer', 0),
                travelling_allowance_for_treatment=perquisites_data.get('travelling_allowance_for_treatment', 0),
                rbi_limit_for_illness=perquisites_data.get('rbi_limit_for_illness', 0),
                
                
                # Leave Travel Allowance
                lta_amount_claimed=perquisites_data.get('lta_amount_claimed', 0),
                lta_claimed_count=perquisites_data.get('lta_claimed_count', 0),
                travel_through=perquisites_data.get('travel_through', 'Air'),
                public_transport_travel_amount_for_same_distance=perquisites_data.get('public_transport_travel_amount_for_same_distance', 0),
                
                # Free Education
                employer_maintained_1st_child=perquisites_data.get('employer_maintained_1st_child', False),
                monthly_count_1st_child=perquisites_data.get('monthly_count_1st_child', 0),
                employer_monthly_expenses_1st_child=perquisites_data.get('employer_monthly_expenses_1st_child', 0),
                employer_maintained_2nd_child=perquisites_data.get('employer_maintained_2nd_child', False),
                monthly_count_2nd_child=perquisites_data.get('monthly_count_2nd_child', 0),
                employer_monthly_expenses_2nd_child=perquisites_data.get('employer_monthly_expenses_2nd_child', 0),

                # Gas, Electricity, Water
                gas_amount_paid_by_employer=perquisites_data.get('gas_amount_paid_by_employer', 0),
                electricity_amount_paid_by_employer=perquisites_data.get('electricity_amount_paid_by_employer', 0),
                water_amount_paid_by_employer=perquisites_data.get('water_amount_paid_by_employer', 0),
                gas_amount_paid_by_employee=perquisites_data.get('gas_amount_paid_by_employee', 0),
                electricity_amount_paid_by_employee=perquisites_data.get('electricity_amount_paid_by_employee', 0),
                water_amount_paid_by_employee=perquisites_data.get('water_amount_paid_by_employee', 0),
                is_gas_manufactured_by_employer=perquisites_data.get('is_gas_manufactured_by_employer', False),
                is_electricity_manufactured_by_employer=perquisites_data.get('is_electricity_manufactured_by_employer', False),
                is_water_manufactured_by_employer=perquisites_data.get('is_water_manufactured_by_employer', False),

                # Domestic help
                domestic_help_amount_paid_by_employer=perquisites_data.get('domestic_help_amount_paid_by_employer', 0),
                domestic_help_amount_paid_by_employee=perquisites_data.get('domestic_help_amount_paid_by_employee', 0),

                # Interest-free/concessional loan
                loan_type=perquisites_data.get('loan_type', 'Personal'),
                loan_amount=perquisites_data.get('loan_amount', 0),
                loan_interest_rate_company=perquisites_data.get('loan_interest_rate_company', 0),
                loan_interest_rate_sbi=perquisites_data.get('loan_interest_rate_sbi', 0),
                loan_month_count=perquisites_data.get('loan_month_count', 0),
                loan_start_date=perquisites_data.get('loan_start_date', ''),
                loan_end_date=perquisites_data.get('loan_end_date', ''),

                # Lunch/Refreshment
                lunch_amount_paid_by_employer=perquisites_data.get('lunch_amount_paid_by_employer', 0),
                lunch_amount_paid_by_employee=perquisites_data.get('lunch_amount_paid_by_employee', 0),

                # ESOP
                number_of_esop_shares_awarded=perquisites_data.get('number_of_esop_shares_awarded', 0),
                esop_exercise_price_per_share=perquisites_data.get('esop_exercise_price_per_share', 0),
                esop_allotment_price_per_share=perquisites_data.get('esop_allotment_price_per_share', 0),
                grant_date=cls._parse_date(perquisites_data.get('grant_date')),
                vesting_date=cls._parse_date(perquisites_data.get('vesting_date')),
                exercise_date=cls._parse_date(perquisites_data.get('exercise_date')),
                vesting_period=perquisites_data.get('vesting_period', 0),
                exercise_period=perquisites_data.get('exercise_period', 0),
                exercise_price_per_share=perquisites_data.get('exercise_price_per_share', 0),

                # Movable assets
                movable_asset_type=perquisites_data.get('movable_asset_type', 'Electronics'),
                movable_asset_value_to_employer=perquisites_data.get('movable_asset_value_to_employer', 0),
                movable_asset_value_to_employee=perquisites_data.get('movable_asset_value_to_employee', 0),
                number_of_completed_years_of_use=perquisites_data.get('number_of_completed_years_of_use', 0),

                # Monetary benefits
                monetary_amount_paid_by_employer=perquisites_data.get('monetary_amount_paid_by_employer', 0),
                expenditure_for_offical_purpose=perquisites_data.get('expenditure_for_offical_purpose', 0),
                monetary_benefits_amount_paid_by_employee=perquisites_data.get('monetary_benefits_amount_paid_by_employee', 0),

                # Gift Vouchers
                gift_vouchers_amount_paid_by_employer=perquisites_data.get('gift_vouchers_amount_paid_by_employer', 0),

                # Club Expenses
                club_expenses_amount_paid_by_employer=perquisites_data.get('club_expenses_amount_paid_by_employer', 0),
                club_expenses_amount_paid_by_employee=perquisites_data.get('club_expenses_amount_paid_by_employee', 0),
                club_expenses_amount_paid_for_offical_purpose=perquisites_data.get('club_expenses_amount_paid_for_offical_purpose', 0)
            )
        
        # Create component objects
        salary = SalaryComponents(
            basic=salary_data.get('basic', 0),
            dearness_allowance=salary_data.get('dearness_allowance', 0),
            hra=salary_data.get('hra', 0),
            hra_city=salary_data.get('hra_city', 'Others'),
            hra_percentage=salary_data.get('hra_percentage', 0),
            special_allowance=salary_data.get('special_allowance', 0),
            bonus=salary_data.get('bonus', 0),
            commission=salary_data.get('commission', 0),
            city_compensatory_allowance=salary_data.get('city_compensatory_allowance', 0),
            rural_allowance=salary_data.get('rural_allowance', 0),
            proctorship_allowance=salary_data.get('proctorship_allowance', 0),
            wardenship_allowance=salary_data.get('wardenship_allowance', 0),
            project_allowance=salary_data.get('project_allowance', 0),
            deputation_allowance=salary_data.get('deputation_allowance', 0),
            overtime_allowance=salary_data.get('overtime_allowance', 0),
            any_other_allowance=salary_data.get('any_other_allowance', 0),
            any_other_allowance_exemption=salary_data.get('any_other_allowance_exemption', 0),
            interim_relief=salary_data.get('interim_relief', 0),
            tiffin_allowance=salary_data.get('tiffin_allowance', 0),
            fixed_medical_allowance=salary_data.get('fixed_medical_allowance', 0),
            servant_allowance=salary_data.get('servant_allowance', 0),
            govt_employees_outside_india_allowance=salary_data.get('govt_employees_outside_india_allowance', 0),
            supreme_high_court_judges_allowance=salary_data.get('supreme_high_court_judges_allowance', 0),
            judge_compensatory_allowance=salary_data.get('judge_compensatory_allowance', 0),
            section_10_14_special_allowances=salary_data.get('section_10_14_special_allowances', 0),
            travel_on_tour_allowance=salary_data.get('travel_on_tour_allowance', 0),
            tour_daily_charge_allowance=salary_data.get('tour_daily_charge_allowance', 0),
            conveyance_in_performace_of_duties=salary_data.get('conveyance_in_performace_of_duties', 0),
            helper_in_performace_of_duties=salary_data.get('helper_in_performace_of_duties', 0),    
            academic_research=salary_data.get('academic_research', 0),
            uniform_allowance=salary_data.get('uniform_allowance', 0),
            perquisites=perquisites
        )
        
        # Setup regime and age info
        regime = data.get('regime', 'old')
        emp_age = data.get('emp_age', 0)
        
        other_sources = IncomeFromOtherSources(
            regime=regime,
            age=emp_age,
            interest_savings=other_sources_data.get('interest_savings', 0),
            interest_fd=other_sources_data.get('interest_fd', 0),
            interest_rd=other_sources_data.get('interest_rd', 0),
            dividend_income=other_sources_data.get('dividend_income', 0),
            gifts=other_sources_data.get('gifts', 0),
            other_interest=other_sources_data.get('other_interest', 0),
            other_income=other_sources_data.get('other_income', 0)
        )
        
        capital_gains = CapitalGains(
            stcg_111a=capital_gains_data.get('stcg_111a', 0),
            stcg_any_other_asset=capital_gains_data.get('stcg_any_other_asset', 0),
            stcg_debt_mutual_fund=capital_gains_data.get('stcg_debt_mutual_fund', 0),
            ltcg_112a=capital_gains_data.get('ltcg_112a', 0),
            ltcg_any_other_asset=capital_gains_data.get('ltcg_any_other_asset', 0),
            ltcg_debt_mutual_fund=capital_gains_data.get('ltcg_debt_mutual_fund', 0)
        )
        
        # Parse date string for EV purchase date
        ev_purchase_date = None
        ev_purchase_date_str = deductions_data.get('ev_purchase_date')
        if ev_purchase_date_str:
            try:
                ev_purchase_date = datetime.datetime.strptime(ev_purchase_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                ev_purchase_date = None
        
        deductions = DeductionComponents(
            regime=regime,
            age=emp_age,
            section_80c_lic=deductions_data.get('section_80c_lic', 0),
            section_80c_epf=deductions_data.get('section_80c_epf', 0),
            section_80c_ssp=deductions_data.get('section_80c_ssp', 0),
            section_80c_nsc=deductions_data.get('section_80c_nsc', 0),
            section_80c_ulip=deductions_data.get('section_80c_ulip', 0),
            section_80c_tsmf=deductions_data.get('section_80c_tsmf', 0),
            section_80c_tffte2c=deductions_data.get('section_80c_tffte2c', 0),
            section_80c_paphl=deductions_data.get('section_80c_paphl', 0),
            section_80c_sdpphp=deductions_data.get('section_80c_sdpphp', 0),
            section_80c_tsfdsb=deductions_data.get('section_80c_tsfdsb', 0),
            section_80c_scss=deductions_data.get('section_80c_scss', 0),
            section_80c_others=deductions_data.get('section_80c_others', 0),
            section_80ccc_ppic=deductions_data.get('section_80ccc_ppic', 0),
            section_80ccd_1_nps=deductions_data.get('section_80ccd_1_nps', 0),
            section_80ccd_1b_additional=deductions_data.get('section_80ccd_1b_additional', 0),
            section_80ccd_2_enps=deductions_data.get('section_80ccd_2_enps', 0),
            section_80d_hisf=deductions_data.get('section_80d_hisf', 0),
            section_80d_phcs=deductions_data.get('section_80d_phcs', 0),
            section_80d_hi_parent=deductions_data.get('section_80d_hi_parent', 0),
            relation_80dd=deductions_data.get('relation_80dd', ''),
            disability_percentage=deductions_data.get('disability_percentage', ''),
            section_80dd=deductions_data.get('section_80dd', 0),
            relation_80ddb=deductions_data.get('relation_80ddb', ''),
            age_80ddb=deductions_data.get('age_80ddb', 0),
            section_80ddb=deductions_data.get('section_80ddb', 0),
            section_80eeb=deductions_data.get('section_80eeb', 0),
            ev_purchase_date=ev_purchase_date or date.today(),
            section_80g_100_wo_ql=deductions_data.get('section_80g_100_wo_ql', 0),
            section_80g_100_head=deductions_data.get('section_80g_100_head', ''),
            section_80g_50_wo_ql=deductions_data.get('section_80g_50_wo_ql', 0),
            section_80g_50_head=deductions_data.get('section_80g_50_head', ''),
            section_80g_100_ql=deductions_data.get('section_80g_100_ql', 0),
            section_80g_100_ql_head=deductions_data.get('section_80g_100_ql_head', ''),
            section_80g_50_ql=deductions_data.get('section_80g_50_ql', 0),
            section_80g_50_ql_head=deductions_data.get('section_80g_50_ql_head', ''),
            section_80ggc=deductions_data.get('section_80ggc', 0),
            section_80u=deductions_data.get('section_80u', 0),
            disability_percentage_80u=deductions_data.get('disability_percentage_80u', '')
        )
        
        # Create and return Taxation object
        return cls(
            emp_id=data.get('emp_id', ''),
            emp_age=emp_age,
            regime=regime,
            salary=salary,
            other_sources=other_sources,
            capital_gains=capital_gains,
            deductions=deductions,
            tax_year=data.get('tax_year', ''),
            filing_status=data.get('filing_status', 'draft'),
            total_tax=data.get('total_tax', 0),
            tax_breakup=data.get('tax_breakup', {}),
            tax_payable=data.get('tax_payable', 0),
            tax_paid=data.get('tax_paid', 0),
            tax_due=data.get('tax_due', 0),
            tax_refundable=data.get('tax_refundable', 0),
            tax_pending=data.get('tax_pending', 0),
            is_govt_employee=data.get('is_govt_employee', False)
        )
    
    @staticmethod
    def _parse_date(date_str):
        """Helper method to parse date strings safely"""
        if not date_str:
            return None
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Try ISO format
            try:
                return datetime.datetime.fromisoformat(date_str).date()
            except (ValueError, TypeError):
                return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert a Taxation object to a dictionary"""
        result = {
            'emp_id': self.emp_id,
            'emp_age': self.emp_age,
            'regime': self.regime,
            'total_tax': self.total_tax,
            'tax_breakup': self.tax_breakup,
            'tax_year': self.tax_year,
            'filing_status': self.filing_status,
            'tax_payable': self.tax_payable,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'tax_pending': self.tax_pending,
            'is_govt_employee': self.is_govt_employee
        }
        
        # Handle salary components
        if isinstance(self.salary, dict):
            result['salary'] = self.salary
        else:
            salary_dict = {}
            for attr in dir(self.salary):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total':
                    value = getattr(self.salary, attr)
                    # Handle perquisites specially
                    if attr == 'perquisites' and value is not None:
                        if isinstance(value, dict):
                            salary_dict['perquisites'] = value
                        else:
                            perq_dict = {}
                            for p_attr in dir(value):
                                if not p_attr.startswith('_') and p_attr != 'to_dict' and p_attr != 'total':
                                    p_value = getattr(value, p_attr)
                                    # Handle date objects
                                    if isinstance(p_value, date):
                                        perq_dict[p_attr] = p_value.isoformat()
                                    else:
                                        perq_dict[p_attr] = p_value
                            salary_dict['perquisites'] = perq_dict
                    else:
                        salary_dict[attr] = value
            result['salary'] = salary_dict
        
        # Handle other_sources components
        if isinstance(self.other_sources, dict):
            result['other_sources'] = self.other_sources
        else:
            other_sources_dict = {}
            for attr in dir(self.other_sources):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_taxable_income_per_slab' and attr != 'get_section_80tt':
                    other_sources_dict[attr] = getattr(self.other_sources, attr)
            result['other_sources'] = other_sources_dict
        
        # Handle capital_gains components
        if isinstance(self.capital_gains, dict):
            result['capital_gains'] = self.capital_gains
        else:
            capital_gains_dict = {}
            for attr in dir(self.capital_gains):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_stcg_special_rate' and attr != 'total_stcg_slab_rate' and attr != 'total_ltcg_special_rate':
                    capital_gains_dict[attr] = getattr(self.capital_gains, attr)
            result['capital_gains'] = capital_gains_dict
        
        # Handle deductions components
        if isinstance(self.deductions, dict):
            result['deductions'] = self.deductions
        else:
            deductions_dict = {}
            for attr in dir(self.deductions):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_deduction' and not attr.startswith('total_deductions_'):
                    value = getattr(self.deductions, attr)
                    # Handle date objects
                    if isinstance(value, date):
                        deductions_dict[attr] = value.isoformat()
                    else:
                        deductions_dict[attr] = value
            result['deductions'] = deductions_dict
        
        return result
        
    def get_taxable_income(self) -> float:
        """Calculate the total taxable income"""
        gross_income = self.salary.total() + self.other_sources.total() + self.capital_gains.total()
        deductions_total = 0 if self.regime == 'new' else self.deductions.total()
        return max(0, gross_income - deductions_total)
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """Get a summary of the taxation"""
        return {
            'emp_id': self.emp_id,
            'emp_age': self.emp_age,
            'tax_year': self.tax_year,
            'regime': self.regime,
            'gross_income': self.salary.total() + self.other_sources.total() + self.capital_gains.total(),
            'deductions': self.deductions.total() if self.regime == 'old' else 0,
            'taxable_income': self.get_taxable_income(),
            'total_tax': self.total_tax,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'filing_status': self.filing_status
        }
        