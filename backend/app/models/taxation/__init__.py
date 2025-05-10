"""
Taxation models for income tax calculations, declarations and processing.
"""

from models.taxation.income_sources import (
    IncomeFromOtherSources,
    IncomeFromHouseProperty,
    CapitalGains
)
from models.taxation.perquisites import Perquisites
from models.taxation.salary import SalaryComponents
from models.taxation.deductions import DeductionComponents
from models.taxation.taxation import Taxation

__all__ = [
    'IncomeFromOtherSources',
    'IncomeFromHouseProperty',
    'CapitalGains',
    'Perquisites',
    'SalaryComponents',
    'DeductionComponents',
    'Taxation'
] 