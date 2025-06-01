"""
Income source models for taxation calculations.

Contains classes for different types of income sources:
- Income from other sources (interest, dividends, etc.)
- Income from house property
- Capital gains (short term and long term)
- Business and professional income
"""

from dataclasses import dataclass
import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class IncomeFromOtherSources:
    """
    Represents income from other sources as per Indian Income Tax Act.
    Includes interest income, dividends, gifts and other sources.
    """
    regime: str = 'new'
    age: int = 0
    interest_savings: float = 0     #Interest on Savings Account
    interest_fd: float = 0          #Interest on Fixed Deposit
    interest_rd: float = 0          #Interest on Recurring Deposit
    dividend_income: float = 0      #Dividend Income
    gifts: float = 0                #Gifts received
    other_interest: float = 0       #Interest on other sources
    business_professional_income: float = 0 #Business or Professional Income
    other_income: float = 0        #Other Income (e.g. Rent, Interest on Bonds, etc.)

    @classmethod
    def get_section_80tt(cls, age: int, regime: str = 'new'):
        """Determine the applicable section for interest income based on age and regime."""
        if regime == 'old':
            if age >= 60:
                return "80TTB"
            else:
                return "80TTA"
        else:
            return "Not Applicable"

    def total_taxable_income_per_slab(self, regime: str = 'new', age: int = 0):
        """
        Calculate taxable income per slab with proper Section 80TTA/80TTB treatment.
        
        FIXES APPLIED:
        1. Section 80TTA (age < 60): Only savings account interest eligible, up to Rs. 10,000
        2. Section 80TTB (age >= 60): All bank interest eligible, up to Rs. 50,000
        3. These deductions only apply in the old regime
        4. Proper segregation of interest types
        
        Args:
            regime: Tax regime ('old' or 'new')
            age: Age of taxpayer for 80TTA/80TTB eligibility
            
        Returns:
            Total taxable income from other sources
        """
        logger.info(f"total_taxable_income_per_slab - Calculating for regime: {regime}, age: {age}")
        
        # Items always fully taxable
        directly_taxable = sum([
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.business_professional_income,
            self.other_income
        ])
        logger.info(f"total_taxable_income_per_slab - Directly taxable income: {directly_taxable}")

        # Interest income treatment based on regime and age
        total_interest = self.interest_savings + self.interest_fd + self.interest_rd
        logger.info(f"total_taxable_income_per_slab - Total interest income: Savings: {self.interest_savings}, FD: {self.interest_fd}, RD: {self.interest_rd}, Total: {total_interest}")
        
        if regime == 'old':
            if age >= 60:
                # Section 80TTB: All bank interest (savings, FD, RD) eligible for exemption up to Rs. 50,000
                exempt_interest = min(50000, total_interest)
                taxable_interest = max(0, total_interest - exempt_interest)
                logger.info(f"total_taxable_income_per_slab - Senior citizen (80TTB): Total interest: {total_interest}, Exempt: {exempt_interest}, Taxable: {taxable_interest}")
            else:
                # Section 80TTA: Only savings account interest eligible for exemption up to Rs. 10,000
                exempt_savings_interest = min(10000, self.interest_savings)
                taxable_interest = max(0, self.interest_savings - exempt_savings_interest) + self.interest_fd + self.interest_rd
                logger.info(f"total_taxable_income_per_slab - Below 60 (80TTA): Savings interest: {self.interest_savings}, Exempt savings: {exempt_savings_interest}, FD+RD: {self.interest_fd + self.interest_rd}, Total taxable interest: {taxable_interest}")
        else:
            # New regime: No exemptions for interest income
            taxable_interest = total_interest
            logger.info(f"total_taxable_income_per_slab - New regime: No interest exemptions, total taxable: {taxable_interest}")

        total_taxable = directly_taxable + taxable_interest
        logger.info(f"total_taxable_income_per_slab - Final taxable income: {total_taxable}")
        
        return total_taxable

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "regime": cls.regime,
            "age": cls.age,
            "interest_savings": cls.interest_savings,
            "interest_fd": cls.interest_fd,
            "interest_rd": cls.interest_rd,
            "dividend_income": cls.dividend_income,
            "gifts": cls.gifts,
            "other_interest": cls.other_interest,
            "business_professional_income": cls.business_professional_income,
            "other_income": cls.other_income
        }


