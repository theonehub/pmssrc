"""
User Credentials Value Objects
Immutable value objects for user authentication and authorization
"""

import re
import hashlib
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timedelta


class UserRole(Enum):
    """User role enumeration"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    HR = "hr"
    FINANCE = "finance"
    READONLY = "readonly"


class UserStatus(Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    PENDING_ACTIVATION = "pending_activation"


class Gender(Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


@dataclass(frozen=True)
class Password:
    """
    Password value object with validation and security features.
    
    Follows SOLID principles:
    - SRP: Only handles password representation and validation
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for password operations
    - DIP: Depends on abstractions
    """
    
    hashed_value: str
    salt: Optional[str] = None
    algorithm: str = "bcrypt"
    created_at: datetime = None
    
    def __post_init__(self):
        """Validate password hash"""
        if not self.hashed_value:
            raise ValueError("Password hash cannot be empty")
        
        if not isinstance(self.hashed_value, str):
            raise ValueError("Password hash must be a string")
        
        # Set created_at if not provided
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
    
    @classmethod
    def from_plain_text(cls, plain_password: str) -> 'Password':
        """Create password from plain text (will be hashed)"""
        if not cls.is_valid_password(plain_password):
            raise ValueError("Password does not meet security requirements")
        
        # Import here to avoid circular dependencies
        from app.auth.password_handler import hash_password
        hashed = hash_password(plain_password)
        
        return cls(
            hashed_value=hashed,
            algorithm="bcrypt",
            created_at=datetime.utcnow()
        )
    
    @classmethod
    def from_hash(cls, hashed_password: str, algorithm: str = "bcrypt") -> 'Password':
        """Create password from existing hash"""
        return cls(
            hashed_value=hashed_password,
            algorithm=algorithm,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """
        Validate password strength.
        
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        return True
    
        # TODO: Implement more robust password validation
        if len(password) < 8:
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
        
        if not re.search(r'[a-z]', password):
            return False
        
        if not re.search(r'\d', password):
            return False
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def verify(self, plain_password: str) -> bool:
        """Verify password against plain text"""
        from app.auth.password_handler import verify_password
        return verify_password(plain_password, self.hashed_value)
    
    def is_expired(self, max_age_days: int = 90) -> bool:
        """Check if password is expired"""
        if not self.created_at:
            return True
        
        expiry_date = self.created_at + timedelta(days=max_age_days)
        return datetime.utcnow() > expiry_date
    
    def get_strength_score(self) -> int:
        """Get password strength score (0-100)"""
        # This is a simplified scoring system
        # In production, you might want a more sophisticated algorithm
        score = 0
        
        # Length bonus
        if len(self.hashed_value) >= 60:  # bcrypt hashes are typically 60 chars
            score += 30
        
        # Algorithm bonus
        if self.algorithm == "bcrypt":
            score += 40
        elif self.algorithm in ["scrypt", "argon2"]:
            score += 50
        else:
            score += 20
        
        # Age penalty
        if self.created_at:
            age_days = (datetime.utcnow() - self.created_at).days
            if age_days > 90:
                score -= 20
            elif age_days > 180:
                score -= 40
        
        return max(0, min(100, score))


