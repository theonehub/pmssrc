"""
Organisation Data Transfer Objects (DTOs)
Handles data transfer for organisation operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field, validator

from app.domain.value_objects.organisation_details import OrganisationType
from app.domain.value_objects.bank_details import BankDetails


# ==================== REQUEST DTOs ====================

@dataclass
class CreateOrganisationRequestDTO:
    """DTO for creating a new organisation"""
    
    # Required Basic Information
    name: str
    email: str
    phone: str
    
    # Required Address Information
    street_address: str
    city: str
    state: str
    country: str
    pin_code: str
    
    # Required Tax Information
    pan_number: str
    
    # Optional Basic Information
    description: Optional[str] = None
    organisation_type: str = OrganisationType.PRIVATE_LIMITED.value
    
    # Optional Contact Information
    website: Optional[str] = None
    fax: Optional[str] = None
    
    # Optional Address Information
    landmark: Optional[str] = None
    
    # Optional Tax Information
    gst_number: Optional[str] = None
    tan_number: Optional[str] = None
    cin_number: Optional[str] = None
    
    # Optional Configuration
    employee_strength: int = 10
    hostname: Optional[str] = None
    
    # Optional Audit
    created_by: Optional[str] = None
    
    # Optional Bank Details
    bank_details: Optional['BankDetailsRequestDTO'] = None
    
    esi_establishment_id: Optional[str] = None
    pf_establishment_id: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        # Basic validation
        if not self.name or not self.name.strip():
            errors.append("Organisation name is required")
        
        if not self.email or not self.email.strip():
            errors.append("Email is required")
        
        if not self.phone or not self.phone.strip():
            errors.append("Phone is required")
        
        if not self.street_address or not self.street_address.strip():
            errors.append("Street address is required")
        
        if not self.city or not self.city.strip():
            errors.append("City is required")
        
        if not self.state or not self.state.strip():
            errors.append("State is required")
        
        if not self.country or not self.country.strip():
            errors.append("Country is required")
        
        if not self.pin_code or not self.pin_code.strip():
            errors.append("Pin code is required")
        
        if not self.pan_number or not self.pan_number.strip():
            errors.append("PAN number is required")
        
        if self.employee_strength <= 0:
            errors.append("Employee strength must be positive")
        
        # Validate organisation type
        try:
            OrganisationType(self.organisation_type)
        except ValueError:
            errors.append("Invalid organisation type")
        
        if self.bank_details:
            errors.extend(self.bank_details.validate())
        
        return errors


class BankDetailsRequestDTO(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: str
    account_holder_name: str
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    account_type: Optional[str] = None

    def validate(self) -> list:
        errors = []
        if not self.bank_name:
            errors.append("Bank name is required")
        if not self.account_number:
            errors.append("Account number is required")
        if not self.ifsc_code:
            errors.append("IFSC code is required")
        if not self.account_holder_name:
            errors.append("Account holder name is required")
        return errors


class UpdateOrganisationRequestDTO(BaseModel):
    organisation_id: str
    name: str
    organisation_type: str
    description: Optional[str] = None
    employee_strength: Optional[int] = 0
    hostname: str
    updated_by: Optional[str] = None
    logo_path: Optional[str] = None
    
    # Contact Information
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    fax: Optional[str] = None
    
    # Address
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pin_code: Optional[str] = None
    landmark: Optional[str] = None
    
    # Tax Information
    pan_number: Optional[str] = None
    tan_number: Optional[str] = None
    gst_number: Optional[str] = None
    cin_number: Optional[str] = None
    
    # Bank Details
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    account_type: Optional[str] = None
    account_holder_name: Optional[str] = None
    bank_details: Optional[BankDetails] = None

    esi_establishment_id: Optional[str] = None
    pf_establishment_id: Optional[str] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True


@dataclass
class OrganisationSearchFiltersDTO:
    """DTO for organisation search filters"""
    
    # Basic filters
    name: Optional[str] = None
    organisation_type: Optional[str] = None
    status: Optional[str] = None
    
    # Location filters
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    
    # Capacity filters
    min_employee_strength: Optional[int] = None
    max_employee_strength: Optional[int] = None
    has_available_capacity: Optional[bool] = None
    
    # Tax filters
    is_gst_registered: Optional[bool] = None
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Pagination
    page: int = 1
    page_size: int = 20
    
    # Sorting
    sort_by: str = "name"
    sort_order: str = "asc"  # asc or desc
    
    def validate(self) -> List[str]:
        """Validate search filters"""
        errors = []
        
        if self.page <= 0:
            errors.append("Page must be positive")
        
        if self.page_size <= 0 or self.page_size > 100:
            errors.append("Page size must be between 1 and 100")
        
        if self.sort_order not in ["asc", "desc"]:
            errors.append("Sort order must be 'asc' or 'desc'")
        
        valid_sort_fields = [
            "name", "organisation_type", "status", "created_at", 
            "updated_at", "employee_strength", "city", "state"
        ]
        if self.sort_by not in valid_sort_fields:
            errors.append(f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}")
        
        return errors


# ==================== RESPONSE DTOs ====================

@dataclass
class ContactInformationResponseDTO:
    """DTO for contact information response"""
    
    email: str
    phone: str
    website: Optional[str] = None
    fax: Optional[str] = None
    formatted_phone: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class AddressResponseDTO:
    """DTO for address response"""
    
    street_address: str
    city: str
    state: str
    country: str
    pin_code: str
    landmark: Optional[str] = None
    full_address: Optional[str] = None
    short_address: Optional[str] = None
    is_indian_address: Optional[bool] = None


@dataclass
class TaxInformationResponseDTO:
    """DTO for tax information response"""
    
    pan_number: str
    gst_number: Optional[str] = None
    tan_number: Optional[str] = None
    cin_number: Optional[str] = None
    is_gst_registered: Optional[bool] = None
    gst_state_code: Optional[str] = None

    esi_establishment_id: Optional[str] = None
    pf_establishment_id: Optional[str] = None


@dataclass
class OrganisationResponseDTO:
    """DTO for organisation response"""
    
    # Required Identity
    organisation_id: str
    name: str
    
    # Optional Basic Information
    description: Optional[str] = None
    organisation_type: str = None
    status: str = None
    
    # Optional Contact and Location
    contact_info: Optional[ContactInformationResponseDTO] = None
    address: Optional[AddressResponseDTO] = None
    
    # Optional Tax Information
    tax_info: Optional[TaxInformationResponseDTO] = None
    
    # Employee Management with defaults
    employee_strength: int = 0
    used_employee_strength: int = 0
    available_capacity: int = 0
    utilization_percentage: float = 0.0
    
    # Optional System Configuration
    hostname: Optional[str] = None
    logo_path: Optional[str] = None
    
    # Optional System Fields
    created_at: str = None
    updated_at: str = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Optional Computed fields
    is_active: bool = False
    is_government: bool = False
    has_available_capacity: bool = False
    display_name: str = None

    # Optional Bank Details
    bank_details: Optional['BankDetailsResponseDTO'] = None


@dataclass
class OrganisationSummaryDTO:
    """DTO for organisation summary (list view)"""
    
    # Required fields
    organisation_id: str
    name: str
    organisation_type: str
    status: str
    
    # Optional fields
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    employee_strength: int = 0
    used_employee_strength: int = 0
    utilization_percentage: float = 0.0
    created_at: str = None
    is_active: bool = False


@dataclass
class OrganisationListResponseDTO:
    """DTO for paginated organisation list response"""
    
    organisations: List[OrganisationSummaryDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class OrganisationStatisticsDTO:
    """DTO for organisation statistics"""
    
    total_organisations: int
    active_organisations: int
    inactive_organisations: int
    suspended_organisations: int
    
    # By type
    organisations_by_type: Dict[str, int]
    
    # By location
    organisations_by_state: Dict[str, int]
    organisations_by_country: Dict[str, int]
    
    # Capacity statistics
    total_employee_capacity: int
    total_used_capacity: int
    average_utilization: float
    
    # Growth statistics
    organisations_created_this_month: int
    organisations_created_this_year: int


@dataclass
class OrganisationAnalyticsDTO:
    """DTO for organisation analytics"""
    
    # Capacity analysis
    organisations_at_capacity: int
    organisations_under_utilized: int
    organisations_over_utilized: int
    
    # Growth trends
    monthly_growth_rate: float
    yearly_growth_rate: float
    
    # Geographic distribution
    top_states_by_count: List[Dict[str, Any]]
    top_cities_by_count: List[Dict[str, Any]]
    
    # Type distribution
    type_distribution: Dict[str, float]  # Percentages
    
    # Status trends
    status_changes_this_month: Dict[str, int]


# ==================== UTILITY DTOs ====================

@dataclass
class OrganisationHealthCheckDTO:
    """DTO for organisation health check"""
    
    organisation_id: str
    name: str
    status: str
    is_healthy: bool
    issues: List[str]
    recommendations: List[str]
    last_checked: str


@dataclass
class BulkOrganisationUpdateDTO:
    """DTO for bulk organisation updates"""
    
    organisation_ids: List[str]
    update_data: Dict[str, Any]
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate bulk update request"""
        errors = []
        
        if not self.organisation_ids:
            errors.append("Organisation IDs list cannot be empty")
        
        if not self.update_data:
            errors.append("Update data cannot be empty")
        
        return errors


