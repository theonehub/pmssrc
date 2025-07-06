"""
Get Organisation Use Case
Handles the business logic for retrieving organisation information
"""

import logging
from typing import Optional

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import ContactInformation, Address, TaxInformation
from app.application.dto.organisation_dto import (
    OrganisationResponseDTO, OrganisationNotFoundError
)
from app.application.interfaces.repositories.organisation_repository import OrganisationQueryRepository


logger = logging.getLogger(__name__)


class GetOrganisationUseCase:
    """
    Use case for retrieving organisation information.
    
    Follows SOLID principles:
    - SRP: Only handles organisation retrieval logic
    - OCP: Can be extended with new retrieval methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories)
    
    Business Rules:
    1. Organisation must exist to be retrieved
    2. Return complete organisation information
    3. Include computed fields and status information
    """
    
    def __init__(self, query_repository: OrganisationQueryRepository):
        self.query_repository = query_repository
    
    async def execute_by_id(self, organisation_id: str) -> OrganisationResponseDTO:
        """
        Execute the get organisation by ID use case.
        
        Args:
            organisation_id: ID of organisation to retrieve
            
        Returns:
            Organisation response DTO
            
        Raises:
            OrganisationNotFoundError: If organisation not found
        """
        logger.info(f"Getting organisation by ID: {organisation_id}")
        
        org_id = OrganisationId.from_string(organisation_id)
        organisation = await self.query_repository.get_by_id(org_id)
        
        if not organisation:
            raise OrganisationNotFoundError(organisation_id)
        
        response = self._convert_to_response_dto(organisation)
        logger.info(f"Organisation retrieved successfully: {organisation_id}")
        return response
    

    
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