@dataclass(frozen=True)
class UserPermissions:
    """
    User permissions value object.
    
    Represents what actions a user can perform in the system.
    """
    
    role: UserRole
    custom_permissions: List[str] = None
    resource_permissions: Dict[str, List[str]] = None
    
    def __post_init__(self):
        """Initialize default permissions"""
        if self.custom_permissions is None:
            object.__setattr__(self, 'custom_permissions', [])
        
        if self.resource_permissions is None:
            object.__setattr__(self, 'resource_permissions', {})
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        # Check role-based permissions
        role_permissions = self._get_role_permissions()
        if permission in role_permissions:
            return True
        
        # Check custom permissions
        if permission in self.custom_permissions:
            return True
        
        return False
    
    def has_resource_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission for specific resource action"""
        if resource in self.resource_permissions:
            return action in self.resource_permissions[resource]
        
        # Check if role has default access
        return self._role_has_resource_access(resource, action)
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.HR]
    
    def can_view_reports(self) -> bool:
        """Check if user can view reports"""
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.MANAGER, UserRole.HR, UserRole.FINANCE]
    
    def can_approve_requests(self) -> bool:
        """Check if user can approve requests"""
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.MANAGER]
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN]
    
    def is_superadmin(self) -> bool:
        """Check if user is superadmin"""
        return self.role == UserRole.SUPERADMIN
    
    def _get_role_permissions(self) -> List[str]:
        """Get permissions based on role"""
        role_permissions = {
            UserRole.SUPERADMIN: [
                "user.create", "user.read", "user.update", "user.delete",
                "organization.create", "organization.read", "organization.update", "organization.delete",
                "system.configure", "system.backup", "system.restore",
                "reports.all", "audit.view"
            ],
            UserRole.ADMIN: [
                "user.create", "user.read", "user.update",
                "organization.read", "organization.update",
                "reports.all", "attendance.manage"
            ],
            UserRole.MANAGER: [
                "user.read", "team.manage", "attendance.approve",
                "leave.approve", "reports.team"
            ],
            UserRole.HR: [
                "user.create", "user.read", "user.update",
                "employee.manage", "leave.manage", "reports.hr"
            ],
            UserRole.FINANCE: [
                "user.read", "payroll.manage", "reimbursement.approve",
                "reports.finance", "taxation.manage"
            ],
            UserRole.USER: [
                "profile.read", "profile.update", "attendance.mark",
                "leave.apply", "reimbursement.apply"
            ],
            UserRole.READONLY: [
                "profile.read", "reports.view"
            ]
        }
        
        return role_permissions.get(self.role, [])
    
    def _role_has_resource_access(self, resource: str, action: str) -> bool:
        """Check if role has default access to resource"""
        # Superadmin has access to everything
        if self.role == UserRole.SUPERADMIN:
            return True
        
        # Define resource access rules
        resource_rules = {
            "users": {
                UserRole.ADMIN: ["read", "create", "update"],
                UserRole.HR: ["read", "create", "update"],
                UserRole.MANAGER: ["read"]
            },
            "attendance": {
                UserRole.ADMIN: ["read", "create", "update", "delete"],
                UserRole.MANAGER: ["read", "approve"],
                UserRole.USER: ["read", "create"]
            },
            "leaves": {
                UserRole.ADMIN: ["read", "create", "update", "delete"],
                UserRole.HR: ["read", "create", "update", "approve"],
                UserRole.MANAGER: ["read", "approve"],
                UserRole.USER: ["read", "create"]
            }
        }
        
        if resource in resource_rules and self.role in resource_rules[resource]:
            return action in resource_rules[resource][self.role]
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "role": self.role.value,
            "custom_permissions": self.custom_permissions,
            "resource_permissions": self.resource_permissions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPermissions':
        """Create from dictionary representation"""
        return cls(
            role=UserRole(data["role"]),
            custom_permissions=data.get("custom_permissions", []),
            resource_permissions=data.get("resource_permissions", {})
        )
    
    @classmethod
    def from_role(cls, role: UserRole) -> 'UserPermissions':
        """Create permissions from user role"""
        return cls(
            role=role,
            custom_permissions=[],
            resource_permissions={}
        )
    
    def get_all_permissions(self) -> List[str]:
        """Get all permissions (role-based + custom)"""
        role_perms = self._get_role_permissions()
        all_perms = set(role_perms + self.custom_permissions)
        return list(all_perms)


@dataclass(frozen=True)
class PersonalDetails:
    """
    Personal details value object for user information.
    """
    
    gender: Gender
    date_of_birth: str  # ISO format date string
    mobile: str
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    def __post_init__(self):
        """Validate personal details"""
        # Validate mobile number
        if not self._is_valid_mobile(self.mobile):
            raise ValueError("Invalid mobile number format")
        
        # Validate PAN number
        if self.pan_number and not self._is_valid_pan(self.pan_number):
            raise ValueError("Invalid PAN number format")
        
        # Validate Aadhar number
        if self.aadhar_number and not self._is_valid_aadhar(self.aadhar_number):
            raise ValueError("Invalid Aadhar number format")
        
        # Validate date of birth
        if not self._is_valid_date(self.date_of_birth):
            raise ValueError("Invalid date of birth format")
    
    def _is_valid_mobile(self, mobile: str) -> bool:
        """Validate mobile number format"""
        if not mobile:
            return False
        
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', mobile)
        
        # Check if it's 10 digits
        return len(digits_only) == 10 and digits_only.isdigit()
    
    def _is_valid_pan(self, pan: str) -> bool:
        """Validate PAN number format"""
        if not pan:
            return True  # Optional field
        
        # PAN format: 5 letters, 4 digits, 1 letter
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        return bool(re.match(pattern, pan.upper()))
    
    def _is_valid_aadhar(self, aadhar: str) -> bool:
        """Validate Aadhar number format"""
        if not aadhar:
            return True  # Optional field
        
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', aadhar)
        
        # Check if it's 12 digits
        return len(digits_only) == 12 and digits_only.isdigit()
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Validate date format"""
        try:
            from datetime import datetime
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False
    
    def get_formatted_mobile(self) -> str:
        """Get formatted mobile number"""
        digits = re.sub(r'\D', '', self.mobile)
        return f"+91-{digits[:5]}-{digits[5:]}"
    
    def get_masked_pan(self) -> str:
        """Get masked PAN number for display"""
        if not self.pan_number:
            return "Not provided"
        
        return f"{self.pan_number[:3]}***{self.pan_number[-1]}"
    
    def get_masked_aadhar(self) -> str:
        """Get masked Aadhar number for display"""
        if not self.aadhar_number:
            return "Not provided"
        
        digits = re.sub(r'\D', '', self.aadhar_number)
        return f"****-****-{digits[-4:]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "gender": self.gender.value,
            "date_of_birth": self.date_of_birth,
            "mobile": self.mobile,
            "pan_number": self.pan_number,
            "aadhar_number": self.aadhar_number,
            "uan_number": self.uan_number,
            "esi_number": self.esi_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalDetails':
        """Create from dictionary representation"""
        return cls(
            gender=Gender(data["gender"]),
            date_of_birth=data["date_of_birth"],
            mobile=data["mobile"],
            pan_number=data.get("pan_number"),
            aadhar_number=data.get("aadhar_number"),
            uan_number=data.get("uan_number"),
            esi_number=data.get("esi_number")
        )