@dataclass
class IncomeFromHouseProperty:
    """
    Represents income from house property as per Indian Income Tax Act.
    Includes rental income, property tax, interest on home loan, etc.
    """
    property_address: str = ''
    occupancy_status: str = ''  # Let-Out, Self-Occupied, Pre-Construction
    rent_income: float = 0
    property_tax: float = 0
    interest_on_home_loan: float = 0
    pre_construction_loan_interest: float = 0

    def __init__(self, property_address: str = '', occupancy_status: str = 'Self-Occupied', 
                 rent_income: float = 0, property_tax: float = 0, 
                 interest_on_home_loan: float = 0, pre_construction_loan_interest: float = 0):
        self.property_address = property_address
        self.occupancy_status = occupancy_status  # Self-Occupied, Let-Out, Deemed Let-Out
        self.rent_income = rent_income
        self.property_tax = property_tax
        self.interest_on_home_loan = interest_on_home_loan
        self.pre_construction_loan_interest = pre_construction_loan_interest
        
    def calculate_annual_value(self) -> float:
        """
        Calculate annual value of house property.
        For Let-Out property: Rent income - Unrealized rent - Municipal tax paid
        For Self-Occupied property: Annual value is zero
        """
        if self.occupancy_status == 'Let-Out':
            annual_value = self.rent_income - self.property_tax
            logger.info(f"Calculating annual value: Rent {self.rent_income} - Property Tax {self.property_tax} = {annual_value}")
            return max(0, annual_value)
        else:
            return 0

    def total_taxable_income_per_slab(self, regime: str = 'old') -> float:
        """
        Calculate taxable income from house property.
        
        For Self-Occupied Property:
        - Annual Value: Nil
        - Less: Interest on home loan (up to Rs. 2 lakh limit)
        
        For Let-Out Property:
        - Annual Value: Rent received or municipal value, whichever is higher
        - Less: Municipal taxes paid (if any)
        - Less: 30% standard deduction on net annual value
        - Less: Interest on home loan (no upper limit)
        
        Args:
            regime: Tax regime ('old' or 'new')
            
        Returns:
            Net taxable income from house property (can be negative)
        """
        logger.info(f"total_taxable_income_per_slab - House property calculation for occupancy: {self.occupancy_status}, regime: {regime}")
        
        if self.occupancy_status == 'Self-Occupied':
            # For self-occupied property
            annual_value = 0
            
            # Deduct interest on home loan (maximum Rs. 2,00,000 for self-occupied)
            interest_deduction = min(200000, self.interest_on_home_loan)
            
            # Pre-construction interest can be claimed in 5 equal installments
            pre_construction_deduction = self.pre_construction_loan_interest / 5
            
            net_income = annual_value - interest_deduction - pre_construction_deduction
            
            logger.info(f"total_taxable_income_per_slab - Self-occupied: Annual value: {annual_value}, "
                       f"Interest deduction (max 2L): {interest_deduction}, "
                       f"Pre-construction interest: {pre_construction_deduction}, "
                       f"Net income: {net_income}")
            
            return net_income
            
        else:  # Let-Out or Deemed Let-Out
            # Annual value is the rent received
            annual_value = self.rent_income
            
            # Less: Municipal taxes paid
            net_annual_value = annual_value - self.property_tax
            
            # Less: 30% standard deduction on net annual value
            standard_deduction = net_annual_value * 0.30
            
            # Less: Interest on home loan (no upper limit for let-out property)
            interest_deduction = self.interest_on_home_loan
            
            # Pre-construction interest in 5 equal installments
            pre_construction_deduction = self.pre_construction_loan_interest / 5
            
            net_income = net_annual_value - standard_deduction - interest_deduction - pre_construction_deduction
            
            logger.info(f"total_taxable_income_per_slab - Let-out: Annual value: {annual_value}, "
                       f"Property tax: {self.property_tax}, Net annual value: {net_annual_value}, "
                       f"Standard deduction (30%): {standard_deduction}, "
                       f"Interest deduction: {interest_deduction}, "
                       f"Pre-construction interest: {pre_construction_deduction}, "
                       f"Net income: {net_income}")
            
            return net_income
    
    def to_dict(self) -> dict:
        return {
            'property_address': self.property_address,
            'occupancy_status': self.occupancy_status,
            'rent_income': self.rent_income,
            'property_tax': self.property_tax,
            'interest_on_home_loan': self.interest_on_home_loan,
            'pre_construction_loan_interest': self.pre_construction_loan_interest
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            property_address=data.get('property_address', ''),
            occupancy_status=data.get('occupancy_status', 'Self-Occupied'),
            rent_income=data.get('rent_income', 0),
            property_tax=data.get('property_tax', 0),
            interest_on_home_loan=data.get('interest_on_home_loan', 0),
            pre_construction_loan_interest=data.get('pre_construction_loan_interest', 0)
        )


