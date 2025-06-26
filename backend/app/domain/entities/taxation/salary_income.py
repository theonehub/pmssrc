"""
Salary Income Entity
Domain entity for handling salary income components and calculations
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


@dataclass
class SpecificAllowances:
    """Specific allowances with their own exemption rules."""
    
    # Hills/High Altitude Allowances
    hills_allowance: Money = Money.zero()           #considered for doc
    hills_exemption_limit: Money = Money.zero()  # Varies by employee
    
    # Border/Remote Area Allowance
    border_allowance: Money = Money.zero()           #considered for doc
    border_exemption_limit: Money = Money.zero()  # Varies by employee
    
    # Transport Employee Allowance
    transport_employee_allowance: Money = Money.zero()       #considered for doc
    
    # Children Allowances
    children_education_allowance: Money = Money.zero()       #considered for doc
    children_count: int = 0
    children_education_months: int = 12

    hostel_allowance: Money = Money.zero()                   #considered for doc
    hostel_count: int = 0
    hostel_months: int = 12
    
    # Disabled Transport Allowance
    disabled_transport_allowance: Money = Money.zero()       #considered for doc
    transport_months: int = 12
    is_disabled: bool = False
    
    # Underground Mines Allowance
    underground_mines_allowance: Money = Money.zero()        #considered for doc
    mine_work_months: int = 0
    
    # Government Employee Entertainment
    government_entertainment_allowance: Money = Money.zero()    #considered for doc
    
    # Additional allowances from old project
    city_compensatory_allowance: Money = Money.zero()           #considered for doc
    rural_allowance: Money = Money.zero()                       #considered for doc
    proctorship_allowance: Money = Money.zero()                 #considered for doc
    wardenship_allowance: Money = Money.zero()                  #considered for doc
    project_allowance: Money = Money.zero()                     #considered for doc
    deputation_allowance: Money = Money.zero()                  #considered for doc
    overtime_allowance: Money = Money.zero()                    #considered for doc
    interim_relief: Money = Money.zero()                        #considered for doc
    tiffin_allowance: Money = Money.zero()                      #considered for doc
    fixed_medical_allowance: Money = Money.zero()               #considered for doc
    servant_allowance: Money = Money.zero()                     #considered for doc


    any_other_allowance: Money = Money.zero()                   #considered for doc
    any_other_allowance_exemption: Money = Money.zero()
    
    # Section 10 exempted allowances
    govt_employees_outside_india_allowance: Money = Money.zero()  #considered for doc
    supreme_high_court_judges_allowance: Money = Money.zero()     #considered for doc
    judge_compensatory_allowance: Money = Money.zero()            #considered for doc
    section_10_14_special_allowances: Money = Money.zero()        #considered for doc
    travel_on_tour_allowance: Money = Money.zero()                #considered for doc
    tour_daily_charge_allowance: Money = Money.zero()             #considered for doc
    conveyance_in_performace_of_duties: Money = Money.zero()       #considered for doc
    helper_in_performace_of_duties: Money = Money.zero()           #considered for doc
    academic_research: Money = Money.zero()                        #considered for doc
    uniform_allowance: Money = Money.zero()                        #considered for doc
    

    #########################################################
    # Calculate exemptions for specific allowances
    #########################################################
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
    
    def calculate_government_entertainment_exemption(self, regime: TaxRegime, basic_salary: Money, is_government_employee: bool) -> Money:
        """Calculate government entertainment allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if not is_government_employee:
            return Money.zero()
        
        # Minimum of (Allowance, 20% of Basic, Rs. 5,000)
        #TODO: Need to check if basic salary is only basic salary or basic salary + dearness allowance
        limit_1 = basic_salary.percentage(20)
        limit_2 = Money.from_int(5000)
        
        return self.government_entertainment_allowance.min(limit_1).min(limit_2)
    
    def calculate_section_10_exemptions(self, regime: TaxRegime, is_government_employee: bool) -> Money:
        """Calculate Section 10 exempted allowances."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        exemptions = Money.zero()

        if is_government_employee:
            exemptions = exemptions.add(self.govt_employees_outside_india_allowance)
            exemptions = exemptions.add(self.supreme_high_court_judges_allowance)
            exemptions = exemptions.add(self.judge_compensatory_allowance)
            exemptions = exemptions.add(self.section_10_14_special_allowances)

        exemptions = exemptions.add(self.travel_on_tour_allowance)
        exemptions = exemptions.add(self.tour_daily_charge_allowance)
        exemptions = exemptions.add(self.conveyance_in_performace_of_duties)
        exemptions = exemptions.add(self.helper_in_performace_of_duties)
        exemptions = exemptions.add(self.academic_research)
        exemptions = exemptions.add(self.uniform_allowance)
        
        # Section 10 allowances are fully exempt
        return exemptions
    
    def calculate_any_other_allowance_exemption(self, regime: TaxRegime) -> Money:
        """Calculate any other allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        return self.any_other_allowance_exemption
    
    #########################################################
    # Calculate total specific allowances received
    #########################################################
    
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
    
    def calculate_total_specific_allowances_exemptions(self, regime: TaxRegime, basic_salary: Money, is_government_employee: bool) -> Money:
        """Calculate total exemptions for specific allowances."""
        total = Money.zero()
        total = total.add(self.calculate_hills_exemption(regime))
        total = total.add(self.calculate_border_exemption(regime))
        total = total.add(self.calculate_transport_employee_exemption(regime))
        total = total.add(self.calculate_children_education_exemption(regime))
        total = total.add(self.calculate_hostel_exemption(regime))
        total = total.add(self.calculate_disabled_transport_exemption(regime))
        total = total.add(self.calculate_underground_mines_exemption(regime))
        total = total.add(self.calculate_government_entertainment_exemption(regime, basic_salary, is_government_employee))
        total = total.add(self.calculate_section_10_exemptions(regime, is_government_employee))
        total = total.add(self.calculate_any_other_allowance_exemption(regime))
        return total


