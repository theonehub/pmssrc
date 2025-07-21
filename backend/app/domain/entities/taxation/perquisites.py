"""
Perquisites Entity
Domain entity for handling all perquisite types and their valuations as per Indian Income Tax Act
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import date
from enum import Enum

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AccommodationType(Enum):
    """Types of accommodation perquisites."""
    GOVERNMENT = "Government"
    EMPLOYER_OWNED = "Employer-Owned"
    EMPLOYER_LEASED = "Employer-Leased"
    HOTEL = "Hotel (15+ days)"


class CityPopulation(Enum):
    """City population categories for accommodation perquisites."""
    ABOVE_40_LAKHS = "Above 40 lakhs"
    BETWEEN_15_40_LAKHS = "Between 15-40 lakhs"
    BELOW_15_LAKHS = "Below 15 lakhs"


class CarUseType(Enum):
    """Types of car usage."""
    PERSONAL = "Personal"
    BUSINESS = "Business"
    MIXED = "Mixed"


class AssetType(Enum):
    """Types of movable assets."""
    ELECTRONICS = "Electronics"
    MOTOR_VEHICLE = "Motor Vehicle"
    OTHERS = "Others"


@dataclass
class AccommodationPerquisite:
    """Accommodation perquisite valuation."""
    
    accommodation_type: AccommodationType
    city_population: CityPopulation = CityPopulation.BELOW_15_LAKHS
    
    # For government accommodation
    license_fees: Money = Money.zero()
    employee_rent_payment: Money = Money.zero()
    
    # For employer-leased
    rent_paid_by_employer: Money = Money.zero()
    
    # For hotel accommodation
    hotel_charges: Money = Money.zero()
    stay_days: int = 0
    
    # Furniture related
    furniture_cost: Money = Money.zero()
    furniture_employee_payment: Money = Money.zero()
    is_furniture_owned_by_employer: bool = True
    
    def calculate_accommodation_value(self, basic_plus_da: Money, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate accommodation perquisite value."""

        if summary_data:
            summary_data['accommodation_type'] = self.accommodation_type
            summary_data['employee_rent_payment'] = self.employee_rent_payment
            summary_data['license_fees'] = self.license_fees
        logger.debug(f"Accommodation: employee_rent_payment: {self.employee_rent_payment}")
        logger.debug(f"Accommodation: license_fees: {self.license_fees}")
        if self.accommodation_type == AccommodationType.GOVERNMENT:
            taxable_value = self.employee_rent_payment.subtract(self.license_fees).max(Money.zero())
            logger.debug(f"Accommodation: Government Provided, Taxable Value: {taxable_value}")
            if summary_data:
                summary_data['taxable_value(employee_rent_payment - license_fees)'] = taxable_value
            return taxable_value
        
        elif self.accommodation_type == AccommodationType.EMPLOYER_OWNED:
            if self.city_population == CityPopulation.ABOVE_40_LAKHS:
                rate = Decimal('0.10')  # 10%
            elif self.city_population == CityPopulation.BETWEEN_15_40_LAKHS:
                rate = Decimal('0.075')  # 7.5%
            else:
                rate = Decimal('0.05')  # 5%
            
            taxable_value = basic_plus_da.percentage(rate)
            logger.debug(f"Accommodation: Employer Owned, Taxable Value: {rate}% of {basic_plus_da} = {taxable_value}")
            if summary_data:
                summary_data['city_population'] = self.city_population
                summary_data['rate'] = rate
                summary_data['taxable_value(basic_plus_da * rate)'] = taxable_value
            return taxable_value
        
        elif self.accommodation_type == AccommodationType.EMPLOYER_LEASED:
            max_limit = basic_plus_da.percentage(10)  # 10% of basic + DA
            logger.debug(f"Accommodation: Employer Leased, Max Limit: {10}% of {basic_plus_da} = {max_limit}")
            logger.debug(f"Accommodation: Employer Leased, Rent Paid by Employer: {self.rent_paid_by_employer}")
            taxable_value = self.rent_paid_by_employer.min(max_limit)
            if summary_data:
                summary_data['max_limit(10% of basic_plus_da)'] = max_limit
                summary_data['taxable_value(min(rent_paid_by_employer, max_limit))'] = taxable_value
            logger.debug(f"Accommodation: Employer Leased, Taxable Value: {taxable_value}")
            return taxable_value
        
        elif self.accommodation_type == AccommodationType.HOTEL:
            logger.debug(f"Accommodation: Hotel, Stay Days: {self.stay_days}")
            if self.stay_days >= 15:
                max_limit = basic_plus_da.percentage(24)  # 24% of basic + DA
                logger.debug(f"Accommodation: Hotel, Max Limit: {24}% of {basic_plus_da} = {max_limit}")
                logger.debug(f"Accommodation: Hotel, Hotel Charges: {self.hotel_charges}")
                taxable_value = self.hotel_charges.min(max_limit)
                if summary_data:
                    summary_data['stay_days'] = self.stay_days
                    summary_data['max_limit(24% of basic_plus_da)'] = max_limit
                    summary_data['taxable_value(min(hotel_charges, max_limit))'] = taxable_value
                logger.debug(f"Accommodation: Hotel, Taxable Value: {taxable_value}")
                return taxable_value
        
        return Money.zero()
    
    def calculate_furniture_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate furniture perquisite value."""
        if self.is_furniture_owned_by_employer:
            furniture_value = self.furniture_cost.percentage(10)  # 10% of cost
            logger.debug(f"Accommodation: Furniture Value(10% of {self.furniture_cost}): {furniture_value}")
            if summary_data:
                summary_data['furniture_cost'] = self.furniture_cost
                summary_data['furniture_value(10% of furniture_cost)'] = furniture_value
        else:
            furniture_value = self.furniture_cost  # Full hire/lease cost
            logger.debug(f"Accommodation: Furniture Value(Full Hire/Lease Cost): {furniture_value}")
            if summary_data:
                summary_data['furniture_cost'] = self.furniture_cost
                summary_data['furniture_value(Full Hire/Lease Cost)'] = furniture_value
        
        taxable_value = furniture_value.subtract(self.furniture_employee_payment).max(Money.zero())
        logger.debug(f"Accommodation: Taxable Value(Furniture): {taxable_value}")
        if summary_data:
            summary_data['taxable_value(furniture_value - furniture_employee_payment)'] = taxable_value
        return taxable_value
    
    def calculate_taxable_accommodation_value(self, basic_plus_da: Money, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate total accommodation perquisite value."""
        accommodation_value = self.calculate_accommodation_value(basic_plus_da, summary_data)
        furniture_value = self.calculate_furniture_value(summary_data)
        if summary_data:
            summary_data['Furniture Value'] = furniture_value
            summary_data['Accommodation Value'] = accommodation_value
        logger.debug(f"Accommodation: Furniture Value: {furniture_value}")
        logger.debug(f"Accommodation: Accommodation Value: {accommodation_value}")
        taxable_value = accommodation_value.add(furniture_value)
        logger.debug(f"Accommodation: Taxable Value(Accommodation + Furniture): {taxable_value}")
        if summary_data:
            summary_data['Taxable Value(Accommodation + Furniture)'] = taxable_value
        return taxable_value


