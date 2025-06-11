"""
Data Transfer Objects package
Comprehensive DTOs for taxation API covering all scenarios and income sources
"""

from .taxation_dto import (
    # Basic Value Objects
    MoneyDTO,
    EmploymentPeriodDTO,
    
    # Salary Income DTOs
    SalaryIncomeDTO,
    PeriodicSalaryDataDTO,
    PeriodicSalaryIncomeDTO,
    MidYearJoinerDTO,
    MidYearIncrementDTO,
    
    # Perquisites DTOs
    AccommodationPerquisiteDTO,
    CarPerquisiteDTO,
    MedicalReimbursementDTO,
    LTAPerquisiteDTO,
    InterestFreeConcessionalLoanDTO,
    ESOPPerquisiteDTO,
    UtilitiesPerquisiteDTO,
    FreeEducationPerquisiteDTO,
    MovableAssetUsageDTO,
    MovableAssetTransferDTO,
    LunchRefreshmentPerquisiteDTO,
    GiftVoucherPerquisiteDTO,
    MonetaryBenefitsPerquisiteDTO,
    ClubExpensesPerquisiteDTO,
    DomesticHelpPerquisiteDTO,
    PerquisitesDTO,
    
    # House Property Income DTOs
    HousePropertyIncomeDTO,
    MultipleHousePropertiesDTO,
    
    # Capital Gains DTOs
    CapitalGainsIncomeDTO,
    
    # Retirement Benefits DTOs
    LeaveEncashmentDTO,
    GratuityDTO,
    VRSDTO,
    PensionDTO,
    RetrenchmentCompensationDTO,
    RetirementBenefitsDTO,
    
    # Other Income DTOs
    InterestIncomeDTO,
    OtherIncomeDTO,
    
    # Monthly Payroll DTOs
    LWPDetailsDTO,
    MonthlyPayrollDTO,
    AnnualPayrollWithLWPDTO,
    
    # Deduction DTOs
    DeductionSection80CDTO,
    DeductionSection80DDTO,
    DeductionSection80GDTO,
    DeductionSection80EDTO,
    DeductionSection80TTADTO,
    OtherDeductionsDTO,
    TaxDeductionsDTO,
    
    # Enhanced Calculation Request DTOs
    EnhancedTaxCalculationRequestDTO,
    ScenarioComparisonRequestDTO,
    ComprehensiveTaxInputDTO,
    
    # Legacy Request DTOs
    CreateTaxationRecordRequest,
    UpdateSalaryIncomeRequest,
    UpdateDeductionsRequest,
    ChangeRegimeRequest,
    CalculateTaxRequest,
    CompareRegimesRequest,
    FinalizeRecordRequest,
    
    # Response DTOs
    SurchargeBreakdownDTO,
    TaxCalculationBreakdownDTO,
    PeriodicTaxCalculationResponseDTO,
    ScenarioComparisonResponseDTO,
    TaxOptimizationSuggestionDTO,
    TaxationRecordSummaryDTO,
    CreateTaxationRecordResponse,
    CalculateTaxResponse,
    DetailedTaxBreakdownResponse,
    RegimeComparisonResponse,
    TaxSavingSuggestionsResponse,
    TaxationRecordListResponse,
    UpdateResponse,
    ErrorResponse,
    
    # Query DTOs
    TaxationRecordQuery,
    TaxYearSummaryQuery,
    TaxAnalyticsQuery,
    TaxAnalyticsResponse,
    TaxYearSummaryResponse,
)

from .user_dto import (
    CreateUserRequestDTO,
    UpdateUserRequestDTO,
    ChangePasswordRequestDTO,
    LoginRequestDTO,
    UserResponseDTO,
    UserSummaryDTO,
    UserListResponseDTO,
    LoginResponseDTO,
    UserProfileDTO,
)

__all__ = [
    # Basic Value Objects
    "MoneyDTO",
    "EmploymentPeriodDTO",
    
    # Salary Income DTOs
    "SalaryIncomeDTO",
    "PeriodicSalaryDataDTO",
    "PeriodicSalaryIncomeDTO",
    "MidYearJoinerDTO",
    "MidYearIncrementDTO",
    
    # Perquisites DTOs
    "AccommodationPerquisiteDTO",
    "CarPerquisiteDTO",
    "MedicalReimbursementDTO",
    "LTAPerquisiteDTO",
    "InterestFreeConcessionalLoanDTO",
    "ESOPPerquisiteDTO",
    "UtilitiesPerquisiteDTO",
    "FreeEducationPerquisiteDTO",
    "MovableAssetUsageDTO",
    "MovableAssetTransferDTO",
    "LunchRefreshmentPerquisiteDTO",
    "GiftVoucherPerquisiteDTO",
    "MonetaryBenefitsPerquisiteDTO",
    "ClubExpensesPerquisiteDTO",
    "DomesticHelpPerquisiteDTO",
    "PerquisitesDTO",
    
    # House Property Income DTOs
    "HousePropertyIncomeDTO",
    "MultipleHousePropertiesDTO",
    
    # Capital Gains DTOs
    "CapitalGainsIncomeDTO",
    
    # Retirement Benefits DTOs
    "LeaveEncashmentDTO",
    "GratuityDTO",
    "VRSDTO",
    "PensionDTO",
    "RetrenchmentCompensationDTO",
    "RetirementBenefitsDTO",
    
    # Other Income DTOs
    "InterestIncomeDTO",
    "OtherIncomeDTO",
    
    # Monthly Payroll DTOs
    "LWPDetailsDTO",
    "MonthlyPayrollDTO",
    "AnnualPayrollWithLWPDTO",
    
    # Deduction DTOs
    "DeductionSection80CDTO",
    "DeductionSection80DDTO",
    "DeductionSection80GDTO",
    "DeductionSection80EDTO",
    "DeductionSection80TTADTO",
    "OtherDeductionsDTO",
    "TaxDeductionsDTO",
    
    # Enhanced Calculation Request DTOs
    "EnhancedTaxCalculationRequestDTO",
    "ScenarioComparisonRequestDTO",
    "ComprehensiveTaxInputDTO",
    
    # Legacy Request DTOs
    "CreateTaxationRecordRequest",
    "UpdateSalaryIncomeRequest",
    "UpdateDeductionsRequest",
    "ChangeRegimeRequest",
    "CalculateTaxRequest",
    "CompareRegimesRequest",
    "FinalizeRecordRequest",
    
    # Response DTOs
    "SurchargeBreakdownDTO",
    "TaxCalculationBreakdownDTO",
    "PeriodicTaxCalculationResponseDTO",
    "ScenarioComparisonResponseDTO",
    "TaxOptimizationSuggestionDTO",
    "TaxationRecordSummaryDTO",
    "CreateTaxationRecordResponse",
    "CalculateTaxResponse",
    "DetailedTaxBreakdownResponse",
    "RegimeComparisonResponse",
    "TaxSavingSuggestionsResponse",
    "TaxationRecordListResponse",
    "UpdateResponse",
    "ErrorResponse",
    
    # Query DTOs
    "TaxationRecordQuery",
    "TaxYearSummaryQuery",
    "TaxAnalyticsQuery",
    "TaxAnalyticsResponse",
    "TaxYearSummaryResponse",
    
    # User DTOs
    "CreateUserRequestDTO",
    "UpdateUserRequestDTO",
    "ChangePasswordRequestDTO",
    "LoginRequestDTO",
    "UserResponseDTO",
    "UserSummaryDTO",
    "UserListResponseDTO",
    "LoginResponseDTO",
    "UserProfileDTO",
] 