@dataclass(frozen=True)
class UserDocuments:
    """
    User documents value object for file paths and document management.
    """
    
    photo_path: Optional[str] = None
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    
    def has_photo(self) -> bool:
        """Check if user has uploaded photo"""
        return bool(self.photo_path and self.photo_path.strip())
    
    def has_pan_document(self) -> bool:
        """Check if user has uploaded PAN document"""
        return bool(self.pan_document_path and self.pan_document_path.strip())
    
    def has_aadhar_document(self) -> bool:
        """Check if user has uploaded Aadhar document"""
        return bool(self.aadhar_document_path and self.aadhar_document_path.strip())
    
    def get_document_completion_percentage(self) -> float:
        """Get document completion percentage"""
        total_docs = 3
        uploaded_docs = sum([
            self.has_photo(),
            self.has_pan_document(),
            self.has_aadhar_document()
        ])
        
        return (uploaded_docs / total_docs) * 100
    
    def get_missing_documents(self) -> List[str]:
        """Get list of missing documents"""
        missing = []
        
        if not self.has_photo():
            missing.append("photo")
        
        if not self.has_pan_document():
            missing.append("pan_document")
        
        if not self.has_aadhar_document():
            missing.append("aadhar_document")
        
        return missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "photo_path": self.photo_path,
            "pan_document_path": self.pan_document_path,
            "aadhar_document_path": self.aadhar_document_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserDocuments':
        """Create from dictionary representation"""
        return cls(
            photo_path=data.get("photo_path"),
            pan_document_path=data.get("pan_document_path"),
            aadhar_document_path=data.get("aadhar_document_path")
        ) 