@dataclass
class CarPerquisite:
    """Car perquisite valuation."""
    
    car_use_type: CarUseType
    engine_capacity_cc: int = 1600
    months_used: int = 12
    months_used_other_vehicle: int = 12
    
    # For personal use
    car_cost_to_employer: Money = Money.zero()
    other_vehicle_cost: Money = Money.zero()
    driver_cost: Money = Money.zero()
    
    # For mixed use
    has_expense_reimbursement: bool = False
    driver_provided: bool = False

    def calculate_monthly_payout(self) -> Money:
        """Calculate monthly payout."""
        total = Money.zero()
        if self.car_cost_to_employer.is_greater_than(Money.zero()):
            total = self.car_cost_to_employer.divide(self.months_used)
        if self.other_vehicle_cost.is_greater_than(Money.zero()):
            total = total.add(self.other_vehicle_cost.divide(self.months_used_other_vehicle))
        if self.driver_cost.is_greater_than(Money.zero()):
            total = total.add(self.driver_cost.divide(self.months_used))
        return total
    
    def calculate_taxable_car_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate car perquisite value."""
        if summary_data:
            summary_data['calculate_taxable_car_value'] = True
            summary_data['car_use_type'] = self.car_use_type
            summary_data['engine_capacity_cc'] = self.engine_capacity_cc
            summary_data['months_used'] = self.months_used
            summary_data['months_used_other_vehicle'] = self.months_used_other_vehicle
            summary_data['car_cost_to_employer'] = self.car_cost_to_employer
            summary_data['other_vehicle_cost'] = self.other_vehicle_cost
            summary_data['driver_cost'] = self.driver_cost
            summary_data['has_expense_reimbursement'] = self.has_expense_reimbursement
            summary_data['driver_provided'] = self.driver_provided
        if self.car_use_type == CarUseType.BUSINESS:
            logger.debug(f"Car: Business Use, Not taxable")
            if summary_data:
                summary_data['taxable_value'] = Money.zero()
            return Money.zero()  # Not taxable
        elif self.car_use_type == CarUseType.PERSONAL:
            logger.debug(f"Car: Personal Use, Car Cost to Employer: {self.car_cost_to_employer}")
            logger.debug(f"Car: Personal Use, Other Vehicle Cost: {self.other_vehicle_cost}")
            logger.debug(f"Car: Personal Use, Months Used: {self.months_used}")
            logger.debug(f"Car: Personal Use, Months Used Other Vehicle: {self.months_used_other_vehicle}")
            
            monthly_cost = self.car_cost_to_employer.multiply(self.months_used)
            monthly_cost_other_vehicle = self.other_vehicle_cost.multiply(self.months_used_other_vehicle)
            monthly_cost_total = monthly_cost.add(monthly_cost_other_vehicle)
            logger.debug(f"Car: Personal Use, Monthly Cost: {monthly_cost_total}")
            if summary_data:
                summary_data['taxable_value'] = monthly_cost_total
            return monthly_cost_total
        elif self.car_use_type == CarUseType.MIXED:
            # Monthly rates based on engine capacity
            logger.debug(f"Car: Mixed Use, Engine Capacity: {self.engine_capacity_cc}")
            logger.debug(f"Car: Mixed Use, Has Expense Reimbursement: {self.has_expense_reimbursement}")
            logger.debug(f"Car: Mixed Use, Driver Provided: {self.driver_provided}")
            if self.engine_capacity_cc > 1600:
                if self.has_expense_reimbursement:
                    monthly_rate = Money.from_int(2400)
                else:
                    monthly_rate = Money.from_int(900)
            else:
                if self.has_expense_reimbursement:
                    monthly_rate = Money.from_int(1800)
                else:
                    monthly_rate = Money.from_int(600)
            logger.debug(f"Car: Mixed Use, tax free value: {monthly_rate} * {self.months_used} = {monthly_rate.multiply(self.months_used)}")
            car_tax_free_value = monthly_rate.multiply(self.months_used)
            if summary_data:
                summary_data['monthly_rate'] = monthly_rate
                summary_data['car_tax_free_value'] = car_tax_free_value
            if self.driver_provided:
                driver_tax_free_value = Money.from_int(900).multiply(self.months_used)
                tax_free_value = car_tax_free_value.add(driver_tax_free_value)
                if summary_data:
                    summary_data['driver_tax_free_value'] = driver_tax_free_value
                    summary_data['tax_free_value'] = tax_free_value
            else:
                tax_free_value = car_tax_free_value
            logger.debug(f"Car: Mixed Use, Total Tax Free Value: {tax_free_value}")
            taxable_value = self.car_cost_to_employer.multiply(self.months_used).subtract(tax_free_value)
            logger.debug(f"Car: Mixed Use, First Vehicle Taxable Value: {taxable_value}")
            if summary_data:
                summary_data['first_vehicle_taxable_value'] = taxable_value
            if self.other_vehicle_cost.is_greater_than(Money.zero()):
                exepmt_limit = Money.from_int(900).multiply(self.months_used_other_vehicle)
                other_vehicle_taxable_value = self.other_vehicle_cost.subtract(exepmt_limit).max(Money.zero())
                logger.debug(f"Car: Mixed Use, Other Vehicle Taxable Value: {other_vehicle_taxable_value}")
                taxable_value = taxable_value.add(other_vehicle_taxable_value)
                if summary_data:
                    summary_data['exepmt_limit'] = exepmt_limit
                    summary_data['other_vehicle_taxable_value'] = other_vehicle_taxable_value
            logger.debug(f"Car: Mixed Use, Total Taxable Value: {taxable_value}")
            if summary_data:
                summary_data['taxable_value'] = taxable_value
            return taxable_value
        if summary_data:
            summary_data['taxable_value'] = Money.zero()
        return Money.zero()

@dataclass
class LTAPerquisite:
    """Leave Travel Allowance perquisite."""
    
    is_monthly_paid: bool = False
    lta_allocated_yearly: Money = Money.zero()
    lta_amount_claimed: Money = Money.zero()
    lta_claimed_count: int = 0
    public_transport_cost: Money = Money.zero()
    travel_mode: str = 'Air'  # Railway, Air, Public Transport

    def calculate_monthly_payout(self) -> Money:
        #TODO check condition if LTA disbursement is done in the month
        return self.lta_allocated_yearly.divide(12)
    
    def calculate_taxable_lta_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable LTA value."""
        
        if self.lta_claimed_count > 2:
            return self.lta_amount_claimed  # Fully taxable if more than 2 journeys in 4 years
        
        # Eligible exemption based on travel mode
        if self.travel_mode == 'Railway':
            # AC First Class fare is the limit for railway
            eligible_exemption = self.public_transport_cost.min(self.lta_amount_claimed)
        elif self.travel_mode == 'Air':
            # Economy class fare is the limit for air travel
            eligible_exemption = self.public_transport_cost.min(self.lta_amount_claimed)
        else:
            # Actual public transport cost for other modes
            eligible_exemption = self.public_transport_cost.min(self.lta_amount_claimed)
            
        if self.lta_allocated_yearly.is_greater_than(eligible_exemption):
            ret_val = self.lta_allocated_yearly.subtract(eligible_exemption)
            if summary_data:
                summary_data['is_monthly_paid'] = self.is_monthly_paid
                summary_data['lta_allocated_yearly'] = self.lta_allocated_yearly
                summary_data['lta_amount_claimed'] = self.lta_amount_claimed
                summary_data['lta_claimed_count'] = self.lta_claimed_count
                summary_data['public_transport_cost'] = self.public_transport_cost
                summary_data['travel_mode'] = self.travel_mode
                summary_data['taxable_lta_value'] = ret_val
            return ret_val
        else:
            if summary_data:
                summary_data['is_monthly_paid'] = self.is_monthly_paid
                summary_data['lta_allocated_yearly'] = self.lta_allocated_yearly
                summary_data['lta_amount_claimed'] = self.lta_amount_claimed
                summary_data['lta_claimed_count'] = self.lta_claimed_count
                summary_data['public_transport_cost'] = self.public_transport_cost
                summary_data['travel_mode'] = self.travel_mode
                summary_data['taxable_lta_value'] = Money.zero()
            return Money.zero()