@dataclass
class BulkOrganisationUpdateResultDTO:
    """DTO for bulk update results"""
    
    total_requested: int
    successful_updates: int
    failed_updates: int
    errors: List[Dict[str, str]]  # {organisation_id: error_message}
    updated_organisation_ids: List[str]


# ==================== EXCEPTION DTOs ====================

class OrganisationValidationError(Exception):
    """Exception for organisation validation errors"""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class OrganisationBusinessRuleError(Exception):
    """Exception for organisation business rule violations"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule


class OrganisationNotFoundError(Exception):
    """Exception for organisation not found"""
    
    def __init__(self, organisation_id: str):
        super().__init__(f"Organisation not found: {organisation_id}")
        self.organisation_id = organisation_id


class OrganisationConflictError(Exception):
    """Exception for organisation conflicts (e.g., duplicate name)"""
    
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field 


# ==================== BANK DETAILS DTOs ====================

@dataclass
class BankDetailsResponseDTO:
    bank_name: str
    account_number: str
    ifsc_code: str
    account_holder_name: str
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    account_type: Optional[str] = None
    # Additional computed fields
    formatted_account_number: Optional[str] = None
    masked_account_number: Optional[str] = None
    bank_code: Optional[str] = None
    branch_code: Optional[str] = None
    is_valid_for_payment: bool = False 