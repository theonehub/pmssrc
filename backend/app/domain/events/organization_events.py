"""
Organization Domain Events
Events for organization lifecycle and business operations
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.domain.events.employee_events import DomainEvent
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.organization_details import (
    ContactInformation, Address, TaxInformation, OrganizationType, OrganizationStatus
)


@dataclass
class OrganizationCreated(DomainEvent):
    """
    Event raised when an organization is created.
    
    This event can trigger:
    - Welcome email to organization admin
    - System configuration setup
    - Initial user account creation
    - Audit logging
    - Integration with external systems
    """
    
    organization_id: OrganizationId
    name: str
    organization_type: OrganizationType
    contact_info: ContactInformation
    address: Address
    created_by: str
    
    def get_event_type(self) -> str:
        return "organization.created"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_organization_details(self) -> dict:
        """Get organization creation details"""
        return {
            "organization_id": str(self.organization_id),
            "name": self.name,
            "type": self.organization_type.value,
            "email": self.contact_info.email,
            "phone": self.contact_info.phone,
            "city": self.address.city,
            "state": self.address.state,
            "country": self.address.country,
            "created_by": self.created_by
        }


@dataclass
class OrganizationUpdated(DomainEvent):
    """
    Event raised when organization details are updated.
    
    This event can trigger:
    - Notification to organization admins
    - System configuration updates
    - Integration sync with external systems
    - Audit logging
    """
    
    organization_id: OrganizationId
    updated_fields: Dict[str, Any]
    updated_by: str
    previous_values: Optional[Dict[str, Any]] = None
    
    def get_event_type(self) -> str:
        return "organization.updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_update_summary(self) -> dict:
        """Get update summary"""
        return {
            "organization_id": str(self.organization_id),
            "updated_fields": list(self.updated_fields.keys()),
            "updated_by": self.updated_by,
            "change_count": len(self.updated_fields)
        }


@dataclass
class OrganizationActivated(DomainEvent):
    """
    Event raised when an organization is activated.
    
    This event can trigger:
    - Enable organization services
    - Notification to organization users
    - System access restoration
    - Audit logging
    """
    
    organization_id: OrganizationId
    activated_by: str
    previous_status: OrganizationStatus
    reason: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "organization.activated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_activation_details(self) -> dict:
        """Get activation details"""
        return {
            "organization_id": str(self.organization_id),
            "activated_by": self.activated_by,
            "previous_status": self.previous_status.value,
            "reason": self.reason
        }


@dataclass
class OrganizationDeactivated(DomainEvent):
    """
    Event raised when an organization is deactivated.
    
    This event can trigger:
    - Disable organization services
    - Notification to organization users
    - System access suspension
    - Data archival processes
    - Audit logging
    """
    
    organization_id: OrganizationId
    deactivated_by: str
    reason: str
    previous_status: OrganizationStatus
    
    def get_event_type(self) -> str:
        return "organization.deactivated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_deactivation_details(self) -> dict:
        """Get deactivation details"""
        return {
            "organization_id": str(self.organization_id),
            "deactivated_by": self.deactivated_by,
            "reason": self.reason,
            "previous_status": self.previous_status.value
        }


@dataclass
class OrganizationSuspended(DomainEvent):
    """
    Event raised when an organization is suspended.
    
    This event can trigger:
    - Temporary service suspension
    - Notification to organization admins
    - Limited system access
    - Compliance team notification
    - Audit logging
    """
    
    organization_id: OrganizationId
    suspended_by: str
    reason: str
    suspension_duration: Optional[int] = None  # Days
    previous_status: OrganizationStatus = OrganizationStatus.ACTIVE
    
    def get_event_type(self) -> str:
        return "organization.suspended"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_suspension_details(self) -> dict:
        """Get suspension details"""
        return {
            "organization_id": str(self.organization_id),
            "suspended_by": self.suspended_by,
            "reason": self.reason,
            "duration_days": self.suspension_duration,
            "previous_status": self.previous_status.value
        }


@dataclass
class OrganizationContactUpdated(DomainEvent):
    """
    Event raised when organization contact information is updated.
    
    This event can trigger:
    - Update contact directories
    - Notification system updates
    - Integration sync
    - Audit logging
    """
    
    organization_id: OrganizationId
    new_contact_info: ContactInformation
    previous_contact_info: ContactInformation
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organization.contact_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
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
            "organization_id": str(self.organization_id),
            "changes": changes,
            "updated_by": self.updated_by
        }


@dataclass
class OrganizationAddressUpdated(DomainEvent):
    """
    Event raised when organization address is updated.
    
    This event can trigger:
    - Update address directories
    - Tax jurisdiction changes
    - Shipping/billing updates
    - Compliance notifications
    - Audit logging
    """
    
    organization_id: OrganizationId
    new_address: Address
    previous_address: Address
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organization.address_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_address_changes(self) -> dict:
        """Get address changes"""
        return {
            "organization_id": str(self.organization_id),
            "previous_address": self.previous_address.get_full_address(),
            "new_address": self.new_address.get_full_address(),
            "city_changed": self.new_address.city != self.previous_address.city,
            "state_changed": self.new_address.state != self.previous_address.state,
            "country_changed": self.new_address.country != self.previous_address.country,
            "updated_by": self.updated_by
        }


@dataclass
class OrganizationTaxInfoUpdated(DomainEvent):
    """
    Event raised when organization tax information is updated.
    
    This event can trigger:
    - Tax system updates
    - Compliance notifications
    - Financial system sync
    - Audit logging
    """
    
    organization_id: OrganizationId
    new_tax_info: TaxInformation
    previous_tax_info: TaxInformation
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organization.tax_info_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
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
            "organization_id": str(self.organization_id),
            "changes": changes,
            "updated_by": self.updated_by
        }


@dataclass
class OrganizationEmployeeStrengthUpdated(DomainEvent):
    """
    Event raised when organization employee strength is updated.
    
    This event can trigger:
    - License management updates
    - Capacity planning notifications
    - Billing adjustments
    - Audit logging
    """
    
    organization_id: OrganizationId
    new_employee_strength: int
    previous_employee_strength: int
    current_used_strength: int
    updated_by: str
    
    def get_event_type(self) -> str:
        return "organization.employee_strength_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_strength_changes(self) -> dict:
        """Get employee strength changes"""
        return {
            "organization_id": str(self.organization_id),
            "previous_strength": self.previous_employee_strength,
            "new_strength": self.new_employee_strength,
            "current_used": self.current_used_strength,
            "available_capacity": self.new_employee_strength - self.current_used_strength,
            "capacity_increased": self.new_employee_strength > self.previous_employee_strength,
            "updated_by": self.updated_by
        }


@dataclass
class OrganizationDeleted(DomainEvent):
    """
    Event raised when an organization is deleted.
    
    This event can trigger:
    - Data archival processes
    - System cleanup
    - User account deactivation
    - Integration cleanup
    - Audit logging
    """
    
    organization_id: OrganizationId
    organization_name: str
    deleted_by: str
    deletion_reason: str
    
    def get_event_type(self) -> str:
        return "organization.deleted"
    
    def get_aggregate_id(self) -> str:
        return str(self.organization_id)
    
    def get_deletion_details(self) -> dict:
        """Get deletion details"""
        return {
            "organization_id": str(self.organization_id),
            "organization_name": self.organization_name,
            "deleted_by": self.deleted_by,
            "deletion_reason": self.deletion_reason
        } 