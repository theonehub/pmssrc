"""
Organization Domain Entity
Aggregate root for organization management following DDD patterns
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.organization_details import (
    ContactInformation, Address, TaxInformation, OrganizationType, OrganizationStatus
)
from app.domain.events.organization_events import (
    OrganizationCreated, OrganizationUpdated, OrganizationActivated,
    OrganizationDeactivated, OrganizationSuspended, OrganizationContactUpdated,
    OrganizationAddressUpdated, OrganizationTaxInfoUpdated,
    OrganizationEmployeeStrengthUpdated, OrganizationDeleted
)


logger = logging.getLogger(__name__)


@dataclass
class Organization:
    """
    Organization aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles organization-related business logic
    - OCP: Can be extended with new organization types without modification
    - LSP: Can be substituted anywhere Organization is expected
    - ISP: Provides focused organization operations
    - DIP: Depends on abstractions (value objects, events)
    
    Domain Events:
    - OrganizationCreated: When organization is created
    - OrganizationUpdated: When organization details are updated
    - OrganizationActivated: When organization is activated
    - OrganizationDeactivated: When organization is deactivated
    - OrganizationSuspended: When organization is suspended
    - OrganizationContactUpdated: When contact info is updated
    - OrganizationAddressUpdated: When address is updated
    - OrganizationTaxInfoUpdated: When tax info is updated
    - OrganizationEmployeeStrengthUpdated: When employee capacity is updated
    - OrganizationDeleted: When organization is deleted
    """
    
    # Identity
    organization_id: OrganizationId
    
    # Basic Information
    name: str
    description: Optional[str] = None
    organization_type: OrganizationType = OrganizationType.PRIVATE_LIMITED
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    
    # Contact and Location
    contact_info: ContactInformation = None
    address: Address = None
    
    # Tax Information
    tax_info: TaxInformation = None
    
    # Employee Management
    employee_strength: int = 0
    used_employee_strength: int = 0
    
    # System Configuration
    hostname: Optional[str] = None
    logo_path: Optional[str] = None
    
    # System Fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Domain Events
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Post initialization validation and setup"""
        self._validate_organization_data()
        
        # Raise domain event for new organization creation
        if not hasattr(self, '_is_existing_organization'):
            self._domain_events.append(
                OrganizationCreated(
                    organization_id=self.organization_id,
                    name=self.name,
                    organization_type=self.organization_type,
                    contact_info=self.contact_info,
                    address=self.address,
                    created_by=self.created_by or "system",
                    occurred_at=datetime.utcnow()
                )
            )
    
    # ==================== FACTORY METHODS ====================
    
    @classmethod
    def create_new_organization(
        cls,
        name: str,
        contact_info: ContactInformation,
        address: Address,
        tax_info: TaxInformation,
        organization_type: OrganizationType = OrganizationType.PRIVATE_LIMITED,
        employee_strength: int = 10,
        hostname: Optional[str] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> 'Organization':
        """Factory method to create a new organization"""
        
        organization_id = OrganizationId.generate()
        
        organization = cls(
            organization_id=organization_id,
            name=name,
            description=description,
            organization_type=organization_type,
            contact_info=contact_info,
            address=address,
            tax_info=tax_info,
            employee_strength=employee_strength,
            hostname=hostname,
            created_by=created_by
        )
        
        return organization
    
    @classmethod
    def from_existing_data(cls, **kwargs) -> 'Organization':
        """Create organization from existing data (for repository loading)"""
        # Convert string IDs to value objects if needed
        if 'organization_id' in kwargs and isinstance(kwargs['organization_id'], str):
            kwargs['organization_id'] = OrganizationId.from_string(kwargs['organization_id'])
        
        # Convert dict data to value objects if needed
        if 'contact_info' in kwargs and isinstance(kwargs['contact_info'], dict):
            kwargs['contact_info'] = ContactInformation.from_dict(kwargs['contact_info'])
        
        if 'address' in kwargs and isinstance(kwargs['address'], dict):
            kwargs['address'] = Address.from_dict(kwargs['address'])
        
        if 'tax_info' in kwargs and isinstance(kwargs['tax_info'], dict):
            kwargs['tax_info'] = TaxInformation.from_dict(kwargs['tax_info'])
        
        if 'organization_type' in kwargs and isinstance(kwargs['organization_type'], str):
            kwargs['organization_type'] = OrganizationType(kwargs['organization_type'])
        
        if 'status' in kwargs and isinstance(kwargs['status'], str):
            kwargs['status'] = OrganizationStatus(kwargs['status'])
        
        organization = cls(**kwargs)
        organization._is_existing_organization = True
        return organization
    
    # ==================== BUSINESS METHODS ====================
    
    def update_basic_info(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        organization_type: Optional[OrganizationType] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update basic organization information.
        
        Business Rules:
        1. Name cannot be empty
        2. Organization type changes may have restrictions
        """
        updated_fields = {}
        previous_values = {}
        
        if name is not None and name.strip() != self.name:
            if not name.strip():
                raise ValueError("Organization name cannot be empty")
            previous_values["name"] = self.name
            self.name = name.strip()
            updated_fields["name"] = self.name
        
        if description is not None and description != self.description:
            previous_values["description"] = self.description
            self.description = description
            updated_fields["description"] = self.description
        
        if organization_type is not None and organization_type != self.organization_type:
            previous_values["organization_type"] = self.organization_type.value
            self.organization_type = organization_type
            updated_fields["organization_type"] = self.organization_type.value
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
            
            # Publish domain event
            self._add_domain_event(OrganizationUpdated(
                organization_id=self.organization_id,
                updated_fields=updated_fields,
                updated_by=updated_by or "system",
                previous_values=previous_values,
                occurred_at=datetime.utcnow()
            ))
            
            logger.info(f"Organization {self.organization_id} basic info updated")
    
    def update_contact_info(
        self,
        new_contact_info: ContactInformation,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organization contact information.
        
        Business Rules:
        1. Contact information must be valid
        2. Email changes may require verification
        """
        if new_contact_info == self.contact_info:
            return  # No changes
        
        previous_contact_info = self.contact_info
        self.contact_info = new_contact_info
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        # Publish domain event
        self._add_domain_event(OrganizationContactUpdated(
            organization_id=self.organization_id,
            new_contact_info=new_contact_info,
            previous_contact_info=previous_contact_info,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} contact info updated")
    
    def update_address(
        self,
        new_address: Address,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organization address.
        
        Business Rules:
        1. Address must be valid
        2. Address changes may affect tax jurisdiction
        """
        if new_address == self.address:
            return  # No changes
        
        previous_address = self.address
        self.address = new_address
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        # Publish domain event
        self._add_domain_event(OrganizationAddressUpdated(
            organization_id=self.organization_id,
            new_address=new_address,
            previous_address=previous_address,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} address updated")
    
    def update_tax_info(
        self,
        new_tax_info: TaxInformation,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organization tax information.
        
        Business Rules:
        1. Tax information must be valid
        2. PAN number changes require special authorization
        3. GST changes may affect billing
        """
        if new_tax_info == self.tax_info:
            return  # No changes
        
        previous_tax_info = self.tax_info
        self.tax_info = new_tax_info
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        # Publish domain event
        self._add_domain_event(OrganizationTaxInfoUpdated(
            organization_id=self.organization_id,
            new_tax_info=new_tax_info,
            previous_tax_info=previous_tax_info,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} tax info updated")
    
    def update_employee_strength(
        self,
        new_employee_strength: int,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organization employee strength.
        
        Business Rules:
        1. Employee strength must be positive
        2. Cannot reduce below current used strength
        3. May affect licensing and billing
        """
        if new_employee_strength <= 0:
            raise ValueError("Employee strength must be positive")
        
        if new_employee_strength < self.used_employee_strength:
            raise ValueError(
                f"Cannot reduce employee strength below current usage "
                f"({self.used_employee_strength})"
            )
        
        if new_employee_strength == self.employee_strength:
            return  # No changes
        
        previous_strength = self.employee_strength
        self.employee_strength = new_employee_strength
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        # Publish domain event
        self._add_domain_event(OrganizationEmployeeStrengthUpdated(
            organization_id=self.organization_id,
            new_employee_strength=new_employee_strength,
            previous_employee_strength=previous_strength,
            current_used_strength=self.used_employee_strength,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} employee strength updated to {new_employee_strength}")
    
    def activate(self, activated_by: Optional[str] = None, reason: Optional[str] = None) -> None:
        """
        Activate the organization.
        
        Business Rules:
        1. Can only activate inactive or suspended organizations
        2. Cannot activate terminated organizations
        """
        if self.status == OrganizationStatus.ACTIVE:
            raise ValueError("Organization is already active")
        
        if self.status == OrganizationStatus.TERMINATED:
            raise ValueError("Cannot activate terminated organization")
        
        previous_status = self.status
        self.status = OrganizationStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = activated_by
        
        # Publish domain event
        self._add_domain_event(OrganizationActivated(
            organization_id=self.organization_id,
            activated_by=activated_by or "system",
            previous_status=previous_status,
            reason=reason,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} activated")
    
    def deactivate(self, reason: str, deactivated_by: Optional[str] = None) -> None:
        """
        Deactivate the organization.
        
        Business Rules:
        1. Can only deactivate active organizations
        2. Must provide reason for deactivation
        """
        if self.status != OrganizationStatus.ACTIVE:
            raise ValueError("Can only deactivate active organizations")
        
        if not reason or not reason.strip():
            raise ValueError("Deactivation reason is required")
        
        previous_status = self.status
        self.status = OrganizationStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = deactivated_by
        
        # Publish domain event
        self._add_domain_event(OrganizationDeactivated(
            organization_id=self.organization_id,
            deactivated_by=deactivated_by or "system",
            reason=reason,
            previous_status=previous_status,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} deactivated: {reason}")
    
    def suspend(
        self,
        reason: str,
        suspended_by: Optional[str] = None,
        suspension_duration: Optional[int] = None
    ) -> None:
        """
        Suspend the organization.
        
        Business Rules:
        1. Can suspend active or inactive organizations
        2. Must provide reason for suspension
        3. Cannot suspend already suspended organizations
        """
        if self.status == OrganizationStatus.SUSPENDED:
            raise ValueError("Organization is already suspended")
        
        if self.status == OrganizationStatus.TERMINATED:
            raise ValueError("Cannot suspend terminated organization")
        
        if not reason or not reason.strip():
            raise ValueError("Suspension reason is required")
        
        previous_status = self.status
        self.status = OrganizationStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
        self.updated_by = suspended_by
        
        # Publish domain event
        self._add_domain_event(OrganizationSuspended(
            organization_id=self.organization_id,
            suspended_by=suspended_by or "system",
            reason=reason,
            suspension_duration=suspension_duration,
            previous_status=previous_status,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} suspended: {reason}")
    
    def increment_used_employee_strength(self) -> None:
        """
        Increment used employee strength when adding an employee.
        
        Business Rules:
        1. Cannot exceed total employee strength
        """
        if self.used_employee_strength >= self.employee_strength:
            raise ValueError("Employee strength limit reached")
        
        self.used_employee_strength += 1
        self.updated_at = datetime.utcnow()
    
    def decrement_used_employee_strength(self) -> None:
        """
        Decrement used employee strength when removing an employee.
        
        Business Rules:
        1. Cannot go below zero
        """
        if self.used_employee_strength <= 0:
            raise ValueError("Used employee strength cannot be negative")
        
        self.used_employee_strength -= 1
        self.updated_at = datetime.utcnow()
    
    def delete(self, deletion_reason: str, deleted_by: Optional[str] = None) -> None:
        """
        Mark organization as deleted.
        
        Business Rules:
        1. Deletion reason is required
        2. Only admin can delete organization
        3. Cannot delete if has active employees
        """
        if not deletion_reason or not deletion_reason.strip():
            raise ValueError("Deletion reason is required")
        
        if self.used_employee_strength > 0:
            raise ValueError("Cannot delete organization with active employees")
        
        # Publish domain event
        self._add_domain_event(OrganizationDeleted(
            organization_id=self.organization_id,
            organization_name=self.name,
            deleted_by=deleted_by or "system",
            deletion_reason=deletion_reason,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organization {self.organization_id} deleted: {deletion_reason}")
    
    # ==================== QUERY METHODS ====================
    
    def is_active(self) -> bool:
        """Check if organization is active"""
        return self.status == OrganizationStatus.ACTIVE
    
    def is_government_organization(self) -> bool:
        """Check if organization is government type"""
        return self.organization_type == OrganizationType.GOVERNMENT
    
    def has_available_employee_capacity(self) -> bool:
        """Check if organization has available employee capacity"""
        return self.used_employee_strength < self.employee_strength
    
    def get_available_employee_capacity(self) -> int:
        """Get available employee capacity"""
        return max(0, self.employee_strength - self.used_employee_strength)
    
    def get_employee_utilization_percentage(self) -> float:
        """Get employee utilization percentage"""
        if self.employee_strength == 0:
            return 0.0
        return (self.used_employee_strength / self.employee_strength) * 100
    
    def is_gst_registered(self) -> bool:
        """Check if organization is GST registered"""
        return self.tax_info and self.tax_info.is_gst_registered()
    
    def get_display_name(self) -> str:
        """Get display name for organization"""
        return self.name
    
    def get_short_address(self) -> str:
        """Get short address"""
        return self.address.get_short_address() if self.address else ""
    
    def get_primary_email(self) -> str:
        """Get primary email"""
        return self.contact_info.email if self.contact_info else ""
    
    def get_primary_phone(self) -> str:
        """Get primary phone"""
        return self.contact_info.phone if self.contact_info else ""
    
    # ==================== HELPER METHODS ====================
    
    def _validate_organization_data(self) -> None:
        """Validate organization data consistency"""
        
        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Organization name is required")
        
        # Validate employee strength
        if self.employee_strength < 0:
            raise ValueError("Employee strength cannot be negative")
        
        if self.used_employee_strength < 0:
            raise ValueError("Used employee strength cannot be negative")
        
        if self.used_employee_strength > self.employee_strength:
            raise ValueError("Used employee strength cannot exceed total strength")
        
        # Validate required value objects
        if not isinstance(self.organization_id, OrganizationId):
            raise ValueError("Invalid organization ID")
        
        if self.contact_info and not isinstance(self.contact_info, ContactInformation):
            raise ValueError("Invalid contact information")
        
        if self.address and not isinstance(self.address, Address):
            raise ValueError("Invalid address")
        
        if self.tax_info and not isinstance(self.tax_info, TaxInformation):
            raise ValueError("Invalid tax information")
    
    def _add_domain_event(self, event: Any) -> None:
        """Add a domain event"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Any]:
        """Get all domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events"""
        self._domain_events.clear()
    
    # ==================== SERIALIZATION ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "organization_id": str(self.organization_id),
            "name": self.name,
            "description": self.description,
            "organization_type": self.organization_type.value,
            "status": self.status.value,
            "contact_info": self.contact_info.to_dict() if self.contact_info else None,
            "address": self.address.to_dict() if self.address else None,
            "tax_info": self.tax_info.to_dict() if self.tax_info else None,
            "employee_strength": self.employee_strength,
            "used_employee_strength": self.used_employee_strength,
            "hostname": self.hostname,
            "logo_path": self.logo_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.name} ({self.organization_id})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Organization(id={self.organization_id}, name='{self.name}', status={self.status.value})" 