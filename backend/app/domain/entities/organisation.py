"""
Organisation Domain Entity
Aggregate root for organisation management following DDD patterns
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    ContactInformation, Address, TaxInformation, OrganisationType, OrganisationStatus
)
from app.domain.events.organisation_events import (
    OrganisationCreated, OrganisationUpdated, OrganisationActivated,
    OrganisationDeactivated, OrganisationSuspended, OrganisationContactUpdated,
    OrganisationAddressUpdated, OrganisationTaxInfoUpdated,
    OrganisationEmployeeStrengthUpdated, OrganisationDeleted
)


logger = logging.getLogger(__name__)


@dataclass
class Organisation:
    """
    Organisation aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles organisation-related business logic
    - OCP: Can be extended with new organisation types without modification
    - LSP: Can be substituted anywhere Organisation is expected
    - ISP: Provides focused organisation operations
    - DIP: Depends on abstractions (value objects, events)
    
    Domain Events:
    - OrganisationCreated: When organisation is created
    - OrganisationUpdated: When organisation details are updated
    - OrganisationActivated: When organisation is activated
    - OrganisationDeactivated: When organisation is deactivated
    - OrganisationSuspended: When organisation is suspended
    - OrganisationContactUpdated: When contact info is updated
    - OrganisationAddressUpdated: When address is updated
    - OrganisationTaxInfoUpdated: When tax info is updated
    - OrganisationEmployeeStrengthUpdated: When employee capacity is updated
    - OrganisationDeleted: When organisation is deleted
    """
    
    # Identity
    organisation_id: OrganisationId
    
    # Basic Information
    name: str
    description: Optional[str] = None
    organisation_type: OrganisationType = OrganisationType.PRIVATE_LIMITED
    status: OrganisationStatus = OrganisationStatus.ACTIVE
    
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
        self._validate_organisation_data()
        
        # Raise domain event for new organisation creation
        if not hasattr(self, '_is_existing_organisation'):
            self._domain_events.append(
                OrganisationCreated(
                    organisation_id=self.organisation_id,
                    name=self.name,
                    organisation_type=self.organisation_type,
                    contact_info=self.contact_info,
                    address=self.address,
                    created_by=self.created_by or "system",
                    occurred_at=datetime.utcnow()
                )
            )
    
    # ==================== FACTORY METHODS ====================
    
    @classmethod
    def create_new_organisation(
        cls,
        name: str,
        contact_info: ContactInformation,
        address: Address,
        tax_info: TaxInformation,
        organisation_type: OrganisationType = OrganisationType.PRIVATE_LIMITED,
        employee_strength: int = 10,
        hostname: Optional[str] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> 'Organisation':
        """Factory method to create a new organisation"""
        
        organisation_id = OrganisationId.generate()
        
        organisation = cls(
            organisation_id=organisation_id,
            name=name,
            description=description,
            organisation_type=organisation_type,
            contact_info=contact_info,
            address=address,
            tax_info=tax_info,
            employee_strength=employee_strength,
            hostname=hostname,
            created_by=created_by
        )
        
        return organisation
    
    @classmethod
    def from_existing_data(cls, **kwargs) -> 'Organisation':
        """Create organisation from existing data (for repository loading)"""
        # Convert string IDs to value objects if needed
        if 'organisation_id' in kwargs and isinstance(kwargs['organisation_id'], str):
            kwargs['organisation_id'] = OrganisationId.from_string(kwargs['organisation_id'])
        
        # Convert dict data to value objects if needed
        if 'contact_info' in kwargs and isinstance(kwargs['contact_info'], dict):
            kwargs['contact_info'] = ContactInformation.from_dict(kwargs['contact_info'])
        
        if 'address' in kwargs and isinstance(kwargs['address'], dict):
            kwargs['address'] = Address.from_dict(kwargs['address'])
        
        if 'tax_info' in kwargs and isinstance(kwargs['tax_info'], dict):
            kwargs['tax_info'] = TaxInformation.from_dict(kwargs['tax_info'])
        
        if 'organisation_type' in kwargs and isinstance(kwargs['organisation_type'], str):
            kwargs['organisation_type'] = OrganisationType(kwargs['organisation_type'])
        
        if 'status' in kwargs and isinstance(kwargs['status'], str):
            kwargs['status'] = OrganisationStatus(kwargs['status'])
        
        organisation = cls(**kwargs)
        organisation._is_existing_organisation = True
        return organisation
    
    # ==================== BUSINESS METHODS ====================
    
    def update_basic_info(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        organisation_type: Optional[OrganisationType] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update basic organisation information.
        
        Business Rules:
        1. Name cannot be empty
        2. Organisation type changes may have restrictions
        """
        updated_fields = {}
        previous_values = {}
        
        if name is not None and name.strip() != self.name:
            if not name.strip():
                raise ValueError("Organisation name cannot be empty")
            previous_values["name"] = self.name
            self.name = name.strip()
            updated_fields["name"] = self.name
        
        if description is not None and description != self.description:
            previous_values["description"] = self.description
            self.description = description
            updated_fields["description"] = self.description
        
        if organisation_type is not None and organisation_type != self.organisation_type:
            previous_values["organisation_type"] = self.organisation_type.value
            self.organisation_type = organisation_type
            updated_fields["organisation_type"] = self.organisation_type.value
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self.updated_by = updated_by
            
            # Publish domain event
            self._add_domain_event(OrganisationUpdated(
                organisation_id=self.organisation_id,
                updated_fields=updated_fields,
                updated_by=updated_by or "system",
                previous_values=previous_values,
                occurred_at=datetime.utcnow()
            ))
            
            logger.info(f"Organisation {self.organisation_id} basic info updated")
    
    def update_contact_info(
        self,
        new_contact_info: ContactInformation,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organisation contact information.
        
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
        self._add_domain_event(OrganisationContactUpdated(
            organisation_id=self.organisation_id,
            new_contact_info=new_contact_info,
            previous_contact_info=previous_contact_info,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} contact info updated")
    
    def update_address(
        self,
        new_address: Address,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organisation address.
        
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
        self._add_domain_event(OrganisationAddressUpdated(
            organisation_id=self.organisation_id,
            new_address=new_address,
            previous_address=previous_address,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} address updated")
    
    def update_tax_info(
        self,
        new_tax_info: TaxInformation,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organisation tax information.
        
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
        self._add_domain_event(OrganisationTaxInfoUpdated(
            organisation_id=self.organisation_id,
            new_tax_info=new_tax_info,
            previous_tax_info=previous_tax_info,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} tax info updated")
    
    def update_employee_strength(
        self,
        new_employee_strength: int,
        updated_by: Optional[str] = None
    ) -> None:
        """
        Update organisation employee strength.
        
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
        self._add_domain_event(OrganisationEmployeeStrengthUpdated(
            organisation_id=self.organisation_id,
            new_employee_strength=new_employee_strength,
            previous_employee_strength=previous_strength,
            current_used_strength=self.used_employee_strength,
            updated_by=updated_by or "system",
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} employee strength updated to {new_employee_strength}")
    
    def activate(self, activated_by: Optional[str] = None, reason: Optional[str] = None) -> None:
        """
        Activate the organisation.
        
        Business Rules:
        1. Can only activate inactive or suspended organisations
        2. Cannot activate terminated organisations
        """
        if self.status == OrganisationStatus.ACTIVE:
            raise ValueError("Organisation is already active")
        
        if self.status == OrganisationStatus.TERMINATED:
            raise ValueError("Cannot activate terminated organisation")
        
        previous_status = self.status
        self.status = OrganisationStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = activated_by
        
        # Publish domain event
        self._add_domain_event(OrganisationActivated(
            organisation_id=self.organisation_id,
            activated_by=activated_by or "system",
            previous_status=previous_status,
            reason=reason,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} activated")
    
    def deactivate(self, reason: str, deactivated_by: Optional[str] = None) -> None:
        """
        Deactivate the organisation.
        
        Business Rules:
        1. Can only deactivate active organisations
        2. Must provide reason for deactivation
        """
        if self.status != OrganisationStatus.ACTIVE:
            raise ValueError("Can only deactivate active organisations")
        
        if not reason or not reason.strip():
            raise ValueError("Deactivation reason is required")
        
        previous_status = self.status
        self.status = OrganisationStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = deactivated_by
        
        # Publish domain event
        self._add_domain_event(OrganisationDeactivated(
            organisation_id=self.organisation_id,
            deactivated_by=deactivated_by or "system",
            reason=reason,
            previous_status=previous_status,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} deactivated: {reason}")
    
    def suspend(
        self,
        reason: str,
        suspended_by: Optional[str] = None,
        suspension_duration: Optional[int] = None
    ) -> None:
        """
        Suspend the organisation.
        
        Business Rules:
        1. Can suspend active or inactive organisations
        2. Must provide reason for suspension
        3. Cannot suspend already suspended organisations
        """
        if self.status == OrganisationStatus.SUSPENDED:
            raise ValueError("Organisation is already suspended")
        
        if self.status == OrganisationStatus.TERMINATED:
            raise ValueError("Cannot suspend terminated organisation")
        
        if not reason or not reason.strip():
            raise ValueError("Suspension reason is required")
        
        previous_status = self.status
        self.status = OrganisationStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
        self.updated_by = suspended_by
        
        # Publish domain event
        self._add_domain_event(OrganisationSuspended(
            organisation_id=self.organisation_id,
            suspended_by=suspended_by or "system",
            reason=reason,
            suspension_duration=suspension_duration,
            previous_status=previous_status,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} suspended: {reason}")
    
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
        Mark organisation as deleted.
        
        Business Rules:
        1. Deletion reason is required
        2. Only admin can delete organisation
        3. Cannot delete if has active employees
        """
        if not deletion_reason or not deletion_reason.strip():
            raise ValueError("Deletion reason is required")
        
        if self.used_employee_strength > 0:
            raise ValueError("Cannot delete organisation with active employees")
        
        # Publish domain event
        self._add_domain_event(OrganisationDeleted(
            organisation_id=self.organisation_id,
            organisation_name=self.name,
            deleted_by=deleted_by or "system",
            deletion_reason=deletion_reason,
            occurred_at=datetime.utcnow()
        ))
        
        logger.info(f"Organisation {self.organisation_id} deleted: {deletion_reason}")
    
    # ==================== QUERY METHODS ====================
    
    def is_active(self) -> bool:
        """Check if organisation is active"""
        return self.status == OrganisationStatus.ACTIVE
    
    def is_government_organisation(self) -> bool:
        """Check if organisation is government type"""
        return self.organisation_type == OrganisationType.GOVERNMENT
    
    def has_available_employee_capacity(self) -> bool:
        """Check if organisation has available employee capacity"""
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
        """Check if organisation is GST registered"""
        return self.tax_info and self.tax_info.is_gst_registered()
    
    def get_display_name(self) -> str:
        """Get display name for organisation"""
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
    
    def _validate_organisation_data(self) -> None:
        """Validate organisation data consistency"""
        
        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Organisation name is required")
        
        # Validate employee strength
        if self.employee_strength < 0:
            raise ValueError("Employee strength cannot be negative")
        
        if self.used_employee_strength < 0:
            raise ValueError("Used employee strength cannot be negative")
        
        if self.used_employee_strength > self.employee_strength:
            raise ValueError("Used employee strength cannot exceed total strength")
        
        # Validate required value objects
        if not isinstance(self.organisation_id, OrganisationId):
            raise ValueError("Invalid organisation ID")
        
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
            "organisation_id": str(self.organisation_id),
            "name": self.name,
            "description": self.description,
            "organisation_type": self.organisation_type.value,
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
        return f"{self.name} ({self.organisation_id})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Organisation(id={self.organisation_id}, name='{self.name}', status={self.status.value})" 