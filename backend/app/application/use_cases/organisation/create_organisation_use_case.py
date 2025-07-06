"""
Create Organisation Use Case
Handles the business logic for creating a new organisation
"""

import logging
from typing import List

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    ContactInformation, Address, TaxInformation, OrganisationType
)
from app.application.dto.organisation_dto import (
    CreateOrganisationRequestDTO, OrganisationResponseDTO,
    OrganisationValidationError, OrganisationConflictError,
    OrganisationBusinessRuleError
)
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationCommandRepository, OrganisationQueryRepository
)
from app.application.interfaces.services.organisation_service import (
    OrganisationValidationService, OrganisationNotificationService
)


logger = logging.getLogger(__name__)


class CreateOrganisationUseCase:
    """
    Use case for creating a new organisation.
    
    Follows SOLID principles:
    - SRP: Only handles organisation creation logic
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Organisation name must be unique
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
        command_repository: OrganisationCommandRepository,
        query_repository: OrganisationQueryRepository,
        validation_service: OrganisationValidationService,
        notification_service: OrganisationNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.validation_service = validation_service
        self.notification_service = notification_service
    
    async def execute(self, request: CreateOrganisationRequestDTO) -> OrganisationResponseDTO:
        """
        Execute the create organisation use case.
        
        Args:
            request: Organisation creation request DTO
            
        Returns:
            Created organisation response DTO
            
        Raises:
            OrganisationValidationError: If request data is invalid
            OrganisationConflictError: If organisation already exists
            OrganisationBusinessRuleError: If business rules are violated
        """
        logger.info(f"Creating organisation: {request.name}")
        
        # Step 1: Validate request data
        await self._validate_request(request)
        
        # Step 2: Check uniqueness constraints
        await self._check_uniqueness_constraints(request)
        
        # Step 3: Create value objects
        contact_info = self._create_contact_information(request)
        address = self._create_address(request)
        tax_info = self._create_tax_information(request)
        organisation_type = OrganisationType(request.organisation_type)
        
        # Step 4: Create organisation entity (add logo_path)
        organisation = Organisation.create_new_organisation(
            name=request.name,
            contact_info=contact_info,
            address=address,
            tax_info=tax_info,
            organisation_type=organisation_type,
            employee_strength=request.employee_strength,
            hostname=request.hostname,
            description=request.description,
            created_by=request.created_by
        )
        if hasattr(request, 'logo_path') and request.logo_path:
            organisation.logo_path = request.logo_path
        
        # Step 5: Validate business rules
        await self._validate_business_rules(organisation)
        
        # Step 6: Save organisation
        saved_organisation = await self.command_repository.save(organisation)
        
        # Step 7: Send notifications (non-blocking)
        try:
            await self.notification_service.send_organisation_created_notification(saved_organisation)
        except Exception as e:
            logger.warning(f"Failed to send organisation created notification: {e}")
        
        # Step 8: Convert to response DTO
        response = self._convert_to_response_dto(saved_organisation)
        
        logger.info(f"Organisation created successfully: {saved_organisation.organisation_id}")
        return response
    
    async def _validate_request(self, request: CreateOrganisationRequestDTO) -> None:
        """Validate the request data"""
        validation_errors = await self.validation_service.validate_organisation_data(request)
        
        if validation_errors:
            raise OrganisationValidationError(
                "Organisation creation data is invalid",
                validation_errors
            )
    
    async def _check_uniqueness_constraints(self, request: CreateOrganisationRequestDTO) -> None:
        """Check uniqueness constraints"""
        uniqueness_errors = await self.validation_service.validate_uniqueness_constraints(
            name=request.name,
            hostname=request.hostname,
            pan_number=request.pan_number
        )
        
        if uniqueness_errors:
            raise OrganisationConflictError(
                "Organisation conflicts with existing data",
                "uniqueness"
            )
    
    def _create_contact_information(self, request: CreateOrganisationRequestDTO) -> ContactInformation:
        """Create contact information value object"""
        try:
            return ContactInformation(
                email=request.email,
                phone=request.phone,
                website=request.website,
                fax=request.fax
            )
        except ValueError as e:
            raise OrganisationValidationError(f"Invalid contact information: {e}")
    
    def _create_address(self, request: CreateOrganisationRequestDTO) -> Address:
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
            raise OrganisationValidationError(f"Invalid address: {e}")
    
    def _create_tax_information(self, request: CreateOrganisationRequestDTO) -> TaxInformation:
        """Create tax information value object"""
        try:
            return TaxInformation(
                pan_number=request.pan_number,
                gst_number=request.gst_number,
                tan_number=request.tan_number,
                cin_number=request.cin_number
            )
        except ValueError as e:
            raise OrganisationValidationError(f"Invalid tax information: {e}")
    
    async def _validate_business_rules(self, organisation: Organisation) -> None:
        """Validate business rules"""
        business_rule_errors = await self.validation_service.validate_business_rules(organisation)
        
        if business_rule_errors:
            raise OrganisationBusinessRuleError(
                "Organisation violates business rules",
                "business_rules"
            )
    
    def _convert_to_response_dto(self, organisation: Organisation) -> OrganisationResponseDTO:
        """Convert organisation entity to response DTO"""
        return OrganisationResponseDTO(
            organisation_id=str(organisation.organisation_id),
            name=organisation.name,
            description=organisation.description,
            organisation_type=organisation.organisation_type.value,
            status=organisation.status.value,
            contact_info=self._convert_contact_info_to_dto(organisation.contact_info),
            address=self._convert_address_to_dto(organisation.address),
            tax_info=self._convert_tax_info_to_dto(organisation.tax_info),
            employee_strength=organisation.employee_strength,
            used_employee_strength=organisation.used_employee_strength,
            available_capacity=organisation.get_available_employee_capacity(),
            utilization_percentage=organisation.get_employee_utilization_percentage(),
            hostname=organisation.hostname,
            logo_path=organisation.logo_path,
            created_at=organisation.created_at.isoformat(),
            updated_at=organisation.updated_at.isoformat(),
            created_by=organisation.created_by,
            updated_by=organisation.updated_by,
            is_active=organisation.is_active(),
            is_government=organisation.is_government_organisation(),
            has_available_capacity=organisation.has_available_employee_capacity(),
            display_name=organisation.get_display_name()
        )
    
    def _convert_contact_info_to_dto(self, contact_info: ContactInformation):
        """Convert contact information to DTO"""
        if not contact_info:
            return None
        
        from app.application.dto.organisation_dto import ContactInformationResponseDTO
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
        
        from app.application.dto.organisation_dto import AddressResponseDTO
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
        
        from app.application.dto.organisation_dto import TaxInformationResponseDTO
        return TaxInformationResponseDTO(
            pan_number=tax_info.pan_number,
            gst_number=tax_info.gst_number,
            tan_number=tax_info.tan_number,
            cin_number=tax_info.cin_number,
            is_gst_registered=tax_info.is_gst_registered(),
            gst_state_code=tax_info.get_state_code_from_gst()
        ) 