"""
User Data Transfer Objects (DTOs)
Handles data transfer for user operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from app.domain.value_objects.user_credentials import UserRole, UserStatus, Gender


# ==================== REQUEST DTOs ====================

@dataclass
class CreateUserRequestDTO:
    """DTO for creating a new user"""
    
    # Identity (required)
    employee_id: str
    
    # Basic Information (required)
    name: str
    email: str
    password: str
    
    # Personal Details (required)
    gender: str
    date_of_birth: str  # ISO format
    date_of_joining: str  # ISO format
    mobile: str
    
    # Optional fields with defaults
    date_of_leaving: Optional[str] = None
    role: str = UserRole.USER.value
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    # Employment Information (optional)
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[str] = None
    
    # Documents (optional)
    photo_path: Optional[str] = None
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    
    # Bank Details (optional)
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    
    # Audit (optional)
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
        
        if not self.date_of_joining:
            errors.append("Date of joining is required")
        
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
    date_of_joining: Optional[str] = None
    date_of_leaving: Optional[str] = None
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
    date_of_leaving: Optional[str] = None
    
    # Bank Details (optional)
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    
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
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the documents update request"""
        errors = []
        
        # At least one document should be provided
        if not any([self.photo_path, self.pan_document_path, self.aadhar_document_path]):
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
            "created_at", "updated_at", "last_login_at", "date_of_joining", 
            "date_of_leaving"
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
    
    username: str
    password: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate login request"""
        errors = []
        
        if not self.username or not self.username.strip():
            errors.append("Username is required")
        
        if not self.password:
            errors.append("Password is required")
        
        return errors


# ==================== RESPONSE DTOs ====================

@dataclass
class PersonalDetailsResponseDTO:
    """DTO for personal details response"""
    
    gender: str
    date_of_birth: str
    date_of_joining: str
    mobile: str
    date_of_leaving: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    # Formatted/masked fields
    formatted_mobile: Optional[str] = None
    masked_pan: Optional[str] = None
    masked_aadhar: Optional[str] = None
    
    @classmethod
    def from_value_object(cls, personal_details) -> 'PersonalDetailsResponseDTO':
        """Create from PersonalDetails value object"""
        if not personal_details:
            return None
            
        return cls(
            gender=personal_details.gender.value,
            date_of_birth=personal_details.date_of_birth.isoformat(),
            date_of_joining=personal_details.date_of_joining.isoformat(),
            date_of_leaving=personal_details.date_of_leaving.isoformat() if personal_details.date_of_leaving else None,
            mobile=personal_details.mobile,
            pan_number=personal_details.pan_number,
            aadhar_number=personal_details.aadhar_number,
            uan_number=personal_details.uan_number,
            esi_number=personal_details.esi_number,
            formatted_mobile=personal_details.get_formatted_mobile(),
            masked_pan=personal_details.get_masked_pan(),
            masked_aadhar=personal_details.get_masked_aadhar()
        )


@dataclass
class UserDocumentsResponseDTO:
    """DTO for user documents response"""
    
    photo_path: Optional[str] = None
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    
    # Computed fields
    has_photo: bool = False
    has_pan_document: bool = False
    has_aadhar_document: bool = False
    completion_percentage: float = 0.0
    missing_documents: List[str] = None

    @classmethod
    def from_value_object(cls, documents_vo):
        """Create UserDocumentsResponseDTO from UserDocuments value object"""
        if not documents_vo:
            return None
        return cls(
            photo_path=documents_vo.photo_path,
            pan_document_path=documents_vo.pan_document_path,
            aadhar_document_path=documents_vo.aadhar_document_path,
            has_photo=documents_vo.has_photo() if hasattr(documents_vo, 'has_photo') else False,
            has_pan_document=documents_vo.has_pan_document() if hasattr(documents_vo, 'has_pan_document') else False,
            has_aadhar_document=documents_vo.has_aadhar_document() if hasattr(documents_vo, 'has_aadhar_document') else False,
            completion_percentage=documents_vo.get_document_completion_percentage() if hasattr(documents_vo, 'get_document_completion_percentage') else 0.0,
            missing_documents=documents_vo.get_missing_documents() if hasattr(documents_vo, 'get_missing_documents') else []
        )


@dataclass
class BankDetailsResponseDTO:
    """DTO for bank details response"""
    
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    
    # Computed fields for security
    masked_account_number: Optional[str] = None
    formatted_account_number: Optional[str] = None
    bank_code: Optional[str] = None
    branch_code: Optional[str] = None
    is_valid_for_payment: bool = False

    @classmethod
    def from_value_object(cls, bank_details_vo):
        """Create BankDetailsResponseDTO from BankDetails value object"""
        if not bank_details_vo:
            return None
        return cls(
            account_number=bank_details_vo.account_number,
            bank_name=bank_details_vo.bank_name,
            ifsc_code=bank_details_vo.ifsc_code,
            account_holder_name=bank_details_vo.account_holder_name,
            branch_name=bank_details_vo.branch_name,
            account_type=bank_details_vo.account_type,  
            masked_account_number=bank_details_vo.get_masked_account_number(),
            formatted_account_number=bank_details_vo.get_formatted_account_number(),
            is_valid_for_payment=bank_details_vo.is_valid_for_payment() if hasattr(bank_details_vo, 'is_valid_for_payment') else False
        )


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

    @classmethod
    def from_value_object(cls, permissions_vo):
        """Create UserPermissionsResponseDTO from UserPermissions value object"""
        if not permissions_vo:
            return None
        return cls(
            role=permissions_vo.role.value if hasattr(permissions_vo.role, 'value') else str(permissions_vo.role),
            custom_permissions=list(permissions_vo.custom_permissions) if permissions_vo.custom_permissions else [],
            resource_permissions=dict(permissions_vo.resource_permissions) if permissions_vo.resource_permissions else {},
            can_manage_users=permissions_vo.can_manage_users() if hasattr(permissions_vo, 'can_manage_users') else False,
            can_view_reports=permissions_vo.can_view_reports() if hasattr(permissions_vo, 'can_view_reports') else False,
            can_approve_requests=permissions_vo.can_approve_requests() if hasattr(permissions_vo, 'can_approve_requests') else False,
            is_admin=permissions_vo.is_admin() if hasattr(permissions_vo, 'is_admin') else False,
            is_superadmin=permissions_vo.is_superadmin() if hasattr(permissions_vo, 'is_superadmin') else False
        )


@dataclass
class UserResponseDTO:
    """DTO for user response"""
    
    # Identity
    employee_id: str
    
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
    
    # Authorization
    permissions: Optional[UserPermissionsResponseDTO] = None
    
    # Document fields at parent level
    photo_path: Optional[str] = None
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    
    # Bank Details
    bank_details: Optional[BankDetailsResponseDTO] = None
    
    # Leave Balance
    leave_balance: Optional[Dict[str, float]] = None
    
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

    @classmethod
    def from_entity(cls, user) -> 'UserResponseDTO':
        """Create UserResponseDTO from User entity"""
        
        def safe_get_attr(obj, attr_path, default=None):
            """Safely get nested attributes"""
            try:
                attrs = attr_path.split('.')
                value = obj
                for attr in attrs:
                    value = getattr(value, attr, None)
                    if value is None:
                        return default
                return value
            except (AttributeError, TypeError):
                return default
        
        def safe_enum_value(field_value):
            """Safely get enum value"""
            if hasattr(field_value, 'value'):
                return field_value.value
            return str(field_value) if field_value is not None else None
        
        def format_datetime(dt_value):
            """Format datetime to string"""
            if not dt_value:
                return None
            if isinstance(dt_value, str):
                return dt_value
            return dt_value.isoformat() if hasattr(dt_value, 'isoformat') else str(dt_value)
        
        # Create personal details response DTO if available
        personal_details = None
        if user.personal_details:
            personal_details = PersonalDetailsResponseDTO.from_value_object(user.personal_details)
        
        # Create permissions response DTO if available
        permissions = None
        if user.permissions:
            permissions = UserPermissionsResponseDTO.from_value_object(user.permissions)
        
        # Create bank details response DTO if available
        bank_details = None
        if user.bank_details:
            bank_details = BankDetailsResponseDTO.from_value_object(user.bank_details)

        documents = None
        if user.documents:
            documents = UserDocumentsResponseDTO.from_value_object(user.documents)
        
        return cls(
            employee_id=str(user.employee_id),
            name=user.name,
            email=user.email,
            status=safe_enum_value(user.status),
            personal_details=personal_details,
            department=user.department,
            designation=user.designation,
            location=user.location,
            manager_id=str(user.manager_id) if user.manager_id else None,
            permissions=permissions,
            photo_path=documents.photo_path if documents else None,
            pan_document_path=documents.pan_document_path if documents else None,
            aadhar_document_path=documents.aadhar_document_path if documents else None,
            bank_details=bank_details,
            leave_balance=user.leave_balance,
            created_at=format_datetime(user.created_at),
            updated_at=format_datetime(user.updated_at),
            created_by=user.created_by,
            updated_by=user.updated_by,
            last_login_at=format_datetime(user.last_login_at),
            is_active=user.is_active() if hasattr(user, 'is_active') else True,
            is_locked=user.is_locked() if hasattr(user, 'is_locked') else False,
            can_login=user.can_login() if hasattr(user, 'can_login') else True,
            profile_completion_percentage=user.get_profile_completion_percentage() if hasattr(user, 'get_profile_completion_percentage') else 0.0,
            display_name=user.get_display_name() if hasattr(user, 'get_display_name') else user.name,
            role_display=user.get_role_display() if hasattr(user, 'get_role_display') else None,
            status_display=user.get_status_display() if hasattr(user, 'get_status_display') else None
        )


@dataclass
class UserSummaryDTO:
    """DTO for user summary (list view)"""
    
    # Required fields (no defaults)
    employee_id: str
    name: str
    email: str
    role: str
    status: str
    
    # Optional fields (with defaults)
    mobile: Optional[str] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    date_of_joining: Optional[str] = None
    date_of_leaving: Optional[str] = None
    last_login_at: Optional[str] = None
    created_at: str = None
    is_active: bool = False
    is_locked: bool = False
    profile_completion_percentage: float = 0.0

    @classmethod
    def from_entity(cls, user) -> 'UserSummaryDTO':
        """Create UserSummaryDTO from User entity"""
        
        # Safe attribute extraction
        def safe_get_attr(obj, attr, default=None):
            try:
                return getattr(obj, attr, default)
            except (AttributeError, TypeError):
                return default
        
        # Safe enum value extraction
        def safe_enum_value(enum_obj):
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            return str(enum_obj) if enum_obj is not None else None
        
        # Safe date formatting
        def format_datetime(dt):
            if dt is None:
                return None
            if hasattr(dt, 'isoformat'):
                return dt.isoformat()
            return str(dt)
        
        # Safe boolean evaluation (handle methods)
        def safe_bool_value(obj, attr, default=False):
            try:
                value = getattr(obj, attr, default)
                if callable(value):
                    return value()
                return bool(value) if value is not None else default
            except (AttributeError, TypeError):
                return default
        user_role = "user"
        # Prefer personal_details for mobile, gender, date_of_joining if present
        personal_details = safe_get_attr(user, 'personal_details')
        mobile = safe_get_attr(personal_details, 'mobile') if personal_details else safe_get_attr(user, 'mobile', '')
        gender = safe_enum_value(safe_get_attr(personal_details, 'gender')) if personal_details else safe_enum_value(safe_get_attr(user, 'gender'))
        date_of_joining = format_datetime(safe_get_attr(personal_details, 'date_of_joining')) if personal_details else format_datetime(safe_get_attr(user, 'date_of_joining'))
        permissions = safe_get_attr(user, 'permissions')
        if permissions:
            user_role = permissions.role.value

        return cls(
            employee_id=str(safe_get_attr(user, 'employee_id', '')),
            name=safe_get_attr(user, 'name', ''),
            email=safe_get_attr(user, 'email', ''),
            role=user_role,
            status=safe_enum_value(safe_get_attr(user, 'status')) or 'active',
            mobile=mobile or '',
            gender=gender,
            department=safe_get_attr(user, 'department'),
            designation=safe_get_attr(user, 'designation'),
            date_of_joining=date_of_joining,
            date_of_leaving=format_datetime(safe_get_attr(user, 'date_of_leaving')),
            last_login_at=format_datetime(safe_get_attr(user, 'last_login')),
            created_at=format_datetime(safe_get_attr(user, 'created_at')),
            is_active=safe_bool_value(user, 'is_active', True),
            is_locked=safe_bool_value(user, 'is_locked', False),
            profile_completion_percentage=safe_get_attr(user, 'profile_completion_percentage', 0.0)
        )


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
    
    employee_id: str
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
    
    employee_id: str
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
    
    employee_ids: List[str]
    update_data: Dict[str, Any]
    updated_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate bulk update request"""
        errors = []
        
        if not self.employee_ids:
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
    errors: List[Dict[str, str]]  # {employee_id: error_message}
    updated_employee_ids: List[str]


@dataclass
class UserAuditLogDTO:
    """DTO for user audit log"""
    
    employee_id: str
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
    
    def __init__(self, employee_id: str):
        super().__init__(f"User not found: {employee_id}")
        self.employee_id = employee_id


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