@dataclass
class CapitalGains:
    """
    Represents capital gains income as per Indian Income Tax Act.
    Includes both short-term and long-term capital gains from various assets.
    """
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

    def total_stcg_special_rate(self) -> float:
        """
        Total short-term capital gains charged at special rates.
        STCG 111A (equity shares/MF with STT): 20% rate (Budget 2024)
        """
        logger.info(f"STCG at special rate (under section 111A): {self.stcg_111a}")
        return self.stcg_111a
    
    def tax_on_stcg_special_rate(self) -> float:
        """
        Tax on short-term capital gains charged at special rates.
        UPDATED: 20% rate as per Budget 2024 (previously 15%)
        """
        tax = self.stcg_111a * 0.20  # Updated rate
        logger.info(f"Tax on STCG at special rate (20% - Budget 2024): {tax}")
        return tax
    
    def total_stcg_slab_rate(self) -> float:
        """Total short-term capital gains taxed at slab rates."""
        total = self.stcg_any_other_asset + self.stcg_debt_mutual_fund
        logger.info(f"STCG at slab rates: {total}")
        return total
    
    def total_ltcg_special_rate(self) -> float:
        """
        Total long-term capital gains charged at special rates.
        UPDATED: 12.5% rate and Rs. 1.25 lakh exemption as per Budget 2024
        """
        # LTCG 112A: Exemption increased from Rs. 1 lakh to Rs. 1.25 lakh
        ltcg_112a_taxable = max(0, self.ltcg_112a - 125000)  # Updated exemption
        
        # Other LTCG: No exemption, direct 12.5% rate
        ltcg_other = self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
        
        total = ltcg_112a_taxable + ltcg_other
        logger.info(f"LTCG at special rates: 112A taxable (after 1.25L exemption): {ltcg_112a_taxable}, Other LTCG: {ltcg_other}, Total: {total}")
        return total
    
    def tax_on_ltcg_special_rate(self) -> float:
        """
        Tax on long-term capital gains charged at special rates.
        UPDATED: 12.5% rate as per Budget 2024 (previously 10% for 112A and 20% for others)
        """
        # LTCG 112A with exemption
        ltcg_112a_taxable = max(0, self.ltcg_112a - 125000)  # Updated exemption
        ltcg_112a_tax = ltcg_112a_taxable * 0.125  # Updated rate
        
        # Other LTCG
        ltcg_other = self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
        ltcg_other_tax = ltcg_other * 0.125  # Updated rate
        
        total_tax = ltcg_112a_tax + ltcg_other_tax
        logger.info(f"Tax on LTCG: 112A tax (12.5%): {ltcg_112a_tax}, Other LTCG tax (12.5%): {ltcg_other_tax}, Total: {total_tax}")
        return total_tax
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "stcg_111a": cls.stcg_111a,
            "stcg_any_other_asset": cls.stcg_any_other_asset,
            "stcg_debt_mutual_fund": cls.stcg_debt_mutual_fund,
            "ltcg_112a": cls.ltcg_112a,
            "ltcg_any_other_asset": cls.ltcg_any_other_asset,
            "ltcg_debt_mutual_fund": cls.ltcg_debt_mutual_fund
        }
    
