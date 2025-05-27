"""
Organization Data Transfer Objects (DTOs)
Handles data transfer for organization operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from domain.value_objects.organization_details import OrganizationType, OrganizationStatus


# ==================== REQUEST DTOs ====================

@dataclass
class CreateOrganizationRequestDTO:
    """DTO for creating a new organization"""
    
    # Basic Information
    name: str
    description: Optional[str] = None
    organization_type: str = OrganizationType.PRIVATE_LIMITED.value
    
    # Contact Information
    email: str
    phone: str
    website: Optional[str] = None
    fax: Optional[str] = None
    
    # Address Information
    street_address: str
    city: str
    state: str
    country: str
    pin_code: str
    landmark: Optional[str] = None
    
    # Tax Information
    pan_number: str
    gst_number: Optional[str] = None
    tan_number: Optional[str] = None
    cin_number: Optional[str] = None
    
    # Configuration
    employee_strength: int = 10
    hostname: Optional[str] = None
    
    # Audit
    created_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        # Basic validation
        if not self.name or not self.name.strip():
            errors.append("Organization name is required")
        
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
        
        # Validate organization type
        try:
            OrganizationType(self.organization_type)
        except ValueError:
            errors.append("Invalid organization type")
        
        return errors


@dataclass
class UpdateOrganizationRequestDTO:
    """DTO for updating organization information"""
    
    # Basic Information
    name: Optional[str] = None
    description: Optional[str] = None
    organization_type: Optional[str] = None
    
    # Contact Information
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    fax: Optional[str] = None
    
    # Address Information
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pin_code: Optional[str] = None
    landmark: Optional[str] = None
    
    # Tax Information
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    tan_number: Optional[str] = None
    cin_number: Optional[str] = None
    
    # Configuration
    employee_strength: Optional[int] = None
    hostname: Optional[str] = None
    logo_path: Optional[str] = None
    
    # Audit
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the update request data"""
        errors = []
        
        # Validate non-empty strings if provided
        if self.name is not None and not self.name.strip():
            errors.append("Organization name cannot be empty")
        
        if self.email is not None and not self.email.strip():
            errors.append("Email cannot be empty")
        
        if self.phone is not None and not self.phone.strip():
            errors.append("Phone cannot be empty")
        
        if self.employee_strength is not None and self.employee_strength <= 0:
            errors.append("Employee strength must be positive")
        
        # Validate organization type if provided
        if self.organization_type is not None:
            try:
                OrganizationType(self.organization_type)
            except ValueError:
                errors.append("Invalid organization type")
        
        return errors


@dataclass
class OrganizationStatusUpdateRequestDTO:
    """DTO for updating organization status"""
    
    action: str  # activate, deactivate, suspend
    reason: Optional[str] = None
    suspension_duration: Optional[int] = None  # Days for suspension
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the status update request"""
        errors = []
        
        valid_actions = ["activate", "deactivate", "suspend"]
        if self.action not in valid_actions:
            errors.append(f"Invalid action. Must be one of: {', '.join(valid_actions)}")
        
        if self.action in ["deactivate", "suspend"] and not self.reason:
            errors.append(f"Reason is required for {self.action} action")
        
        if self.action == "suspend" and self.suspension_duration is not None:
            if self.suspension_duration <= 0:
                errors.append("Suspension duration must be positive")
        
        return errors


@dataclass
class OrganizationSearchFiltersDTO:
    """DTO for organization search filters"""
    
    # Basic filters
    name: Optional[str] = None
    organization_type: Optional[str] = None
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
            "name", "organization_type", "status", "created_at", 
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


@dataclass
class OrganizationResponseDTO:
    """DTO for organization response"""
    
    # Identity
    organization_id: str
    
    # Basic Information
    name: str
    description: Optional[str] = None
    organization_type: str = None
    status: str = None
    
    # Contact and Location
    contact_info: Optional[ContactInformationResponseDTO] = None
    address: Optional[AddressResponseDTO] = None
    
    # Tax Information
    tax_info: Optional[TaxInformationResponseDTO] = None
    
    # Employee Management
    employee_strength: int = 0
    used_employee_strength: int = 0
    available_capacity: int = 0
    utilization_percentage: float = 0.0
    
    # System Configuration
    hostname: Optional[str] = None
    logo_path: Optional[str] = None
    
    # System Fields
    created_at: str = None
    updated_at: str = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Computed fields
    is_active: bool = False
    is_government: bool = False
    has_available_capacity: bool = False
    display_name: str = None


@dataclass
class OrganizationSummaryDTO:
    """DTO for organization summary (list view)"""
    
    organization_id: str
    name: str
    organization_type: str
    status: str
    city: Optional[str] = None
    state: Optional[str] = None
    employee_strength: int = 0
    used_employee_strength: int = 0
    utilization_percentage: float = 0.0
    created_at: str = None
    is_active: bool = False


@dataclass
class OrganizationListResponseDTO:
    """DTO for paginated organization list response"""
    
    organizations: List[OrganizationSummaryDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class OrganizationStatisticsDTO:
    """DTO for organization statistics"""
    
    total_organizations: int
    active_organizations: int
    inactive_organizations: int
    suspended_organizations: int
    
    # By type
    organizations_by_type: Dict[str, int]
    
    # By location
    organizations_by_state: Dict[str, int]
    organizations_by_country: Dict[str, int]
    
    # Capacity statistics
    total_employee_capacity: int
    total_used_capacity: int
    average_utilization: float
    
    # Growth statistics
    organizations_created_this_month: int
    organizations_created_this_year: int


@dataclass
class OrganizationAnalyticsDTO:
    """DTO for organization analytics"""
    
    # Capacity analysis
    organizations_at_capacity: int
    organizations_under_utilized: int
    organizations_over_utilized: int
    
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
class OrganizationHealthCheckDTO:
    """DTO for organization health check"""
    
    organization_id: str
    name: str
    status: str
    is_healthy: bool
    issues: List[str]
    recommendations: List[str]
    last_checked: str


@dataclass
class BulkOrganizationUpdateDTO:
    """DTO for bulk organization updates"""
    
    organization_ids: List[str]
    update_data: Dict[str, Any]
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate bulk update request"""
        errors = []
        
        if not self.organization_ids:
            errors.append("Organization IDs list cannot be empty")
        
        if not self.update_data:
            errors.append("Update data cannot be empty")
        
        return errors


@dataclass
class BulkOrganizationUpdateResultDTO:
    """DTO for bulk update results"""
    
    total_requested: int
    successful_updates: int
    failed_updates: int
    errors: List[Dict[str, str]]  # {organization_id: error_message}
    updated_organization_ids: List[str]


# ==================== EXCEPTION DTOs ====================

class OrganizationValidationError(Exception):
    """Exception for organization validation errors"""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class OrganizationBusinessRuleError(Exception):
    """Exception for organization business rule violations"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule


class OrganizationNotFoundError(Exception):
    """Exception for organization not found"""
    
    def __init__(self, organization_id: str):
        super().__init__(f"Organization not found: {organization_id}")
        self.organization_id = organization_id


class OrganizationConflictError(Exception):
    """Exception for organization conflicts (e.g., duplicate name)"""
    
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field 