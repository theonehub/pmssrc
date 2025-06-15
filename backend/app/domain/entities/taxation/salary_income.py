"""
Salary Income Entity
Domain entity for handling salary income components and calculations
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


@dataclass
class SpecificAllowances:
    """Specific allowances with their own exemption rules."""
    
    # Hills/High Altitude Allowances
    hills_allowance: Money = Money.zero()
    hills_exemption_limit: Money = Money.zero()  # Varies by employee
    
    # Border/Remote Area Allowance
    border_allowance: Money = Money.zero()
    border_exemption_limit: Money = Money.zero()  # Varies by employee
    
    # Transport Employee Allowance
    transport_employee_allowance: Money = Money.zero()
    
    # Children Allowances
    children_education_allowance: Money = Money.zero()
    children_count: int = 0
    children_education_months: int = 12
    hostel_allowance: Money = Money.zero()
    hostel_count: int = 0
    hostel_months: int = 12
    
    # Disabled Transport Allowance
    disabled_transport_allowance: Money = Money.zero()
    transport_months: int = 12
    is_disabled: bool = False
    
    # Underground Mines Allowance
    underground_mines_allowance: Money = Money.zero()
    mine_work_months: int = 0
    
    # Government Employee Entertainment
    government_entertainment_allowance: Money = Money.zero()
    is_government_employee: bool = False
    basic_salary: Money = Money.zero()
    
    # Additional allowances from old project
    city_compensatory_allowance: Money = Money.zero()
    rural_allowance: Money = Money.zero()
    proctorship_allowance: Money = Money.zero()
    wardenship_allowance: Money = Money.zero()
    project_allowance: Money = Money.zero()
    deputation_allowance: Money = Money.zero()
    overtime_allowance: Money = Money.zero()
    interim_relief: Money = Money.zero()
    tiffin_allowance: Money = Money.zero()
    fixed_medical_allowance: Money = Money.zero()
    servant_allowance: Money = Money.zero()
    any_other_allowance: Money = Money.zero()
    any_other_allowance_exemption: Money = Money.zero()
    
    # Section 10 exempted allowances
    govt_employees_outside_india_allowance: Money = Money.zero()
    supreme_high_court_judges_allowance: Money = Money.zero()
    judge_compensatory_allowance: Money = Money.zero()
    section_10_14_special_allowances: Money = Money.zero()
    travel_on_tour_allowance: Money = Money.zero()
    tour_daily_charge_allowance: Money = Money.zero()
    conveyance_in_performace_of_duties: Money = Money.zero()
    helper_in_performace_of_duties: Money = Money.zero()
    academic_research: Money = Money.zero()
    uniform_allowance: Money = Money.zero()
    
    def calculate_hills_exemption(self, regime: TaxRegime) -> Money:
        """Calculate hills allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        return self.hills_allowance.min(self.hills_exemption_limit)
    
    def calculate_border_exemption(self, regime: TaxRegime) -> Money:
        """Calculate border area allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        return self.border_allowance.min(self.border_exemption_limit)
    
    def calculate_transport_employee_exemption(self, regime: TaxRegime) -> Money:
        """Calculate transport employee allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        limit_1 = Money.from_int(10000)
        limit_2 = self.transport_employee_allowance.percentage(70)
        exemption_limit = limit_1.min(limit_2)
        
        return self.transport_employee_allowance.min(exemption_limit)
    
    def calculate_children_education_exemption(self, regime: TaxRegime) -> Money:
        """Calculate children education allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Rs. 100 per month per child (max 2 children)
        max_children = min(self.children_count, 2)
        exemption_limit = Money.from_int(100 * self.children_education_months * max_children)
        
        return self.children_education_allowance.min(exemption_limit)
    
    def calculate_hostel_exemption(self, regime: TaxRegime) -> Money:
        """Calculate hostel allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Rs. 300 per month per child (max 2 children)
        max_children = min(self.hostel_count, 2)
        exemption_limit = Money.from_int(300 * self.hostel_months * max_children)
        
        return self.hostel_allowance.min(exemption_limit)
    
    def calculate_disabled_transport_exemption(self, regime: TaxRegime) -> Money:
        """Calculate disabled transport allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if not self.is_disabled:
            return Money.zero()
        
        # Rs. 3,200 per month
        exemption_limit = Money.from_int(3200 * self.transport_months)
        return self.disabled_transport_allowance.min(exemption_limit)
    
    def calculate_underground_mines_exemption(self, regime: TaxRegime) -> Money:
        """Calculate underground mines allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Rs. 800 per month
        exemption_limit = Money.from_int(800 * self.mine_work_months)
        return self.underground_mines_allowance.min(exemption_limit)
    
    def calculate_government_entertainment_exemption(self, regime: TaxRegime) -> Money:
        """Calculate government entertainment allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if not self.is_government_employee:
            return Money.zero()
        
        # Minimum of (Allowance, 20% of Basic, Rs. 5,000)
        limit_1 = self.basic_salary.percentage(20)
        limit_2 = Money.from_int(5000)
        
        return self.government_entertainment_allowance.min(limit_1).min(limit_2)
    
    def calculate_section_10_exemptions(self, regime: TaxRegime) -> Money:
        """Calculate Section 10 exempted allowances."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Section 10 allowances are fully exempt
        return (self.govt_employees_outside_india_allowance
                .add(self.supreme_high_court_judges_allowance)
                .add(self.judge_compensatory_allowance)
                .add(self.section_10_14_special_allowances)
                .add(self.travel_on_tour_allowance)
                .add(self.tour_daily_charge_allowance)
                .add(self.conveyance_in_performace_of_duties)
                .add(self.helper_in_performace_of_duties)
                .add(self.academic_research)
                .add(self.uniform_allowance)
                .add(self.any_other_allowance_exemption))
    
    def calculate_total_specific_allowances(self) -> Money:
        """Calculate total specific allowances received."""
        return (self.hills_allowance
                .add(self.border_allowance)
                .add(self.transport_employee_allowance)
                .add(self.children_education_allowance)
                .add(self.hostel_allowance)
                .add(self.disabled_transport_allowance)
                .add(self.underground_mines_allowance)
                .add(self.government_entertainment_allowance)
                .add(self.city_compensatory_allowance)
                .add(self.rural_allowance)
                .add(self.proctorship_allowance)
                .add(self.wardenship_allowance)
                .add(self.project_allowance)
                .add(self.deputation_allowance)
                .add(self.overtime_allowance)
                .add(self.interim_relief)
                .add(self.tiffin_allowance)
                .add(self.fixed_medical_allowance)
                .add(self.servant_allowance)
                .add(self.any_other_allowance)
                .add(self.govt_employees_outside_india_allowance)
                .add(self.supreme_high_court_judges_allowance)
                .add(self.judge_compensatory_allowance)
                .add(self.section_10_14_special_allowances)
                .add(self.travel_on_tour_allowance)
                .add(self.tour_daily_charge_allowance)
                .add(self.conveyance_in_performace_of_duties)
                .add(self.helper_in_performace_of_duties)
                .add(self.academic_research)
                .add(self.uniform_allowance))
    
    def calculate_total_exemptions(self, regime: TaxRegime) -> Money:
        """Calculate total exemptions for specific allowances."""
        total = Money.zero()
        total = total.add(self.calculate_hills_exemption(regime))
        total = total.add(self.calculate_border_exemption(regime))
        total = total.add(self.calculate_transport_employee_exemption(regime))
        total = total.add(self.calculate_children_education_exemption(regime))
        total = total.add(self.calculate_hostel_exemption(regime))
        total = total.add(self.calculate_disabled_transport_exemption(regime))
        total = total.add(self.calculate_underground_mines_exemption(regime))
        total = total.add(self.calculate_government_entertainment_exemption(regime))
        total = total.add(self.calculate_section_10_exemptions(regime))
        return total