@dataclass
class LeaveEncashment:
    """
    Represents leave encashment income as per Indian Income Tax Act.
    Includes leave encashment income from various sources.
    """
    leave_encashment_income_received: float = 0
    leave_encashed: float = 0
    is_deceased: bool = False
    during_employment: bool = True


    def total_taxable_income_per_slab(self, regime: str = 'old', is_govt_employee: bool = False, service_years: int = 0, average_monthly_salary: float = 0) -> float:
        """
        Calculate taxable leave encashment income.
        
        Exemption is least of:
        1. Actual leave encashment received
        2. 10 months' average salary (assumed as 100000 per month)
        3. Maximum exemption limit (₹25,00,000)
        4. Average salary × unexpired leave (30 days per year calculated for service years)
        """
        if regime == 'new':
            # In new regime, leave encashment is fully taxable
            logger.info(f"New regime - Leave encashment fully taxable: {self.leave_encashment_income_received}")
            return self.leave_encashment_income_received
            
        logger.info(f"Calculating leave encashment for regime: {regime}")
        logger.info(f"During employment: {self.during_employment}")
        logger.info(f"Leave encashment Amount: {self.leave_encashment_income_received}")
        logger.info(f"Service years: {service_years}")
        logger.info(f"Leave Encashed: {self.leave_encashed}")
        logger.info(f"Is deceased: {self.is_deceased}")
        logger.info(f"Is govt employee: {is_govt_employee}")
        logger.info(f"Average monthly salary: {average_monthly_salary}")

        if self.during_employment:
            return self.leave_encashment_income_received
        
        if is_govt_employee or self.is_deceased:
            return 0
        
        # Calculate all possible exemption amounts
        actual_received = self.leave_encashment_income_received
        ten_months_salary = average_monthly_salary * 10
        statutory_limit = 2500000
        
        # Calculate unexpired leave based on service years
        # Assume entitlement of 30 days per year and calculate unused leave value
        salary_per_day = average_monthly_salary / 30
        max_leave_encashed_allowed = service_years * 30
        if self.leave_encashed <= max_leave_encashed_allowed:
            # If leave balance is provided, use it directly
            unexpired_leave_value = self.leave_encashed * salary_per_day
        else:
            # Otherwise calculate based on service years (assuming 30 days per year)
            unexpired_leave_value = max_leave_encashed_allowed * salary_per_day
        
        # Exemption is the least of the four amounts
        exemption = min(statutory_limit, unexpired_leave_value, actual_received, ten_months_salary)
        
        # Taxable amount is received amount minus exemption
        taxable_amount = max(0, self.leave_encashment_income_received - exemption)
        
        logger.info(f"Leave encashment exemption calculation:")
        logger.info(f"Actual received: {actual_received}")
        logger.info(f"10 months salary: {ten_months_salary}")
        logger.info(f"Statutory limit: {statutory_limit}")
        logger.info(f"Unexpired leave value: {unexpired_leave_value}")
        logger.info(f"Exemption amount: {exemption}")
        logger.info(f"Taxable amount: {taxable_amount}")
        
        return taxable_amount

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "leave_encashment_income_received": cls.leave_encashment_income_received,
            "leave_encashed": cls.leave_encashed,
            "is_deceased": cls.is_deceased,
            "during_employment": cls.during_employment,
        }
    
