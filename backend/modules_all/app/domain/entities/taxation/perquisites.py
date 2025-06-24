"""
Perquisites Entity
Domain entity for handling all perquisite types and their valuations as per Indian Income Tax Act
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import date
from enum import Enum

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


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
    
    def calculate_accommodation_value(self, basic_plus_da: Money) -> Money:
        """Calculate accommodation perquisite value."""
        
        if self.accommodation_type == AccommodationType.GOVERNMENT:
            return self.license_fees.subtract(self.employee_rent_payment).max(Money.zero())
        
        elif self.accommodation_type == AccommodationType.EMPLOYER_OWNED:
            if self.city_population == CityPopulation.ABOVE_40_LAKHS:
                rate = Decimal('0.10')  # 10%
            elif self.city_population == CityPopulation.BETWEEN_15_40_LAKHS:
                rate = Decimal('0.075')  # 7.5%
            else:
                rate = Decimal('0.05')  # 5%
            
            return basic_plus_da.percentage(rate * 100)
        
        elif self.accommodation_type == AccommodationType.EMPLOYER_LEASED:
            max_limit = basic_plus_da.percentage(10)  # 10% of basic + DA
            return self.rent_paid_by_employer.min(max_limit)
        
        elif self.accommodation_type == AccommodationType.HOTEL:
            if self.stay_days >= 15:
                max_limit = basic_plus_da.percentage(24)  # 24% of basic + DA
                return self.hotel_charges.min(max_limit)
        
        return Money.zero()
    
    def calculate_furniture_value(self) -> Money:
        """Calculate furniture perquisite value."""
        if self.is_furniture_owned_by_employer:
            furniture_value = self.furniture_cost.percentage(10)  # 10% of cost
        else:
            furniture_value = self.furniture_cost  # Full hire/lease cost
        
        return furniture_value.subtract(self.furniture_employee_payment).max(Money.zero())
    
    def calculate_total_value(self) -> Money:
        """Calculate total accommodation perquisite value."""
        accommodation_value = self.calculate_accommodation_value()
        furniture_value = self.calculate_furniture_value()
        return accommodation_value.add(furniture_value)


@dataclass
class CarPerquisite:
    """Car perquisite valuation."""
    
    car_use_type: CarUseType
    engine_capacity_cc: int = 1600
    months_used: int = 12
    
    # For personal use
    car_cost_to_employer: Money = Money.zero()
    other_vehicle_cost: Money = Money.zero()
    
    # For mixed use
    has_expense_reimbursement: bool = False
    driver_provided: bool = False
    
    def calculate_car_value(self) -> Money:
        """Calculate car perquisite value."""
        if self.car_use_type == CarUseType.BUSINESS:
            return Money.zero()  # Not taxable
        
        elif self.car_use_type == CarUseType.PERSONAL:
            monthly_cost = self.car_cost_to_employer.add(self.other_vehicle_cost)
            return monthly_cost.multiply(self.months_used)
        
        elif self.car_use_type == CarUseType.MIXED:
            # Monthly rates based on engine capacity
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
            
            total_value = monthly_rate.multiply(self.months_used)
            
            # Add driver cost if provided
            if self.driver_provided:
                driver_cost = Money.from_int(900).multiply(self.months_used)
                total_value = total_value.add(driver_cost)
            
            return total_value
        
        return Money.zero()


@dataclass
class MedicalReimbursement:
    """Medical reimbursement perquisite."""
    
    medical_reimbursement_amount: Money = Money.zero()
    is_overseas_treatment: bool = False
    travel_expenses: Money = Money.zero()
    medical_expenses: Money = Money.zero()
    rbi_limit: Money = Money.zero()
    gross_salary: Money = Money.zero()
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable medical reimbursement value."""
        if not self.is_overseas_treatment:
            # Treatment in India - Rs. 15,000 exemption
            exemption = Money.from_int(15000)
            if self.medical_reimbursement_amount.is_greater_than(exemption):
                return self.medical_reimbursement_amount.subtract(exemption)
            else:
                return Money.zero()
        else:
            # Overseas treatment
            travel_value = Money.zero()
            if self.gross_salary.is_greater_than(Money.from_int(200000)):
                travel_value = self.travel_expenses
            
            if self.medical_expenses.is_greater_than(self.rbi_limit):
                medical_excess = self.medical_expenses.subtract(self.rbi_limit)
            else:
                medical_excess = Money.zero()
            return travel_value.add(medical_excess)


