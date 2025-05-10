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
        """Convert the object to a dictionary for JSON serialization."""
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