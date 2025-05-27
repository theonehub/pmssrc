"""
User Data Transfer Objects (DTOs)
Handles data transfer for user operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from domain.value_objects.user_credentials import UserRole, UserStatus, Gender


# ==================== REQUEST DTOs ====================

@dataclass
class CreateUserRequestDTO:
    """DTO for creating a new user"""
    
    # Identity
    employee_id: str
    
    # Basic Information
    name: str
    email: str
    password: str
    
    # Personal Details (required)
    gender: str
    date_of_birth: str  # ISO format
    mobile: str
    
    # Role (with default)
    role: str = UserRole.USER.value
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    # Employment Information
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[str] = None
    date_of_joining: Optional[str] = None  # ISO format
    
    # Documents
    photo_path: Optional[str] = None
    pan_file_path: Optional[str] = None
    aadhar_file_path: Optional[str] = None
    
    # Audit
    created_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        # Basic validation
        if not self.employee_id or not self.employee_id.strip():
            errors.append("Employee ID is required")
        
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        
        if not self.email or not self.email.strip():
            errors.append("Email is required")
        elif '@' not in self.email:
            errors.append("Valid email is required")
        
        if not self.password or len(self.password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not self.mobile or not self.mobile.strip():
            errors.append("Mobile number is required")
        
        if not self.date_of_birth:
            errors.append("Date of birth is required")
        
        # Validate enums
        try:
            UserRole(self.role)
        except ValueError:
            errors.append("Invalid user role")
        
        try:
            Gender(self.gender)
        except ValueError:
            errors.append("Invalid gender")
        
        return errors


@dataclass
class UpdateUserRequestDTO:
    """DTO for updating user information"""
    
    # Basic Information
    name: Optional[str] = None
    email: Optional[str] = None
    
    # Personal Details
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    mobile: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    # Employment Information
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[str] = None
    date_of_joining: Optional[str] = None
    date_of_leaving: Optional[str] = None
    
    # Audit
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the update request data"""
        errors = []
        
        # Validate non-empty strings if provided
        if self.name is not None and not self.name.strip():
            errors.append("Name cannot be empty")
        
        if self.email is not None:
            if not self.email.strip():
                errors.append("Email cannot be empty")
            elif '@' not in self.email:
                errors.append("Valid email is required")
        
        if self.mobile is not None and not self.mobile.strip():
            errors.append("Mobile number cannot be empty")
        
        # Validate gender if provided
        if self.gender is not None:
            try:
                Gender(self.gender)
            except ValueError:
                errors.append("Invalid gender")
        
        return errors


@dataclass
class UpdateUserDocumentsRequestDTO:
    """DTO for updating user documents"""
    
    photo_path: Optional[str] = None
    pan_file_path: Optional[str] = None
    aadhar_file_path: Optional[str] = None
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the documents update request"""
        errors = []
        
        # At least one document should be provided
        if not any([self.photo_path, self.pan_file_path, self.aadhar_file_path]):
            errors.append("At least one document must be provided")
        
        return errors


@dataclass
class ChangeUserPasswordRequestDTO:
    """DTO for changing user password"""
    
    new_password: str
    confirm_password: str
    current_password: Optional[str] = None  # Required for self-change
    is_admin_reset: bool = False
    changed_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the password change request"""
        errors = []
        
        if not self.new_password:
            errors.append("New password is required")
        elif len(self.new_password) < 8:
            errors.append("New password must be at least 8 characters")
        
        if self.new_password != self.confirm_password:
            errors.append("Password confirmation does not match")
        
        if not self.is_admin_reset and not self.current_password:
            errors.append("Current password is required for self-change")
        
        return errors