@dataclass
class SalaryIncome:
    """
    Enhanced salary income entity with all salary components and exemption calculations.
    
    Handles comprehensive salary components including HRA, LTA, allowances, and exemptions.
    """
    
    # Core salary components
    basic_salary: Money
    dearness_allowance: Money
    hra_received: Money
    hra_city_type: str  # "metro" or "non_metro"
    actual_rent_paid: Money
    special_allowance: Money
    other_allowances: Money
    
    # Optional components with defaults
    bonus: Money = Money.zero()
    commission: Money = Money.zero()
    lta_received: Money = Money.zero()
    medical_allowance: Money = Money.zero()
    conveyance_allowance: Money = Money.zero()
    
    # Specific allowances with exemption rules
    specific_allowances: SpecificAllowances = None
    
    def __post_init__(self):
        """Validate salary components and initialize defaults."""
        if self.hra_city_type not in ["metro", "non_metro"]:
            raise ValueError("HRA city type must be 'metro' or 'non_metro'")
        
        if self.specific_allowances is None:
            self.specific_allowances = SpecificAllowances(basic_salary=self.basic_salary)
    
    def calculate_hra_exemption(self, regime: TaxRegime) -> Money:
        """
        Calculate HRA exemption as per tax rules.
        
        Args:
            regime: Tax regime (old/new)
            
        Returns:
            Money: HRA exemption amount
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()  # No HRA exemption in new regime
        
        basic_plus_da = self.basic_salary.add(self.dearness_allowance)
        
        # Three calculations - minimum is exempt
        actual_hra = self.hra_received
        
        # 50% for metro, 40% for non-metro
        percentage = Decimal('50') if self.hra_city_type == "metro" else Decimal('40')
        percent_of_salary = basic_plus_da.percentage(percentage)
        
        # Rent paid minus 10% of salary
        ten_percent_salary = basic_plus_da.percentage(Decimal('10'))
        
        if self.actual_rent_paid.is_greater_than(ten_percent_salary):
            rent_minus_ten_percent = self.actual_rent_paid.subtract(ten_percent_salary)
        else:
            rent_minus_ten_percent = Money.zero()
        
        # Minimum of the three amounts
        min_amount = Money.zero()
        if actual_hra.is_positive():
            min_amount = actual_hra.min(percent_of_salary).min(rent_minus_ten_percent)
        
        return min_amount
    
    def calculate_lta_exemption(self, regime: TaxRegime) -> Money:
        """
        Calculate LTA exemption (only in old regime).
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: LTA exemption amount
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # LTA exemption rules would be implemented here
        # For simplicity, assuming full LTA is exempt if within limits
        return self.lta_received
    
    def calculate_medical_allowance_exemption(self, regime: TaxRegime) -> Money:
        """
        Calculate medical allowance exemption.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Medical allowance exemption
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Medical allowance up to ₹15,000 is exempt
        max_exempt = Money.from_int(15000)
        return self.medical_allowance.min(max_exempt)
    
    def calculate_conveyance_exemption(self, regime: TaxRegime) -> Money:
        """
        Calculate conveyance allowance exemption.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Conveyance allowance exemption
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Conveyance allowance up to ₹1,600 per month (₹19,200 per year) is exempt
        max_exempt = Money.from_int(19200)
        return self.conveyance_allowance.min(max_exempt)
    
    def calculate_gross_salary(self) -> Money:
        """
        Calculate gross salary (all components).
        
        Returns:
            Money: Total gross salary
        """
        gross = (self.basic_salary
                .add(self.dearness_allowance)
                .add(self.bonus)
                .add(self.commission)
                .add(self.hra_received)
                .add(self.special_allowance)
                .add(self.other_allowances)
                .add(self.lta_received)
                .add(self.medical_allowance)
                .add(self.conveyance_allowance))
        
        # Add specific allowances
        gross = gross.add(self.specific_allowances.calculate_total_specific_allowances())
        
        return gross
    
    def calculate_total_exemptions(self, regime: TaxRegime) -> Money:
        """
        Calculate total salary exemptions.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total exemptions
        """
        total_exemptions = Money.zero()
        
        # Standard exemptions
        total_exemptions = total_exemptions.add(self.calculate_hra_exemption(regime))
        total_exemptions = total_exemptions.add(self.calculate_lta_exemption(regime))
        total_exemptions = total_exemptions.add(self.calculate_medical_allowance_exemption(regime))
        total_exemptions = total_exemptions.add(self.calculate_conveyance_exemption(regime))
        
        # Specific allowances exemptions
        total_exemptions = total_exemptions.add(self.specific_allowances.calculate_total_exemptions(regime))
        
        return total_exemptions
    
    def calculate_taxable_salary(self, regime: TaxRegime) -> Money:
        """
        Calculate taxable salary after exemptions and standard deduction.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Taxable salary
        """
        gross_salary = self.calculate_gross_salary()
        
        # Apply salary exemptions
        total_exemptions = self.calculate_total_exemptions(regime)
        
        # Apply standard deduction
        standard_deduction = regime.get_standard_deduction()
        
        # Calculate taxable salary
        salary_after_exemptions = gross_salary.subtract(total_exemptions)
        taxable_salary = salary_after_exemptions.subtract(standard_deduction)
        
        return taxable_salary if taxable_salary.is_positive() else Money.zero()
    
    def get_salary_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed salary breakdown.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Comprehensive salary breakdown with amounts and exemptions
        """
        return {
            "gross_salary_components": {
                "basic_salary": self.basic_salary.to_float(),
                "dearness_allowance": self.dearness_allowance.to_float(),
                "bonus": self.bonus.to_float(),
                "commission": self.commission.to_float(),
                "hra_received": self.hra_received.to_float(),
                "special_allowance": self.special_allowance.to_float(),
                "other_allowances": self.other_allowances.to_float(),
                "lta_received": self.lta_received.to_float(),
                "medical_allowance": self.medical_allowance.to_float(),
                "conveyance_allowance": self.conveyance_allowance.to_float(),
                "specific_allowances": self.specific_allowances.calculate_total_specific_allowances().to_float()
            },
            "gross_salary_total": self.calculate_gross_salary().to_float(),
            "exemptions": {
                "hra_exemption": self.calculate_hra_exemption(regime).to_float(),
                "lta_exemption": self.calculate_lta_exemption(regime).to_float(),
                "medical_exemption": self.calculate_medical_allowance_exemption(regime).to_float(),
                "conveyance_exemption": self.calculate_conveyance_exemption(regime).to_float(),
                "specific_allowances_exemption": self.specific_allowances.calculate_total_exemptions(regime).to_float(),
                "standard_deduction": regime.get_standard_deduction().to_float()
            },
            "total_exemptions": self.calculate_total_exemptions(regime).add(regime.get_standard_deduction()).to_float(),
            "taxable_salary": self.calculate_taxable_salary(regime).to_float(),
            "regime_used": regime.regime_type.value
        }
    
    def validate_hra_details(self) -> Dict[str, str]:
        """
        Validate HRA details and return any warnings.
        
        Returns:
            Dict: Validation warnings if any
        """
        warnings = {}
        
        if self.hra_received.is_positive() and self.actual_rent_paid.is_zero():
            warnings["rent_validation"] = "HRA received but no rent paid - HRA exemption may not be available"
        
        if self.actual_rent_paid.is_greater_than(self.hra_received):
            warnings["rent_vs_hra"] = "Rent paid is more than HRA received - consider claiming full HRA"
        
        basic_plus_da = self.basic_salary.add(self.dearness_allowance)
        if self.hra_received.is_greater_than(basic_plus_da.percentage(Decimal('50'))):
            warnings["hra_limit"] = "HRA received exceeds 50% of basic salary - exemption may be limited"
        
        return warnings 