@dataclass
class LTAPerquisite:
    """Leave Travel Allowance perquisite."""
    
    lta_amount_claimed: Money = Money.zero()
    lta_claimed_count: int = 0
    public_transport_cost: Money = Money.zero()
    travel_mode: str = 'Air'  # Railway, Air, Public Transport
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable LTA value."""
        if self.lta_claimed_count > 2:
            return self.lta_amount_claimed  # Fully taxable if more than 2 journeys in 4 years
        
        # Eligible exemption based on travel mode
        if self.travel_mode == 'Railway':
            # AC First Class fare is the limit for railway
            eligible_exemption = self.public_transport_cost
        elif self.travel_mode == 'Air':
            # Economy class fare is the limit for air travel
            eligible_exemption = self.public_transport_cost
        else:
            # Actual public transport cost for other modes
            eligible_exemption = self.public_transport_cost
            
        if self.lta_amount_claimed.is_greater_than(eligible_exemption):
            return self.lta_amount_claimed.subtract(eligible_exemption)
        else:
            return Money.zero()


@dataclass
class InterestFreeConcessionalLoan:
    """Interest-free/concessional loan perquisite."""
    
    loan_amount: Money = Money.zero()
    outstanding_amount: Money = Money.zero()
    company_interest_rate: Decimal = Decimal('0')
    sbi_interest_rate: Decimal = Decimal('8.5')
    loan_months: int = 12
    is_medical_loan: bool = False
    loan_type: str = 'Personal'  # Personal, Medical, etc.
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable benefit from interest-free/concessional loan."""
        if self.is_medical_loan or self.loan_type == 'Medical' or self.loan_amount <= Money.from_int(20000):
            return Money.zero()  # Fully exempt
        
        interest_rate_diff = self.sbi_interest_rate - self.company_interest_rate
        if interest_rate_diff <= 0:
            return Money.zero()
        
        principal = self.outstanding_amount if self.outstanding_amount.is_positive() else self.loan_amount
        annual_benefit = principal.percentage(float(interest_rate_diff))
        
        if self.loan_months < 12:
            return annual_benefit.multiply(self.loan_months).divide(12)
        
        return annual_benefit


@dataclass
class ESOPPerquisite:
    """Employee Stock Option Plan perquisite."""
    
    shares_exercised: int = 0
    exercise_price: Money = Money.zero()
    allotment_price: Money = Money.zero()
    
    def calculate_allocation_gain(self) -> Money:
        """Calculate ESOP allocation gain."""
        if self.shares_exercised <= 0:
            return Money.zero()
        
        if self.exercise_price.is_greater_than(self.allotment_price):
            gain_per_share = self.exercise_price.subtract(self.allotment_price)
        else:
            gain_per_share = Money.zero()
        return gain_per_share.multiply(self.shares_exercised)


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
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable utilities value."""
        employer_total = (self.gas_paid_by_employer
                         .add(self.electricity_paid_by_employer)
                         .add(self.water_paid_by_employer))
        
        employee_total = (self.gas_paid_by_employee
                         .add(self.electricity_paid_by_employee)
                         .add(self.water_paid_by_employee))
        
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
    
    def calculate_taxable_value(self) -> Money:
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
        
        return total_taxable


@dataclass
class MovableAssetUsage:
    """Movable asset usage perquisite."""
    
    asset_type: AssetType
    asset_value: Money = Money.zero()
    hire_cost: Money = Money.zero()
    employee_payment: Money = Money.zero()
    is_employer_owned: bool = True
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable movable asset usage value."""
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
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable movable asset transfer value."""
        depreciation_rate = self.get_depreciation_rate()
        annual_depreciation = self.asset_cost.percentage(float(depreciation_rate * 100))
        total_depreciation = annual_depreciation.multiply(self.years_of_use)
        
        depreciated_value = self.asset_cost.subtract(total_depreciation).max(Money.zero())
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
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable lunch/refreshment value."""
        exemption_per_meal = Money.from_int(50)
        annual_exemption = exemption_per_meal.multiply(self.meal_days_per_year)
        
        if self.employer_cost.is_greater_than(self.employee_payment):
            net_employer_cost = self.employer_cost.subtract(self.employee_payment)
        else:
            net_employer_cost = Money.zero()
        
        if net_employer_cost.is_greater_than(annual_exemption):
            return net_employer_cost.subtract(annual_exemption)
        else:
            return Money.zero()