@dataclass
class MonthlyPaymentSchedule:
    """Monthly payment schedule for a loan."""
    
    month: int
    outstanding_amount: Money
    principal_amount: Money
    interest_amount: Money


@dataclass
class InterestFreeConcessionalLoan:
    """Interest-free/concessional loan perquisite."""
    
    loan_amount: Money = Money.zero()
    emi_amount: Money = Money.zero()
    outstanding_amount: Money = Money.zero()
    company_interest_rate: Decimal = Decimal('0')
    sbi_interest_rate: Decimal = Decimal('8.5')
    loan_start_date: date = date.today()
    loan_type: str = 'Personal'  # Personal, Medical, etc.
    # monthly_payment_schedule: list[MonthlyPaymentSchedule] = None
    # current_month: int = 1  # Track current month for payment processing

    def calculate_monthly_payment_schedule(self, interest_rate: Decimal, summary_data: Dict[str, Any] = None) -> tuple[list[MonthlyPaymentSchedule], Money]:
        """Calculate monthly payment schedule for a loan."""
        #TODO: Add a condition to check if the loan start date is before tax year start date
        interest_paid = Money.zero()
        outstanding_amount = self.outstanding_amount
        monthly_payment_schedule = []
        # Log loan details using table logger
        if summary_data:
            summary_data['loan_amount'] = self.loan_amount
            summary_data['emi_amount'] = self.emi_amount
            summary_data['outstanding_amount'] = self.outstanding_amount
            summary_data['company_interest_rate'] = self.company_interest_rate
            summary_data['sbi_interest_rate'] = self.sbi_interest_rate
            summary_data['loan_start_date'] = self.loan_start_date
        # Prepare monthly schedule data
        schedule_data = []
        for month in range(1, 13):
            if outstanding_amount.is_zero():
                break
            monthly_interest_rate = interest_rate/12
            interest_amount = outstanding_amount.percentage(monthly_interest_rate)
            interest_paid = interest_paid.add(interest_amount)
            
            # Handle case where outstanding amount is less than EMI
            if outstanding_amount.is_less_than(self.emi_amount):
                # If outstanding amount is less than EMI, principal amount equals outstanding amount
                principal_amount = outstanding_amount
                # Adjust interest amount to ensure total payment doesn't exceed outstanding amount
                total_payment = principal_amount.add(interest_amount)
                if total_payment.is_greater_than(outstanding_amount):
                    # Reduce interest amount to fit within outstanding amount
                    interest_amount = outstanding_amount.subtract(principal_amount).max(Money.zero())
                    interest_paid = interest_paid.subtract(outstanding_amount.percentage(monthly_interest_rate)).add(interest_amount)
            else:
                # Normal case: principal amount is EMI minus interest
                principal_amount = self.emi_amount.subtract(interest_amount)
            
            monthly_payment_schedule.append(MonthlyPaymentSchedule(month, outstanding_amount, principal_amount, interest_amount))
            outstanding_amount = outstanding_amount.subtract(principal_amount)
            
            # Calculate EMI deducted (principal + interest)
            emi_deducted = principal_amount.add(interest_amount)
            
            # Add to schedule data for table logging
            if summary_data:
                summary_data[f'outstanding_amount_{month}'] = outstanding_amount
                summary_data[f'interest_paid_{month}'] = interest_paid
                summary_data[f'principal_amount_{month}'] = principal_amount
                summary_data[f'emi_deducted_{month}'] = emi_deducted
            schedule_data.append([
                f"{month:02d}",
                f"₹{outstanding_amount.to_float():.2f}",
                f"₹{interest_amount.to_float():.2f}",
                f"₹{principal_amount.to_float():.2f}",
                f"₹{emi_deducted.to_float():.2f}"
            ])
        
        return monthly_payment_schedule, interest_paid

    
    def calculate_taxable_loan_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable benefit from interest-free/concessional loan."""

        monthly_payment_schedule_company, interest_paid_company = self.calculate_monthly_payment_schedule(self.company_interest_rate)
        monthly_payment_schedule_sbi, interest_paid_sbi = self.calculate_monthly_payment_schedule(self.sbi_interest_rate)
        if summary_data:
            summary_data['calculate_taxable_loan_value'] = True
            summary_data['monthly_payment_schedule_company'] = monthly_payment_schedule_company
            summary_data['monthly_payment_schedule_sbi'] = monthly_payment_schedule_sbi
            summary_data['interest_paid_company'] = interest_paid_company
            summary_data['interest_paid_sbi'] = interest_paid_sbi
        if interest_paid_sbi.is_greater_than(interest_paid_company):
            interest_saved = interest_paid_sbi.subtract(interest_paid_company)
            logger.debug(f"CL: Interest Saved: {interest_saved.to_float():.2f}")
            summary_data['interest_saved'] = interest_saved
            return interest_saved
        else:
            return Money.zero()


@dataclass
class ESOPPerquisite:
    """Employee Stock Option Plan perquisite."""
    
    shares_exercised: int = 0
    exercise_price: Money = Money.zero()
    allotment_price: Money = Money.zero()
    
    def calculate_esop_allocation_gain(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate ESOP allocation gain."""
        if self.shares_exercised <= 0:
            return Money.zero()
        
        if self.exercise_price.is_greater_than(self.allotment_price):
            gain_per_share = self.exercise_price.subtract(self.allotment_price)
        else:
            gain_per_share = Money.zero()
        ret_val = gain_per_share.multiply(self.shares_exercised)
        if summary_data:
            summary_data['calculate_esop_allocation_gain'] = True
            summary_data['gain_per_share'] = gain_per_share
            summary_data['shares_exercised'] = self.shares_exercised
            summary_data['exercise_price'] = self.exercise_price
            summary_data['allotment_price'] = self.allotment_price
            summary_data['esop_allocation_gain'] = ret_val
        return ret_val


