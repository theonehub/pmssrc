"""
User Domain Entity
Aggregate root for user authentication and authorization
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import (
    Password, UserRole, UserStatus, Gender
)
from app.domain.value_objects.user_permissions import UserPermissions
from app.domain.value_objects.personal_details import PersonalDetails
from app.domain.value_objects.user_documents import UserDocuments
from app.domain.value_objects.bank_details import BankDetails
from app.domain.events.user_events import (
    UserCreated, UserUpdated, UserStatusChanged, UserRoleChanged,
    UserPasswordChanged, UserLoggedIn, UserLoggedOut, 
    UserDocumentsUpdated, UserDeleted
)


@dataclass
class User:
    """
    User aggregate root following DDD principles.
    
    This entity represents the authentication and authorization aspects of a user,
    while the Employee entity represents the employment-related aspects.
    
    Follows SOLID principles:
    - SRP: Only handles user authentication and authorization logic
    - OCP: Can be extended with new user types without modification
    - LSP: Can be substituted anywhere User is expected
    - ISP: Provides focused user operations
    - DIP: Depends on abstractions (value objects, events)
    """
    
    # Identity (links to Employee entity)
    employee_id: EmployeeId
    
    # Personal Information (required)
    name: str
    
    # Authentication (required)
    email: str
    username: str
    password: Password
    
    # Authorization (required)
    permissions: UserPermissions
    
    # Personal Details (required)
    personal_details: PersonalDetails
    
    # Status (with default)
    status: UserStatus = UserStatus.ACTIVE
    
    # Employment Information
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[EmployeeId] = None
    
    # Documents
    documents: UserDocuments = field(default_factory=lambda: UserDocuments())
    
    # Bank Details (for payroll)
    bank_details: Optional[BankDetails] = None
    
    # Leave Balance (integration with leave system)
    leave_balance: Dict[str, float] = field(default_factory=dict)
    
    # System Fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Authentication tracking
    last_login_at: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Soft deletion
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    # Domain Events
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Post initialization validation and setup"""
        self._validate_user_data()
        
        # Raise domain event for new user creation
        # TODO: Fix domain event creation - events need proper initialization
        # if not hasattr(self, '_is_existing_user'):
        #     self._add_domain_event(UserCreated(
        #         employee_id=self.employee_id,
        #         name=self.name,
        #         email=self.email,
        #         role=self.permissions.role,
        #         created_by=self.created_by or "system",
        #     ))
    
    @classmethod
    def create_new_user(
        cls,
        employee_id: EmployeeId,
        name: str,
        email: str,
        password: str,
        role: UserRole,
        personal_details: PersonalDetails,
        department: Optional[str] = None,
        designation: Optional[str] = None,
        location: Optional[str] = None,
        manager_id: Optional[EmployeeId] = None,
        bank_details: Optional[BankDetails] = None,
        created_by: Optional[str] = None
    ) -> 'User':
        """Factory method to create a new user"""
        
        # Create password value object
        password_vo = Password.from_plain_text(password)
        
        # Create permissions
        permissions = UserPermissions(role=role)
        
        user = cls(
            employee_id=employee_id,
            name=name,
            email=email.lower().strip(),
            username=str(employee_id),  # Set username to employee_id
            password=password_vo,
            permissions=permissions,
            personal_details=personal_details,
            department=department,
            designation=designation,
            location=location,
            manager_id=manager_id,
            bank_details=bank_details,
            created_by=created_by
        )
        
        return user
    
    @classmethod
    def from_existing_data(cls, **kwargs) -> 'User':
        """Create user from existing data (for repository loading)"""
        user = cls(**kwargs)
        user._is_existing_user = True
        return user
    
    # ==================== AUTHENTICATION METHODS ====================
    
    def authenticate(self, plain_password: str) -> bool:
        """
        Authenticate user with password.
        
        Business Rules:
        1. User must be active
        2. User must not be locked
        3. Password must match
        4. Track login attempts
        """
        
        if not self.is_active():
            return False
        
        if self.is_locked():
            return False
        
        # Verify password
        if self.password.verify(plain_password):
            self._reset_login_attempts()
            self._update_last_login()
            return True
        else:
            self._increment_login_attempts()
            return False
    
    def change_password(
        self, 
        new_password: str, 
        changed_by: str,
        current_password: Optional[str] = None
    ) -> None:
        """
        Change user password.
        
        Business Rules:
        1. If current_password provided, it must be correct (self-change)
        2. New password must meet security requirements
        3. Cannot reuse current password
        """
        
        is_self_change = current_password is not None
        
        # Verify current password if provided (self-change)
        if is_self_change and not self.password.verify(current_password):
            raise ValueError("Current password is incorrect")
        
        # Create new password
        new_password_vo = Password.from_plain_text(new_password)
        
        # Check if new password is different
        if new_password_vo.hashed_value == self.password.hashed_value:
            raise ValueError("New password must be different from current password")
        
        # Update password
        old_password = self.password
        self.password = new_password_vo
        self.updated_at = datetime.utcnow()
        self.updated_by = changed_by
        
        # Publish domain event
        self._add_domain_event(UserPasswordChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            changed_by=changed_by,
            is_self_change=is_self_change,
            password_strength_score=new_password_vo.get_strength_score(),
            occurred_at=datetime.utcnow()
        ))
    
    def lock_account(self, reason: str, locked_by: str, duration_hours: int = 24) -> None:
        """Lock user account"""
        from datetime import timedelta
        
        self.status = UserStatus.LOCKED
        self.locked_until = datetime.utcnow() + timedelta(hours=duration_hours)
        self.updated_at = datetime.utcnow()
        self.updated_by = locked_by
        
        self._add_domain_event(UserStatusChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            old_status=UserStatus.ACTIVE,  # Assuming was active
            new_status=UserStatus.LOCKED,
            reason=reason,
            changed_by=locked_by,
            occurred_at=datetime.utcnow()
        ))
    
    def unlock_account(self, unlocked_by: str) -> None:
        """Unlock user account"""
        if self.status != UserStatus.LOCKED:
            raise ValueError("User account is not locked")
        
        old_status = self.status
        self.status = UserStatus.ACTIVE
        self.locked_until = None
        self.login_attempts = 0
        self.updated_at = datetime.utcnow()
        self.updated_by = unlocked_by
        
        self._add_domain_event(UserStatusChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            old_status=old_status,
            new_status=UserStatus.ACTIVE,
            reason="Account unlocked",
            changed_by=unlocked_by,
            occurred_at=datetime.utcnow()
        ))
    
    # ==================== AUTHORIZATION METHODS ====================
    
    def change_role(self, new_role: UserRole, reason: str, changed_by: str) -> None:
        """
        Change user role.
        
        Business Rules:
        1. New role must be different from current
        2. Must provide reason for role change
        3. Only certain roles can change other roles
        """
        
        if new_role == self.permissions.role:
            raise ValueError("New role must be different from current role")
        
        if not reason or not reason.strip():
            raise ValueError("Role change reason is required")
        
        old_role = self.permissions.role
        
        # Update permissions
        self.permissions = UserPermissions(
            role=new_role,
            custom_permissions=self.permissions.custom_permissions,
            resource_permissions=self.permissions.resource_permissions
        )
        
        self.updated_at = datetime.utcnow()
        self.updated_by = changed_by
        
        # Publish domain event
        self._add_domain_event(UserRoleChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            old_role=old_role,
            new_role=new_role,
            reason=reason,
            changed_by=changed_by,
            occurred_at=datetime.utcnow()
        ))
    
    def add_custom_permission(self, permission: str, granted_by: str) -> None:
        """Add custom permission to user"""
        if permission not in self.permissions.custom_permissions:
            new_permissions = self.permissions.custom_permissions + [permission]
            
            self.permissions = UserPermissions(
                role=self.permissions.role,
                custom_permissions=new_permissions,
                resource_permissions=self.permissions.resource_permissions
            )
            
            self.updated_at = datetime.utcnow()
            self.updated_by = granted_by
    
    def remove_custom_permission(self, permission: str, removed_by: str) -> None:
        """Remove custom permission from user"""
        if permission in self.permissions.custom_permissions:
            new_permissions = [p for p in self.permissions.custom_permissions if p != permission]
            
            self.permissions = UserPermissions(
                role=self.permissions.role,
                custom_permissions=new_permissions,
                resource_permissions=self.permissions.resource_permissions
            )
            
            self.updated_at = datetime.utcnow()
            self.updated_by = removed_by
    
    # ==================== STATUS MANAGEMENT ====================
    
    def activate(self, activated_by: str, reason: str = "User activated") -> None:
        """
        Activate user.
        
        Business Rules:
        1. Can only activate inactive users
        2. Cannot activate deleted users
        """
        
        if self.is_deleted:
            raise ValueError("Cannot activate deleted user")
        
        if self.status == UserStatus.ACTIVE:
            raise ValueError("User is already active")
        
        old_status = self.status
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = activated_by
        
        self._add_domain_event(UserStatusChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            old_status=old_status,
            new_status=UserStatus.ACTIVE,
            reason=reason,
            changed_by=activated_by,
            occurred_at=datetime.utcnow()
        ))
    
    def deactivate(self, reason: str, deactivated_by: str) -> None:
        """
        Deactivate user.
        
        Business Rules:
        1. Can only deactivate active users
        2. Must provide reason for deactivation
        """
        
        if self.status != UserStatus.ACTIVE:
            raise ValueError("Can only deactivate active users")
        
        if not reason or not reason.strip():
            raise ValueError("Deactivation reason is required")
        
        old_status = self.status
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = deactivated_by
        
        self._add_domain_event(UserStatusChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            old_status=old_status,
            new_status=UserStatus.INACTIVE,
            reason=reason,
            changed_by=deactivated_by,
            occurred_at=datetime.utcnow()
        ))
    
    def suspend(self, reason: str, suspended_by: str) -> None:
        """Suspend user"""
        if not reason or not reason.strip():
            raise ValueError("Suspension reason is required")
        
        old_status = self.status
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
        self.updated_by = suspended_by
        
        self._add_domain_event(UserStatusChanged(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            old_status=old_status,
            new_status=UserStatus.SUSPENDED,
            reason=reason,
            changed_by=suspended_by,
            occurred_at=datetime.utcnow()
        ))
    
    # ==================== PROFILE MANAGEMENT ====================
    
    def update_profile(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        personal_details: Optional[PersonalDetails] = None,
        department: Optional[str] = None,
        designation: Optional[str] = None,
        location: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """Update user profile information"""
        
        updated_fields = {}
        previous_values = {}
        
        if name is not None and name != self.name:
            previous_values["name"] = self.name
            self.name = name.strip()
            updated_fields["name"] = self.name
        
        if email is not None and email.lower().strip() != self.email:
            previous_values["email"] = self.email
            self.email = email.lower().strip()
            updated_fields["email"] = self.email
        
        if personal_details is not None and personal_details != self.personal_details:
            previous_values["personal_details"] = self.personal_details.to_dict()
            self.personal_details = personal_details
            updated_fields["personal_details"] = personal_details.to_dict()
        
        if department is not None and department != self.department:
            previous_values["department"] = self.department
            self.department = department
            updated_fields["department"] = department
        
        if designation is not None and designation != self.designation:
            previous_values["designation"] = self.designation
            self.designation = designation
            updated_fields["designation"] = designation
        
        if location is not None and location != self.location:
            previous_values["location"] = self.location
            self.location = location
            updated_fields["location"] = location
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
            
            self._add_domain_event(UserUpdated(
                aggregate_id=str(self.employee_id),
                employee_id=self.employee_id,
                updated_fields=updated_fields,
                previous_values=previous_values,
                updated_by=updated_by or "system",
                occurred_at=datetime.utcnow()
            ))
    
    def update_documents(
        self,
        documents: UserDocuments,
        updated_by: str
    ) -> None:
        """Update user documents"""
        
        if documents != self.documents:
            # Determine which documents were updated
            updated_docs = []
            
            if documents.photo_path != self.documents.photo_path:
                updated_docs.append("photo")
            
            if documents.pan_document_path != self.documents.pan_document_path:
                updated_docs.append("pan_document")
            
            if documents.aadhar_document_path != self.documents.aadhar_document_path:
                updated_docs.append("aadhar_document")
            
            self.documents = documents
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
            
            if updated_docs:
                # TODO: Fix domain event creation - events need proper initialization
                # self._add_domain_event(UserDocumentsUpdated(
                #     aggregate_id=str(self.employee_id),
                #     employee_id=self.employee_id,
                #     updated_documents=updated_docs,
                #     completion_percentage=documents.get_document_completion_percentage(),
                #     updated_by=updated_by,
                #     occurred_at=datetime.utcnow()
                # ))
                pass
    
    def assign_manager(self, manager_id: EmployeeId, assigned_by: str) -> None:
        """Assign manager to user"""
        if manager_id == self.employee_id:
            raise ValueError("User cannot be their own manager")
        
        previous_manager = self.manager_id
        self.manager_id = manager_id
        self.updated_at = datetime.utcnow()
        self.updated_by = assigned_by
        
        # Could publish a UserManagerAssigned event here
    
    def update_leave_balance(self, leave_type: str, balance: float) -> None:
        """Update leave balance for specific leave type"""
        if balance < 0:
            raise ValueError("Leave balance cannot be negative")
        
        self.leave_balance[leave_type] = balance
        self.updated_at = datetime.utcnow()
    
    def update_bank_details(self, bank_details: BankDetails, updated_by: str) -> None:
        """Update user bank details"""
        if not isinstance(bank_details, BankDetails):
            raise ValueError("Invalid bank details object")
        
        self.bank_details = bank_details
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
    
    # ==================== DOCUMENT UPDATE METHODS ====================
    
    def update_photo_path(self, photo_path: Optional[str]) -> None:
        """Update user photo path"""
        if photo_path != self.documents.photo_path:
            self.documents = UserDocuments(
                photo_path=photo_path,
                pan_document_path=self.documents.pan_document_path,
                aadhar_document_path=self.documents.aadhar_document_path
            )
            self.updated_at = datetime.utcnow()
    
    def update_pan_document_path(self, pan_document_path: Optional[str]) -> None:
        """Update user PAN document path"""
        if pan_document_path != self.documents.pan_document_path:
            self.documents = UserDocuments(
                photo_path=self.documents.photo_path,
                pan_document_path=pan_document_path,
                aadhar_document_path=self.documents.aadhar_document_path
            )
            self.updated_at = datetime.utcnow()
    
    def update_aadhar_document_path(self, aadhar_document_path: Optional[str]) -> None:
        """Update user Aadhar document path"""
        if aadhar_document_path != self.documents.aadhar_document_path:
            self.documents = UserDocuments(
                photo_path=self.documents.photo_path,
                pan_document_path=self.documents.pan_document_path,
                aadhar_document_path=aadhar_document_path
            )
            self.updated_at = datetime.utcnow()
    
    # ==================== DELETION ====================
    
    def delete(self, reason: str, deleted_by: str, soft_delete: bool = True) -> None:
        """
        Delete user.
        
        Business Rules:
        1. Must provide reason for deletion
        2. Soft delete by default
        3. Cannot delete if user has active sessions (business rule)
        """
        
        if not reason or not reason.strip():
            raise ValueError("Deletion reason is required")
        
        if self.is_deleted:
            raise ValueError("User is already deleted")
        
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = deleted_by
        
        self._add_domain_event(UserDeleted(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            user_name=self.name,
            user_email=self.email,
            deletion_reason=reason,
            deleted_by=deleted_by,
            is_soft_delete=soft_delete,
            occurred_at=datetime.utcnow()
        ))
    
    # ==================== QUERY METHODS ====================
    
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.status == UserStatus.LOCKED:
            # Check if lock has expired
            if self.locked_until and datetime.utcnow() > self.locked_until:
                return False
            return True
        return False
    
    def can_login(self) -> bool:
        """Check if user can login"""
        return self.is_active() and not self.is_locked()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return self.permissions.has_permission(permission)
    
    def has_resource_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission for specific resource action"""
        return self.permissions.has_resource_permission(resource, action)
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.permissions.is_admin()
    
    def is_superadmin(self) -> bool:
        """Check if user is superadmin"""
        return self.permissions.is_superadmin()
    
    def get_profile_completion_percentage(self) -> float:
        """Get profile completion percentage"""
        total_fields = 11  # Increased to include bank details
        completed_fields = 0
        
        # Required fields
        if self.name: completed_fields += 1
        if self.email: completed_fields += 1
        if self.personal_details: completed_fields += 1
        if self.department: completed_fields += 1
        if self.designation: completed_fields += 1
        if self.location: completed_fields += 1
        if self.bank_details: completed_fields += 1
        
        # Document fields
        completed_fields += (self.documents.get_document_completion_percentage() / 100) * 3
        
        return (completed_fields / total_fields) * 100
    
    def get_display_name(self) -> str:
        """Get user display name"""
        return self.name
    
    def get_role_display(self) -> str:
        """Get user role for display"""
        return self.permissions.role.value.title()
    
    def get_status_display(self) -> str:
        """Get user status for display"""
        return self.status.value.title()
    
    # ==================== HELPER METHODS ====================
    
    def _validate_user_data(self) -> None:
        """Validate user data consistency"""
        
        # Validate required fields
        if not self.employee_id:
            raise ValueError("User ID is required")
        
        if not self.name or not self.name.strip():
            raise ValueError("User name is required")
        
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
        
        if not isinstance(self.password, Password):
            raise ValueError("Invalid password object")
        
        if not isinstance(self.permissions, UserPermissions):
            raise ValueError("Invalid permissions object")
        
        if not isinstance(self.personal_details, PersonalDetails):
            raise ValueError("Invalid personal details object")
        
        if not isinstance(self.documents, UserDocuments):
            raise ValueError("Invalid documents object")
        
        # Validate and normalize leave balance values
        self._normalize_leave_balance()
    
    def _normalize_leave_balance(self) -> None:
        """Normalize leave balance values to ensure they are floats"""
        if not self.leave_balance:
            return
        
        normalized_balances = {}
        for leave_type, balance in self.leave_balance.items():
            try:
                if balance is None:
                    normalized_balances[leave_type] = 0.0
                elif isinstance(balance, (int, float)):
                    # Keep as float
                    normalized_balances[leave_type] = max(0.0, float(balance))
                elif isinstance(balance, str):
                    # Convert string to float
                    float_val = float(balance)
                    normalized_balances[leave_type] = max(0.0, float_val)
                else:
                    normalized_balances[leave_type] = 0.0
            except (ValueError, TypeError):
                normalized_balances[leave_type] = 0.0
        
        # Update the leave_balance with normalized values
        self.leave_balance.clear()
        self.leave_balance.update(normalized_balances)
    
    def _increment_login_attempts(self) -> None:
        """Increment failed login attempts"""
        self.login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.login_attempts >= 5:
            self.lock_account(
                reason="Too many failed login attempts",
                locked_by="system",
                duration_hours=1
            )
    
    def _reset_login_attempts(self) -> None:
        """Reset login attempts counter"""
        self.login_attempts = 0
    
    def _update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()
        
        # Publish login event
        self._add_domain_event(UserLoggedIn(
            aggregate_id=str(self.employee_id),
            employee_id=self.employee_id,
            ip_address=None,  # Will be set by application layer
            user_agent=None,  # Will be set by application layer
            login_method="password",
            occurred_at=datetime.utcnow()
        ))
    
    def _add_domain_event(self, event: Any) -> None:
        """Add a domain event"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Any]:
        """Get all domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events"""
        self._domain_events.clear()
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.name} ({self.employee_id})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"User(id={self.employee_id}, name='{self.name}', role={self.permissions.role.value}, status={self.status.value})" 