@dataclass
class GiftVoucherPerquisite:
    """Gift voucher perquisite."""
    
    gift_voucher_amount: Money = Money.zero()
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable gift voucher value."""
        exemption_limit = Money.from_int(5000)
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
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable monetary benefits value."""
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
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable club expenses value."""
        return (self.club_expenses_paid_by_employer
                .subtract(self.club_expenses_paid_by_employee)
                .subtract(self.club_expenses_for_official_purpose)
                .max(Money.zero()))


@dataclass
class DomesticHelpPerquisite:
    """Domestic help perquisite."""
    
    domestic_help_paid_by_employer: Money = Money.zero()
    domestic_help_paid_by_employee: Money = Money.zero()
    
    def calculate_taxable_value(self) -> Money:
        """Calculate taxable domestic help value."""
        return (self.domestic_help_paid_by_employer
                .subtract(self.domestic_help_paid_by_employee)
                .max(Money.zero()))


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
    
    # Medical and travel perquisites
    medical_reimbursement: Optional[MedicalReimbursement] = None
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
    
    def calculate_total_perquisites(self, regime: TaxRegime) -> Money:
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
        
        # Core perquisites
        if self.accommodation:
            total = total.add(self.accommodation.calculate_total_value())
        
        if self.car:
            total = total.add(self.car.calculate_car_value())
        
        # Medical and travel perquisites
        if self.medical_reimbursement:
            total = total.add(self.medical_reimbursement.calculate_taxable_value())
        
        if self.lta:
            total = total.add(self.lta.calculate_taxable_value())
        
        # Financial perquisites
        if self.interest_free_loan:
            total = total.add(self.interest_free_loan.calculate_taxable_value())
        
        if self.esop:
            total = total.add(self.esop.calculate_allocation_gain())
        
        # Utilities and facilities
        if self.utilities:
            total = total.add(self.utilities.calculate_taxable_value())
        
        if self.free_education:
            total = total.add(self.free_education.calculate_taxable_value())
        
        if self.lunch_refreshment:
            total = total.add(self.lunch_refreshment.calculate_taxable_value())
        
        if self.domestic_help:
            total = total.add(self.domestic_help.calculate_taxable_value())
        
        # Asset-related perquisites
        if self.movable_asset_usage:
            total = total.add(self.movable_asset_usage.calculate_taxable_value())
        
        if self.movable_asset_transfer:
            total = total.add(self.movable_asset_transfer.calculate_taxable_value())
        
        # Miscellaneous perquisites
        if self.gift_voucher:
            total = total.add(self.gift_voucher.calculate_taxable_value())
        
        if self.monetary_benefits:
            total = total.add(self.monetary_benefits.calculate_taxable_value())
        
        if self.club_expenses:
            total = total.add(self.club_expenses.calculate_taxable_value())
        
        return total
    
    def get_perquisites_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
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
                "accommodation": self.accommodation.calculate_total_value().to_float() if self.accommodation else 0,
                "car": self.car.calculate_car_value().to_float() if self.car else 0,
                
                # Medical and travel perquisites
                "medical_reimbursement": (
                    self.medical_reimbursement.calculate_taxable_value().to_float()
                    if self.medical_reimbursement else 0
                ),
                "lta": (
                    self.lta.calculate_taxable_value().to_float()
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
    
    def get_perquisites_summary(self, regime: TaxRegime) -> Dict[str, Any]:
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
            core_total = core_total.add(self.accommodation.calculate_total_value())
        if self.car:
            core_total = core_total.add(self.car.calculate_car_value())
        
        # Financial perquisites
        financial_total = Money.zero()
        if self.interest_free_loan:
            financial_total = financial_total.add(self.interest_free_loan.calculate_taxable_value())
        if self.esop:
            financial_total = financial_total.add(self.esop.calculate_allocation_gain())
        
        # Benefits and facilities
        benefits_total = Money.zero()
        if self.medical_reimbursement:
            benefits_total = benefits_total.add(self.medical_reimbursement.calculate_taxable_value())
        if self.lta:
            benefits_total = benefits_total.add(self.lta.calculate_taxable_value())
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
    
    # Backward compatibility properties for legacy code
    @property
    def rent_free_accommodation(self) -> Money:
        """Backward compatibility: Get accommodation perquisite value."""
        if self.accommodation:
            return self.accommodation.calculate_total_value()
        return Money.zero()
    
    @property
    def concessional_accommodation(self) -> Money:
        """Backward compatibility: Get concessional accommodation value."""
        # This is typically part of accommodation perquisite
        if self.accommodation and self.accommodation.accommodation_type == AccommodationType.EMPLOYER_LEASED:
            return self.accommodation.calculate_accommodation_value()
        return Money.zero()
    
    @property
    def car_perquisite(self) -> Money:
        """Backward compatibility: Get car perquisite value."""
        if self.car:
            return self.car.calculate_car_value()
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