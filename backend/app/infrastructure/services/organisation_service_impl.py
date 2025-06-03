"""
Concrete Implementation of Organisation Services
Implements all organisation service interfaces with business logic
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.application.interfaces.services.organisation_service import (
    OrganisationCommandService,
    OrganisationQueryService,
    OrganisationAnalyticsService,
    OrganisationHealthService,
    OrganisationBulkOperationsService,
    OrganisationValidationService,
    OrganisationNotificationService,
    OrganisationService
)
from app.application.interfaces.repositories.organisation_repository import OrganisationRepository
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.dto.organisation_dto import (
    CreateOrganisationRequestDTO,
    UpdateOrganisationRequestDTO,
    OrganisationStatusUpdateRequestDTO,
    OrganisationSearchFiltersDTO,
    OrganisationResponseDTO,
    OrganisationSummaryDTO,
    OrganisationListResponseDTO,
    OrganisationStatisticsDTO,
    OrganisationAnalyticsDTO,
    OrganisationHealthCheckDTO,
    BulkOrganisationUpdateDTO,
    BulkOrganisationUpdateResultDTO,
    OrganisationValidationError,
    OrganisationBusinessRuleError,
    OrganisationNotFoundError,
    OrganisationConflictError
)
from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    OrganisationType, OrganisationStatus, ContactInformation, 
    Address, TaxInformation
)
from app.infrastructure.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class OrganisationServiceImpl(OrganisationService):
    """
    Concrete implementation of all organisation services.
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (repository, event publisher)
    """
    
    def __init__(
        self,
        repository: OrganisationRepository,
        notification_service: NotificationService,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.event_publisher = event_publisher
        self.notification_service = notification_service
        self.logger = logging.getLogger(__name__)
    
    # ==================== COMMAND OPERATIONS ====================
    
    async def create_organisation(self, request: CreateOrganisationRequestDTO) -> OrganisationResponseDTO:
        """Create a new organisation"""
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
            
            # Create organisation entity
            organisation = Organisation.create_new_organisation(
                name=request.name,
                description=request.description,
                organisation_type=OrganisationType(request.organisation_type),
                hostname=request.hostname,
                contact_information=contact_info,
                address=address,
                tax_information=tax_info,
                employee_strength=request.employee_strength
            )
            
            # Save to repository
            saved_organisation = await self.repository.save(organisation)
            
            # Publish domain events
            for event in saved_organisation.get_domain_events():
                self.event_publisher.publish(event)
            
            # Send notifications
            await self._send_creation_notification(saved_organisation)
            
            self.logger.info(f"Created organisation: {saved_organisation.organisation_id}")
            
            return self._organisation_to_response_dto(saved_organisation)
            
        except Exception as e:
            self.logger.error(f"Error creating organisation: {e}")
            raise
    
    async def update_organisation(
        self,
        organisation_id: str,
        request: UpdateOrganisationRequestDTO
    ) -> OrganisationResponseDTO:
        """Update an existing organisation"""
        try:
            # Get existing organisation
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                raise OrganisationNotFoundError(f"Organisation {organisation_id} not found")
            
            # Validate update request
            await self._validate_update_request(request, organisation)
            
            # Apply updates
            if request.name or request.description or request.organisation_type:
                organisation.update_basic_info(
                    name=request.name or organisation.name,
                    description=request.description or organisation.description,
                    organisation_type=OrganisationType(request.organisation_type) if request.organisation_type else organisation.organisation_type
                )
            
            if any([request.contact_email, request.contact_phone, request.contact_website, request.contact_fax]):
                contact_info = ContactInformation(
                    email=request.contact_email or organisation.contact_information.email,
                    phone=request.contact_phone or organisation.contact_information.phone,
                    website=request.contact_website or organisation.contact_information.website,
                    fax=request.contact_fax or organisation.contact_information.fax
                )
                organisation.update_contact_info(contact_info)
            
            if any([request.address_street, request.address_city, request.address_state, 
                   request.address_country, request.address_pin_code, request.address_landmark]):
                address = Address(
                    street_address=request.address_street or organisation.address.street_address,
                    city=request.address_city or organisation.address.city,
                    state=request.address_state or organisation.address.state,
                    country=request.address_country or organisation.address.country,
                    pin_code=request.address_pin_code or organisation.address.pin_code,
                    landmark=request.address_landmark or organisation.address.landmark
                )
                organisation.update_address(address)
            
            if any([request.pan_number, request.gst_number, request.tan_number, request.cin_number]):
                tax_info = TaxInformation(
                    pan_number=request.pan_number or organisation.tax_information.pan_number,
                    gst_number=request.gst_number or organisation.tax_information.gst_number,
                    tan_number=request.tan_number or organisation.tax_information.tan_number,
                    cin_number=request.cin_number or organisation.tax_information.cin_number
                )
                organisation.update_tax_info(tax_info)
            
            if request.employee_strength is not None:
                organisation.update_employee_strength(request.employee_strength)
            
            # Save updated organisation
            updated_organisation = await self.repository.update(organisation)
            
            # Publish domain events
            for event in updated_organisation.get_domain_events():
                self.event_publisher.publish(event)
            
            # Send notifications
            await self._send_update_notification(updated_organisation)
            
            self.logger.info(f"Updated organisation: {updated_organisation.organisation_id}")
            
            return self._organisation_to_response_dto(updated_organisation)
            
        except Exception as e:
            self.logger.error(f"Error updating organisation {organisation_id}: {e}")
            raise
    
    async def update_organisation_status(
        self,
        organisation_id: str,
        request: OrganisationStatusUpdateRequestDTO
    ) -> OrganisationResponseDTO:
        """Update organisation status"""
        try:
            # Get existing organisation
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                raise OrganisationNotFoundError(f"Organisation {organisation_id} not found")
            
            # Apply status update
            new_status = OrganisationStatus(request.status)
            
            if new_status == OrganisationStatus.ACTIVE:
                organisation.activate(request.reason)
            elif new_status == OrganisationStatus.INACTIVE:
                organisation.deactivate(request.reason)
            elif new_status == OrganisationStatus.SUSPENDED:
                organisation.suspend(request.reason, request.suspension_duration)
            
            # Save updated organisation
            updated_organisation = await self.repository.update(organisation)
            
            # Publish domain events
            for event in updated_organisation.get_domain_events():
                self.event_publisher.publish(event)
            
            # Send notifications
            await self._send_status_change_notification(updated_organisation, new_status, request.reason)
            
            self.logger.info(f"Updated organisation status: {updated_organisation.organisation_id} to {new_status}")
            
            return self._organisation_to_response_dto(updated_organisation)
            
        except Exception as e:
            self.logger.error(f"Error updating organisation status {organisation_id}: {e}")
            raise
    
    async def delete_organisation(self, organisation_id: str, force: bool = False) -> bool:
        """Delete an organisation"""
        try:
            # Get existing organisation
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                raise OrganisationNotFoundError(f"Organisation {organisation_id} not found")
            
            # Check deletion eligibility
            if not force and not organisation.can_be_deleted():
                raise OrganisationBusinessRuleError("Organisation cannot be deleted due to business rules")
            
            # Perform deletion
            organisation.delete()
            
            # Save updated organisation
            await self.repository.update(organisation)
            
            # Publish domain events
            for event in organisation.get_domain_events():
                self.event_publisher.publish(event)
            
            self.logger.info(f"Deleted organisation: {organisation_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting organisation {organisation_id}: {e}")
            raise
    
    async def increment_employee_usage(self, organisation_id: str) -> OrganisationResponseDTO:
        """Increment employee usage count"""
        try:
            # Get existing organisation
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                raise OrganisationNotFoundError(f"Organisation {organisation_id} not found")
            
            # Increment usage
            organisation.increment_used_employee_strength()
            
            # Save updated organisation
            updated_organisation = await self.repository.update(organisation)
            
            # Publish domain events
            for event in updated_organisation.get_domain_events():
                self.event_publisher.publish(event)
            
            # Check capacity alerts
            await self._check_capacity_alerts(updated_organisation)
            
            return self._organisation_to_response_dto(updated_organisation)
            
        except Exception as e:
            self.logger.error(f"Error incrementing employee usage for organisation {organisation_id}: {e}")
            raise
    
    async def decrement_employee_usage(self, organisation_id: str) -> OrganisationResponseDTO:
        """Decrement employee usage count"""
        try:
            # Get existing organisation
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                raise OrganisationNotFoundError(f"Organisation {organisation_id} not found")
            
            # Decrement usage
            organisation.decrement_used_employee_strength()
            
            # Save updated organisation
            updated_organisation = await self.repository.update(organisation)
            
            # Publish domain events
            for event in updated_organisation.get_domain_events():
                self.event_publisher.publish(event)
            
            return self._organisation_to_response_dto(updated_organisation)
            
        except Exception as e:
            self.logger.error(f"Error decrementing employee usage for organisation {organisation_id}: {e}")
            raise
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_organisation_by_id(self, organisation_id: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by ID"""
        try:
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if organisation:
                return self._organisation_to_response_dto(organisation)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organisation by ID {organisation_id}: {e}")
            raise
    
    async def get_organisation_by_name(self, name: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by name"""
        try:
            organisation = await self.repository.get_by_name(name)
            
            if organisation:
                return self._organisation_to_response_dto(organisation)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organisation by name {name}: {e}")
            raise
    
    async def get_organisation_by_hostname(self, hostname: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by hostname"""
        try:
            organisation = await self.repository.get_by_hostname(hostname)
            
            if organisation:
                return self._organisation_to_response_dto(organisation)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organisation by hostname {hostname}: {e}")
            raise
    
    async def get_organisation_by_pan_number(self, pan_number: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by PAN number"""
        try:
            organisation = await self.repository.get_by_pan_number(pan_number)
            
            if organisation:
                return self._organisation_to_response_dto(organisation)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting organisation by PAN {pan_number}: {e}")
            raise
    
    async def search_organisations(self, filters: OrganisationSearchFiltersDTO) -> OrganisationListResponseDTO:
        """Search organisations with filters"""
        try:
            organisations = await self.repository.search(filters)
            total_count = await self.repository.count_all()
            
            organisation_summaries = [
                self._organisation_to_summary_dto(org) for org in organisations
            ]
            
            return OrganisationListResponseDTO(
                organisations=organisation_summaries,
                total_count=total_count,
                page=filters.skip // filters.limit + 1 if filters.limit else 1,
                page_size=filters.limit or len(organisation_summaries),
                total_pages=(total_count + filters.limit - 1) // filters.limit if filters.limit else 1
            )
            
        except Exception as e:
            self.logger.error(f"Error searching organisations: {e}")
            raise
    
    async def list_organisations(self, skip: int = 0, limit: int = 100) -> OrganisationListResponseDTO:
        """List all organisations with pagination"""
        try:
            organisations = await self.repository.get_all(skip, limit)
            total_count = await self.repository.count_all()
            
            organisation_summaries = [
                self._organisation_to_summary_dto(org) for org in organisations
            ]
            
            return OrganisationListResponseDTO(
                organisations=organisation_summaries,
                total_count=total_count,
                page=skip // limit + 1,
                page_size=limit,
                total_pages=(total_count + limit - 1) // limit
            )
            
        except Exception as e:
            self.logger.error(f"Error listing organisations: {e}")
            raise
    
    async def organisation_exists_by_name(self, name: str) -> bool:
        """Check if organisation exists by name"""
        try:
            return await self.repository.exists_by_name(name)
        except Exception as e:
            self.logger.error(f"Error checking organisation existence by name {name}: {e}")
            raise
    
    async def organisation_exists_by_hostname(self, hostname: str) -> bool:
        """Check if organisation exists by hostname"""
        try:
            return await self.repository.exists_by_hostname(hostname)
        except Exception as e:
            self.logger.error(f"Error checking organisation existence by hostname {hostname}: {e}")
            raise
    
    async def organisation_exists_by_pan_number(self, pan_number: str) -> bool:
        """Check if organisation exists by PAN number"""
        try:
            return await self.repository.exists_by_pan_number(pan_number)
        except Exception as e:
            self.logger.error(f"Error checking organisation existence by PAN {pan_number}: {e}")
            raise
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_organisation_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> OrganisationStatisticsDTO:
        """Get organisation statistics"""
        try:
            return await self.repository.get_statistics(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting organisation statistics: {e}")
            raise
    
    # ==================== VALIDATION OPERATIONS ====================
    
    async def validate_organisation_data(self, request: CreateOrganisationRequestDTO) -> List[str]:
        """Validate organisation data"""
        try:
            errors = []
            
            # Validate basic fields
            if not request.name or len(request.name.strip()) < 2:
                errors.append("Organisation name must be at least 2 characters long")
            
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
            self.logger.error(f"Error validating organisation data: {e}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    async def _validate_create_request(self, request: CreateOrganisationRequestDTO):
        """Validate create organisation request"""
        errors = await self.validate_organisation_data(request)
        
        if errors:
            raise OrganisationValidationError(f"Validation errors: {', '.join(errors)}")
    
    async def _validate_update_request(self, request: UpdateOrganisationRequestDTO, organisation: Organisation):
        """Validate update organisation request"""
        # Add specific update validation logic here
        pass
    
    async def _check_uniqueness_constraints(self, request: CreateOrganisationRequestDTO):
        """Check uniqueness constraints"""
        if await self.repository.exists_by_name(request.name):
            raise OrganisationConflictError(f"Organisation with name '{request.name}' already exists")
        
        if await self.repository.exists_by_hostname(request.hostname):
            raise OrganisationConflictError(f"Organisation with hostname '{request.hostname}' already exists")
        
        if request.pan_number and await self.repository.exists_by_pan_number(request.pan_number):
            raise OrganisationConflictError(f"Organisation with PAN '{request.pan_number}' already exists")
    
    async def _send_creation_notification(self, organisation: Organisation):
        """Send organisation creation notification"""
        # Implement notification logic
        self.logger.info(f"Organisation created notification sent for: {organisation.organisation_id}")
    
    async def _send_update_notification(self, organisation: Organisation):
        """Send organisation update notification"""
        # Implement notification logic
        self.logger.info(f"Organisation updated notification sent for: {organisation.organisation_id}")
    
    async def _send_status_change_notification(self, organisation: Organisation, new_status: OrganisationStatus, reason: str):
        """Send organisation status change notification"""
        # Implement notification logic
        self.logger.info(f"Organisation status change notification sent for: {organisation.organisation_id} to {new_status}")
    
    async def _check_capacity_alerts(self, organisation: Organisation):
        """Check and send capacity alerts if needed"""
        utilization = organisation.get_capacity_utilization_percentage()
        
        if utilization >= 90:
            self.logger.warning(f"High capacity utilization ({utilization}%) for organisation: {organisation.organisation_id}")
            # Send capacity alert notification
    
    def _organisation_to_response_dto(self, organisation: Organisation) -> OrganisationResponseDTO:
        """Convert organisation entity to response DTO"""
        return OrganisationResponseDTO(
            organisation_id=organisation.organisation_id.value,
            name=organisation.name,
            description=organisation.description,
            organisation_type=organisation.organisation_type.value,
            status=organisation.status.value,
            hostname=organisation.hostname,
            contact_email=organisation.contact_information.email,
            contact_phone=organisation.contact_information.phone,
            contact_website=organisation.contact_information.website,
            contact_fax=organisation.contact_information.fax,
            address_street=organisation.address.street_address,
            address_city=organisation.address.city,
            address_state=organisation.address.state,
            address_country=organisation.address.country,
            address_pin_code=organisation.address.pin_code,
            address_landmark=organisation.address.landmark,
            pan_number=organisation.tax_information.pan_number,
            gst_number=organisation.tax_information.gst_number,
            tan_number=organisation.tax_information.tan_number,
            cin_number=organisation.tax_information.cin_number,
            employee_strength=organisation.employee_strength,
            used_employee_strength=organisation.used_employee_strength,
            capacity_utilization_percentage=organisation.get_capacity_utilization_percentage(),
            is_gst_registered=organisation.is_gst_registered(),
            created_at=organisation.created_at,
            updated_at=organisation.updated_at
        )
    
    def _organisation_to_summary_dto(self, organisation: Organisation) -> OrganisationSummaryDTO:
        """Convert organisation entity to summary DTO"""
        return OrganisationSummaryDTO(
            organisation_id=str(organisation.organisation_id),
            name=organisation.name,
            organisation_type=organisation.organisation_type.value,
            hostname=organisation.hostname,
            status=organisation.status.value,
            employee_strength=organisation.employee_strength,
            employee_usage=organisation.employee_usage,
            city=organisation.address.city,
            state=organisation.address.state,
            country=organisation.address.country,
            created_at=organisation.created_at,
            updated_at=organisation.updated_at
        )

    # ==================== MISSING ABSTRACT METHODS ====================

    async def get_organisation_by_pan(self, pan_number: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by PAN number"""
        try:
            organisation = await self.repository.get_by_pan_number(pan_number)
            if organisation:
                return self._organisation_to_response_dto(organisation)
            return None
        except Exception as e:
            self.logger.error(f"Error getting organisation by PAN {pan_number}: {e}")
            raise

    async def get_all_organisations(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> OrganisationListResponseDTO:
        """Get all organisations with pagination"""
        try:
            filters = OrganisationSearchFiltersDTO(
                page=skip // limit + 1,
                page_size=limit,
                include_inactive=include_inactive
            )
            return await self.search_organisations(filters)
        except Exception as e:
            self.logger.error(f"Error getting all organisations: {e}")
            raise

    async def get_organisations_by_status(self, status: str) -> List[OrganisationSummaryDTO]:
        """Get organisations by status"""
        try:
            filters = OrganisationSearchFiltersDTO(
                status=status,
                page=1,
                page_size=1000  # Large limit to get all
            )
            result = await self.search_organisations(filters)
            return result.organisations
        except Exception as e:
            self.logger.error(f"Error getting organisations by status {status}: {e}")
            raise

    async def get_organisations_by_type(self, organisation_type: str) -> List[OrganisationSummaryDTO]:
        """Get organisations by type"""
        try:
            filters = OrganisationSearchFiltersDTO(
                organisation_type=organisation_type,
                page=1,
                page_size=1000  # Large limit to get all
            )
            result = await self.search_organisations(filters)
            return result.organisations
        except Exception as e:
            self.logger.error(f"Error getting organisations by type {organisation_type}: {e}")
            raise

    async def get_organisations_by_location(
        self, 
        city: Optional[str] = None, 
        state: Optional[str] = None, 
        country: Optional[str] = None
    ) -> List[OrganisationSummaryDTO]:
        """Get organisations by location"""
        try:
            filters = OrganisationSearchFiltersDTO(
                city=city,
                state=state,
                country=country,
                page=1,
                page_size=1000  # Large limit to get all
            )
            result = await self.search_organisations(filters)
            return result.organisations
        except Exception as e:
            self.logger.error(f"Error getting organisations by location: {e}")
            raise

    async def check_organisation_exists(
        self, 
        name: Optional[str] = None,
        hostname: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """Check if organisation exists by various criteria"""
        try:
            result = {}
            
            if name:
                exists = await self.organisation_exists_by_name(name)
                if exclude_id and exists:
                    # Check if it's the same organisation being excluded
                    org = await self.repository.get_by_name(name)
                    if org and str(org.organisation_id) == exclude_id:
                        exists = False
                result["name"] = exists
            
            if hostname:
                exists = await self.organisation_exists_by_hostname(hostname)
                if exclude_id and exists:
                    # Check if it's the same organisation being excluded
                    org = await self.repository.get_by_hostname(hostname)
                    if org and str(org.organisation_id) == exclude_id:
                        exists = False
                result["hostname"] = exists
            
            if pan_number:
                exists = await self.organisation_exists_by_pan_number(pan_number)
                if exclude_id and exists:
                    # Check if it's the same organisation being excluded
                    org = await self.repository.get_by_pan_number(pan_number)
                    if org and str(org.organisation_id) == exclude_id:
                        exists = False
                result["pan_number"] = exists
            
            return result
        except Exception as e:
            self.logger.error(f"Error checking organisation existence: {e}")
            raise

    # ==================== ANALYTICS METHODS ====================

    async def get_organisation_analytics(self) -> OrganisationAnalyticsDTO:
        """Get advanced organisation analytics"""
        try:
            stats = await self.get_organisation_statistics()
            
            # Create analytics DTO with basic stats for now
            return OrganisationAnalyticsDTO(
                total_organisations=stats.total_organisations,
                active_organisations=stats.active_organisations,
                inactive_organisations=stats.inactive_organisations,
                total_employee_capacity=stats.total_employee_capacity,
                total_employee_usage=stats.total_employee_usage,
                capacity_utilization_percentage=stats.capacity_utilization_percentage,
                growth_metrics={
                    "monthly_growth": 0.0,
                    "quarterly_growth": 0.0,
                    "yearly_growth": 0.0
                },
                type_distribution=stats.organisations_by_type,
                status_distribution=stats.organisations_by_status,
                geographic_distribution={
                    "total_countries": 0,
                    "total_states": 0,
                    "total_cities": 0
                }
            )
        except Exception as e:
            self.logger.error(f"Error getting organisation analytics: {e}")
            raise

    async def get_capacity_utilization_report(self) -> Dict[str, Any]:
        """Get employee capacity utilization report"""
        try:
            stats = await self.get_organisation_statistics()
            
            return {
                "total_capacity": stats.total_employee_capacity,
                "total_usage": stats.total_employee_usage,
                "utilization_percentage": stats.capacity_utilization_percentage,
                "available_capacity": stats.total_employee_capacity - stats.total_employee_usage,
                "over_capacity_count": 0,  # Would need repository query
                "near_capacity_count": 0,  # Would need repository query
                "report_generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting capacity utilization report: {e}")
            raise

    async def get_growth_trends_report(self, months: int = 12) -> Dict[str, Any]:
        """Get organisation growth trends report"""
        try:
            # Basic implementation - would need time-series data from repository
            return {
                "period_months": months,
                "growth_data": [],
                "trend": "stable",
                "growth_rate": 0.0,
                "projected_growth": 0.0,
                "report_generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting growth trends report: {e}")
            raise

    async def get_geographic_distribution_report(self) -> Dict[str, Any]:
        """Get geographic distribution report"""
        try:
            # Basic implementation - would need aggregated data from repository
            return {
                "country_distribution": {},
                "state_distribution": {},
                "city_distribution": {},
                "total_countries": 0,
                "total_states": 0,
                "total_cities": 0,
                "report_generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting geographic distribution report: {e}")
            raise

    async def get_type_distribution_report(self) -> Dict[str, Any]:
        """Get organisation type distribution report"""
        try:
            stats = await self.get_organisation_statistics()
            
            return {
                "type_distribution": stats.organisations_by_type,
                "total_organisations": stats.total_organisations,
                "most_common_type": max(stats.organisations_by_type.items(), key=lambda x: x[1])[0] if stats.organisations_by_type else None,
                "report_generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting type distribution report: {e}")
            raise

    async def get_top_organisations_report(
        self, 
        criteria: str = "capacity", 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top organisations report by various criteria"""
        try:
            # Basic implementation - would need sorted query from repository
            filters = OrganisationSearchFiltersDTO(
                page=1,
                page_size=limit,
                sort_by=criteria,
                sort_order="desc"
            )
            result = await self.search_organisations(filters)
            
            return [
                {
                    "organisation_id": org.organisation_id,
                    "name": org.name,
                    "criteria_value": getattr(org, criteria, 0),
                    "rank": idx + 1
                }
                for idx, org in enumerate(result.organisations)
            ]
        except Exception as e:
            self.logger.error(f"Error getting top organisations report: {e}")
            raise

    # ==================== HEALTH METHODS ====================

    async def perform_health_check(self, organisation_id: str) -> OrganisationHealthCheckDTO:
        """Perform comprehensive health check for an organisation"""
        try:
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                raise OrganisationNotFoundError(f"Organisation {organisation_id} not found")
            
            # Basic health check implementation
            health_score = 100
            issues = []
            
            # Check capacity utilization
            if organisation.employee_usage > organisation.employee_strength:
                health_score -= 30
                issues.append("Over capacity")
            elif organisation.employee_usage / organisation.employee_strength > 0.9:
                health_score -= 10
                issues.append("Near capacity")
            
            # Check status
            if organisation.status != OrganisationStatus.ACTIVE:
                health_score -= 50
                issues.append(f"Organisation is {organisation.status.value}")
            
            return OrganisationHealthCheckDTO(
                organisation_id=organisation_id,
                organisation_name=organisation.name,
                health_score=max(0, health_score),
                status="healthy" if health_score >= 80 else "warning" if health_score >= 50 else "critical",
                issues=issues,
                last_checked=datetime.now(),
                recommendations=["Monitor capacity utilization"] if health_score < 100 else []
            )
        except Exception as e:
            self.logger.error(f"Error performing health check for {organisation_id}: {e}")
            raise

    async def get_unhealthy_organisations(self) -> List[OrganisationHealthCheckDTO]:
        """Get list of organisations with health issues"""
        try:
            # Get all organisations and check health
            all_orgs = await self.get_all_organisations(skip=0, limit=1000)
            unhealthy = []
            
            for org_summary in all_orgs.organisations:
                health_check = await self.perform_health_check(org_summary.organisation_id)
                if health_check.health_score < 80:
                    unhealthy.append(health_check)
            
            return unhealthy
        except Exception as e:
            self.logger.error(f"Error getting unhealthy organisations: {e}")
            raise

    # ==================== BULK OPERATIONS METHODS ====================

    async def bulk_update_status(
        self, 
        organisation_ids: List[str], 
        status: str,
        reason: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> BulkOrganisationUpdateResultDTO:
        """Bulk update organisation status"""
        try:
            successful_updates = []
            failed_updates = []
            
            for org_id in organisation_ids:
                try:
                    request = OrganisationStatusUpdateRequestDTO(
                        status=status,
                        reason=reason or "Bulk status update",
                        updated_by=updated_by
                    )
                    result = await self.update_organisation_status(org_id, request)
                    successful_updates.append(org_id)
                except Exception as e:
                    failed_updates.append({
                        "organisation_id": org_id,
                        "error": str(e)
                    })
            
            return BulkOrganisationUpdateResultDTO(
                total_requested=len(organisation_ids),
                successful_count=len(successful_updates),
                failed_count=len(failed_updates),
                successful_ids=successful_updates,
                failed_updates=failed_updates,
                operation_type="status_update",
                completed_at=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error in bulk status update: {e}")
            raise

    # ==================== VALIDATION METHODS ====================

    async def validate_organisation_update(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO
    ) -> List[str]:
        """Validate organisation update data"""
        try:
            errors = []
            
            # Get existing organisation
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.repository.get_by_id(org_id)
            
            if not organisation:
                errors.append(f"Organisation {organisation_id} not found")
                return errors
            
            # Validate uniqueness if name/hostname/pan changed
            if request.name and request.name != organisation.name:
                if await self.organisation_exists_by_name(request.name):
                    errors.append(f"Organisation with name '{request.name}' already exists")
            
            if request.hostname and request.hostname != organisation.hostname:
                if await self.organisation_exists_by_hostname(request.hostname):
                    errors.append(f"Organisation with hostname '{request.hostname}' already exists")
            
            if request.pan_number and request.pan_number != organisation.tax_information.pan_number:
                if await self.organisation_exists_by_pan_number(request.pan_number):
                    errors.append(f"Organisation with PAN '{request.pan_number}' already exists")
            
            return errors
        except Exception as e:
            self.logger.error(f"Error validating organisation update: {e}")
            raise

    async def validate_business_rules(self, organisation: Organisation) -> List[str]:
        """Validate organisation business rules"""
        try:
            errors = []
            
            # Check employee capacity constraints
            if organisation.employee_usage > organisation.employee_strength:
                errors.append("Employee usage cannot exceed employee strength")
            
            # Check status transitions
            if organisation.status == OrganisationStatus.DELETED and organisation.employee_usage > 0:
                errors.append("Cannot delete organisation with active employees")
            
            # Check required fields
            if not organisation.name or len(organisation.name.strip()) == 0:
                errors.append("Organisation name is required")
            
            if not organisation.hostname or len(organisation.hostname.strip()) == 0:
                errors.append("Organisation hostname is required")
            
            return errors
        except Exception as e:
            self.logger.error(f"Error validating business rules: {e}")
            raise

    async def validate_uniqueness_constraints(
        self, 
        name: Optional[str] = None,
        hostname: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> List[str]:
        """Validate uniqueness constraints"""
        try:
            errors = []
            
            existence_check = await self.check_organisation_exists(
                name=name,
                hostname=hostname,
                pan_number=pan_number,
                exclude_id=exclude_id
            )
            
            if existence_check.get("name", False):
                errors.append(f"Organisation with name '{name}' already exists")
            
            if existence_check.get("hostname", False):
                errors.append(f"Organisation with hostname '{hostname}' already exists")
            
            if existence_check.get("pan_number", False):
                errors.append(f"Organisation with PAN '{pan_number}' already exists")
            
            return errors
        except Exception as e:
            self.logger.error(f"Error validating uniqueness constraints: {e}")
            raise

    # ==================== NOTIFICATION METHODS ====================

    async def send_organisation_created_notification(self, organisation: Organisation) -> bool:
        """Send notification when organisation is created"""
        try:
            await self._send_creation_notification(organisation)
            return True
        except Exception as e:
            self.logger.error(f"Error sending creation notification: {e}")
            return False

    async def send_organisation_updated_notification(
        self, 
        organisation: Organisation, 
        updated_fields: List[str]
    ) -> bool:
        """Send notification when organisation is updated"""
        try:
            await self._send_update_notification(organisation)
            return True
        except Exception as e:
            self.logger.error(f"Error sending update notification: {e}")
            return False

    async def send_status_change_notification(
        self, 
        organisation: Organisation, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send notification when organisation status changes"""
        try:
            await self._send_status_change_notification(
                organisation, 
                OrganisationStatus(new_status), 
                reason or "Status changed"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error sending status change notification: {e}")
            return False

    async def send_capacity_alert_notification(
        self, 
        organisation: Organisation, 
        alert_type: str
    ) -> bool:
        """Send notification for capacity alerts"""
        try:
            await self._check_capacity_alerts(organisation)
            return True
        except Exception as e:
            self.logger.error(f"Error sending capacity alert notification: {e}")
            return False

    # ==================== PRIVATE HELPER METHODS ==================== 