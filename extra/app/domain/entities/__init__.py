"""
Domain entities package
"""

from .user import User
from .salary_income import SalaryIncome, SpecificAllowances
from .periodic_salary_income import PeriodicSalaryIncome, PeriodicSalaryData
from .tax_deductions import (
    TaxDeductions, 
    DeductionSection80C, 
    DeductionSection80CCC,
    DeductionSection80CCD,
    DeductionSection80D,
    DeductionSection80DD,
    DeductionSection80DDB,
    DeductionSection80E,
    DeductionSection80EEB,
    DeductionSection80G,
    DeductionSection80GGC,
    DeductionSection80U,
    DeductionSection80TTA_TTB,
    DisabilityPercentage,
    RelationType
)
from .perquisites import (
    Perquisites,
    AccommodationPerquisite,
    CarPerquisite,
    AccommodationType,
    CityPopulation,
    CarUseType,
    AssetType,
    MedicalReimbursement,
    LTAPerquisite,
    InterestFreeConcessionalLoan,
    ESOPPerquisite,
    UtilitiesPerquisite,
    FreeEducationPerquisite,
    MovableAssetUsage,
    MovableAssetTransfer,
    LunchRefreshmentPerquisite,
    GiftVoucherPerquisite,
    MonetaryBenefitsPerquisite,
    ClubExpensesPerquisite,
    DomesticHelpPerquisite
)
from .house_property_income import (
    HousePropertyIncome,
    MultipleHouseProperties,
    PropertyType
)
from .capital_gains import (
    CapitalGainsIncome,
    CapitalGainsType
)
from .retirement_benefits import (
    RetirementBenefits,
    LeaveEncashment,
    Gratuity,
    VRS,
    Pension,
    RetrenchmentCompensation
)
from .other_income import OtherIncome, InterestIncome
from .taxation_record import TaxationRecord
from .monthly_payroll import (
    MonthlyPayroll,
    AnnualPayrollWithLWP,
    LWPDetails
)

__all__ = [
    "User",
    "SalaryIncome",
    "SpecificAllowances",
    "PeriodicSalaryIncome",
    "PeriodicSalaryData",
    "TaxDeductions",
    "DeductionSection80C",
    "DeductionSection80CCC",
    "DeductionSection80CCD", 
    "DeductionSection80D",
    "DeductionSection80DD",
    "DeductionSection80DDB",
    "DeductionSection80E",
    "DeductionSection80EEB",
    "DeductionSection80G",
    "DeductionSection80GGC",
    "DeductionSection80U",
    "DeductionSection80TTA_TTB",
    "DisabilityPercentage",
    "RelationType",
    "Perquisites",
    "AccommodationPerquisite",
    "CarPerquisite",
    "AccommodationType",
    "CityPopulation",
    "CarUseType",
    "AssetType",

    "MedicalReimbursement",
    "LTAPerquisite",
    "InterestFreeConcessionalLoan",
    "ESOPPerquisite",
    "UtilitiesPerquisite",
    "FreeEducationPerquisite",
    "MovableAssetUsage",
    "MovableAssetTransfer",
    "LunchRefreshmentPerquisite",
    "GiftVoucherPerquisite",
    "HousePropertyIncome",
    "MultipleHouseProperties",
    "PropertyType",
    "CapitalGainsIncome",
    "CapitalGainsType",
    "RetirementBenefits",
    "LeaveEncashment",
    "Gratuity",
    "VRS",
    "Pension",
    "RetrenchmentCompensation",
    "OtherIncome",
    "InterestIncome",
    "TaxationRecord",
    "MonthlyPayroll",
    "AnnualPayrollWithLWP",
    "LWPDetails"
] 