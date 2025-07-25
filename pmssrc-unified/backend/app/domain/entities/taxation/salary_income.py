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

from app.utils.logger import get_detailed_logger, get_simple_logger
from app.utils.table_logger import log_taxation_breakdown

d_logger = get_detailed_logger()
s_logger = get_simple_logger()


@dataclass
class SpecificAllowances:
    """Specific allowances with their own exemption rules."""
    
    # Hills/High Altitude Allowances
    monthly_hills_allowance: Money = Money.zero()           #considered for doc
    monthly_hills_exemption_limit: Money = Money.zero()  # Varies by employee
    
    # Border/Remote Area Allowance
    monthly_border_allowance: Money = Money.zero()           #considered for doc
    monthly_border_exemption_limit: Money = Money.zero()  # Varies by employee
    
    # Transport Employee Allowance
    transport_employee_allowance: Money = Money.zero()       #considered for doc
    
    # Children Allowances
    children_education_allowance: Money = Money.zero()       #considered for doc
    children_education_count: int = 0

    hostel_allowance: Money = Money.zero()                   #considered for doc
    children_hostel_count: int = 0
    
    # Disabled Transport Allowance
    disabled_transport_allowance: Money = Money.zero()       #considered for doc
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
    
    # Additional fields for backward compatibility and code access
    hills_allowance: Money = Money.zero()                          # Alias for monthly_hills_allowance
    border_allowance: Money = Money.zero()                         # Alias for monthly_border_allowance
    hills_exemption_limit: Money = Money.zero()                    # Alias for monthly_hills_exemption_limit
    border_exemption_limit: Money = Money.zero()                   # Alias for monthly_border_exemption_limit
    children_count: int = 0                                        # Alias for children_education_count
    
    def __post_init__(self):
        """Sync alias fields with their corresponding monthly fields."""
        # Sync alias fields
        self.hills_allowance = self.monthly_hills_allowance
        self.border_allowance = self.monthly_border_allowance
        self.hills_exemption_limit = self.monthly_hills_exemption_limit
        self.border_exemption_limit = self.monthly_border_exemption_limit
        self.children_count = self.children_education_count
    
    #########################################################
    # Calculate exemptions for specific allowances
    #########################################################
    def calculate_hills_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate hills allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if summary_data:
            summary_data['monthly_hills_allowance'] = self.monthly_hills_allowance
            summary_data['monthly_hills_exemption_limit'] = self.monthly_hills_exemption_limit
        return self.monthly_hills_allowance.min(self.monthly_hills_exemption_limit)
    
    def calculate_border_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate border area allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if summary_data:
            summary_data['monthly_border_allowance'] = self.monthly_border_allowance
            summary_data['monthly_border_exemption_limit'] = self.monthly_border_exemption_limit
        return self.monthly_border_allowance.min(self.monthly_border_exemption_limit)
    
    def calculate_transport_employee_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate transport employee allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        limit_1 = Money.from_int(10000)
        limit_2 = self.transport_employee_allowance.percentage(70)
        exemption_limit = limit_1.min(limit_2)
        if summary_data:
            summary_data['transport_employee_allowance'] = self.transport_employee_allowance
            summary_data['transport_employee_exemption_limit min(10000, 70% of transport_employee_allowance)'] = exemption_limit
        return self.transport_employee_allowance.min(exemption_limit)
    
    def calculate_children_education_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate children education allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Rs. 100 per month per child (max 2 children)
        max_children = min(self.children_education_count, 2)
        exemption_limit = Money.from_int(100 * max_children)
        if summary_data:
            summary_data['children_education_allowance'] = self.children_education_allowance
            summary_data['children_education_exemption_limit max(100 * max_children, children_education_allowance)'] = exemption_limit
        return self.children_education_allowance.min(exemption_limit)
    
    def calculate_hostel_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate hostel allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Rs. 300 per month per child (max 2 children)
        max_children = min(self.children_hostel_count, 2)
        exemption_limit = Money.from_int(300 * max_children)
        if summary_data:
            summary_data['hostel_allowance'] = self.hostel_allowance
            summary_data['hostel_exemption_limit max(300 * max_children, hostel_allowance)'] = exemption_limit
        return self.hostel_allowance.min(exemption_limit)
    
    def calculate_disabled_transport_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate disabled transport allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if not self.is_disabled:
            return Money.zero()
        
        # Rs. 3,200 per month
        exemption_limit = Money.from_int(3200)
        if summary_data:
            summary_data['disabled_transport_allowance'] = self.disabled_transport_allowance
            summary_data['disabled_transport_exemption_limit 3200'] = exemption_limit
        return self.disabled_transport_allowance.min(exemption_limit)
    
    def calculate_underground_mines_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate underground mines allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Rs. 800 per month
        exemption_limit = Money.from_int(800)
        if summary_data:
            summary_data['underground_mines_allowance'] = self.underground_mines_allowance
            summary_data['underground_mines_exemption_limit 800'] = exemption_limit
        return self.underground_mines_allowance.min(exemption_limit)
    
    def calculate_government_entertainment_exemption(self, regime: TaxRegime, basic_salary: Money, is_government_employee: bool, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate government entertainment allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if not is_government_employee:
            return Money.zero()
        
        # Minimum of (Allowance, 20% of Basic, Rs. 5,000)
        #TODO: Need to check if basic salary is only basic salary or basic salary + dearness allowance
        limit_1 = basic_salary.percentage(20)
        limit_2 = Money.from_int(5000)
        if summary_data:
            summary_data['government_entertainment_allowance'] = self.government_entertainment_allowance
            summary_data['government_entertainment_exemption_limit min(20% of basic_salary)'] = limit_1
            summary_data['government_entertainment_exemption_limit min(5000)'] = limit_2
        return self.government_entertainment_allowance.min(limit_1).min(limit_2)
    
    def calculate_section_10_exemptions(self, regime: TaxRegime, is_government_employee: bool, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate Section 10 exempted allowances."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        if summary_data:
            summary_data['calculate_section_10_exemptions'] = True
        exemptions = Money.zero()

        if is_government_employee:
            if summary_data:
                summary_data['govt_employees_outside_india_allowance'] = self.govt_employees_outside_india_allowance
                summary_data['supreme_high_court_judges_allowance'] = self.supreme_high_court_judges_allowance
                summary_data['judge_compensatory_allowance'] = self.judge_compensatory_allowance
                summary_data['section_10_14_special_allowances'] = self.section_10_14_special_allowances
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

        if summary_data:
            summary_data['travel_on_tour_allowance'] = self.travel_on_tour_allowance
            summary_data['tour_daily_charge_allowance'] = self.tour_daily_charge_allowance
            summary_data['conveyance_in_performace_of_duties'] = self.conveyance_in_performace_of_duties
            summary_data['helper_in_performace_of_duties'] = self.helper_in_performace_of_duties
            summary_data['academic_research'] = self.academic_research
            summary_data['uniform_allowance'] = self.uniform_allowance

        # Section 10 allowances are fully exempt
        return exemptions
    
    def calculate_any_other_allowance_exemption(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate any other allowance exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        if summary_data:
            summary_data['any_other_allowance_exemption'] = self.any_other_allowance_exemption
        return self.any_other_allowance_exemption
    
    #########################################################
    # Calculate total specific allowances received
    #########################################################
    
    def calculate_total_specific_allowances(self, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate total specific allowances received."""
        
        specific_allowances = (self.monthly_hills_allowance
                .add(self.monthly_border_allowance)
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
                .add(self.uniform_allowance)
        )

        if summary_data:
            summary_data['calculate_total_specific_allowances'] = 'start'
            summary_data['Monthly Hills Allowance'] = self.monthly_hills_allowance
            summary_data['Monthly Border Allowance'] = self.monthly_border_allowance
            summary_data['Transport Employee Allowance'] = self.transport_employee_allowance
            summary_data['Children Education Allowance'] = self.children_education_allowance
            summary_data['Hostel Allowance'] = self.hostel_allowance
            summary_data['Disabled Transport Allowance'] = self.disabled_transport_allowance
            summary_data['Underground Mines Allowance'] = self.underground_mines_allowance
            summary_data['Government Entertainment Allowance'] = self.government_entertainment_allowance
            summary_data['City Compensatory Allowance'] = self.city_compensatory_allowance
            summary_data['Rural Allowance'] = self.rural_allowance
            summary_data['Proctorship Allowance'] = self.proctorship_allowance
            summary_data['Wardenship Allowance'] = self.wardenship_allowance
            summary_data['Project Allowance'] = self.project_allowance
            summary_data['Deputation Allowance'] = self.deputation_allowance
            summary_data['Overtime Allowance'] = self.overtime_allowance
            summary_data['Interim Relief'] = self.interim_relief
            summary_data['Tiffin Allowance'] = self.tiffin_allowance
            summary_data['Fixed Medical Allowance'] = self.fixed_medical_allowance
            summary_data['Servant Allowance'] = self.servant_allowance
            summary_data['Any Other Allowance'] = self.any_other_allowance
            summary_data['Govt Employees Outside India Allowance'] = self.govt_employees_outside_india_allowance
            summary_data['Supreme High Court Judges Allowance'] = self.supreme_high_court_judges_allowance
            summary_data['Judge Compensatory Allowance'] = self.judge_compensatory_allowance
            summary_data['Section 10 14 Special Allowances'] = self.section_10_14_special_allowances
            summary_data['Travel On Tour Allowance'] = self.travel_on_tour_allowance
            summary_data['Tour Daily Charge Allowance'] = self.tour_daily_charge_allowance
            summary_data['Conveyance In Performace Of Duties'] = self.conveyance_in_performace_of_duties
            summary_data['Helper In Performace Of Duties'] = self.helper_in_performace_of_duties
            summary_data['Academic Research'] = self.academic_research
            summary_data['Uniform Allowance'] = self.uniform_allowance
            summary_data['Total Specific Allowances'] = specific_allowances

        return specific_allowances
    
    def calculate_total_specific_allowances_exemptions(self, regime: TaxRegime, basic_salary: Money, is_government_employee: bool, summary_data: Dict[str, Any] = None) -> Money:
        """Calculate total exemptions for specific allowances."""
        d_logger.info(f"Start")
        if summary_data:
            summary_data['calculate_total_specific_allowances_exemptions'] = 'start'
        # Calculate all exemptions first
        hills_exemption = self.calculate_hills_exemption(regime, summary_data)
        border_exemption = self.calculate_border_exemption(regime, summary_data)
        transport_exemption = self.calculate_transport_employee_exemption(regime, summary_data)
        children_edu_exemption = self.calculate_children_education_exemption(regime, summary_data)
        hostel_exemption = self.calculate_hostel_exemption(regime, summary_data)
        disabled_transport_exemption = self.calculate_disabled_transport_exemption(regime, summary_data)
        mines_exemption = self.calculate_underground_mines_exemption(regime, summary_data)
        govt_entertainment_exemption = self.calculate_government_entertainment_exemption(regime, basic_salary, is_government_employee, summary_data)
        section_10_exemptions = self.calculate_section_10_exemptions(regime, is_government_employee, summary_data)
        any_other_exemption = self.calculate_any_other_allowance_exemption(regime, summary_data)
        
        total = (hills_exemption
                .add(border_exemption)
                .add(transport_exemption)
                .add(children_edu_exemption)
                .add(hostel_exemption)
                .add(disabled_transport_exemption)
                .add(mines_exemption)
                .add(govt_entertainment_exemption)
                .add(section_10_exemptions)
                .add(any_other_exemption))
        
        if summary_data:
            summary_data['hills_exemption'] = hills_exemption
            summary_data['border_exemption'] = border_exemption
            summary_data['transport_exemption'] = transport_exemption
            summary_data['children_edu_exemption'] = children_edu_exemption
            summary_data['hostel_exemption'] = hostel_exemption
            summary_data['disabled_transport_exemption'] = disabled_transport_exemption
            summary_data['mines_exemption'] = mines_exemption
            summary_data['govt_entertainment_exemption'] = govt_entertainment_exemption
            summary_data['section_10_exemptions'] = section_10_exemptions
            summary_data['any_other_exemption'] = any_other_exemption
            summary_data['total_exemptions'] = total
        
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

    epf_employee: Money = Money.zero()
    vps_employee: Money = Money.zero()

    epf_employer: Money = Money.zero()

    eps_employee: Money = Money.zero()
    eps_employer: Money = Money.zero()

    esi_contribution: Money = Money.zero()

    # Optional components with defaults
    commission: Money = Money.zero()

    # Specific allowances with exemption rules
    specific_allowances: SpecificAllowances = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.specific_allowances is None:
            self.specific_allowances = SpecificAllowances()

    
    def calculate_gross_salary(self, summary_data: Dict[str, Any] = None) -> Money:
        """
        Calculate gross salary (all components).
        
        Returns:
            Money: Total gross salary
        """
        specific_allowances = Money.zero()
        if self.specific_allowances:
            specific_allowances = self.specific_allowances.calculate_total_specific_allowances(summary_data)
        
        gross = (self.basic_salary                  #considered for doc 
                .add(self.dearness_allowance)       #considered for doc
                .add(self.commission)               #considered for doc
                .add(self.hra_provided)             #considered for doc
                .add(self.special_allowance)
                .add(specific_allowances))
            
        if summary_data:
            summary_data['calculate_gross_salary'] = 'start'
            summary_data['Basic Salary'] = self.basic_salary
            summary_data['Dearness Allowance'] = self.dearness_allowance
            summary_data['Commission'] = self.commission
            summary_data['HRA Provided'] = self.hra_provided
            summary_data['Special Allowance'] = self.special_allowance
            summary_data['Specific Allowances'] = specific_allowances
            summary_data['Total Gross Salary'] = gross

        return gross
    
    def get_pf_employee_contribution(self) -> Money:
        """
        Get the PF employee contribution.
        """
        return self.epf_employee + self.vps_employee

    def calculate_basic_plus_da(self) -> Money:
        """
        Calculate basic plus DA.
        """
        return self.basic_salary.add(self.dearness_allowance)
    
    def calculate_total_exemptions(self, regime: TaxRegime, is_government_employee: bool = False, summary_data: Dict[str, Any] = None) -> Money:
        """
        Calculate total salary exemptions.
        Note: HRA exemption is now calculated in the deductions module.
        
        Args:
            regime: Tax regime
            is_government_employee: Whether the employee is a government employee
            
        Returns:
            Money: Total exemptions
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        #TODO: Need to check if this is correct
        total_exemptions = Money.zero()

        # Specific allowances exemptions
        if self.specific_allowances:
            specific_allowance_exemptions = self.specific_allowances.calculate_total_specific_allowances_exemptions(regime, self.basic_salary, is_government_employee, summary_data)
            total_exemptions = total_exemptions.add(specific_allowance_exemptions)
        
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
                "commission": self.commission.to_float(),
                "hra_provided": self.hra_provided.to_float(),
                "special_allowance": self.special_allowance.to_float(),
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
 