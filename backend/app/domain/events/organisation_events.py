"""
Organisation Domain Events
Events for organisation lifecycle and business operations
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.domain.events.employee_events import DomainEvent
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    ContactInformation, Address, TaxInformation, OrganisationType, OrganisationStatus
)


@dataclass
class OrganisationCreated(DomainEvent):
    """
    Event raised when an organisation is created.
    
    This event can trigger:
    - Welcome email to organisation admin
    - System configuration setup
    - Initial user account creation
    - Audit logging
    - Integration with external systems
    """
    
    organisation_id: OrganisationId
    name: str
    organisation_type: OrganisationType
    contact_info: ContactInformation
    address: Address
    created_by: str
    
    def get_event_type(self) -> str:
        return "organisation.created"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_organisation_details(self) -> dict:
        """Get organisation creation details"""
        return {
            "organisation_id": str(self.organisation_id),
            "name": self.name,
            "type": self.organisation_type.value,
            "email": self.contact_info.email,
            "phone": self.contact_info.phone,
            "city": self.address.city,
            "state": self.address.state,
            "country": self.address.country,
            "created_by": self.created_by
        }


@dataclass
class OrganisationUpdated(DomainEvent):
    """
    Event raised when organisation details are updated.
    
    This event can trigger:
    - Notification to organisation admins
    - System configuration updates
    - Integration sync with external systems
    - Audit logging
    """
    
    organisation_id: OrganisationId
    updated_fields: Dict[str, Any]
    updated_by: str
    previous_values: Optional[Dict[str, Any]] = None
    
    def get_event_type(self) -> str:
        return "organisation.updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_update_summary(self) -> dict:
        """Get update summary"""
        return {
            "organisation_id": str(self.organisation_id),
            "updated_fields": list(self.updated_fields.keys()),
            "updated_by": self.updated_by,
            "change_count": len(self.updated_fields)
        }


@dataclass
class OrganisationActivated(DomainEvent):
    """
    Event raised when an organisation is activated.
    
    This event can trigger:
    - Enable organisation services
    - Notification to organisation users
    - System access restoration
    - Audit logging
    """
    
    organisation_id: OrganisationId
    activated_by: str
    previous_status: OrganisationStatus
    reason: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "organisation.activated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_activation_details(self) -> dict:
        """Get activation details"""
        return {
            "organisation_id": str(self.organisation_id),
            "activated_by": self.activated_by,
            "previous_status": self.previous_status.value,
            "reason": self.reason
        }


@dataclass
class OrganisationDeactivated(DomainEvent):
    """
    Event raised when an organisation is deactivated.
    
    This event can trigger:
    - Disable organisation services
    - Notification to organisation users
    - System access suspension
    - Data archival processes
    - Audit logging
    """
    
    organisation_id: OrganisationId
    deactivated_by: str
    reason: str
    previous_status: OrganisationStatus
    
    def get_event_type(self) -> str:
        return "organisation.deactivated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_deactivation_details(self) -> dict:
        """Get deactivation details"""
        return {
            "organisation_id": str(self.organisation_id),
            "deactivated_by": self.deactivated_by,
            "reason": self.reason,
            "previous_status": self.previous_status.value
        }


@dataclass
class OrganisationSuspended(DomainEvent):
    """
    Event raised when an organisation is suspended.
    
    This event can trigger:
    - Temporary service suspension
    - Notification to organisation admins
    - Limited system access
    - Compliance team notification
    - Audit logging
    """
    
    organisation_id: OrganisationId
    suspended_by: str
    reason: str
    suspension_duration: Optional[int] = None  # Days
    previous_status: OrganisationStatus = OrganisationStatus.ACTIVE
    
    def get_event_type(self) -> str:
        return "organisation.suspended"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_suspension_details(self) -> dict:
        """Get suspension details"""
        return {
            "organisation_id": str(self.organisation_id),
            "suspended_by": self.suspended_by,
            "reason": self.reason,
            "duration_days": self.suspension_duration,
            "previous_status": self.previous_status.value
        }


@dataclass
class OrganisationContactUpdated(DomainEvent):
    """
    Event raised when organisation contact information is updated.
    
    This event can trigger:
    - Update contact directories
    - Notification system updates
    - Integration sync
    - Audit logging
    """
    
    organisation_id: OrganisationId
    new_contact_info: ContactInformation
    previous_contact_info: ContactInformation
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organisation.contact_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_contact_changes(self) -> dict:
        """Get contact information changes"""
        changes = {}
        
        if self.new_contact_info.email != self.previous_contact_info.email:
            changes["email"] = {
                "old": self.previous_contact_info.email,
                "new": self.new_contact_info.email
            }
        
        if self.new_contact_info.phone != self.previous_contact_info.phone:
            changes["phone"] = {
                "old": self.previous_contact_info.phone,
                "new": self.new_contact_info.phone
            }
        
        if self.new_contact_info.website != self.previous_contact_info.website:
            changes["website"] = {
                "old": self.previous_contact_info.website,
                "new": self.new_contact_info.website
            }
        
        return {
            "organisation_id": str(self.organisation_id),
            "changes": changes,
            "updated_by": self.updated_by
        }


@dataclass
class OrganisationAddressUpdated(DomainEvent):
    """
    Event raised when organisation address is updated.
    
    This event can trigger:
    - Update address directories
    - Tax jurisdiction changes
    - Shipping/billing updates
    - Compliance notifications
    - Audit logging
    """
    
    organisation_id: OrganisationId
    new_address: Address
    previous_address: Address
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organisation.address_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_address_changes(self) -> dict:
        """Get address changes"""
        return {
            "organisation_id": str(self.organisation_id),
            "previous_address": self.previous_address.get_full_address(),
            "new_address": self.new_address.get_full_address(),
            "city_changed": self.new_address.city != self.previous_address.city,
            "state_changed": self.new_address.state != self.previous_address.state,
            "country_changed": self.new_address.country != self.previous_address.country,
            "updated_by": self.updated_by
        }


@dataclass
class OrganisationTaxInfoUpdated(DomainEvent):
    """
    Event raised when organisation tax information is updated.
    
    This event can trigger:
    - Tax system updates
    - Compliance notifications
    - Financial system sync
    - Audit logging
    """
    
    organisation_id: OrganisationId
    new_tax_info: TaxInformation
    previous_tax_info: TaxInformation
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organisation.tax_info_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_tax_changes(self) -> dict:
        """Get tax information changes"""
        changes = {}
        
        if self.new_tax_info.pan_number != self.previous_tax_info.pan_number:
            changes["pan_number"] = {
                "old": self.previous_tax_info.pan_number,
                "new": self.new_tax_info.pan_number
            }
        
        if self.new_tax_info.gst_number != self.previous_tax_info.gst_number:
            changes["gst_number"] = {
                "old": self.previous_tax_info.gst_number,
                "new": self.new_tax_info.gst_number
            }
        
        if self.new_tax_info.tan_number != self.previous_tax_info.tan_number:
            changes["tan_number"] = {
                "old": self.previous_tax_info.tan_number,
                "new": self.new_tax_info.tan_number
            }
        
        return {
            "organisation_id": str(self.organisation_id),
            "changes": changes,
            "updated_by": self.updated_by
        }


@dataclass
class OrganisationEmployeeStrengthUpdated(DomainEvent):
    """
    Event raised when organisation employee strength is updated.
    
    This event can trigger:
    - License management updates
    - Capacity planning notifications
    - Billing adjustments
    - Audit logging
    """
    
    organisation_id: OrganisationId
    new_employee_strength: int
    previous_employee_strength: int
    current_used_strength: int
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organisation.employee_strength_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_strength_changes(self) -> dict:
        """Get employee strength changes"""
        return {
            "organisation_id": str(self.organisation_id),
            "previous_strength": self.previous_employee_strength,
            "new_strength": self.new_employee_strength,
            "current_used": self.current_used_strength,
            "available_capacity": self.new_employee_strength - self.current_used_strength,
            "capacity_increased": self.new_employee_strength > self.previous_employee_strength,
            "updated_by": self.updated_by
        }


@dataclass
class OrganisationDeleted(DomainEvent):
    """
    Event raised when an organisation is deleted.
    
    This event can trigger:
    - Data archival processes
    - System cleanup
    - User account deactivation
    - Integration cleanup
    - Audit logging
    """
    
    organisation_id: OrganisationId
    organisation_name: str
    deleted_by: str
    deletion_reason: str
    
    def get_event_type(self) -> str:
        return "organisation.deleted"
    
    def get_aggregate_id(self) -> str:
        return str(self.organisation_id)
    
    def get_deletion_details(self) -> dict:
        """Get deletion details"""
        return {
            "organisation_id": str(self.organisation_id),
            "organisation_name": self.organisation_name,
            "deleted_by": self.deleted_by,
            "deletion_reason": self.deletion_reason
        } 