@dataclass
class VoluntaryRetirement:
    """
    Represents voluntary retirement income as per Indian Income Tax Act.
    Includes voluntary retirement income from various sources.
    """
    is_vrs_requested: bool = False
    voluntary_retirement_amount: float = 0

    def compute_vrs_value(self, age: int, service_years: int, last_drawn_monthly_salary: float) -> float:
        """
        Compute the value of voluntary retirement scheme.
        """
        logger.info(f"Computing VRS value for age: {age}, service years: {service_years}, last drawn monthly salary: {last_drawn_monthly_salary}")
        if age < 40 or service_years < 10:
            return 0
        
        single_day_salary = last_drawn_monthly_salary / 30
        salary_45_days = single_day_salary * 45
        logger.info(f"Salary for 45 days: {salary_45_days}")

        months_remaining_for_retirement = (60 - age) * 12
        logger.info(f"Months remaining for retirement: {months_remaining_for_retirement}")
        salary_for_months_remaining = last_drawn_monthly_salary * months_remaining_for_retirement
        logger.info(f"Salary for months remaining: {salary_for_months_remaining}")
        salary_against_service_span = salary_45_days * service_years
        logger.info(f"Salary against service span: {salary_against_service_span}")
        vrs_value = min(salary_for_months_remaining, salary_against_service_span)
        logger.info(f"VRS value: {vrs_value}")
        return vrs_value

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "is_vrs_requested": cls.is_vrs_requested,
            "voluntary_retirement_amount": cls.voluntary_retirement_amount
        }

    def total_taxable_income_per_slab(self, regime: str = 'old', age: int = 0, service_years: int = 0, last_drawn_monthly_salary: float = 0) -> float:
        """
        Calculate taxable voluntary retirement income.
        """
        if regime == 'new':
            return self.voluntary_retirement_amount
        
        vrs_value = self.compute_vrs_value(age, service_years, last_drawn_monthly_salary)
        vrs_taxable_amount = max(0, self.voluntary_retirement_amount - 500000)
        return vrs_taxable_amount
    

@dataclass
class Pension:
    """
    Represents pension income as per Indian Income Tax Act.
    Includes both computed (regular monthly pension) and uncomputed pension (commutation, gratuity).
    Different exemption rules apply for government vs non-government employees.
    """
    # Regular monthly pension (fully taxable)
    total_pension_income: float = 0
    computed_pension_percentage: float = 0
    uncomputed_pension_frequency: str = 'monthly' # monthly, quarterly, annually
    uncomputed_pension_amount: float = 0
    
    def total_taxable_income_per_slab_computed(self, regime: str = 'old', is_govt_employee: bool = False, is_gratuity_received: bool = False) -> float:
        """
        Calculate total taxable pension income.
        
        For regular monthly pension: Fully taxable in both regimes
        For commuted pension and gratuity: Exemption depends on employee type
        New regime: Some exemptions that are available in old regime may not apply
        """
        computed_taxable_pension = 0
        computed_pension_amount = self.total_pension_income * self.computed_pension_percentage
        if not is_govt_employee:
            exemption_fraction = 1/3 if is_gratuity_received else 1/2
            exemption_limit = self.total_pension_income * exemption_fraction
            computed_taxable_pension =  min(computed_pension_amount, exemption_limit)
            logger.info(f"Computed pension amount: {computed_pension_amount}")
            logger.info(f"Exemption limit: {exemption_limit}")
            logger.info(f"Computed taxable pension: {computed_taxable_pension}")
        
        return computed_taxable_pension
    
    def total_taxable_income_per_slab_uncomputed(self, regime: str = 'old') -> float:
        """
        Calculate total taxable pension income.
        """
        uncomputed_taxable_pension = 0
        if self.uncomputed_pension_frequency == 'monthly':
            uncomputed_taxable_pension = self.uncomputed_pension_amount*12
        elif self.uncomputed_pension_frequency == 'quarterly':
            uncomputed_taxable_pension = self.uncomputed_pension_amount*4
        elif self.uncomputed_pension_frequency == 'annually':
            uncomputed_taxable_pension = self.uncomputed_pension_amount
        return uncomputed_taxable_pension

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "total_pension_income": cls.total_pension_income,
            "computed_pension_percentage": cls.computed_pension_percentage,
            "uncomputed_pension_frequency": cls.uncomputed_pension_frequency,
            "uncomputed_pension_amount": cls.uncomputed_pension_amount
        }

