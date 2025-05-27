"""
Taxation models for income tax calculations, declarations and processing.
"""

from domain.entities.taxation_models.income_sources import (
    IncomeFromOtherSources,
    IncomeFromHouseProperty,
    CapitalGains,
    LeaveEncashment,
    VoluntaryRetirement,
    Pension,
    Gratuity,
    RetrenchmentCompensation
)
from domain.entities.taxation_models.perquisites import Perquisites
from domain.entities.taxation_models.salary_components import SalaryComponents
from domain.entities.taxation_models.deductions import DeductionComponents
from models.taxation.legacy_taxation_model import Taxation

__all__ = [
    'IncomeFromOtherSources',
    'IncomeFromHouseProperty',
    'CapitalGains',
    'LeaveEncashment',
    'VoluntaryRetirement',
    'Gratuity',
    'RetrenchmentCompensation',
    'Perquisites',
    'SalaryComponents',
    'DeductionComponents',
    'Taxation'
] 