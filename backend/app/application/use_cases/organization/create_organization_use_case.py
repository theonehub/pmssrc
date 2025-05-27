"""
Create Organization Use Case
Handles the business logic for creating a new organization
"""

import logging
from typing import List

from domain.entities.organization import Organization
from domain.value_objects.organization_id import OrganizationId
from domain.value_objects.organization_details import (
    ContactInformation, Address, TaxInformation, OrganizationType
)
from application.dto.organization_dto import (
    CreateOrganizationRequestDTO, OrganizationResponseDTO,
    OrganizationValidationError, OrganizationConflictError,
    OrganizationBusinessRuleError
)
from application.interfaces.repositories.organization_repository import (
    OrganizationCommandRepository, OrganizationQueryRepository
)
from application.interfaces.services.organization_service import (
    OrganizationValidationService, OrganizationNotificationService
)


logger = logging.getLogger(__name__)


class CreateOrganizationUseCase:
    """
    Use case for creating a new organization.
    
    Follows SOLID principles:
    - SRP: Only handles organization creation logic
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Organization name must be unique
    2. Hostname must be unique (if provided)
    3. PAN number must be unique
    4. All required fields must be provided
    5. Contact information must be valid
    6. Address must be valid
    7. Tax information must be valid
    8. Employee strength must be positive
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
    
    async def execute(self, request: CreateOrganizationRequestDTO) -> OrganizationResponseDTO:
        """
        Execute the create organization use case.
        
        Args:
            request: Organization creation request DTO
            
        Returns:
            Created organization response DTO
            
        Raises:
            OrganizationValidationError: If request data is invalid
            OrganizationConflictError: If organization already exists
            OrganizationBusinessRuleError: If business rules are violated
        """
        logger.info(f"Creating organization: {request.name}")
        
        # Step 1: Validate request data
        await self._validate_request(request)
        
        # Step 2: Check uniqueness constraints
        await self._check_uniqueness_constraints(request)
        
        # Step 3: Create value objects
        contact_info = self._create_contact_information(request)
        address = self._create_address(request)
        tax_info = self._create_tax_information(request)
        organization_type = OrganizationType(request.organization_type)
        
        # Step 4: Create organization entity
        organization = Organization.create_new_organization(
            name=request.name,
            contact_info=contact_info,
            address=address,
            tax_info=tax_info,
            organization_type=organization_type,
            employee_strength=request.employee_strength,
            hostname=request.hostname,
            description=request.description,
            created_by=request.created_by
        )
        
        # Step 5: Validate business rules
        await self._validate_business_rules(organization)
        
        # Step 6: Save organization
        saved_organization = await self.command_repository.save(organization)
        
        # Step 7: Send notifications (non-blocking)
        try:
            await self.notification_service.send_organization_created_notification(saved_organization)
        except Exception as e:
            logger.warning(f"Failed to send organization created notification: {e}")
        
        # Step 8: Convert to response DTO
        response = self._convert_to_response_dto(saved_organization)
        
        logger.info(f"Organization created successfully: {saved_organization.organization_id}")
        return response
    
    async def _validate_request(self, request: CreateOrganizationRequestDTO) -> None:
        """Validate the request data"""
        validation_errors = await self.validation_service.validate_organization_data(request)
        
        if validation_errors:
            raise OrganizationValidationError(
                "Organization creation data is invalid",
                validation_errors
            )
    
    async def _check_uniqueness_constraints(self, request: CreateOrganizationRequestDTO) -> None:
        """Check uniqueness constraints"""
        uniqueness_errors = await self.validation_service.validate_uniqueness_constraints(
            name=request.name,
            hostname=request.hostname,
            pan_number=request.pan_number
        )
        
        if uniqueness_errors:
            raise OrganizationConflictError(
                "Organization conflicts with existing data",
                "uniqueness"
            )
    
    def _create_contact_information(self, request: CreateOrganizationRequestDTO) -> ContactInformation:
        """Create contact information value object"""
        try:
            return ContactInformation(
                email=request.email,
                phone=request.phone,
                website=request.website,
                fax=request.fax
            )
        except ValueError as e:
            raise OrganizationValidationError(f"Invalid contact information: {e}")
    
    def _create_address(self, request: CreateOrganizationRequestDTO) -> Address:
        """Create address value object"""
        try:
            return Address(
                street_address=request.street_address,
                city=request.city,
                state=request.state,
                country=request.country,
                pin_code=request.pin_code,
                landmark=request.landmark
            )
        except ValueError as e:
            raise OrganizationValidationError(f"Invalid address: {e}")
    
    def _create_tax_information(self, request: CreateOrganizationRequestDTO) -> TaxInformation:
        """Create tax information value object"""
        try:
            return TaxInformation(
                pan_number=request.pan_number,
                gst_number=request.gst_number,
                tan_number=request.tan_number,
                cin_number=request.cin_number
            )
        except ValueError as e:
            raise OrganizationValidationError(f"Invalid tax information: {e}")
    
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