@dataclass
class Gratuity:
    """
    Represents gratuity income as per Indian Income Tax Act.
    Includes gratuity income from various sources.
    """
    gratuity_income: float = 0
    #last_drawn_monthly_salary: float = 100000   #Basic + DA
    
    def compute_service_years(self, date_of_joining: datetime.datetime, date_of_leaving: datetime.datetime) -> float:
        """
        Compute the number of years of service based on date of joining and date of leaving.
        """
        if not date_of_joining or not date_of_leaving:
            logger.warning("Date of joining or date of leaving is missing, cannot compute service years")
            return 0
        
        # Calculate the difference between date of joining and date of leaving
        service_days = (date_of_leaving - date_of_joining).days
        service_years = service_days / 365.25  # Account for leap years
        
        logger.info(f"Computed service period: Date of joining={date_of_joining}, Date of leaving={date_of_leaving}, days={service_days}, years={service_years:.2f}")
        return service_years
    
    def total_taxable_income_per_slab(self, regime: str = 'old', date_of_joining: datetime.datetime = None, date_of_leaving: datetime.datetime = None, last_drawn_monthly_salary: float = 0, is_govt_employee: bool = False) -> float:
        """
        Calculate taxable gratuity income based on the tax regime.
        
        For government employees: Gratuity is fully exempt
        For non-government employees: Exemption is least of:
        1. Actual gratuity received
        2. 15 days' salary for each year of service (based on last drawn salary)
        3. ₹20,00,000 (statutory limit)
        
        In new regime: Some exemptions that are available in old regime may not apply
        """
        logger.info(f"Calculating gratuity for regime: {regime}")
        logger.info(f"Gratuity income: {self.gratuity_income}")
        logger.info(f"Last drawn monthly salary: {last_drawn_monthly_salary}")
        
        # Compute service years from date of joining and date of leaving
        service_years = self.compute_service_years(date_of_joining, date_of_leaving)
        logger.info(f"Computed service years: {service_years:.2f}")
        
        if regime == 'new':
            # In new regime, different rules may apply, but for now using same as old
            pass
        
        # For government employees, gratuity is fully exempt
        if is_govt_employee:
            logger.info("Government employee: Gratuity fully exempt")
            return 0
        
        # For non-government employees, calculate exemption
        # 1. Actual gratuity received
        actual_received = self.gratuity_income
        
        # 2. 15 days' salary for each year of service
        daily_salary = last_drawn_monthly_salary / 26  # Considering 26 working days in a month
        fifteen_days_salary = daily_salary * 15
        salary_based_exemption = fifteen_days_salary * service_years
        
        # 3. Statutory limit (₹20,00,000)
        statutory_limit = 2000000
        
        # Exemption is the least of the three amounts
        exemption = min(actual_received, salary_based_exemption, statutory_limit)
        
        # Taxable amount is actual received minus exemption
        taxable_amount = max(0, self.gratuity_income - exemption)
        
        logger.info(f"Gratuity exemption calculation:")
        logger.info(f"Actual received: {actual_received}")
        logger.info(f"Salary-based exemption: {salary_based_exemption}")
        logger.info(f"Statutory limit: {statutory_limit}")
        logger.info(f"Exemption amount: {exemption}")
        logger.info(f"Taxable amount: {taxable_amount}")
        
        return taxable_amount
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "gratuity_income": cls.gratuity_income
        }