@dataclass
class UtilitiesPerquisite:
    """Gas, Electricity, Water perquisite."""
    
    gas_paid_by_employer: Money = Money.zero()
    electricity_paid_by_employer: Money = Money.zero()
    water_paid_by_employer: Money = Money.zero()
    gas_paid_by_employee: Money = Money.zero()
    electricity_paid_by_employee: Money = Money.zero()
    water_paid_by_employee: Money = Money.zero()
    is_gas_manufactured_by_employer: bool = False
    is_electricity_manufactured_by_employer: bool = False
    is_water_manufactured_by_employer: bool = False
    
    def calculate_taxable_utilities_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable utilities value."""
        
        employer_total = (self.gas_paid_by_employer
                         .add(self.electricity_paid_by_employer)
                         .add(self.water_paid_by_employer))
        
        employee_total = (self.gas_paid_by_employee
                         .add(self.electricity_paid_by_employee)
                         .add(self.water_paid_by_employee))
        if summary_data:
            summary_data['calculate_taxable_utilities_value'] = True
            summary_data['gas_paid_by_employer'] = self.gas_paid_by_employer
            summary_data['electricity_paid_by_employer'] = self.electricity_paid_by_employer
            summary_data['water_paid_by_employer'] = self.water_paid_by_employer
            summary_data['gas_paid_by_employee'] = self.gas_paid_by_employee
            summary_data['electricity_paid_by_employee'] = self.electricity_paid_by_employee
            summary_data['water_paid_by_employee'] = self.water_paid_by_employee
            summary_data['is_gas_manufactured_by_employer'] = self.is_gas_manufactured_by_employer
            summary_data['is_electricity_manufactured_by_employer'] = self.is_electricity_manufactured_by_employer
            summary_data['is_water_manufactured_by_employer'] = self.is_water_manufactured_by_employer
            summary_data['employer_total'] = employer_total
            summary_data['employee_total'] = employee_total 
        if employer_total.is_greater_than(employee_total):
            return employer_total.subtract(employee_total)
        else:
            return Money.zero()


@dataclass
class FreeEducationPerquisite:
    """Free education perquisite."""
    
    monthly_expenses_child1: Money = Money.zero()
    monthly_expenses_child2: Money = Money.zero()
    months_child1: int = 12
    months_child2: int = 12
    employer_maintained_1st_child: bool = False
    employer_maintained_2nd_child: bool = False
    
    def calculate_taxable_education_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable free education value."""
        exemption_per_child_per_month = Money.from_int(1000)
        total_taxable = Money.zero()


        # Child 1
        if self.employer_maintained_1st_child and self.months_child1 > 0:
            if self.monthly_expenses_child1.is_greater_than(exemption_per_child_per_month):
                monthly_taxable_child1 = self.monthly_expenses_child1.subtract(exemption_per_child_per_month)
            else:
                monthly_taxable_child1 = Money.zero()
            child1_taxable = monthly_taxable_child1.multiply(self.months_child1)
            total_taxable = total_taxable.add(child1_taxable)
        
        # Child 2
        if self.employer_maintained_2nd_child and self.months_child2 > 0:
            if self.monthly_expenses_child2.is_greater_than(exemption_per_child_per_month):
                monthly_taxable_child2 = self.monthly_expenses_child2.subtract(exemption_per_child_per_month)
            else:
                monthly_taxable_child2 = Money.zero()
            child2_taxable = monthly_taxable_child2.multiply(self.months_child2)
            total_taxable = total_taxable.add(child2_taxable)

        if summary_data:
            summary_data['calculate_taxable_education_value'] = True
            summary_data['monthly_expenses_child1'] = self.monthly_expenses_child1
            summary_data['monthly_expenses_child2'] = self.monthly_expenses_child2
            summary_data['months_child1'] = self.months_child1
            summary_data['months_child2'] = self.months_child2
            summary_data['employer_maintained_1st_child'] = self.employer_maintained_1st_child
            summary_data['employer_maintained_2nd_child'] = self.employer_maintained_2nd_child  
            summary_data['total_taxable'] = total_taxable
        
        return total_taxable


