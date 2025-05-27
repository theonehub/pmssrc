"""
Concrete Implementation of Organization Services
Implements all organization service interfaces with business logic
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from application.interfaces.services.organization_service import (
    OrganizationCommandService,
    OrganizationQueryService,
    OrganizationAnalyticsService,
    OrganizationHealthService,
    OrganizationBulkOperationsService,
    OrganizationValidationService,
    OrganizationNotificationService,
    OrganizationService
)
from application.interfaces.repositories.organization_repository import OrganizationRepository
from application.interfaces.services.event_publisher import EventPublisher
from application.dto.organization_dto import (
    CreateOrganizationRequestDTO,
    UpdateOrganizationRequestDTO,
    OrganizationStatusUpdateRequestDTO,
    OrganizationSearchFiltersDTO,
    OrganizationResponseDTO,
    OrganizationSummaryDTO,
    OrganizationListResponseDTO,
    OrganizationStatisticsDTO,
    OrganizationAnalyticsDTO,
    OrganizationHealthCheckDTO,
    BulkOrganizationUpdateDTO,
    BulkOrganizationUpdateResultDTO,
    OrganizationValidationError,
    OrganizationBusinessRuleError,
    OrganizationNotFoundError,
    OrganizationConflictError
)
from domain.entities.organization import Organization
from domain.value_objects.organization_id import OrganizationId
from domain.value_objects.organization_details import (
    OrganizationType, OrganizationStatus, ContactInformation, 
    Address, TaxInformation
)


logger = logging.getLogger(__name__)


class OrganizationServiceImpl(OrganizationService):
    """
    Concrete implementation of all organization services.
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (repository, event publisher)
    """
    
    def __init__(
        self,
        repository: OrganizationRepository,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.event_publisher = event_publisher
        self.logger = logging.getLogger(__name__)
    
    # ==================== COMMAND OPERATIONS ====================
    
    async def create_organization(self, request: CreateOrganizationRequestDTO) -> OrganizationResponseDTO:
        """Create a new organization"""
        try:
            # Validate request
            await self._validate_create_request(request)
            
            # Check uniqueness constraints
            await self._check_uniqueness_constraints(request)
            
            # Create value objects
            contact_info = ContactInformation(
                email=request.contact_email,
                phone=request.contact_phone,
                website=request.contact_website,
                fax=request.contact_fax
            )
            
            address = Address(
                street_address=request.address_street,
                city=request.address_city,
                state=request.address_state,
                country=request.address_country,
                pin_code=request.address_pin_code,
                landmark=request.address_landmark
            )
            
            tax_info = TaxInformation(
                pan_number=request.pan_number,
                gst_number=request.gst_number,
                tan_number=request.tan_number,
                cin_number=request.cin_number
            )
            
            # Create organization entity
            organization = Organization.create_new_organization(
                name=request.name,
                description=request.description,
                organization_type=OrganizationType(request.organization_type),
                hostname=request.hostname,
                contact_information=contact_info,
                address=address,
                tax_information=tax_info,
                employee_strength=request.employee_strength
            )
            
            # Save to repository
            saved_organization = await self.repository.save(organization)
            
            # Publish domain events
            for event in saved_organization.get_domain_events():
                self.event_publisher.publish(event)
            
            # Send notifications
            await self._send_creation_notification(saved_organization)
            
            self.logger.info(f"Created organization: {saved_organization.organization_id}")
            
            return self._organization_to_response_dto(saved_organization)
            
        except Exception as e:
            self.logger.error(f"Error creating organization: {e}")
            raise
    
    async def update_organization(
        self,
        organization_id: str,
        request: UpdateOrganizationRequestDTO
    ) -> OrganizationResponseDTO:
        """Update an existing organization"""
        try:
            # Get existing organization
            org_id = OrganizationId.from_string(organization_id)
            organization = await self.repository.get_by_id(org_id)
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization {organization_id} not found")
            
            # Validate update request
            await self._validate_update_request(request, organization)
            
            # Apply updates
            if request.name or request.description or request.organization_type:
                organization.update_basic_info(
                    name=request.name or organization.name,
                    description=request.description or organization.description,
                    organization_type=OrganizationType(request.organization_type) if request.organization_type else organization.organization_type
                )
            
            if any([request.contact_email, request.contact_phone, request.contact_website, request.contact_fax]):
                contact_info = ContactInformation(
                    email=request.contact_email or organization.contact_information.email,
                    phone=request.contact_phone or organization.contact_information.phone,
                    website=request.contact_website or organization.contact_information.website,
                    fax=request.contact_fax or organization.contact_information.fax
                )
                organization.update_contact_info(contact_info)
            
            if any([request.address_street, request.address_city, request.address_state, 
                   request.address_country, request.address_pin_code, request.address_landmark]):
                address = Address(
                    street_address=request.address_street or organization.address.street_address,
                    city=request.address_city or organization.address.city,
                    state=request.address_state or organization.address.state,
                    country=request.address_country or organization.address.country,
                    pin_code=request.address_pin_code or organization.address.pin_code,
                    landmark=request.address_landmark or organization.address.landmark
                )
                organization.update_address(address)
            
            if any([request.pan_number, request.gst_number, request.tan_number, request.cin_number]):
                tax_info = TaxInformation(
                    pan_number=request.pan_number or organization.tax_information.pan_number,
                    gst_number=request.gst_number or organization.tax_information.gst_number,
                    tan_number=request.tan_number or organization.tax_information.tan_number,
                    cin_number=request.cin_number or organization.tax_information.cin_number
                )
                organization.update_tax_info(tax_info)
            
            if request.employee_strength is not None:
                organization.update_employee_strength(request.employee_strength)
            
            # Save updated organization
            updated_organization = await self.repository.update(organization)
            
            # Publish domain events
            for event in updated_organization.get_domain_events():
                self.event_publisher.publish(event)
            
            # Send notifications
            await self._send_update_notification(updated_organization)
            
            self.logger.info(f"Updated organization: {updated_organization.organization_id}")
            
            return self._organization_to_response_dto(updated_organization)
            
        except Exception as e:
            self.logger.error(f"Error updating organization {organization_id}: {e}")
            raise
    
    async def update_organization_status(
        self,
        organization_id: str,
        request: OrganizationStatusUpdateRequestDTO
    ) -> OrganizationResponseDTO:
        """Update organization status"""
        try:
            # Get existing organization
            org_id = OrganizationId.from_string(organization_id)
            organization = await self.repository.get_by_id(org_id)
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization {organization_id} not found")
            
            # Apply status update
            new_status = OrganizationStatus(request.status)
            
            if new_status == OrganizationStatus.ACTIVE:
                organization.activate(request.reason)
            elif new_status == OrganizationStatus.INACTIVE:
                organization.deactivate(request.reason)
            elif new_status == OrganizationStatus.SUSPENDED:
                organization.suspend(request.reason, request.suspension_duration)
            
            # Save updated organization
            updated_organization = await self.repository.update(organization)
            
            # Publish domain events
            for event in updated_organization.get_domain_events():
                self.event_publisher.publish(event)
            
            # Send notifications
            await self._send_status_change_notification(updated_organization, new_status, request.reason)
            
            self.logger.info(f"Updated organization status: {updated_organization.organization_id} to {new_status}")
            
            return self._organization_to_response_dto(updated_organization)
            
        except Exception as e:
            self.logger.error(f"Error updating organization status {organization_id}: {e}")
            raise
    
    async def delete_organization(self, organization_id: str, force: bool = False) -> bool:
        """Delete an organization"""
        try:
            # Get existing organization
            org_id = OrganizationId.from_string(organization_id)
            organization = await self.repository.get_by_id(org_id)
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization {organization_id} not found")
            
            # Check deletion eligibility
            if not force and not organization.can_be_deleted():
                raise OrganizationBusinessRuleError("Organization cannot be deleted due to business rules")
            
            # Perform deletion
            organization.delete()
            
            # Save updated organization
            await self.repository.update(organization)
            
            # Publish domain events
            for event in organization.get_domain_events():
                self.event_publisher.publish(event)
            
            self.logger.info(f"Deleted organization: {organization_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting organization {organization_id}: {e}")
            raise
    
    async def increment_employee_usage(self, organization_id: str) -> OrganizationResponseDTO:
        """Increment employee usage count"""
        try:
            # Get existing organization
            org_id = OrganizationId.from_string(organization_id)
            organization = await self.repository.get_by_id(org_id)
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization {organization_id} not found")
            
            # Increment usage
            organization.increment_used_employee_strength()
            
            # Save updated organization
            updated_organization = await self.repository.update(organization)
            
            # Publish domain events
            for event in updated_organization.get_domain_events():
                self.event_publisher.publish(event)
            
            # Check capacity alerts
            await self._check_capacity_alerts(updated_organization)
            
            return self._organization_to_response_dto(updated_organization)
            
        except Exception as e:
            self.logger.error(f"Error incrementing employee usage for organization {organization_id}: {e}")
            raise
    
    async def decrement_employee_usage(self, organization_id: str) -> OrganizationResponseDTO:
        """Decrement employee usage count"""
        try:
            # Get existing organization
            org_id = OrganizationId.from_string(organization_id)
            organization = await self.repository.get_by_id(org_id)
            
            if not organization:
                raise OrganizationNotFoundError(f"Organization {organization_id} not found")
            
            # Decrement usage
            organization.decrement_used_employee_strength()
            
            # Save updated organization
            updated_organization = await self.repository.update(organization)
            
            # Publish domain events
            for event in updated_organization.get_domain_events():
                self.event_publisher.publish(event)
            
            return self._organization_to_response_dto(updated_organization)
            
        except Exception as e:
            self.logger.error(f"Error decrementing employee usage for organization {organization_id}: {e}")
            raise
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_organization_by_id(self, organization_id: str) -> Optional[OrganizationResponseDTO]:
        """Get organization by ID"""
        try:
            org_id = OrganizationId.from_string(organization_id)
            organization = await self.repository.get_by_id(org_id)
            
            if organization:
                return self._organization_to_response_dto(organization)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organization by ID {organization_id}: {e}")
            raise
    
    async def get_organization_by_name(self, name: str) -> Optional[OrganizationResponseDTO]:
        """Get organization by name"""
        try:
            organization = await self.repository.get_by_name(name)
            
            if organization:
                return self._organization_to_response_dto(organization)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organization by name {name}: {e}")
            raise
    
    async def get_organization_by_hostname(self, hostname: str) -> Optional[OrganizationResponseDTO]:
        """Get organization by hostname"""
        try:
            organization = await self.repository.get_by_hostname(hostname)
            
            if organization:
                return self._organization_to_response_dto(organization)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organization by hostname {hostname}: {e}")
            raise
    
    async def get_organization_by_pan_number(self, pan_number: str) -> Optional[OrganizationResponseDTO]:
        """Get organization by PAN number"""
        try:
            organization = await self.repository.get_by_pan_number(pan_number)
            
            if organization:
                return self._organization_to_response_dto(organization)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organization by PAN {pan_number}: {e}")
            raise
    
    async def search_organizations(self, filters: OrganizationSearchFiltersDTO) -> OrganizationListResponseDTO:
        """Search organizations with filters"""
        try:
            organizations = await self.repository.search(filters)
            total_count = await self.repository.count_all()
            
            organization_summaries = [
                self._organization_to_summary_dto(org) for org in organizations
            ]
            
            return OrganizationListResponseDTO(
                organizations=organization_summaries,
                total_count=total_count,
                page=filters.skip // filters.limit + 1 if filters.limit else 1,
                page_size=filters.limit or len(organization_summaries),
                total_pages=(total_count + filters.limit - 1) // filters.limit if filters.limit else 1
            )
            
        except Exception as e:
            self.logger.error(f"Error searching organizations: {e}")
            raise
    
    async def list_organizations(self, skip: int = 0, limit: int = 100) -> OrganizationListResponseDTO:
        """List all organizations with pagination"""
        try:
            organizations = await self.repository.get_all(skip, limit)
            total_count = await self.repository.count_all()
            
            organization_summaries = [
                self._organization_to_summary_dto(org) for org in organizations
            ]
            
            return OrganizationListResponseDTO(
                organizations=organization_summaries,
                total_count=total_count,
                page=skip // limit + 1,
                page_size=limit,
                total_pages=(total_count + limit - 1) // limit
            )
            
        except Exception as e:
            self.logger.error(f"Error listing organizations: {e}")
            raise
    
    async def organization_exists_by_name(self, name: str) -> bool:
        """Check if organization exists by name"""
        try:
            return await self.repository.exists_by_name(name)
        except Exception as e:
            self.logger.error(f"Error checking organization existence by name {name}: {e}")
            raise
    
    async def organization_exists_by_hostname(self, hostname: str) -> bool:
        """Check if organization exists by hostname"""
        try:
            return await self.repository.exists_by_hostname(hostname)
        except Exception as e:
            self.logger.error(f"Error checking organization existence by hostname {hostname}: {e}")
            raise
    
    async def organization_exists_by_pan_number(self, pan_number: str) -> bool:
        """Check if organization exists by PAN number"""
        try:
            return await self.repository.exists_by_pan_number(pan_number)
        except Exception as e:
            self.logger.error(f"Error checking organization existence by PAN {pan_number}: {e}")
            raise
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_organization_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> OrganizationStatisticsDTO:
        """Get organization statistics"""
        try:
            return await self.repository.get_statistics(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting organization statistics: {e}")
            raise
    
    # ==================== VALIDATION OPERATIONS ====================
    
    async def validate_organization_data(self, request: CreateOrganizationRequestDTO) -> List[str]:
        """Validate organization data"""
        try:
            errors = []
            
            # Validate basic fields
            if not request.name or len(request.name.strip()) < 2:
                errors.append("Organization name must be at least 2 characters long")
            
            if not request.hostname or len(request.hostname.strip()) < 3:
                errors.append("Hostname must be at least 3 characters long")
            
            # Validate contact information
            try:
                ContactInformation(
                    email=request.contact_email,
                    phone=request.contact_phone,
                    website=request.contact_website,
                    fax=request.contact_fax
                )
            except Exception as e:
                errors.append(f"Invalid contact information: {str(e)}")
            
            # Validate address
            try:
                Address(
                    street_address=request.address_street,
                    city=request.address_city,
                    state=request.address_state,
                    country=request.address_country,
                    pin_code=request.address_pin_code,
                    landmark=request.address_landmark
                )
            except Exception as e:
                errors.append(f"Invalid address: {str(e)}")
            
            # Validate tax information
            try:
                TaxInformation(
                    pan_number=request.pan_number,
                    gst_number=request.gst_number,
                    tan_number=request.tan_number,
                    cin_number=request.cin_number
                )
            except Exception as e:
                errors.append(f"Invalid tax information: {str(e)}")
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error validating organization data: {e}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    async def _validate_create_request(self, request: CreateOrganizationRequestDTO):
        """Validate create organization request"""
        errors = await self.validate_organization_data(request)
        
        if errors:
            raise OrganizationValidationError(f"Validation errors: {', '.join(errors)}")
    
    async def _validate_update_request(self, request: UpdateOrganizationRequestDTO, organization: Organization):
        """Validate update organization request"""
        # Add specific update validation logic here
        pass
    
    async def _check_uniqueness_constraints(self, request: CreateOrganizationRequestDTO):
        """Check uniqueness constraints"""
        if await self.repository.exists_by_name(request.name):
            raise OrganizationConflictError(f"Organization with name '{request.name}' already exists")
        
        if await self.repository.exists_by_hostname(request.hostname):
            raise OrganizationConflictError(f"Organization with hostname '{request.hostname}' already exists")
        
        if request.pan_number and await self.repository.exists_by_pan_number(request.pan_number):
            raise OrganizationConflictError(f"Organization with PAN '{request.pan_number}' already exists")
    
    async def _send_creation_notification(self, organization: Organization):
        """Send organization creation notification"""
        # Implement notification logic
        self.logger.info(f"Organization created notification sent for: {organization.organization_id}")
    
    async def _send_update_notification(self, organization: Organization):
        """Send organization update notification"""
        # Implement notification logic
        self.logger.info(f"Organization updated notification sent for: {organization.organization_id}")
    
    async def _send_status_change_notification(self, organization: Organization, new_status: OrganizationStatus, reason: str):
        """Send organization status change notification"""
        # Implement notification logic
        self.logger.info(f"Organization status change notification sent for: {organization.organization_id} to {new_status}")
    
    async def _check_capacity_alerts(self, organization: Organization):
        """Check and send capacity alerts if needed"""
        utilization = organization.get_capacity_utilization_percentage()
        
        if utilization >= 90:
            self.logger.warning(f"High capacity utilization ({utilization}%) for organization: {organization.organization_id}")
            # Send capacity alert notification
    
    def _organization_to_response_dto(self, organization: Organization) -> OrganizationResponseDTO:
        """Convert organization entity to response DTO"""
        return OrganizationResponseDTO(
            organization_id=organization.organization_id.value,
            name=organization.name,
            description=organization.description,
            organization_type=organization.organization_type.value,
            status=organization.status.value,
            hostname=organization.hostname,
            contact_email=organization.contact_information.email,
            contact_phone=organization.contact_information.phone,
            contact_website=organization.contact_information.website,
            contact_fax=organization.contact_information.fax,
            address_street=organization.address.street_address,
            address_city=organization.address.city,
            address_state=organization.address.state,
            address_country=organization.address.country,
            address_pin_code=organization.address.pin_code,
            address_landmark=organization.address.landmark,
            pan_number=organization.tax_information.pan_number,
            gst_number=organization.tax_information.gst_number,
            tan_number=organization.tax_information.tan_number,
            cin_number=organization.tax_information.cin_number,
            employee_strength=organization.employee_strength,
            used_employee_strength=organization.used_employee_strength,
            capacity_utilization_percentage=organization.get_capacity_utilization_percentage(),
            is_gst_registered=organization.is_gst_registered(),
            created_at=organization.created_at,
            updated_at=organization.updated_at
        )
    
    def _organization_to_summary_dto(self, organization: Organization) -> OrganizationSummaryDTO:
        """Convert organization entity to summary DTO"""
        return OrganizationSummaryDTO(
            organization_id=organization.organization_id.value,
            name=organization.name,
            organization_type=organization.organization_type.value,
            status=organization.status.value,
            hostname=organization.hostname,
            city=organization.address.city,
            state=organization.address.state,
            employee_strength=organization.employee_strength,
            used_employee_strength=organization.used_employee_strength,
            capacity_utilization_percentage=organization.get_capacity_utilization_percentage(),
            created_at=organization.created_at
        ) 