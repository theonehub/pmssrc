"""
User Domain Events
Events that represent important business occurrences in the user domain
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from app.domain.events.base_event import DomainEvent
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import UserRole, UserStatus


@dataclass
class UserCreated(DomainEvent):
    """
    Event raised when a new user is created.
    
    This event can trigger:
    - Welcome email sending
    - Account setup processes
    - Onboarding workflow initiation
    - Audit logging
    - Integration with external systems
    """
    
    employee_id: EmployeeId
    name: str
    email: str
    role: UserRole
    created_by: str
    
    def get_event_type(self) -> str:
        return "user.created"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserCreated':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            name=data["name"],
            email=data["email"],
            role=UserRole(data["role"]),
            created_by=data["created_by"]
        )


@dataclass
class UserUpdated(DomainEvent):
    """
    Event raised when user information is updated.
    
    This event can trigger:
    - Profile synchronization
    - Cache invalidation
    - Notification to administrators
    - Audit trail updates
    """
    
    employee_id: EmployeeId
    updated_fields: Dict[str, Any]
    previous_values: Dict[str, Any]
    updated_by: str
    
    def get_event_type(self) -> str:
        return "user.updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def get_changed_fields(self) -> list:
        """Get list of changed field names"""
        return list(self.updated_fields.keys())
    
    def has_sensitive_changes(self) -> bool:
        """Check if sensitive information was changed"""
        sensitive_fields = ["email", "role", "permissions", "password"]
        return any(field in self.updated_fields for field in sensitive_fields)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "updated_fields": self.updated_fields,
            "previous_values": self.previous_values,
            "updated_by": self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserUpdated':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            updated_fields=data["updated_fields"],
            previous_values=data["previous_values"],
            updated_by=data["updated_by"]
        )


@dataclass
class UserStatusChanged(DomainEvent):
    """
    Event raised when user status changes.
    
    This event can trigger:
    - Access control updates
    - Session management
    - Notification to user and administrators
    - Compliance reporting
    """
    
    employee_id: EmployeeId
    old_status: UserStatus
    new_status: UserStatus
    reason: str
    changed_by: str
    
    def get_event_type(self) -> str:
        return "user.status_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def is_activation(self) -> bool:
        """Check if this is a user activation"""
        return (self.old_status in [UserStatus.INACTIVE, UserStatus.PENDING_ACTIVATION] 
                and self.new_status == UserStatus.ACTIVE)
    
    def is_deactivation(self) -> bool:
        """Check if this is a user deactivation"""
        return (self.old_status == UserStatus.ACTIVE 
                and self.new_status in [UserStatus.INACTIVE, UserStatus.SUSPENDED])
    
    def is_suspension(self) -> bool:
        """Check if this is a user suspension"""
        return self.new_status == UserStatus.SUSPENDED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "old_status": self.old_status.value,
            "new_status": self.new_status.value,
            "reason": self.reason,
            "changed_by": self.changed_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStatusChanged':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            old_status=UserStatus(data["old_status"]),
            new_status=UserStatus(data["new_status"]),
            reason=data["reason"],
            changed_by=data["changed_by"]
        )


@dataclass
class UserRoleChanged(DomainEvent):
    """
    Event raised when user role changes.
    
    This event can trigger:
    - Permission updates
    - Access control recalculation
    - Notification to administrators
    - Security audit logging
    """
    
    employee_id: EmployeeId
    old_role: UserRole
    new_role: UserRole
    reason: str
    changed_by: str
    
    def get_event_type(self) -> str:
        return "user.role_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def is_privilege_escalation(self) -> bool:
        """Check if this is a privilege escalation"""
        role_hierarchy = {
            UserRole.READONLY: 0,
            UserRole.USER: 1,
            UserRole.MANAGER: 2,
            UserRole.HR: 3,
            UserRole.FINANCE: 3,
            UserRole.ADMIN: 4,
            UserRole.SUPERADMIN: 5
        }
        
        old_level = role_hierarchy.get(self.old_role, 0)
        new_level = role_hierarchy.get(self.new_role, 0)
        
        return new_level > old_level
    
    def is_privilege_reduction(self) -> bool:
        """Check if this is a privilege reduction"""
        role_hierarchy = {
            UserRole.READONLY: 0,
            UserRole.USER: 1,
            UserRole.MANAGER: 2,
            UserRole.HR: 3,
            UserRole.FINANCE: 3,
            UserRole.ADMIN: 4,
            UserRole.SUPERADMIN: 5
        }
        
        old_level = role_hierarchy.get(self.old_role, 0)
        new_level = role_hierarchy.get(self.new_role, 0)
        
        return new_level < old_level
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "old_role": self.old_role.value,
            "new_role": self.new_role.value,
            "reason": self.reason,
            "changed_by": self.changed_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserRoleChanged':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            old_role=UserRole(data["old_role"]),
            new_role=UserRole(data["new_role"]),
            reason=data["reason"],
            changed_by=data["changed_by"]
        )


@dataclass
class UserPasswordChanged(DomainEvent):
    """
    Event raised when user password is changed.
    
    This event can trigger:
    - Security notifications
    - Session invalidation
    - Audit logging
    - Password policy compliance checks
    """
    
    employee_id: EmployeeId
    changed_by: str
    is_self_change: bool
    password_strength_score: int
    
    def get_event_type(self) -> str:
        return "user.password_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def is_admin_reset(self) -> bool:
        """Check if this was an admin password reset"""
        return not self.is_self_change
    
    def has_weak_password(self) -> bool:
        """Check if the new password is weak"""
        return self.password_strength_score < 60
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "changed_by": self.changed_by,
            "is_self_change": self.is_self_change,
            "password_strength_score": self.password_strength_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPasswordChanged':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            changed_by=data["changed_by"],
            is_self_change=data["is_self_change"],
            password_strength_score=data["password_strength_score"]
        )


@dataclass
class UserLoggedIn(DomainEvent):
    """
    Event raised when user successfully logs in.
    
    This event can trigger:
    - Session tracking
    - Security monitoring
    - Usage analytics
    - Last login updates
    """
    
    employee_id: EmployeeId
    ip_address: Optional[str]
    user_agent: Optional[str]
    login_method: str  # "password", "sso", "token", etc.
    
    def get_event_type(self) -> str:
        return "user.logged_in"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "login_method": self.login_method
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserLoggedIn':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            login_method=data["login_method"]
        )


@dataclass
class UserLoggedOut(DomainEvent):
    """
    Event raised when user logs out.
    
    This event can trigger:
    - Session cleanup
    - Usage analytics
    - Security monitoring
    """
    
    employee_id: EmployeeId
    session_duration_minutes: Optional[int]
    logout_method: str  # "manual", "timeout", "forced", etc.
    
    def get_event_type(self) -> str:
        return "user.logged_out"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "session_duration_minutes": self.session_duration_minutes,
            "logout_method": self.logout_method
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserLoggedOut':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            session_duration_minutes=data.get("session_duration_minutes"),
            logout_method=data["logout_method"]
        )


@dataclass
class UserDocumentsUpdated(DomainEvent):
    """
    Event raised when user documents are updated.
    
    This event can trigger:
    - Document verification workflows
    - Compliance checks
    - Notification to HR
    - Profile completion tracking
    """
    
    employee_id: EmployeeId
    updated_documents: list  # List of document types updated
    completion_percentage: float
    updated_by: str
    
    def get_event_type(self) -> str:
        return "user.documents_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def is_profile_complete(self) -> bool:
        """Check if user profile is now complete"""
        return self.completion_percentage >= 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "updated_documents": self.updated_documents,
            "completion_percentage": self.completion_percentage,
            "updated_by": self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserDocumentsUpdated':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            updated_documents=data["updated_documents"],
            completion_percentage=data["completion_percentage"],
            updated_by=data["updated_by"]
        )


@dataclass
class UserDeleted(DomainEvent):
    """
    Event raised when user is deleted.
    
    This event can trigger:
    - Data cleanup processes
    - Access revocation
    - Audit logging
    - Notification to administrators
    """
    
    employee_id: EmployeeId
    user_name: str
    user_email: str
    deletion_reason: str
    deleted_by: str
    is_soft_delete: bool
    
    def get_event_type(self) -> str:
        return "user.deleted"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.get_aggregate_id(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": str(self.employee_id),
            "user_name": self.user_name,
            "user_email": self.user_email,
            "deletion_reason": self.deletion_reason,
            "deleted_by": self.deleted_by,
            "is_soft_delete": self.is_soft_delete
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserDeleted':
        return cls(
            aggregate_id=data["aggregate_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            employee_id=EmployeeId.from_string(data["employee_id"]),
            user_name=data["user_name"],
            user_email=data["user_email"],
            deletion_reason=data["deletion_reason"],
            deleted_by=data["deleted_by"],
            is_soft_delete=data["is_soft_delete"]
        ) 