@dataclass
class MovableAssetUsage:
    """Movable asset usage perquisite."""
    
    asset_type: AssetType
    asset_value: Money = Money.zero()
    hire_cost: Money = Money.zero()
    employee_payment: Money = Money.zero()
    is_employer_owned: bool = True
    
    def calculate_taxable_movable_asset_usage_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable movable asset usage value."""

        ret_val = Money.zero()
        if summary_data:
            summary_data['calculate_taxable_movable_asset_usage_value'] = "Employer-owned: 10% of asset value, otherwise hire cost"
            summary_data['asset_type'] = self.asset_type
            summary_data['asset_value'] = self.asset_value
            summary_data['hire_cost'] = self.hire_cost
            summary_data['employee_payment'] = self.employee_payment
            summary_data['is_employer_owned'] = self.is_employer_owned

        if self.is_employer_owned:
            # Employer-owned: 10% of asset value
            asset_value = self.asset_value.percentage(10)
        else:
            # Employer-hired: Full hire cost
            asset_value = self.hire_cost
        
        if asset_value.is_greater_than(self.employee_payment):
            return asset_value.subtract(self.employee_payment)
        else:
            return Money.zero()


@dataclass
class MovableAssetTransfer:
    """Movable asset transfer perquisite."""
    
    asset_type: AssetType
    asset_cost: Money = Money.zero()
    years_of_use: int = 1
    employee_payment: Money = Money.zero()
    
    def get_depreciation_rate(self) -> Decimal:
        """Get depreciation rate based on asset type."""
        if self.asset_type == AssetType.ELECTRONICS:
            return Decimal('0.5')  # 50% per year
        elif self.asset_type == AssetType.MOTOR_VEHICLE:
            return Decimal('0.2')  # 20% per year
        else:
            return Decimal('0.1')  # 10% per year
    
    def calculate_taxable_movable_asset_transfer_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable movable asset transfer value."""

        depreciation_rate = self.get_depreciation_rate()
        annual_depreciation = self.asset_cost.percentage(float(depreciation_rate * 100))
        total_depreciation = annual_depreciation.multiply(self.years_of_use)
            
        depreciated_value = self.asset_cost.subtract(total_depreciation).max(Money.zero())

                
        if summary_data:
            summary_data['calculate_taxable_movable_asset_transfer_value'] = True
            summary_data['asset_type'] = self.asset_type
            summary_data['asset_cost'] = self.asset_cost
            summary_data['years_of_use'] = self.years_of_use
            summary_data['employee_payment'] = self.employee_payment
            summary_data['depreciation_rate'] = depreciation_rate
            summary_data['annual_depreciation'] = annual_depreciation
            summary_data['total_depreciation'] = total_depreciation
            summary_data['depreciated_value'] = depreciated_value

        if depreciated_value.is_greater_than(self.employee_payment):
            return depreciated_value.subtract(self.employee_payment)
        else:
            return Money.zero()


