"""
User Permissions Value Object
Encapsulates user authorization and permissions following DDD principles
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from app.domain.value_objects.user_credentials import UserRole


@dataclass(frozen=True)
class UserPermissions:
    """
    Value object for user permissions and authorization.
    
    Follows SOLID principles:
    - SRP: Only handles permission-related operations
    - OCP: Can be extended with new permission types
    - LSP: Can be substituted anywhere UserPermissions is expected
    - ISP: Focused interface for permission operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    role: UserRole
    custom_permissions: List[str] = field(default_factory=list)
    resource_permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate permissions after initialization"""
        self._validate_permissions()
    
    def _validate_permissions(self) -> None:
        """Validate permission data"""
        if not isinstance(self.role, UserRole):
            raise ValueError("Invalid user role")
        
        if not isinstance(self.custom_permissions, list):
            raise ValueError("Custom permissions must be a list")
        
        if not isinstance(self.resource_permissions, dict):
            raise ValueError("Resource permissions must be a dictionary")
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if user has the permission
        """
        # Check role-based permissions
        if permission in self._get_role_permissions():
            return True
        
        # Check custom permissions
        if permission in self.custom_permissions:
            return True
        
        return False
    
    def has_resource_permission(self, resource: str, action: str) -> bool:
        """
        Check if user has permission for a specific resource action.
        
        Args:
            resource: Resource name (e.g., 'users', 'reports')
            action: Action to perform (e.g., 'read', 'write', 'delete')
            
        Returns:
            True if user has the permission
        """
        # Check role-based resource permissions
        role_resource_perms = self._get_role_resource_permissions()
        if resource in role_resource_perms and action in role_resource_perms[resource]:
            return True
        
        # Check custom resource permissions
        if resource in self.resource_permissions and action in self.resource_permissions[resource]:
            return True
        
        return False
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    def is_superadmin(self) -> bool:
        """Check if user is superadmin"""
        return self.role == UserRole.SUPERADMIN
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return (
            self.is_admin() or
            self.has_permission("manage_users") or
            self.has_resource_permission("users", "write")
        )
    
    def can_view_reports(self) -> bool:
        """Check if user can view reports"""
        return (
            self.is_admin() or
            self.role == UserRole.MANAGER or
            self.has_permission("view_reports") or
            self.has_resource_permission("reports", "read")
        )
    
    def can_approve_requests(self) -> bool:
        """Check if user can approve requests (leaves, reimbursements, etc.)"""
        return (
            self.is_admin() or
            self.role == UserRole.MANAGER or
            self.has_permission("approve_requests")
        )
    
    def can_access_payroll(self) -> bool:
        """Check if user can access payroll information"""
        return (
            self.is_admin() or
            self.has_permission("access_payroll") or
            self.has_resource_permission("payroll", "read")
        )
    
    def can_manage_organisation(self) -> bool:
        """Check if user can manage organisation settings"""
        return (
            self.is_superadmin() or
            self.has_permission("manage_organisation")
        )
    
    def _get_role_permissions(self) -> List[str]:
        """Get permissions based on user role"""
        role_permissions = {
            UserRole.USER: [
                "view_own_profile",
                "update_own_profile",
                "view_own_payslip",
                "apply_leave",
                "view_own_attendance",
                "submit_reimbursement"
            ],
            UserRole.MANAGER: [
                "view_own_profile",
                "update_own_profile",
                "view_own_payslip",
                "apply_leave",
                "view_own_attendance",
                "submit_reimbursement",
                "view_team_attendance",
                "approve_team_leaves",
                "view_team_reports",
                "approve_team_reimbursements"
            ],
            UserRole.ADMIN: [
                "manage_users",
                "view_all_attendance",
                "manage_leaves",
                "view_reports",
                "manage_payroll",
                "manage_company_policies"
            ],
            UserRole.SUPERADMIN: [
                "manage_users",
                "view_all_attendance",
                "manage_leaves",
                "view_reports",
                "manage_payroll",
                "manage_company_policies",
                "manage_system_settings",
                "view_audit_logs"
            ],
        }
        
        return role_permissions.get(self.role, [])
    
    def _get_role_resource_permissions(self) -> Dict[str, List[str]]:
        """Get resource permissions based on user role"""
        role_resource_permissions = {
            UserRole.USER: {
                "profile": ["read", "update"],
                "payslip": ["read"],
                "attendance": ["read", "create"],
                "leaves": ["read", "create"],
                "reimbursements": ["read", "create"]
            },
            UserRole.MANAGER: {
                "profile": ["read", "update"],
                "payslip": ["read"],
                "attendance": ["read", "create"],
                "leaves": ["read", "create", "approve"],
                "reimbursements": ["read", "create", "approve"],
                "team": ["read"],
                "reports": ["read"]
            },
            UserRole.ADMIN: {
                "profile": ["read", "update"],
                "payslip": ["read"],
                "attendance": ["read", "create", "update", "delete"],
                "leaves": ["read", "create", "update", "delete", "approve"],
                "reimbursements": ["read", "create", "update", "delete", "approve"],
                "users": ["read", "create", "update", "delete"],
                "reports": ["read", "create"],
                "payroll": ["read", "create", "update", "delete"],
                "policies": ["read", "create", "update", "delete"],
                "system": ["read", "update"],
                "audit": ["read"]
            }
        }
        
        return role_resource_permissions.get(self.role, {})
    
    def get_all_permissions(self) -> List[str]:
        """Get all permissions for this user"""
        permissions = self._get_role_permissions().copy()
        permissions.extend(self.custom_permissions)
        return list(set(permissions))  # Remove duplicates
    
    def get_all_resource_permissions(self) -> Dict[str, List[str]]:
        """Get all resource permissions for this user"""
        permissions = self._get_role_resource_permissions().copy()
        
        # Merge custom resource permissions
        for resource, actions in self.resource_permissions.items():
            if resource in permissions:
                permissions[resource].extend(actions)
                permissions[resource] = list(set(permissions[resource]))  # Remove duplicates
            else:
                permissions[resource] = actions.copy()
        
        return permissions
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "role": self.role.value,
            "custom_permissions": self.custom_permissions,
            "resource_permissions": self.resource_permissions,
            "computed_permissions": {
                "all_permissions": self.get_all_permissions(),
                "all_resource_permissions": self.get_all_resource_permissions(),
                "is_admin": self.is_admin(),
                "is_superadmin": self.is_superadmin(),
                "can_manage_users": self.can_manage_users(),
                "can_view_reports": self.can_view_reports(),
                "can_approve_requests": self.can_approve_requests(),
                "can_access_payroll": self.can_access_payroll(),
                "can_manage_organisation": self.can_manage_organisation()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserPermissions':
        """Create from dictionary"""
        return cls(
            role=UserRole(data["role"]),
            custom_permissions=data.get("custom_permissions", []),
            resource_permissions=data.get("resource_permissions", {})
        )
    
    @classmethod
    def create_for_role(cls, role: UserRole) -> 'UserPermissions':
        """Create permissions for a specific role with default settings"""
        return cls(role=role)
    
    def __str__(self) -> str:
        """String representation"""
        return f"UserPermissions(role={self.role.value}, custom_perms={len(self.custom_permissions)})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"UserPermissions(role={self.role}, custom_permissions={self.custom_permissions}, resource_permissions={self.resource_permissions})" 