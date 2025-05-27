"""
Update Organization Use Case
Handles the business logic for updating an existing organization
"""

import logging
from typing import List, Optional

from domain.entities.organization import Organization
from domain.value_objects.organization_id import OrganizationId
from domain.value_objects.organization_details import (
    ContactInformation, Address, TaxInformation, OrganizationType
)
from application.dto.organization_dto import (
    UpdateOrganizationRequestDTO, OrganizationResponseDTO,
    OrganizationValidationError, OrganizationNotFoundError,
    OrganizationBusinessRuleError, OrganizationConflictError
)
from application.interfaces.repositories.organization_repository import (
    OrganizationCommandRepository, OrganizationQueryRepository
)
from application.interfaces.services.organization_service import (
    OrganizationValidationService, OrganizationNotificationService
)


logger = logging.getLogger(__name__)


class UpdateOrganizationUseCase:
    """
    Use case for updating an existing organization.
    
    Follows SOLID principles:
    - SRP: Only handles organization update logic
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Organization must exist
    2. Organization name must be unique (if changed)
    3. Hostname must be unique (if changed)
    4. PAN number must be unique (if changed)
    5. Contact information must be valid (if provided)
    6. Address must be valid (if provided)
    7. Tax information must be valid (if provided)
    8. Employee strength cannot be reduced below current usage
    """
    
    def __init__(
        self,
        command_repository: OrganizationCommandRepository,
        query_repository: OrganizationQueryRepository,
        validation_service: OrganizationValidationService,
        notification_service: OrganizationNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.validation_service = validation_service
        self.notification_service = notification_service
    
    async def execute(
        self, 
        organization_id: str, 
        request: UpdateOrganizationRequestDTO
    ) -> OrganizationResponseDTO:
        """
        Execute the update organization use case.
        
        Args:
            organization_id: ID of organization to update
            request: Organization update request DTO
            
        Returns:
            Updated organization response DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationValidationError: If request data is invalid
            OrganizationConflictError: If update conflicts with existing data
            OrganizationBusinessRuleError: If business rules are violated
        """
        logger.info(f"Updating organization: {organization_id}")
        
        # Step 1: Get existing organization
        organization = await self._get_existing_organization(organization_id)
        
        # Step 2: Validate request data
        await self._validate_request(organization_id, request)
        
        # Step 3: Check uniqueness constraints (if applicable)
        await self._check_uniqueness_constraints(organization_id, request)
        
        # Step 4: Track updated fields for notifications
        updated_fields = []
        
        # Step 5: Update basic information
        if self._should_update_basic_info(request):
            self._update_basic_info(organization, request, updated_fields)
        
        # Step 6: Update contact information
        if self._should_update_contact_info(request):
            await self._update_contact_info(organization, request, updated_fields)
        
        # Step 7: Update address
        if self._should_update_address(request):
            await self._update_address(organization, request, updated_fields)
        
        # Step 8: Update tax information
        if self._should_update_tax_info(request):
            await self._update_tax_info(organization, request, updated_fields)
        
        # Step 9: Update employee strength
        if request.employee_strength is not None:
            await self._update_employee_strength(organization, request, updated_fields)
        
        # Step 10: Update system configuration
        if self._should_update_system_config(request):
            self._update_system_config(organization, request, updated_fields)
        
        # Step 11: Validate business rules
        await self._validate_business_rules(organization)
        
        # Step 12: Save organization
        saved_organization = await self.command_repository.save(organization)
        
        # Step 13: Send notifications (non-blocking)
        if updated_fields:
            try:
                await self.notification_service.send_organization_updated_notification(
                    saved_organization, updated_fields
                )
            except Exception as e:
                logger.warning(f"Failed to send organization updated notification: {e}")
        
        # Step 14: Convert to response DTO
        response = self._convert_to_response_dto(saved_organization)
        
        logger.info(f"Organization updated successfully: {organization_id}")
        return response
    
    async def _get_existing_organization(self, organization_id: str) -> Organization:
        """Get existing organization"""
        org_id = OrganizationId.from_string(organization_id)
        organization = await self.query_repository.get_by_id(org_id)
        
        if not organization:
            raise OrganizationNotFoundError(organization_id)
        
        return organization
    
    async def _validate_request(
        self, 
        organization_id: str, 
        request: UpdateOrganizationRequestDTO
    ) -> None:
        """Validate the request data"""
        validation_errors = await self.validation_service.validate_organization_update(
            organization_id, request
        )
        
        if validation_errors:
            raise OrganizationValidationError(
                "Organization update data is invalid",
                validation_errors
            )
    
    async def _check_uniqueness_constraints(
        self, 
        organization_id: str, 
        request: UpdateOrganizationRequestDTO
    ) -> None:
        """Check uniqueness constraints for changed fields"""
        uniqueness_errors = await self.validation_service.validate_uniqueness_constraints(
            name=request.name,
            hostname=request.hostname,
            pan_number=request.pan_number,
            exclude_id=organization_id
        )
        
        if uniqueness_errors:
            raise OrganizationConflictError(
                "Organization update conflicts with existing data",
                "uniqueness"
            )
    
    def _should_update_basic_info(self, request: UpdateOrganizationRequestDTO) -> bool:
        """Check if basic info should be updated"""
        return any([
            request.name is not None,
            request.description is not None,
            request.organization_type is not None
        ])
    
    def _update_basic_info(
        self, 
        organization: Organization, 
        request: UpdateOrganizationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update basic organization information"""
        organization_type = None
        if request.organization_type:
            organization_type = OrganizationType(request.organization_type)
        
        organization.update_basic_info(
            name=request.name,
            description=request.description,
            organization_type=organization_type,
            updated_by=request.updated_by
        )
        
        if request.name is not None:
            updated_fields.append("name")
        if request.description is not None:
            updated_fields.append("description")
        if request.organization_type is not None:
            updated_fields.append("organization_type")
    
    def _should_update_contact_info(self, request: UpdateOrganizationRequestDTO) -> bool:
        """Check if contact info should be updated"""
        return any([
            request.email is not None,
            request.phone is not None,
            request.website is not None,
            request.fax is not None
        ])
    
    async def _update_contact_info(
        self, 
        organization: Organization, 
        request: UpdateOrganizationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update contact information"""
        try:
            # Use existing values if not provided in request
            current_contact = organization.contact_info
            
            new_contact_info = ContactInformation(
                email=request.email if request.email is not None else current_contact.email,
                phone=request.phone if request.phone is not None else current_contact.phone,
                website=request.website if request.website is not None else current_contact.website,
                fax=request.fax if request.fax is not None else current_contact.fax
            )
            
            organization.update_contact_info(new_contact_info, request.updated_by)
            updated_fields.append("contact_info")
            
        except ValueError as e:
            raise OrganizationValidationError(f"Invalid contact information: {e}")
    
    def _should_update_address(self, request: UpdateOrganizationRequestDTO) -> bool:
        """Check if address should be updated"""
        return any([
            request.street_address is not None,
            request.city is not None,
            request.state is not None,
            request.country is not None,
            request.pin_code is not None,
            request.landmark is not None
        ])
    
    async def _update_address(
        self, 
        organization: Organization, 
        request: UpdateOrganizationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update address"""
        try:
            # Use existing values if not provided in request
            current_address = organization.address
            
            new_address = Address(
                street_address=request.street_address if request.street_address is not None else current_address.street_address,
                city=request.city if request.city is not None else current_address.city,
                state=request.state if request.state is not None else current_address.state,
                country=request.country if request.country is not None else current_address.country,
                pin_code=request.pin_code if request.pin_code is not None else current_address.pin_code,
                landmark=request.landmark if request.landmark is not None else current_address.landmark
            )
            
            organization.update_address(new_address, request.updated_by)
            updated_fields.append("address")
            
        except ValueError as e:
            raise OrganizationValidationError(f"Invalid address: {e}")
    
    def _should_update_tax_info(self, request: UpdateOrganizationRequestDTO) -> bool:
        """Check if tax info should be updated"""
        return any([
            request.pan_number is not None,
            request.gst_number is not None,
            request.tan_number is not None,
            request.cin_number is not None
        ])
    
    async def _update_tax_info(
        self, 
        organization: Organization, 
        request: UpdateOrganizationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update tax information"""
        try:
            # Use existing values if not provided in request
            current_tax = organization.tax_info
            
            new_tax_info = TaxInformation(
                pan_number=request.pan_number if request.pan_number is not None else current_tax.pan_number,
                gst_number=request.gst_number if request.gst_number is not None else current_tax.gst_number,
                tan_number=request.tan_number if request.tan_number is not None else current_tax.tan_number,
                cin_number=request.cin_number if request.cin_number is not None else current_tax.cin_number
            )
            
            organization.update_tax_info(new_tax_info, request.updated_by)
            updated_fields.append("tax_info")
            
        except ValueError as e:
            raise OrganizationValidationError(f"Invalid tax information: {e}")
    
    async def _update_employee_strength(
        self, 
        organization: Organization, 
        request: UpdateOrganizationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update employee strength"""
        try:
            organization.update_employee_strength(
                request.employee_strength, 
                request.updated_by
            )
            updated_fields.append("employee_strength")
            
        except ValueError as e:
            raise OrganizationBusinessRuleError(f"Employee strength update failed: {e}")
    
    def _should_update_system_config(self, request: UpdateOrganizationRequestDTO) -> bool:
        """Check if system config should be updated"""
        return any([
            request.hostname is not None,
            request.logo_path is not None
        ])
    
    def _update_system_config(
        self, 
        organization: Organization, 
        request: UpdateOrganizationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update system configuration"""
        if request.hostname is not None:
            organization.hostname = request.hostname
            updated_fields.append("hostname")
        
        if request.logo_path is not None:
            organization.logo_path = request.logo_path
            updated_fields.append("logo_path")
        
        if updated_fields:
            organization.updated_by = request.updated_by
    
    async def _validate_business_rules(self, organization: Organization) -> None:
        """Validate business rules"""
        business_rule_errors = await self.validation_service.validate_business_rules(organization)
        
        if business_rule_errors:
            raise OrganizationBusinessRuleError(
                "Organization violates business rules",
                "business_rules"
            )
    
    def _convert_to_response_dto(self, organization: Organization) -> OrganizationResponseDTO:
        """Convert organization entity to response DTO"""
        return OrganizationResponseDTO(
            organization_id=str(organization.organization_id),
            name=organization.name,
            description=organization.description,
            organization_type=organization.organization_type.value,
            status=organization.status.value,
            contact_info=self._convert_contact_info_to_dto(organization.contact_info),
            address=self._convert_address_to_dto(organization.address),
            tax_info=self._convert_tax_info_to_dto(organization.tax_info),
            employee_strength=organization.employee_strength,
            used_employee_strength=organization.used_employee_strength,
            available_capacity=organization.get_available_employee_capacity(),
            utilization_percentage=organization.get_employee_utilization_percentage(),
            hostname=organization.hostname,
            logo_path=organization.logo_path,
            created_at=organization.created_at.isoformat(),
            updated_at=organization.updated_at.isoformat(),
            created_by=organization.created_by,
            updated_by=organization.updated_by,
            is_active=organization.is_active(),
            is_government=organization.is_government_organization(),
            has_available_capacity=organization.has_available_employee_capacity(),
            display_name=organization.get_display_name()
        )
    
    def _convert_contact_info_to_dto(self, contact_info: ContactInformation):
        """Convert contact information to DTO"""
        if not contact_info:
            return None
        
        from application.dto.organization_dto import ContactInformationResponseDTO
        return ContactInformationResponseDTO(
            email=contact_info.email,
            phone=contact_info.phone,
            website=contact_info.website,
            fax=contact_info.fax,
            formatted_phone=contact_info.get_formatted_phone(),
            domain=contact_info.get_domain_from_email()
        )
    
    def _convert_address_to_dto(self, address: Address):
        """Convert address to DTO"""
        if not address:
            return None
        
        from application.dto.organization_dto import AddressResponseDTO
        return AddressResponseDTO(
            street_address=address.street_address,
            city=address.city,
            state=address.state,
            country=address.country,
            pin_code=address.pin_code,
            landmark=address.landmark,
            full_address=address.get_full_address(),
            short_address=address.get_short_address(),
            is_indian_address=address.is_indian_address()
        )
    
    def _convert_tax_info_to_dto(self, tax_info: TaxInformation):
        """Convert tax information to DTO"""
        if not tax_info:
            return None
        
        from application.dto.organization_dto import TaxInformationResponseDTO
        return TaxInformationResponseDTO(
            pan_number=tax_info.pan_number,
            gst_number=tax_info.gst_number,
            tan_number=tax_info.tan_number,
            cin_number=tax_info.cin_number,
            is_gst_registered=tax_info.is_gst_registered(),
            gst_state_code=tax_info.get_state_code_from_gst()
        ) 