@dataclass
class LunchRefreshmentPerquisite:
    """Lunch/refreshment perquisite."""
    
    employer_cost: Money = Money.zero()
    employee_payment: Money = Money.zero()
    meal_days_per_year: int = 250
    
    def calculate_taxable_meal_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable lunch/refreshment value."""
        exemption_per_meal = Money.from_int(50)
        annual_exemption = exemption_per_meal.multiply(self.meal_days_per_year)

        if self.employer_cost.is_greater_than(self.employee_payment):
            net_employer_cost = self.employer_cost.subtract(self.employee_payment)
        else:
            net_employer_cost = Money.zero()

        if summary_data:
            summary_data['calculate_taxable_meal_value'] = True
            summary_data['employer_cost'] = self.employer_cost
            summary_data['employee_payment'] = self.employee_payment
            summary_data['meal_days_per_year'] = self.meal_days_per_year
            summary_data['annual_exemption'] = annual_exemption
            summary_data['net_employer_cost'] = net_employer_cost
        
        if net_employer_cost.is_greater_than(annual_exemption):
            return net_employer_cost.subtract(annual_exemption)
        else:
            return Money.zero()


@dataclass
class GiftVoucherPerquisite:
    """Gift voucher perquisite."""
    
    gift_voucher_amount: Money = Money.zero()
    
    def calculate_taxable_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable gift voucher value."""
        exemption_limit = Money.from_int(5000)
        if summary_data:
            summary_data['calculate_taxable_value'] = True
            summary_data['gift_voucher_amount'] = self.gift_voucher_amount
            summary_data['exemption_limit'] = exemption_limit
        if self.gift_voucher_amount.is_greater_than(exemption_limit):
            return self.gift_voucher_amount.subtract(exemption_limit)
        else:
            return Money.zero()


@dataclass
class MonetaryBenefitsPerquisite:
    """Monetary benefits perquisite."""
    
    monetary_amount_paid_by_employer: Money = Money.zero()
    expenditure_for_official_purpose: Money = Money.zero()
    amount_paid_by_employee: Money = Money.zero()
    
    def calculate_taxable_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable monetary benefits value."""
        if summary_data:
            summary_data['calculate_taxable_value'] = True
            summary_data['monetary_amount_paid_by_employer'] = self.monetary_amount_paid_by_employer
            summary_data['expenditure_for_official_purpose'] = self.expenditure_for_official_purpose
            summary_data['amount_paid_by_employee'] = self.amount_paid_by_employee
        return (self.monetary_amount_paid_by_employer
                .subtract(self.expenditure_for_official_purpose)
                .subtract(self.amount_paid_by_employee)
                .max(Money.zero()))


@dataclass
class ClubExpensesPerquisite:
    """Club expenses perquisite."""
    
    club_expenses_paid_by_employer: Money = Money.zero()
    club_expenses_paid_by_employee: Money = Money.zero()
    club_expenses_for_official_purpose: Money = Money.zero()
    
    def calculate_taxable_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable club expenses value."""
        if summary_data:
            summary_data['calculate_taxable_value'] = True
            summary_data['club_expenses_paid_by_employer'] = self.club_expenses_paid_by_employer
            summary_data['club_expenses_paid_by_employee'] = self.club_expenses_paid_by_employee
            summary_data['club_expenses_for_official_purpose'] = self.club_expenses_for_official_purpose
        return (self.club_expenses_paid_by_employer
                .subtract(self.club_expenses_paid_by_employee)
                .subtract(self.club_expenses_for_official_purpose)
                .max(Money.zero()))


