"""
Get Organization Use Case
Handles the business logic for retrieving organization information
"""

import logging
from typing import Optional

from domain.entities.organization import Organization
from domain.value_objects.organization_id import OrganizationId
from domain.value_objects.organization_details import ContactInformation, Address, TaxInformation
from application.dto.organization_dto import (
    OrganizationResponseDTO, OrganizationNotFoundError
)
from application.interfaces.repositories.organization_repository import OrganizationQueryRepository


logger = logging.getLogger(__name__)


class GetOrganizationUseCase:
    """
    Use case for retrieving organization information.
    
    Follows SOLID principles:
    - SRP: Only handles organization retrieval logic
    - OCP: Can be extended with new retrieval methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories)
    
    Business Rules:
    1. Organization must exist to be retrieved
    2. Return complete organization information
    3. Include computed fields and status information
    """
    
    def __init__(self, query_repository: OrganizationQueryRepository):
        self.query_repository = query_repository
    
    async def execute_by_id(self, organization_id: str) -> OrganizationResponseDTO:
        """
        Execute the get organization by ID use case.
        
        Args:
            organization_id: ID of organization to retrieve
            
        Returns:
            Organization response DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
        """
        logger.info(f"Getting organization by ID: {organization_id}")
        
        org_id = OrganizationId.from_string(organization_id)
        organization = await self.query_repository.get_by_id(org_id)
        
        if not organization:
            raise OrganizationNotFoundError(organization_id)
        
        response = self._convert_to_response_dto(organization)
        logger.info(f"Organization retrieved successfully: {organization_id}")
        return response
    
    async def execute_by_name(self, name: str) -> Optional[OrganizationResponseDTO]:
        """
        Execute the get organization by name use case.
        
        Args:
            name: Name of organization to retrieve
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        logger.info(f"Getting organization by name: {name}")
        
        organization = await self.query_repository.get_by_name(name)
        
        if not organization:
            logger.info(f"Organization not found by name: {name}")
            return None
        
        response = self._convert_to_response_dto(organization)
        logger.info(f"Organization retrieved successfully by name: {name}")
        return response
    
    async def execute_by_hostname(self, hostname: str) -> Optional[OrganizationResponseDTO]:
        """
        Execute the get organization by hostname use case.
        
        Args:
            hostname: Hostname of organization to retrieve
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        logger.info(f"Getting organization by hostname: {hostname}")
        
        organization = await self.query_repository.get_by_hostname(hostname)
        
        if not organization:
            logger.info(f"Organization not found by hostname: {hostname}")
            return None
        
        response = self._convert_to_response_dto(organization)
        logger.info(f"Organization retrieved successfully by hostname: {hostname}")
        return response
    
    async def execute_by_pan_number(self, pan_number: str) -> Optional[OrganizationResponseDTO]:
        """
        Execute the get organization by PAN number use case.
        
        Args:
            pan_number: PAN number of organization to retrieve
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        logger.info(f"Getting organization by PAN number: {pan_number}")
        
        organization = await self.query_repository.get_by_pan_number(pan_number)
        
        if not organization:
            logger.info(f"Organization not found by PAN number: {pan_number}")
            return None
        
        response = self._convert_to_response_dto(organization)
        logger.info(f"Organization retrieved successfully by PAN number: {pan_number}")
        return response
    
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