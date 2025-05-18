"""
Redirector module to maintain backward compatibility with existing imports.
This file is deprecated and will be removed in future versions.
"""

import warnings

from models.taxation.income_sources import (
    IncomeFromOtherSources,
    IncomeFromHouseProperty,
    CapitalGains,
    LeaveEncashment,
    VoluntaryRetirement
)
from models.taxation.perquisites import Perquisites
from models.taxation.salary import SalaryComponents
from models.taxation.deductions import DeductionComponents
from models.taxation.taxation import Taxation
from models.taxation.constants import (
    section_80g_100_wo_ql_heads,
    section_80g_50_wo_ql_heads,
    section_80g_100_ql_heads,
    section_80g_50_ql_heads
)

# Show deprecation warning
warnings.warn(
    "Direct import from 'models.taxation' is deprecated. "
    "Use 'models.taxation.income_sources', 'models.taxation.perquisites', etc. instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'IncomeFromOtherSources',
    'IncomeFromHouseProperty',
    'CapitalGains',
    'LeaveEncashment',
    'VoluntaryRetirement',
    'Perquisites',
    'SalaryComponents',
    'DeductionComponents',
    'Taxation',
    'section_80g_100_wo_ql_heads',
    'section_80g_50_wo_ql_heads',
    'section_80g_100_ql_heads',
    'section_80g_50_ql_heads'
]
        