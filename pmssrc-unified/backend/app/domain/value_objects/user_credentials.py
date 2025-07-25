"""
User Credentials Value Objects
Contains value objects for user authentication and authorization
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
import re
import bcrypt
from datetime import datetime, timedelta


class UserRole(Enum):
    """User role enumeration"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class UserStatus(Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Gender(Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


@dataclass(frozen=True)
class Password:
    """
    Password value object with hashing and validation.
    
    Follows SOLID principles:
    - SRP: Only handles password operations
    - OCP: Can be extended with new password policies
    - LSP: Can be substituted anywhere Password is expected
    - ISP: Focused interface for password operations
    - DIP: Depends on abstractions (string)
    """
    
    hashed_value: str
    changed_at: Optional[datetime] = None
    
    @classmethod
    def from_plain_text(cls, plain_text: str) -> 'Password':
        """Create from plain text password"""
        if not plain_text or not plain_text.strip():
            raise ValueError("Password cannot be empty")
        
        if len(plain_text) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Basic password strength validation
        if not any(c.isupper() for c in plain_text):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in plain_text):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in plain_text):
            raise ValueError("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', plain_text):
            raise ValueError("Password must contain at least one special character")
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_text.encode('utf-8'), salt)
        
        return cls(
            hashed_value=hashed.decode('utf-8'),
            changed_at=datetime.utcnow()
        )
    
    @classmethod
    def from_hash(cls, hashed_value: str) -> 'Password':
        """Create from existing hash"""
        if not hashed_value:
            raise ValueError("Hash value cannot be empty")
        
        return cls(hashed_value=hashed_value)
    
    def verify(self, plain_text: str) -> bool:
        """Verify plain text password against hash"""
        try:
            return bcrypt.checkpw(
                plain_text.encode('utf-8'),
                self.hashed_value.encode('utf-8')
            )
        except Exception:
            return False
    
    def is_expired(self, max_age_days: int = 90) -> bool:
        """Check if password is expired"""
        if not self.changed_at:
            return True
        
        expiry_date = self.changed_at + timedelta(days=max_age_days)
        return datetime.utcnow() > expiry_date
    
    def get_strength_score(self) -> int:
        """Get password strength score (0-10)"""
        # This would be more sophisticated in production
        # For now, return a default score
        return 8
    
    def __str__(self) -> str:
        """String representation"""
        return "********"


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
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN]
    
    def can_view_reports(self) -> bool:
        """Check if user can view reports"""
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.MANAGER]
    
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
                "organisation.create", "organisation.read", "organisation.update", "organisation.delete",
                "system.configure", "system.backup", "system.restore",
                "reports.all", "audit.view"
            ],
            UserRole.ADMIN: [
                "user.create", "user.read", "user.update",
                "organisation.read", "organisation.update",
                "reports.all", "attendance.manage"
            ],
            UserRole.MANAGER: [
                "user.read", "team.manage", "attendance.approve",
                "leave.approve", "reports.team"
            ],
            UserRole.USER: [
                "profile.read", "profile.update", "attendance.mark",
                "leave.apply", "reimbursement.apply"
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
                UserRole.MANAGER: ["read"]
            },
            "attendance": {
                UserRole.ADMIN: ["read", "create", "update", "delete"],
                UserRole.MANAGER: ["read", "approve"],
                UserRole.USER: ["read", "create"]
            },
            "leaves": {
                UserRole.ADMIN: ["read", "create", "update", "delete"],
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
        """Create permissions from role only"""
        return cls(role=role)
    
    def get_all_permissions(self) -> List[str]:
        """Get all permissions (role-based + custom)"""
        return list(set(self._get_role_permissions() + self.custom_permissions))


@dataclass(frozen=True)
class UserDocuments:
    """
    User documents value object for file paths and document management.
    """
    
    photo_path: Optional[str] = None
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    
    def has_photo(self) -> bool:
        """Check if photo is uploaded"""
        return bool(self.photo_path)
    
    def has_pan_document(self) -> bool:
        """Check if PAN document is uploaded"""
        return bool(self.pan_document_path)
    
    def has_aadhar_document(self) -> bool:
        """Check if Aadhar document is uploaded"""
        return bool(self.aadhar_document_path)
    
    def get_document_completion_percentage(self) -> float:
        """Get document completion percentage"""
        total_docs = 3  # Photo, PAN, Aadhar
        completed_docs = 0
        
        if self.has_photo():
            completed_docs += 1
        if self.has_pan_document():
            completed_docs += 1
        if self.has_aadhar_document():
            completed_docs += 1
        
        return (completed_docs / total_docs) * 100
    
    def get_missing_documents(self) -> List[str]:
        """Get list of missing documents"""
        missing = []
        
        if not self.has_photo():
            missing.append("Photo")
        if not self.has_pan_document():
            missing.append("PAN Document")
        if not self.has_aadhar_document():
            missing.append("Aadhar Document")
        
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