@dataclass
class DomesticHelpPerquisite:
    """Domestic help perquisite."""
    
    domestic_help_paid_by_employer: Money = Money.zero()
    domestic_help_paid_by_employee: Money = Money.zero()
    
    def calculate_taxable_domestic_help_value(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate taxable domestic help value."""
        if summary_data:
            summary_data['calculate_taxable_domestic_help_value'] = True
            summary_data['domestic_help_paid_by_employer'] = self.domestic_help_paid_by_employer
            summary_data['domestic_help_paid_by_employee'] = self.domestic_help_paid_by_employee
        return (self.domestic_help_paid_by_employer
                .subtract(self.domestic_help_paid_by_employee)
                .max(Money.zero()))

@dataclass
class MonthlyPerquisitesComponents:
    """Monthly perquisites entity."""
    key: str
    display_name: str
    value: Money


@dataclass
class MonthlyPerquisitesPayouts:
    """Monthly perquisites entity."""
    components: List[MonthlyPerquisitesComponents]
    total: Money


@dataclass
class Perquisites:
    """
    Complete perquisites entity encompassing all perquisite types as per Indian Income Tax Act.
    
    This unified entity handles:
    - Core perquisites (accommodation, car)
    - Medical and travel benefits
    - Financial benefits (loans, ESOPs)
    - Utilities and facilities
    - Asset-related perquisites
    - Miscellaneous benefits
    """
    
    # Core perquisites
    accommodation: Optional[AccommodationPerquisite] = None
    car: Optional[CarPerquisite] = None
    
    lta: Optional[LTAPerquisite] = None
    
    # Financial perquisites
    interest_free_loan: Optional[InterestFreeConcessionalLoan] = None
    esop: Optional[ESOPPerquisite] = None
    
    # Utilities and facilities
    utilities: Optional[UtilitiesPerquisite] = None
    free_education: Optional[FreeEducationPerquisite] = None
    lunch_refreshment: Optional[LunchRefreshmentPerquisite] = None
    domestic_help: Optional[DomesticHelpPerquisite] = None
    
    # Asset-related perquisites
    movable_asset_usage: Optional[MovableAssetUsage] = None
    movable_asset_transfer: Optional[MovableAssetTransfer] = None
    
    # Miscellaneous perquisites
    gift_voucher: Optional[GiftVoucherPerquisite] = None
    monetary_benefits: Optional[MonetaryBenefitsPerquisite] = None
    club_expenses: Optional[ClubExpensesPerquisite] = None
    
    def calculate_total_perquisites(self, regime: TaxRegime, basic_plus_da: Money, summary_data: Dict[str, Any] = None) -> Money:
        """
        Calculate total perquisite value for all perquisite types.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total perquisite value
        """
        if regime.regime_type == TaxRegimeType.NEW:
            # Perquisites generally not taxable in new regime
            return Money.zero()
        
        total = Money.zero()
        if summary_data:
            summary_data['calculate_total_perquisites'] = 'start'
        # Core perquisites
        if self.accommodation:
            total = total.add(self.accommodation.calculate_taxable_accommodation_value(basic_plus_da, summary_data))
        
        if self.car:
            total = total.add(self.car.calculate_taxable_car_value(summary_data))
        
        if self.lta:
            total = total.add(self.lta.calculate_taxable_lta_value(summary_data))
        
        # Financial perquisites
        if self.interest_free_loan:
            total = total.add(self.interest_free_loan.calculate_taxable_loan_value(summary_data))
        
        if self.esop:
            total = total.add(self.esop.calculate_esop_allocation_gain(summary_data))
        
        # Utilities and facilities
        if self.utilities:
            total = total.add(self.utilities.calculate_taxable_utilities_value(summary_data))
        
        if self.free_education:
            total = total.add(self.free_education.calculate_taxable_education_value(summary_data))
        
        if self.lunch_refreshment:
            total = total.add(self.lunch_refreshment.calculate_taxable_meal_value(summary_data))
        
        if self.domestic_help:
            total = total.add(self.domestic_help.calculate_taxable_domestic_help_value(summary_data))
        
        # Asset-related perquisites
        if self.movable_asset_usage:
            total = total.add(self.movable_asset_usage.calculate_taxable_movable_asset_usage_value(summary_data))
        
        if self.movable_asset_transfer:
            total = total.add(self.movable_asset_transfer.calculate_taxable_movable_asset_transfer_value(summary_data))
        
        # Miscellaneous perquisites
        if self.gift_voucher:
            total = total.add(self.gift_voucher.calculate_taxable_value(summary_data))
        
        if self.monetary_benefits:
            total = total.add(self.monetary_benefits.calculate_taxable_value(summary_data))
        
        if self.club_expenses:
            total = total.add(self.club_expenses.calculate_taxable_value(summary_data))
        
        return total
    
    def get_perquisites_breakdown(self, regime: TaxRegime, basic_plus_da: Money) -> Dict[str, Any]:
        """
        Get detailed breakdown of all perquisites.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Complete perquisites breakdown
        """
        breakdown = {
            "regime": regime.regime_type.value,
            "perquisites_applicable": regime.regime_type == TaxRegimeType.OLD
        }
        
        if regime.regime_type == TaxRegimeType.OLD:
            breakdown.update({
                # Core perquisites
                "accommodation": self.accommodation.calculate_total_value(basic_plus_da).to_float() if self.accommodation else 0,
                "car": self.car.calculate_taxable_car_value().to_float() if self.car else 0,
                
                "lta": (
                    self.lta.calculate_taxable_lta_value().to_float()
                    if self.lta else 0
                ),
                
                # Financial perquisites
                "interest_free_loan": (
                    self.interest_free_loan.calculate_taxable_value().to_float()
                    if self.interest_free_loan else 0
                ),
                "esop": (
                    self.esop.calculate_allocation_gain().to_float()
                    if self.esop else 0
                ),
                
                # Utilities and facilities
                "utilities": (
                    self.utilities.calculate_taxable_value().to_float()
                    if self.utilities else 0
                ),
                "free_education": (
                    self.free_education.calculate_taxable_value().to_float()
                    if self.free_education else 0
                ),
                "lunch_refreshment": (
                    self.lunch_refreshment.calculate_taxable_value().to_float()
                    if self.lunch_refreshment else 0
                ),
                "domestic_help": (
                    self.domestic_help.calculate_taxable_value().to_float()
                    if self.domestic_help else 0
                ),
                
                # Asset-related perquisites
                "movable_asset_usage": (
                    self.movable_asset_usage.calculate_taxable_value().to_float()
                    if self.movable_asset_usage else 0
                ),
                "movable_asset_transfer": (
                    self.movable_asset_transfer.calculate_taxable_value().to_float()
                    if self.movable_asset_transfer else 0
                ),
                
                # Miscellaneous perquisites
                "gift_voucher": (
                    self.gift_voucher.calculate_taxable_value().to_float()
                    if self.gift_voucher else 0
                ),
                "monetary_benefits": (
                    self.monetary_benefits.calculate_taxable_value().to_float()
                    if self.monetary_benefits else 0
                ),
                "club_expenses": (
                    self.club_expenses.calculate_taxable_value().to_float()
                    if self.club_expenses else 0
                ),
                
                "total_perquisites": self.calculate_total_perquisites(regime).to_float()
            })
        else:
            breakdown.update({
                "message": "Perquisites generally not taxable in new tax regime",
                "total_perquisites": 0.0
            })
        
        return breakdown
    
    def get_perquisites_summary(self, regime: TaxRegime, basic_plus_da: Money) -> Dict[str, Any]:
        """
        Get a summary of perquisites by category.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Categorized perquisites summary
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return {
                "regime": regime.regime_type.value,
                "message": "Perquisites generally not taxable in new tax regime",
                "total_perquisites": 0.0
            }
        
        # Core perquisites
        core_total = Money.zero()
        if self.accommodation:
            core_total = core_total.add(self.accommodation.calculate_total_value(basic_plus_da))
        if self.car:
            core_total = core_total.add(self.car.calculate_taxable_car_value())
        
        # Financial perquisites
        financial_total = Money.zero()
        if self.interest_free_loan:
            financial_total = financial_total.add(self.interest_free_loan.calculate_taxable_value())
        if self.esop:
            financial_total = financial_total.add(self.esop.calculate_allocation_gain())
        
        # Benefits and facilities
        benefits_total = Money.zero()
        if self.lta:
            benefits_total = benefits_total.add(self.lta.calculate_taxable_lta_value())
        if self.free_education:
            benefits_total = benefits_total.add(self.free_education.calculate_taxable_value())
        if self.lunch_refreshment:
            benefits_total = benefits_total.add(self.lunch_refreshment.calculate_taxable_value())
        if self.domestic_help:
            benefits_total = benefits_total.add(self.domestic_help.calculate_taxable_value())
        
        # Asset and miscellaneous
        misc_total = Money.zero()
        if self.utilities:
            misc_total = misc_total.add(self.utilities.calculate_taxable_value())
        if self.movable_asset_usage:
            misc_total = misc_total.add(self.movable_asset_usage.calculate_taxable_value())
        if self.movable_asset_transfer:
            misc_total = misc_total.add(self.movable_asset_transfer.calculate_taxable_value())
        if self.gift_voucher:
            misc_total = misc_total.add(self.gift_voucher.calculate_taxable_value())
        if self.monetary_benefits:
            misc_total = misc_total.add(self.monetary_benefits.calculate_taxable_value())
        if self.club_expenses:
            misc_total = misc_total.add(self.club_expenses.calculate_taxable_value())
        
        total_all = core_total.add(financial_total).add(benefits_total).add(misc_total)
        
        return {
            "regime": regime.regime_type.value,
            "perquisites_by_category": {
                "core_perquisites": {
                    "accommodation_and_car": core_total.to_float(),
                    "description": "Accommodation and car perquisites"
                },
                "financial_perquisites": {
                    "loans_and_esop": financial_total.to_float(),
                    "description": "Interest-free loans and ESOP benefits"
                },
                "employee_benefits": {
                    "medical_travel_education": benefits_total.to_float(),
                    "description": "Medical, travel, education and facility benefits"
                },
                "miscellaneous": {
                    "utilities_assets_gifts": misc_total.to_float(),
                    "description": "Utilities, assets, gifts and other perquisites"
                }
            },
            "total_perquisites": total_all.to_float(),
            "highest_category": self._get_highest_category(core_total, financial_total, benefits_total, misc_total)
        }
    
    def _get_highest_category(self, core: Money, financial: Money, benefits: Money, misc: Money) -> str:
        """Get the category with highest perquisite value."""
        amounts = {
            "Core Perquisites": core,
            "Financial Perquisites": financial,
            "Employee Benefits": benefits,
            "Miscellaneous": misc
        }
        
        max_category = max(amounts.keys(), key=lambda k: amounts[k].to_float())
        return max_category if amounts[max_category].is_positive() else "None"
    
    def get_perquisites_components(self) -> List[MonthlyPerquisitesComponents]:
        """Get the perquisites components."""
        components = []
        if self.car:
            components.append(MonthlyPerquisitesComponents(key="car", display_name="Car Reimbursement", value=self.car.calculate_monthly_payout()))
        if self.lta:
            components.append(MonthlyPerquisitesComponents(key="lta", display_name="LTA", value=self.lta.calculate_monthly_payout()))
        if self.interest_free_loan:
            components.append(MonthlyPerquisitesComponents(key="loan", display_name="Loan EMI", value=self.interest_free_loan.emi_amount))
        #TODO add other perquisites components
        return components
    
    def get_loan_emi_amount(self) -> Money:
        """Get the loan EMI amount from interest-free loan perquisite."""
        if self.interest_free_loan:
            return self.interest_free_loan.emi_amount
        return Money.zero()

    @property
    def car_perquisite(self) -> Money:
        """Backward compatibility: Get car perquisite value."""
        if self.car:
            return self.car.calculate_taxable_car_value()
        return Money.zero()
    
    @property
    def driver_perquisite(self) -> Money:
        """Backward compatibility: Get driver perquisite value."""
        if self.car and self.car.driver_provided:
            # Driver cost is Rs. 900 per month
            return Money.from_int(900).multiply(self.car.months_used)
        return Money.zero()
    
    @property
    def fuel_perquisite(self) -> Money:
        """Backward compatibility: Get fuel perquisite value."""
        # Fuel is typically included in car perquisite calculation
        return Money.zero()
    
    @property
    def education_perquisite(self) -> Money:
        """Backward compatibility: Get education perquisite value."""
        if self.free_education:
            return self.free_education.calculate_taxable_value()
        return Money.zero()
    
    @property
    def domestic_servant_perquisite(self) -> Money:
        """Backward compatibility: Get domestic help perquisite value."""
        if self.domestic_help:
            return self.domestic_help.calculate_taxable_value()
        return Money.zero()
    
    @property
    def utility_perquisite(self) -> Money:
        """Backward compatibility: Get utilities perquisite value."""
        if self.utilities:
            return self.utilities.calculate_taxable_value()
        return Money.zero()
    
    @property
    def loan_perquisite(self) -> Money:
        """Backward compatibility: Get loan perquisite value."""
        if self.interest_free_loan:
            return self.interest_free_loan.calculate_taxable_value()
        return Money.zero()
    
    @property
    def esop_perquisite(self) -> Money:
        """Backward compatibility: Get ESOP perquisite value."""
        if self.esop:
            return self.esop.calculate_allocation_gain()
        return Money.zero()
    
    @property
    def club_membership_perquisite(self) -> Money:
        """Backward compatibility: Get club expenses perquisite value."""
        if self.club_expenses:
            return self.club_expenses.calculate_taxable_value()
        return Money.zero()
    
    @property
    def other_perquisites(self) -> Money:
        """Backward compatibility: Get other perquisites value."""
        total = Money.zero()
        
        # Sum up miscellaneous perquisites
        if self.gift_voucher:
            total = total.add(self.gift_voucher.calculate_taxable_value())
        
        if self.monetary_benefits:
            total = total.add(self.monetary_benefits.calculate_taxable_value())
        
        if self.lunch_refreshment:
            total = total.add(self.lunch_refreshment.calculate_taxable_value())
        
        if self.movable_asset_usage:
            total = total.add(self.movable_asset_usage.calculate_taxable_value())
        
        if self.movable_asset_transfer:
            total = total.add(self.movable_asset_transfer.calculate_taxable_value())
        
        return total 