@dataclass
class RetrenchmentCompensation:
    """
    Represents retrenchment compensation under Section 10(10B) of the Income Tax Act.
    Retrenchment compensation is exempt up to the lower of:
    1. Actual amount received
    2. Rs. 5,00,000
    3. 15 days' average pay for each completed year of service or part thereof in excess of 6 months
    """
    retrenchment_amount: float = 0
    is_provided: bool = False
    
    def compute_service_years(self, date_of_joining: datetime.datetime, date_of_leaving: datetime.datetime) -> float:
        """
        Compute the number of years of service based on date of joining and date of leaving.
        """
        if not date_of_joining or not date_of_leaving:
            logger.warning("Date of joining or date of leaving is missing, cannot compute service years")
            return 0.0
            
        # Calculate the difference between date of joining and date of leaving
        service_days = (date_of_leaving - date_of_joining).days
        service_years = service_days / 365.25  # Using 365.25 to account for leap years
        
        logger.info(f"Computed service period: Date of joining={date_of_joining}, Date of leaving={date_of_leaving}, days={service_days}, years={service_years:.2f}")
        return service_years
    
    def total_taxable_income_per_slab(self, regime: str = 'old', date_of_joining: datetime.datetime = None, date_of_leaving: datetime.datetime = None, last_drawn_monthly_salary: float = 0) -> float:
        """
        Calculate taxable retrenchment compensation based on the tax regime.
        
        Exemption is least of:
        1. Actual amount received
        2. Rs. 5,00,000 (statutory limit)
        3. 15 days' average pay for each completed year of service
        
        Non-workmen may have different rules in some cases, but generally same calculation applies.
        """
        logger.info(f"Calculating retrenchment compensation for regime: {regime}")
        logger.info(f"Retrenchment amount: {self.retrenchment_amount}")
        logger.info(f"Last drawn monthly salary: {last_drawn_monthly_salary}")
        
        if regime == 'new':
            # In new regime, different rules may apply, but for now using same as old
            pass
        
        # If not a workman under Industrial Disputes Act, may have different exemption rules
        # But for simplicity, assuming same calculation
        
        # Compute service years from date of joining and date of leaving
        service_years = self.compute_service_years(date_of_joining, date_of_leaving)
        logger.info(f"Computed service years: {service_years:.2f}")
        
        # Calculate exemption
        # 1. Actual amount received
        actual_received = self.retrenchment_amount
        
        # 2. Statutory limit (₹5,00,000)
        statutory_limit = 500000
        
        # 3. 15 days' average pay for each completed year of service
        daily_salary = last_drawn_monthly_salary / 30  # Average daily wage
        fifteen_days_salary = daily_salary * 15
        
        # Count completed years of service and part thereof in excess of 6 months
        completed_years = int(service_years)
        remaining_days = (service_years - completed_years) * 365.25
        if remaining_days > 182.625:  # More than 6 months
            completed_years += 1
            
        salary_based_exemption = fifteen_days_salary * completed_years
        
        # Exemption is the least of the three amounts
        exemption = min(actual_received, salary_based_exemption, statutory_limit)
        
        # Taxable amount is actual received minus exemption
        taxable_amount = max(0, self.retrenchment_amount - exemption)
        
        logger.info(f"Retrenchment compensation exemption calculation:")
        logger.info(f"Actual received: {actual_received}")
        logger.info(f"Salary-based exemption: {salary_based_exemption}")
        logger.info(f"Statutory limit: {statutory_limit}")
        logger.info(f"Exemption amount: {exemption}")
        logger.info(f"Taxable amount: {taxable_amount}")
        
        return taxable_amount
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "retrenchment_amount": cls.retrenchment_amount,
            "is_provided": cls.is_provided
        }
    