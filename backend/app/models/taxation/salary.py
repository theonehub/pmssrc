"""
Salary components model for taxation calculations.

Represents all salary components as per Indian Income Tax Act.
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

from models.taxation.perquisites import Perquisites

logger = logging.getLogger(__name__)


@dataclass
class SalaryComponents:
    """
    Represents all salary components as per Indian Income Tax Act.
    Includes all allowances and perquisites.
    """
    basic: float = 0                                    # Basic Pay(Slab)
    dearness_allowance: float = 0                       # Dearness Allowance(Slab)
    hra_city: str = 'Others'                            # HRA_City_selected(Metadata)
    hra_percentage: float = 0                           # HRA_Percentage(Metadata)
    hra: float = 0                                       # HRA(Slab)
    actual_rent_paid: float = 0                          # Actual Rent Paid(Slab)
    special_allowance: float = 0                        # Special Allowance(Slab)
    bonus: float = 0                                    # Bonus(Slab)
    commission: float = 0                               # Commission(Slab)
    city_compensatory_allowance: float = 0              # City Compensatory Allowance(Slab)
    rural_allowance: float = 0                          # Rural Allowance(Slab)
    proctorship_allowance: float = 0                    # Proctorship Allowance(Slab)
    wardenship_allowance: float = 0                     # Wardenship Allowance(Slab)
    project_allowance: float = 0                        # Project Allowance(Slab)
    deputation_allowance: float = 0                     # Deputation Allowance(Slab)
    overtime_allowance: float = 0                       # Overtime Allowance(Slab)
    interim_relief: float = 0                           # Interim Relief(Slab)
    tiffin_allowance: float = 0                         # Tiffin Allowance(Slab)
    fixed_medical_allowance: float = 0                  # Fixed Medical Allowance(Slab)
    servant_allowance: float = 0                        # Servant Allowance(Slab)
    any_other_allowance: float = 0                      # Any Other Allowance(Slab)
    any_other_allowance_exemption: float = 0            # Any Other Allowance Exemption(Slab-Deduction)
    govt_employee_entertainment_allowance: float = 0    # Entertainment Allowance(Exempted)
    govt_employees_outside_india_allowance: float = 0   # Allowances to Government employees outside India(Exempted)
    supreme_high_court_judges_allowance: float = 0      # Allowance to High Court & Supreme Court Judges(Exempted)
    judge_compensatory_allowance: float = 0             # Compensatory Allowance received by a Judge(Exempted)
    section_10_14_special_allowances: float = 0         # Special Allowances exempt under Section 10(14)(Exempted)
    travel_on_tour_allowance: float = 0                 # Allowance granted to meet cost of travel on tour(Exempted)
    tour_daily_charge_allowance: float = 0              # Allowance granted to meet cost of daily charges incurred on tour(Exempted)
    conveyance_in_performace_of_duties: float = 0       # Allowance granted to meet expenditure incurred on conveyance in performace of duties(Exempted)
    helper_in_performace_of_duties: float = 0           # Allowance granted to meet expenditure incurred on helper in performace of duties(Exempted)      
    academic_research: float = 0                        # Allowance granted for encouraging the academic, research & training pursuits in educational & research institutions(Exempted)
    uniform_allowance: float = 0                        # Allowance granted for expenditure incurred on purchase or maintenance of uniform for wear during performace of duties(Exempted)

    #Other Allowances
    hills_high_altd_allowance: float = 0                # Compensatory Allowances for Hilly Area or High Altitute Allowance - Rs. 300 pm to Rs. 7,000 pm
    hills_high_altd_exemption_limit: float = 0       # Exemption limit for Hills & High Altitude Allowance
    border_remote_allowance: float = 0                  # Border & Remote Area Allowance - Rs. 200 pm to Rs. 3,000 pm
    border_remote_exemption_limit: float = 0            # Exemption limit for Border & Remote Area Allowance
    transport_employee_allowance: float = 0             # Allowances allowed to Transport Employees - Rs. 10,000 or 70% of Such Allowance, Whichever is less
    children_education_allowance: float = 0             # Children Education Allowance - Rs. 100 pm per child upto maximum 2 children
    children_education_count: int = 0                             # Number of children for children education allowance
    children_education_months: int = 0                   # Number of months for children education allowance
    hostel_allowance: float = 0                         # Hostel Expenditure Allowance - Rs. 300 pm per child upto maximum 2 children
    hostel_count: int = 0                             # Number of children for children education allowance
    hostel_months: int = 0  
    transport_allowance: float = 0   
    transport_months: int = 0                   # Transport Allowance -Rs. 3,200 per month for blind or deaf and dumb
    underground_mines_allowance: float = 0              # Underground allowance to employee working in underground mines - Rs. 800 pm
    underground_mines_months: int = 0                   # Number of months for underground mines allowance

    perquisites: Optional[Perquisites] = None

    def calculate_hra_exemption(self, regime: str = 'old') -> float:
        """Calculate HRA exemption as per Income Tax rules."""
        if regime == 'new':
            return 0
            
        # Basic components for HRA calculation
        basic_plus_da = self.basic + self.dearness_allowance
        logger.info(f"Basic + DA: {basic_plus_da}")
        
        # HRA exemption calculation is the minimum of:
        # 1. Actual HRA received
        # 2. 50% of salary (for metro cities) or 40% (for non-metro)
        # 3. Rent paid minus 10% of salary
        
        logger.info(f"Rent paid: {self.actual_rent_paid}")
        # Determine percentage based on city
        if self.hra_city in ['Delhi', 'Mumbai', 'Kolkata', 'Chennai']:
            percent_of_salary = 0.5 * basic_plus_da
        else:
            percent_of_salary = 0.4 * basic_plus_da

        logger.info(f"Percent of salary: {percent_of_salary}")  
        
        rent_minus_salary = max(0, self.actual_rent_paid - (0.1 * basic_plus_da))
        logger.info(f"Rent minus salary: {rent_minus_salary}")
        
        # Calculate exemption
        hra_exemption = min(self.hra, percent_of_salary, rent_minus_salary)
        logger.info(f"[Computed]HRA exemption calculated: {hra_exemption}")
        
        return hra_exemption

    def calculate_exemptions(self, regime: str = 'old') -> float:
        """Calculate all exemptions applicable to salary components."""
        if regime == 'new':
            return 0
            
        # HRA exemption
        hra_exemption = self.calculate_hra_exemption(regime)
        
        
        # Section 10 and other exemptions
        section10_exemptions = (
            self.govt_employees_outside_india_allowance +
            self.supreme_high_court_judges_allowance +
            self.judge_compensatory_allowance +
            self.section_10_14_special_allowances +
            self.travel_on_tour_allowance +
            self.tour_daily_charge_allowance +
            self.conveyance_in_performace_of_duties +
            self.helper_in_performace_of_duties +
            self.academic_research +
            self.uniform_allowance
        )
        logger.info(f"govt_employees_outside_india_allowance: {self.govt_employees_outside_india_allowance}")
        logger.info(f"supreme_high_court_judges_allowance: {self.supreme_high_court_judges_allowance}")
        logger.info(f"judge_compensatory_allowance: {self.judge_compensatory_allowance}")
        logger.info(f"section_10_14_special_allowances: {self.section_10_14_special_allowances}")
        logger.info(f"travel_on_tour_allowance: {self.travel_on_tour_allowance}")
        logger.info(f"tour_daily_charge_allowance: {self.tour_daily_charge_allowance}")
        logger.info(f"conveyance_in_performace_of_duties: {self.conveyance_in_performace_of_duties}")
        logger.info(f"helper_in_performace_of_duties: {self.helper_in_performace_of_duties}")
        logger.info(f"[Computed] Section 10 and other exemptions: {section10_exemptions}")
        
        # Other allowance exemptions
        other_allowances_exemption = (
            min(self.hills_high_altd_allowance, self.hills_high_altd_exemption_limit) +   #TODO: take exemption limit as input
            min(self.border_remote_allowance, self.border_remote_exemption_limit) +   #TODO: take exemption limit as input
            min(self.transport_employee_allowance, min(10000, 0.7 * self.transport_employee_allowance)) +
            min(self.children_education_allowance, (self.children_education_count*100*self.children_education_months)) +  # 100*2*12 #TODO: take number of kids and months limit as input
            min(self.hostel_allowance, (self.hostel_count*300*self.hostel_months)) +  # 300*2*12 #TODO: take months limit as input
            min(self.transport_allowance, (self.transport_months*3200)) +  # 3200*12 #TODO: take months limit as input
            min(self.underground_mines_allowance, (self.underground_mines_months*800)) # 800*12 #TODO: take months limit as input
        )

        if self.govt_employee_entertainment_allowance > 0 and self.is_govt_employee:
            other_allowances_exemption += min(self.govt_employee_entertainment_allowance, self.basic * 0.2, 5000)

        logger.info(f"hills_high_altd_allowance: {self.hills_high_altd_allowance}, {min(self.hills_high_altd_allowance, self.hills_high_altd_exemption_limit)}")
        logger.info(f"border_remote_allowance: {self.border_remote_allowance}, {min(self.border_remote_allowance, self.border_remote_exemption_limit)}")
        logger.info(f"transport_employee_allowance: {self.transport_employee_allowance}, {min(self.transport_employee_allowance, min(10000, 0.7 * self.transport_employee_allowance))}")
        logger.info(f"children_education_allowance: {self.children_education_allowance}, {min(self.children_education_allowance, (self.children_education_count*100*self.children_education_months))}")
        logger.info(f"hostel_allowance: {self.hostel_allowance}, {min(self.hostel_allowance, (self.hostel_count*300*self.hostel_months))}")
        logger.info(f"transport_allowance: {self.transport_allowance}, {min(self.transport_allowance, (self.transport_months*3200))}")
        logger.info(f"underground_mines_allowance: {self.underground_mines_allowance}, {min(self.underground_mines_allowance, (self.underground_mines_months*800))}")
        logger.info(f"govt_employee_entertainment_allowance: {self.govt_employee_entertainment_allowance}, {min(self.govt_employee_entertainment_allowance, self.basic * 0.2, 5000)}")
        logger.info(f"Other allowance exemptions: {other_allowances_exemption}")

        logger.info(f"Total salary exemptions - HRA: {hra_exemption}, Section 10: {section10_exemptions}, Other: {other_allowances_exemption}")
        
        return hra_exemption + section10_exemptions + other_allowances_exemption + self.any_other_allowance_exemption

    def total(self, regime: str = 'old') -> float:
        """Calculate total taxable salary components."""
        # Sum all salary components
        gross_salary = (
            self.basic +
            self.dearness_allowance +
            self.hra +
            self.special_allowance +
            self.bonus +
            self.commission +
            self.city_compensatory_allowance +
            self.rural_allowance +
            self.proctorship_allowance +
            self.wardenship_allowance +
            self.project_allowance +
            self.deputation_allowance +
            self.overtime_allowance +
            self.interim_relief +
            self.tiffin_allowance +
            self.fixed_medical_allowance +
            self.servant_allowance +
            self.any_other_allowance +
            self.hills_high_altd_allowance +
            self.border_remote_allowance +
            self.transport_employee_allowance +
            self.children_education_allowance +
            self.hostel_allowance +
            self.transport_allowance +
            self.underground_mines_allowance +
            self.govt_employee_entertainment_allowance
        )
        
        # Calculate exemptions
        exemptions = self.calculate_exemptions(regime)
        
        # Add perquisites value if exists
        perquisites_value = 0
        if self.perquisites:
            perquisites_value = self.perquisites.total(gross_salary=gross_salary, regime=regime)
            logger.info(f"Perquisites total: {perquisites_value}")
        
        # Calculate taxable salary
        taxable_salary = gross_salary - exemptions + perquisites_value
        logger.info(f"Salary calculation - Gross: {gross_salary}, Exemptions: {exemptions}, Perquisites: {perquisites_value}, Taxable: {taxable_salary}")
        
        return taxable_salary
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "basic": cls.basic,
            "dearness_allowance": cls.dearness_allowance,
            "hra_city": cls.hra_city,
            "hra_percentage": cls.hra_percentage,
            "hra": cls.hra,
            "actual_rent_paid": cls.actual_rent_paid,
            "special_allowance": cls.special_allowance,
            "bonus": cls.bonus,
            "commission": cls.commission,
            "city_compensatory_allowance": cls.city_compensatory_allowance,
            "rural_allowance": cls.rural_allowance,
            "proctorship_allowance": cls.proctorship_allowance,
            "wardenship_allowance": cls.wardenship_allowance,
            "project_allowance": cls.project_allowance,
            "deputation_allowance": cls.deputation_allowance,
            "overtime_allowance": cls.overtime_allowance,
            "any_other_allowance": cls.any_other_allowance,
            "any_other_allowance_exemption": cls.any_other_allowance_exemption,
            "interim_relief": cls.interim_relief,
            "tiffin_allowance": cls.tiffin_allowance,
            "fixed_medical_allowance": cls.fixed_medical_allowance,
            "servant_allowance": cls.servant_allowance,
            "govt_employees_outside_india_allowance": cls.govt_employees_outside_india_allowance,
            "supreme_high_court_judges_allowance": cls.supreme_high_court_judges_allowance,
            "judge_compensatory_allowance": cls.judge_compensatory_allowance,
            "section_10_14_special_allowances": cls.section_10_14_special_allowances,
            "travel_on_tour_allowance": cls.travel_on_tour_allowance,
            "tour_daily_charge_allowance": cls.tour_daily_charge_allowance,
            "conveyance_in_performace_of_duties": cls.conveyance_in_performace_of_duties,
            "helper_in_performace_of_duties": cls.helper_in_performace_of_duties,
            "academic_research": cls.academic_research,
            "uniform_allowance": cls.uniform_allowance,
            "hills_high_altd_allowance": cls.hills_high_altd_allowance,
            "hills_high_altd_exemption_limit": cls.hills_high_altd_exemption_limit,
            "border_remote_allowance": cls.border_remote_allowance,
            "border_remote_exemption_limit": cls.border_remote_exemption_limit,
            "transport_employee_allowance": cls.transport_employee_allowance,
            "transport_months": cls.transport_months,
            "children_education_allowance": cls.children_education_allowance,
            "children_education_count": cls.children_education_count,
            "children_education_months": cls.children_education_months,
            "hostel_allowance": cls.hostel_allowance,
            "hostel_count": cls.hostel_count,
            "hostel_months": cls.hostel_months,
            "transport_allowance": cls.transport_allowance,
            "transport_months": cls.transport_months,
            "underground_mines_allowance": cls.underground_mines_allowance,
            "govt_employee_entertainment_allowance": cls.govt_employee_entertainment_allowance,
            "perquisites": cls.perquisites.to_dict() if cls.perquisites else None
        } 