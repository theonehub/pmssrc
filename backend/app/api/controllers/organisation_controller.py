"""
Organisation Controller Implementation
SOLID-compliant controller for organisation HTTP operations
"""

import logging
from typing import Optional

from app.application.use_cases.organisation.create_organisation_use_case import CreateOrganisationUseCase
from app.application.use_cases.organisation.update_organisation_use_case import UpdateOrganisationUseCase
from app.application.use_cases.organisation.get_organisation_use_case import GetOrganisationUseCase
from app.application.use_cases.organisation.list_organisations_use_case import ListOrganisationsUseCase
from app.application.use_cases.organisation.delete_organisation_use_case import DeleteOrganisationUseCase
from app.application.dto.organisation_dto import (
    CreateOrganisationRequestDTO,
    UpdateOrganisationRequestDTO,
    OrganisationStatusUpdateRequestDTO,
    OrganisationSearchFiltersDTO,
    OrganisationResponseDTO,
    OrganisationListResponseDTO,
    OrganisationStatisticsDTO
)


logger = logging.getLogger(__name__)


class OrganisationController:
    """
    Controller for organisation management operations.
    
    Follows SOLID principles:
    - SRP: Each method handles a single operation
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused on organisation operations
    - DIP: Depends on use case abstractions
    """
    
    def __init__(
        self,
        create_use_case: CreateOrganisationUseCase,
        update_use_case: UpdateOrganisationUseCase,
        get_use_case: GetOrganisationUseCase,
        list_use_case: ListOrganisationsUseCase,
        delete_use_case: DeleteOrganisationUseCase
    ):
        self.create_use_case = create_use_case
        self.update_use_case = update_use_case
        self.get_use_case = get_use_case
        self.list_use_case = list_use_case
        self.delete_use_case = delete_use_case

    async def create_organisation(
        self, 
        request: CreateOrganisationRequestDTO, 
        created_by: str
    ) -> OrganisationResponseDTO:
        """Create a new organisation"""
        logger.info(f"Creating organisation: {request.name} by {created_by}")
        return await self.create_use_case.execute(request=request, created_by=created_by)

    async def list_organisations(
        self, 
        filters: OrganisationSearchFiltersDTO
    ) -> OrganisationListResponseDTO:
        """List organisations with optional filters and pagination"""
        logger.info("Listing organisations with filters")
        return await self.list_use_case.execute(filters)

    async def get_organisation_by_id(self, organisation_id: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by ID"""
        logger.info(f"Getting organisation: {organisation_id}")
        return await self.get_use_case.execute_by_id(organisation_id)

    async def get_organisation_by_name(self, name: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by name"""
        logger.info(f"Getting organisation by name: {name}")
        return await self.get_use_case.execute_by_name(name)

    async def get_organisation_by_hostname(self, hostname: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by hostname"""
        logger.info(f"Getting organisation by hostname: {hostname}")
        return await self.get_use_case.execute_by_hostname(hostname)

    async def get_organisation_by_pan_number(self, pan_number: str) -> Optional[OrganisationResponseDTO]:
        """Get organisation by PAN number"""
        logger.info(f"Getting organisation by PAN: {pan_number}")
        return await self.get_use_case.execute_by_pan_number(pan_number)

    async def update_organisation(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO, 
        updated_by: str
    ) -> OrganisationResponseDTO:
        """Update an existing organisation"""
        logger.info(f"Updating organisation: {organisation_id} by {updated_by}")
        return await self.update_use_case.execute(
            organisation_id=organisation_id,
            request=request,
            updated_by=updated_by
        )

    async def update_organisation_status(
        self, 
        organisation_id: str, 
        request: OrganisationStatusUpdateRequestDTO, 
        updated_by: str
    ) -> OrganisationResponseDTO:
        """Update organisation status"""
        logger.info(f"Updating organisation status: {organisation_id} to {request.status} by {updated_by}")
        return await self.update_use_case.execute_status_update(
            organisation_id=organisation_id,
            request=request,
            updated_by=updated_by
        )

    async def delete_organisation(
        self, 
        organisation_id: str, 
        force: bool, 
        deleted_by: str
    ) -> bool:
        """Delete an organisation"""
        logger.info(f"Deleting organisation: {organisation_id} by {deleted_by} (force: {force})")
        return await self.delete_use_case.execute(
            organisation_id=organisation_id,
            force=force,
            deleted_by=deleted_by
        )

    async def increment_employee_usage(
        self, 
        organisation_id: str, 
        updated_by: str
    ) -> OrganisationResponseDTO:
        """Increment employee usage count"""
        logger.info(f"Incrementing employee usage for organisation: {organisation_id}")
        return await self.update_use_case.execute_increment_employee_usage(
            organisation_id=organisation_id,
            updated_by=updated_by
        )

    async def decrement_employee_usage(
        self, 
        organisation_id: str, 
        updated_by: str
    ) -> OrganisationResponseDTO:
        """Decrement employee usage count"""
        logger.info(f"Decrementing employee usage for organisation: {organisation_id}")
        return await self.update_use_case.execute_decrement_employee_usage(
            organisation_id=organisation_id,
            updated_by=updated_by
        )

    async def get_organisation_statistics(
        self, 
        start_date=None, 
        end_date=None
    ) -> OrganisationStatisticsDTO:
        """Get organisation statistics"""
        logger.info(f"Getting organisation statistics (start: {start_date}, end: {end_date})")
        return await self.list_use_case.execute_statistics(
            start_date=start_date,
            end_date=end_date
        )

    async def check_name_exists(self, name: str) -> bool:
        """Check if organisation name exists"""
        logger.info(f"Checking name availability: {name}")
        return await self.get_use_case.execute_exists_by_name(name)

    async def check_hostname_exists(self, hostname: str) -> bool:
        """Check if hostname exists"""
        logger.info(f"Checking hostname availability: {hostname}")
        return await self.get_use_case.execute_exists_by_hostname(hostname)

    async def check_pan_exists(self, pan_number: str) -> bool:
        """Check if PAN number exists"""
        logger.info(f"Checking PAN availability: {pan_number}")
        return await self.get_use_case.execute_exists_by_pan_number(pan_number) 