@dataclass
class ChangeUserRoleRequestDTO:
    """DTO for changing user role"""
    
    new_role: str
    reason: str
    changed_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the role change request"""
        errors = []
        
        if not self.reason or not self.reason.strip():
            errors.append("Reason for role change is required")
        
        try:
            UserRole(self.new_role)
        except ValueError:
            errors.append("Invalid user role")
        
        return errors


@dataclass
class UserStatusUpdateRequestDTO:
    """DTO for updating user status"""
    
    action: str  # activate, deactivate, suspend, unlock
    reason: Optional[str] = None
    suspension_duration_hours: Optional[int] = None  # Hours for suspension
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the status update request"""
        errors = []
        
        valid_actions = ["activate", "deactivate", "suspend", "unlock"]
        if self.action not in valid_actions:
            errors.append(f"Invalid action. Must be one of: {', '.join(valid_actions)}")
        
        if self.action in ["deactivate", "suspend"] and not self.reason:
            errors.append(f"Reason is required for {self.action} action")
        
        if self.action == "suspend" and self.suspension_duration_hours is not None:
            if self.suspension_duration_hours <= 0:
                errors.append("Suspension duration must be positive")
        
        return errors


@dataclass
class UserSearchFiltersDTO:
    """DTO for user search filters"""
    
    # Basic filters
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    
    # Employment filters
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[str] = None
    
    # Personal filters
    gender: Optional[str] = None
    
    # Date filters
    joined_after: Optional[datetime] = None
    joined_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Status filters
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    has_complete_profile: Optional[bool] = None
    
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
            "name", "email", "role", "status", "department", "designation",
            "created_at", "updated_at", "last_login_at", "date_of_joining"
        ]
        if self.sort_by not in valid_sort_fields:
            errors.append(f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}")
        
        # Validate enum values if provided
        if self.role is not None:
            try:
                UserRole(self.role)
            except ValueError:
                errors.append("Invalid user role filter")
        
        if self.status is not None:
            try:
                UserStatus(self.status)
            except ValueError:
                errors.append("Invalid user status filter")
        
        if self.gender is not None:
            try:
                Gender(self.gender)
            except ValueError:
                errors.append("Invalid gender filter")
        
        return errors