@dataclass
class SalaryIncome:
    """
    Enhanced salary income entity with all salary components and exemption calculations.
    
    Handles comprehensive salary components including allowances and exemptions.
    Note: HRA exemption is now handled in the deductions module.
    """
    # Core salary components
    effective_from: datetime
    effective_till: datetime
    basic_salary: Money
    dearness_allowance: Money
    hra_provided: Money
    special_allowance: Money
    
    # Optional components with defaults
    bonus: Money = Money.zero()
    commission: Money = Money.zero()
    arrears: Money = Money.zero()

    # Specific allowances with exemption rules
    specific_allowances: SpecificAllowances = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.specific_allowances is None:
            self.specific_allowances = SpecificAllowances()
        # Remove automatic setting of effective_from - it must be provided by user
        # if self.effective_from is None:
        #     self.effective_from = datetime.now()
    
    def calculate_gross_salary(self) -> Money:
        """
        Calculate gross salary (all components).
        
        Returns:
            Money: Total gross salary
        """
        gross = (self.basic_salary                  #considered for doc 
                .add(self.dearness_allowance)       #considered for doc
                .add(self.bonus)                    #considered for doc
                .add(self.commission)               #considered for doc
                .add(self.hra_provided)             #considered for doc
                .add(self.special_allowance)        
                .add(self.arrears))
        
        # Add specific allowances if available
        if self.specific_allowances:
            gross = gross.add(self.specific_allowances.calculate_total_specific_allowances())
        
        return gross
    
    def calculate_total_exemptions(self, regime: TaxRegime, is_government_employee: bool = False) -> Money:
        """
        Calculate total salary exemptions.
        Note: HRA exemption is now calculated in the deductions module.
        
        Args:
            regime: Tax regime
            is_government_employee: Whether the employee is a government employee
            
        Returns:
            Money: Total exemptions
        """
        total_exemptions = Money.zero()
        
        # Specific allowances exemptions
        if self.specific_allowances:
            total_exemptions = total_exemptions.add(self.specific_allowances.calculate_total_specific_allowances_exemptions(regime, self.basic_salary, is_government_employee))
        
        return total_exemptions
    
    def calculate_taxable_salary(self, regime: TaxRegime, is_government_employee: bool = False) -> Money:
        """
        Calculate taxable salary after exemptions and standard deduction.
        
        Args:
            regime: Tax regime
            is_government_employee: Whether the employee is a government employee
            
        Returns:
            Money: Taxable salary
        """
        gross_salary = self.calculate_gross_salary()
        
        # Apply salary exemptions
        total_exemptions = self.calculate_total_exemptions(regime, is_government_employee)
        
        # Apply standard deduction
        standard_deduction = regime.get_standard_deduction()
        
        # Calculate taxable salary
        salary_after_exemptions = gross_salary.subtract(total_exemptions)
        taxable_salary = salary_after_exemptions.subtract(standard_deduction)
        
        return taxable_salary if taxable_salary.is_positive() else Money.zero()
    
    def get_salary_breakdown(self, regime: TaxRegime, is_government_employee: bool = False) -> Dict[str, Any]:
        """
        Get detailed salary breakdown.
        
        Args:
            regime: Tax regime
            is_government_employee: Whether the employee is a government employee
            
        Returns:
            Dict: Comprehensive salary breakdown with amounts and exemptions
        """
        return {
            "gross_salary_components": {
                "basic_salary": self.basic_salary.to_float(),
                "dearness_allowance": self.dearness_allowance.to_float(),
                "bonus": self.bonus.to_float(),
                "commission": self.commission.to_float(),
                "hra_provided": self.hra_provided.to_float(),
                "special_allowance": self.special_allowance.to_float(),
                "arrears": self.arrears.to_float(),
                "specific_allowances": self.specific_allowances.calculate_total_specific_allowances().to_float() if self.specific_allowances else 0.0
            },
            "gross_salary_total": self.calculate_gross_salary().to_float(),
            "exemptions": {
                "specific_allowances_exemption": self.specific_allowances.calculate_total_specific_allowances_exemptions(regime, self.basic_salary, is_government_employee).to_float() if self.specific_allowances else 0.0,
                "standard_deduction": regime.get_standard_deduction().to_float(),
                "note": "HRA exemption is calculated in deductions module"
            },
            "total_exemptions": self.calculate_total_exemptions(regime, is_government_employee).add(regime.get_standard_deduction()).to_float(),
            "taxable_salary": self.calculate_taxable_salary(regime, is_government_employee).to_float(),
            "regime_used": regime.regime_type.value
        }
 