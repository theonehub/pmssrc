"""
Update Organisation Use Case
Handles the business logic for updating an existing organisation
"""

import logging
from typing import List, Optional

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    ContactInformation, Address, TaxInformation, OrganisationType, BankDetails
)
from app.application.dto.organisation_dto import (
    UpdateOrganisationRequestDTO, OrganisationResponseDTO,
    OrganisationValidationError, OrganisationNotFoundError,
    OrganisationBusinessRuleError, OrganisationConflictError
)
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationCommandRepository, OrganisationQueryRepository
)
from app.application.interfaces.services.organisation_service import (
    OrganisationValidationService, OrganisationNotificationService
)


logger = logging.getLogger(__name__)


class UpdateOrganisationUseCase:
    """
    Use case for updating an existing organisation.
    
    Follows SOLID principles:
    - SRP: Only handles organisation update logic
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Organisation must exist
    2. Organisation name must be unique (if changed)
    3. Hostname must be unique (if changed)
    4. PAN number must be unique (if changed)
    5. Contact information must be valid (if provided)
    6. Address must be valid (if provided)
    7. Tax information must be valid (if provided)
    8. Employee strength cannot be reduced below current usage
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
    
    async def execute(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO
    ) -> OrganisationResponseDTO:
        """
        Execute the update organisation use case.
        
        Args:
            organisation_id: ID of organisation to update
            request: Organisation update request DTO
            
        Returns:
            Updated organisation response DTO
            
        Raises:
            OrganisationNotFoundError: If organisation not found
            OrganisationValidationError: If request data is invalid
            OrganisationConflictError: If update conflicts with existing data
            OrganisationBusinessRuleError: If business rules are violated
        """
        logger.info(f"Updating organisation: {organisation_id}")
        
        # Step 1: Get existing organisation
        organisation = await self._get_existing_organisation(organisation_id)
        
        # Step 2: Validate request data
        await self._validate_request(organisation_id, request)
        
        # Step 3: Check uniqueness constraints (if applicable)
        await self._check_uniqueness_constraints(organisation_id, request)
        
        # Step 4: Track updated fields for notifications
        updated_fields = []
        
        # Step 5: Update basic information
        if self._should_update_basic_info(request):
            self._update_basic_info(organisation, request, updated_fields)
        
        # Step 6: Update contact information
        if self._should_update_contact_info(request):
            await self._update_contact_info(organisation, request, updated_fields)
        
        # Step 7: Update address
        if self._should_update_address(request):
            await self._update_address(organisation, request, updated_fields)
        
        # Step 8: Update tax information
        if self._should_update_tax_info(request):
            await self._update_tax_info(organisation, request, updated_fields)
        
        # Step 9: Update employee strength
        if request.employee_strength is not None:
            await self._update_employee_strength(organisation, request, updated_fields)
        
        # Step 10: Update system configuration
        if self._should_update_system_config(request):
            self._update_system_config(organisation, request, updated_fields)
        
        # Step 10.5: Update bank details if provided
        if hasattr(request, 'bank_details') and request.bank_details:
            bank_details = self._create_bank_details(request)
            organisation.update_bank_details(bank_details, request.updated_by)
            updated_fields.append("bank_details")
        
        # Step 11: Validate business rules
        await self._validate_business_rules(organisation)
        
        # Step 12: Save organisation
        saved_organisation = await self.command_repository.save(organisation)
        
        # Step 13: Send notifications (non-blocking)
        if updated_fields:
            try:
                await self.notification_service.send_organisation_updated_notification(
                    saved_organisation, updated_fields
                )
            except Exception as e:
                logger.warning(f"Failed to send organisation updated notification: {e}")
        
        # Step 14: Convert to response DTO
        response = self._convert_to_response_dto(saved_organisation)
        
        logger.info(f"Organisation updated successfully: {organisation_id}")
        return response
    
    async def _get_existing_organisation(self, organisation_id: str) -> Organisation:
        """Get existing organisation"""
        org_id = OrganisationId.from_string(organisation_id)
        organisation = await self.query_repository.get_by_id(org_id)
        
        if not organisation:
            raise OrganisationNotFoundError(organisation_id)
        
        return organisation
    
    async def _validate_request(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO
    ) -> None:
        """Validate the request data"""
        validation_errors = await self.validation_service.validate_organisation_update(
            organisation_id, request
        )
        
        if validation_errors:
            raise OrganisationValidationError(
                "Organisation update data is invalid",
                validation_errors
            )
    
    async def _check_uniqueness_constraints(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO
    ) -> None:
        """Check uniqueness constraints for changed fields"""
        uniqueness_errors = await self.validation_service.validate_uniqueness_constraints(
            name=request.name,
            hostname=request.hostname,
            pan_number=request.pan_number,
            exclude_id=organisation_id
        )
        
        if uniqueness_errors:
            raise OrganisationConflictError(
                "Organisation update conflicts with existing data",
                "uniqueness"
            )
    
    def _should_update_basic_info(self, request: UpdateOrganisationRequestDTO) -> bool:
        """Check if basic info should be updated"""
        return any([
            request.name is not None,
            request.description is not None,
            request.organisation_type is not None
        ])
    
    def _update_basic_info(
        self, 
        organisation: Organisation, 
        request: UpdateOrganisationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update basic organisation information"""
        organisation_type = None
        if request.organisation_type:
            organisation_type = OrganisationType(request.organisation_type)
        
        organisation.update_basic_info(
            name=request.name,
            description=request.description,
            organisation_type=organisation_type,
            updated_by=request.updated_by
        )
        
        if request.name is not None:
            updated_fields.append("name")
        if request.description is not None:
            updated_fields.append("description")
        if request.organisation_type is not None:
            updated_fields.append("organisation_type")
    
    def _should_update_contact_info(self, request: UpdateOrganisationRequestDTO) -> bool:
        """Check if contact info should be updated"""
        return any([
            request.email is not None,
            request.phone is not None,
            request.website is not None,
            request.fax is not None
        ])
    
    async def _update_contact_info(
        self, 
        organisation: Organisation, 
        request: UpdateOrganisationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update contact information"""
        try:
            # Use existing values if not provided in request
            current_contact = organisation.contact_info
            
            new_contact_info = ContactInformation(
                email=request.email if request.email is not None else current_contact.email,
                phone=request.phone if request.phone is not None else current_contact.phone,
                website=request.website if request.website is not None else current_contact.website,
                fax=request.fax if request.fax is not None else current_contact.fax
            )
            
            organisation.update_contact_info(new_contact_info, request.updated_by)
            updated_fields.append("contact_info")
            
        except ValueError as e:
            raise OrganisationValidationError(f"Invalid contact information: {e}")
    
    def _should_update_address(self, request: UpdateOrganisationRequestDTO) -> bool:
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
        organisation: Organisation, 
        request: UpdateOrganisationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update address"""
        try:
            # Use existing values if not provided in request
            current_address = organisation.address
            
            new_address = Address(
                street_address=request.street_address if request.street_address is not None else current_address.street_address,
                city=request.city if request.city is not None else current_address.city,
                state=request.state if request.state is not None else current_address.state,
                country=request.country if request.country is not None else current_address.country,
                pin_code=request.pin_code if request.pin_code is not None else current_address.pin_code,
                landmark=request.landmark if request.landmark is not None else current_address.landmark
            )
            
            organisation.update_address(new_address, request.updated_by)
            updated_fields.append("address")
            
        except ValueError as e:
            raise OrganisationValidationError(f"Invalid address: {e}")
    
    def _should_update_tax_info(self, request: UpdateOrganisationRequestDTO) -> bool:
        """Check if tax info should be updated"""
        return any([
            request.pan_number is not None,
            request.gst_number is not None,
            request.tan_number is not None,
            request.cin_number is not None
        ])
    
    async def _update_tax_info(
        self, 
        organisation: Organisation, 
        request: UpdateOrganisationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update tax information"""
        try:
            # Use existing values if not provided in request
            current_tax = organisation.tax_info
            
            new_tax_info = TaxInformation(
                pan_number=request.pan_number if request.pan_number is not None else current_tax.pan_number,
                gst_number=request.gst_number if request.gst_number is not None else current_tax.gst_number,
                tan_number=request.tan_number if request.tan_number is not None else current_tax.tan_number,
                cin_number=request.cin_number if request.cin_number is not None else current_tax.cin_number
            )
            
            organisation.update_tax_info(new_tax_info, request.updated_by)
            updated_fields.append("tax_info")
            
        except ValueError as e:
            raise OrganisationValidationError(f"Invalid tax information: {e}")
    
    async def _update_employee_strength(
        self, 
        organisation: Organisation, 
        request: UpdateOrganisationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update employee strength"""
        try:
            organisation.update_employee_strength(
                request.employee_strength, 
                request.updated_by
            )
            updated_fields.append("employee_strength")
            
        except ValueError as e:
            raise OrganisationBusinessRuleError(f"Employee strength update failed: {e}")
    
    def _should_update_system_config(self, request: UpdateOrganisationRequestDTO) -> bool:
        """Check if system config should be updated"""
        return any([
            request.hostname is not None,
            request.logo_path is not None
        ])
    
    def _update_system_config(
        self, 
        organisation: Organisation, 
        request: UpdateOrganisationRequestDTO,
        updated_fields: List[str]
    ) -> None:
        """Update system configuration"""
        if request.hostname is not None:
            organisation.hostname = request.hostname
            updated_fields.append("hostname")
        
        if request.logo_path is not None:
            organisation.logo_path = request.logo_path
            updated_fields.append("logo_path")
        
        if updated_fields:
            organisation.updated_by = request.updated_by
    
    def _create_bank_details(self, request: UpdateOrganisationRequestDTO) -> BankDetails:
        """Create bank details value object if provided"""
        if not hasattr(request, 'bank_details') or not request.bank_details:
            return None
        bd = request.bank_details
        try:
            return BankDetails(
                bank_name=bd.bank_name,
                account_number=bd.account_number,
                ifsc_code=bd.ifsc_code,
                branch_name=bd.branch_name,
                branch_address=bd.branch_address,
                account_type=bd.account_type,
                account_holder_name=bd.account_holder_name
            )
        except Exception as e:
            raise OrganisationValidationError(f"Invalid bank details: {e}")
    
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
        from app.application.dto.organisation_dto import BankDetailsResponseDTO
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
            display_name=organisation.get_display_name(),
            bank_details=BankDetailsResponseDTO(**organisation.bank_details.__dict__) if organisation.bank_details else None
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