@dataclass
class UserLoginRequestDTO:
    """DTO for user login"""
    
    email: str
    password: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate login request"""
        errors = []
        
        if not self.email or not self.email.strip():
            errors.append("Email is required")
        
        if not self.password:
            errors.append("Password is required")
        
        return errors


# ==================== RESPONSE DTOs ====================

@dataclass
class PersonalDetailsResponseDTO:
    """DTO for personal details response"""
    
    gender: str
    date_of_birth: str
    mobile: str
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    # Formatted/masked fields
    formatted_mobile: Optional[str] = None
    masked_pan: Optional[str] = None
    masked_aadhar: Optional[str] = None


@dataclass
class UserDocumentsResponseDTO:
    """DTO for user documents response"""
    
    photo_path: Optional[str] = None
    pan_file_path: Optional[str] = None
    aadhar_file_path: Optional[str] = None
    
    # Computed fields
    has_photo: bool = False
    has_pan_document: bool = False
    has_aadhar_document: bool = False
    completion_percentage: float = 0.0
    missing_documents: List[str] = None


@dataclass
class UserPermissionsResponseDTO:
    """DTO for user permissions response"""
    
    role: str
    custom_permissions: List[str] = None
    resource_permissions: Dict[str, List[str]] = None
    
    # Computed fields
    can_manage_users: bool = False
    can_view_reports: bool = False
    can_approve_requests: bool = False
    is_admin: bool = False
    is_superadmin: bool = False


@dataclass
class UserResponseDTO:
    """DTO for user response"""
    
    # Identity
    user_id: str
    
    # Basic Information
    name: str
    email: str
    status: str
    
    # Personal Details
    personal_details: Optional[PersonalDetailsResponseDTO] = None
    
    # Employment Information
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[str] = None
    date_of_joining: Optional[str] = None
    date_of_leaving: Optional[str] = None
    
    # Authorization
    permissions: Optional[UserPermissionsResponseDTO] = None
    
    # Documents
    documents: Optional[UserDocumentsResponseDTO] = None
    
    # Leave Balance
    leave_balance: Dict[str, int] = None
    
    # System Fields
    created_at: str = None
    updated_at: str = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    last_login_at: Optional[str] = None
    
    # Computed fields
    is_active: bool = False
    is_locked: bool = False
    can_login: bool = False
    profile_completion_percentage: float = 0.0
    display_name: str = None
    role_display: str = None
    status_display: str = None


@dataclass
class UserSummaryDTO:
    """DTO for user summary (list view)"""
    
    user_id: str
    name: str
    email: str
    role: str
    status: str
    department: Optional[str] = None
    designation: Optional[str] = None
    last_login_at: Optional[str] = None
    created_at: str = None
    is_active: bool = False
    is_locked: bool = False
    profile_completion_percentage: float = 0.0


@dataclass
class UserListResponseDTO:
    """DTO for paginated user list response"""
    
    users: List[UserSummaryDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class UserStatisticsDTO:
    """DTO for user statistics"""
    
    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    locked_users: int
    
    # By role
    users_by_role: Dict[str, int]
    
    # By department
    users_by_department: Dict[str, int]
    
    # By location
    users_by_location: Dict[str, int]
    
    # Profile completion
    users_with_complete_profiles: int
    average_profile_completion: float
    
    # Activity statistics
    users_logged_in_today: int
    users_logged_in_this_week: int
    users_logged_in_this_month: int
    
    # Growth statistics
    users_created_this_month: int
    users_created_this_year: int


@dataclass
class UserAnalyticsDTO:
    """DTO for user analytics"""
    
    # Activity analysis
    most_active_users: List[Dict[str, Any]]
    least_active_users: List[Dict[str, Any]]
    
    # Role distribution
    role_distribution: Dict[str, float]  # Percentages
    
    # Department distribution
    department_distribution: Dict[str, float]  # Percentages
    
    # Login patterns
    login_frequency_by_day: Dict[str, int]
    login_frequency_by_hour: Dict[str, int]
    
    # Profile completion trends
    profile_completion_by_department: Dict[str, float]
    
    # Security metrics
    users_with_weak_passwords: int
    users_with_expired_passwords: int
    recent_password_changes: int


@dataclass
class UserLoginResponseDTO:
    """DTO for user login response"""
    
    user_id: str
    name: str
    email: str
    role: str
    permissions: List[str]
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = 3600  # seconds
    last_login_at: Optional[str] = None


@dataclass
class UserProfileCompletionDTO:
    """DTO for user profile completion status"""
    
    user_id: str
    completion_percentage: float
    completed_sections: List[str]
    missing_sections: List[str]
    required_documents: List[str]
    uploaded_documents: List[str]
    missing_documents: List[str]
    recommendations: List[str]


@dataclass
class BulkUserUpdateDTO:
    """DTO for bulk user updates"""
    
    user_ids: List[str]
    update_data: Dict[str, Any]
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate bulk update request"""
        errors = []
        
        if not self.user_ids:
            errors.append("User IDs list cannot be empty")
        
        if not self.update_data:
            errors.append("Update data cannot be empty")
        
        return errors


@dataclass
class BulkUserUpdateResultDTO:
    """DTO for bulk update results"""
    
    total_requested: int
    successful_updates: int
    failed_updates: int
    errors: List[Dict[str, str]]  # {user_id: error_message}
    updated_user_ids: List[str]


@dataclass
class UserAuditLogDTO:
    """DTO for user audit log"""
    
    user_id: str
    action: str
    details: Dict[str, Any]
    performed_by: str
    performed_at: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# ==================== ERROR CLASSES ====================

class UserValidationError(Exception):
    """Raised when user data validation fails"""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class UserBusinessRuleError(Exception):
    """Raised when user business rule is violated"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule


class UserNotFoundError(Exception):
    """Raised when user is not found"""
    
    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}")
        self.user_id = user_id


class UserConflictError(Exception):
    """Raised when user operation conflicts with existing data"""
    
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field


class UserAuthenticationError(Exception):
    """Raised when user authentication fails"""
    
    def __init__(self, message: str, reason: str = None):
        super().__init__(message)
        self.reason = reason


class UserAuthorizationError(Exception):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str, required_permission: str = None):
        super().__init__(message)
        self.required_permission = required_permission 