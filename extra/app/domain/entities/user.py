"""
User Domain Entity
Rich domain entity with business behavior
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email


@dataclass
class User:
    """
    User domain entity with rich behavior.
    
    Represents a user in the system with all business rules
    and behaviors encapsulated within the entity.
    """
    
    id: UserId
    employee_id: str
    username: str
    email: Email
    full_name: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    is_superuser: bool = False
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        id: UserId,
        employee_id: str,
        username: str,
        email: Email,
        full_name: str,
        password_hash: str,
        created_by: str,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None
    ) -> 'User':
        """Create a new user entity."""
        now = datetime.utcnow()
        
        return cls(
            id=id,
            employee_id=employee_id,
            username=username,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            roles=roles or [],
            permissions=permissions or [],
            is_active=True,
            is_superuser=False,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by
        )
    
    def update(
        self,
        username: Optional[str] = None,
        email: Optional[Email] = None,
        full_name: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """Update user information."""
        if username is not None:
            self.username = username
        
        if email is not None:
            self.email = email
        
        if full_name is not None:
            self.full_name = full_name
        
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by
    
    def activate(self, activated_by: str) -> None:
        """Activate the user."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
        self.updated_by = activated_by
    
    def deactivate(self, deactivated_by: str) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        self.updated_by = deactivated_by
    
    def add_role(self, role: str, updated_by: str) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
    
    def remove_role(self, role: str, updated_by: str) -> None:
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
    
    def add_permission(self, permission: str, updated_by: str) -> None:
        """Add a permission to the user."""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
    
    def remove_permission(self, permission: str, updated_by: str) -> None:
        """Remove a permission from the user."""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
    
    def update_password(self, password_hash: str, updated_by: str) -> None:
        """Update user password hash."""
        self.password_hash = password_hash
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
    
    def record_login(self) -> None:
        """Record user login timestamp."""
        self.last_login = datetime.utcnow()
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles or self.is_superuser
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or self.is_superuser
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(self.has_role(role) for role in roles)
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(perm) for perm in permissions)
    
    def can_login(self) -> bool:
        """Check if user can login."""
        return self.is_active and self.password_hash is not None
    
    def is_new(self) -> bool:
        """Check if this is a new entity (not persisted)."""
        return self.created_at is None
    
    def __str__(self) -> str:
        """String representation of user."""
        return f"User({self.username} - {self.email.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of user."""
        return (
            f"User(id={self.id.value}, username={self.username}, "
            f"email={self.email.value}, is_active={self.is_active})"
        ) 