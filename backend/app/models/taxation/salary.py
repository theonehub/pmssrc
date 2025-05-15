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
    hra: float = 0                                      # HRA(Slab)
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
    border_remote_allowance: float = 0                  # Border & Remote Area Allowance - Rs. 200 pm to Rs. 3,000 pm
    transport_employee_allowance: float = 0             # Allowances allowed to Transport Employees - Rs. 10,000 or 70% of Such Allowance, Whichever is less
    children_education_allowance: float = 0             # Children Education Allowance - Rs. 100 pm per child upto maximum 2 children
    hostel_allowance: float = 0                         # Hostel Expenditure Allowance - Rs. 300 pm per child upto maximum 2 children
    transport_allowance: float = 0                      # Transport Allowance -Rs. 3,200 per month for blind or deaf and dumb
    underground_mines_allowance: float = 0              # Underground allowance to employee working in underground mines - Rs. 800 pm

    perquisites: Optional[Perquisites] = None

    def total(self) -> float:
        """Calculate total salary components."""
        return (
            self.basic +
            self.dearness_allowance 
        )
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "basic": cls.basic,
            "dearness_allowance": cls.dearness_allowance,
            "hra_city": cls.hra_city,
            "hra_percentage": cls.hra_percentage,
            "hra": cls.hra,
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
            "border_remote_allowance": cls.border_remote_allowance,
            "transport_employee_allowance": cls.transport_employee_allowance,
            "children_education_allowance": cls.children_education_allowance,
            "hostel_allowance": cls.hostel_allowance,
            "transport_allowance": cls.transport_allowance,
            "underground_mines_allowance": cls.underground_mines_allowance,
            "perquisites": cls.perquisites.to_dict() if cls.perquisites else None
        } 