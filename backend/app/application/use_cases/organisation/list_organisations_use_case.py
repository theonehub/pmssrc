"""
List Organisations Use Case
Handles the business logic for listing and searching organisations
"""

import logging
import math
from typing import List

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_details import OrganisationType
from app.application.dto.organisation_dto import (
    OrganisationSearchFiltersDTO, OrganisationListResponseDTO,
    OrganisationSummaryDTO, OrganisationValidationError
)
from app.application.interfaces.repositories.organisation_repository import OrganisationQueryRepository


logger = logging.getLogger(__name__)


class ListOrganisationsUseCase:
    """
    Use case for listing and searching organisations.
    
    Follows SOLID principles:
    - SRP: Only handles organisation listing logic
    - OCP: Can be extended with new search criteria
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories)
    
    Business Rules:
    1. Support pagination for large datasets
    2. Support filtering by various criteria
    3. Support sorting by different fields
    4. Return summary information for list views
    5. Include metadata for pagination
    """
    
    def __init__(self, query_repository: OrganisationQueryRepository):
        self.query_repository = query_repository
    
    async def execute(self, filters: OrganisationSearchFiltersDTO) -> OrganisationListResponseDTO:
        """
        Execute the list organisations use case.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            Paginated list of organisation summaries
            
        Raises:
            OrganisationValidationError: If filters are invalid
        """
        logger.info(f"Listing organisations with filters: {filters}")
        
        # Step 1: Validate filters
        await self._validate_filters(filters)
        
        # Step 2: Get organisations from repository
        organisations = await self.query_repository.search(filters)
        
        # Step 3: Get total count for pagination
        total_count = await self._get_total_count(filters)
        
        # Step 4: Convert to summary DTOs
        organisation_summaries = [
            self._convert_to_summary_dto(org) for org in organisations
        ]
        
        # Step 5: Calculate pagination metadata
        total_pages = math.ceil(total_count / filters.page_size) if total_count > 0 else 0
        has_next = filters.page < total_pages
        has_previous = filters.page > 1
        
        # Step 6: Create response DTO
        response = OrganisationListResponseDTO(
            organisations=organisation_summaries,
            total_count=total_count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        logger.info(f"Listed {len(organisation_summaries)} organisations (total: {total_count})")
        return response
    
    async def execute_simple(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> OrganisationListResponseDTO:
        """
        Execute simple organisation listing without complex filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive organisations
            
        Returns:
            Paginated list of organisation summaries
        """
        logger.info(f"Simple listing organisations: skip={skip}, limit={limit}")
        
        # Step 1: Get organisations from repository
        organisations = await self.query_repository.get_all(
            skip=skip, 
            limit=limit, 
            include_inactive=include_inactive
        )
        
        # Step 2: Get total count
        total_count = await self.query_repository.count_total()
        
        # Step 3: Convert to summary DTOs
        organisation_summaries = [
            self._convert_to_summary_dto(org) for org in organisations
        ]
        
        # Step 4: Calculate pagination metadata
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total_count / limit) if total_count > 0 and limit > 0 else 0
        has_next = skip + limit < total_count
        has_previous = skip > 0
        
        # Step 5: Create response DTO
        response = OrganisationListResponseDTO(
            organisations=organisation_summaries,
            total_count=total_count,
            page=page,
            page_size=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        logger.info(f"Simple listed {len(organisation_summaries)} organisations (total: {total_count})")
        return response
    
    async def execute_by_type(self, organisation_type: str) -> List[OrganisationSummaryDTO]:
        """
        Execute organisation listing by type.
        
        Args:
            organisation_type: Organisation type to filter by
            
        Returns:
            List of organisation summaries with specified type
        """
        logger.info(f"Listing organisations by type: {organisation_type}")
        
        try:
            org_type = OrganisationType(organisation_type)
        except ValueError:
            raise OrganisationValidationError(f"Invalid organisation type: {organisation_type}")
        
        organisations = await self.query_repository.get_by_type(org_type)
        
        organisation_summaries = [
            self._convert_to_summary_dto(org) for org in organisations
        ]
        
        logger.info(f"Listed {len(organisation_summaries)} organisations with type: {organisation_type}")
        return organisation_summaries
    
    async def execute_by_location(
        self, 
        city: str = None, 
        state: str = None, 
        country: str = None
    ) -> List[OrganisationSummaryDTO]:
        """
        Execute organisation listing by location.
        
        Args:
            city: City to filter by
            state: State to filter by
            country: Country to filter by
            
        Returns:
            List of organisation summaries in specified location
        """
        logger.info(f"Listing organisations by location: city={city}, state={state}, country={country}")
        
        organisations = await self.query_repository.get_by_location(
            city=city, 
            state=state, 
            country=country
        )
        
        organisation_summaries = [
            self._convert_to_summary_dto(org) for org in organisations
        ]
        
        logger.info(f"Listed {len(organisation_summaries)} organisations by location")
        return organisation_summaries
    
    async def _validate_filters(self, filters: OrganisationSearchFiltersDTO) -> None:
        """Validate search filters"""
        validation_errors = filters.validate()
        
        if validation_errors:
            raise OrganisationValidationError(
                "Invalid search filters",
                validation_errors
            )
    
    async def _get_total_count(self, filters: OrganisationSearchFiltersDTO) -> int:
        """Get total count of organisations matching filters"""
        # For now, return total count
        # In a real implementation, this would apply the same filters
        # but only count records instead of retrieving them
        return await self.query_repository.count_total()
    
    def _convert_to_summary_dto(self, organisation: Organisation) -> OrganisationSummaryDTO:
        """Convert organisation entity to summary DTO"""
        return OrganisationSummaryDTO(
            organisation_id=str(organisation.organisation_id),
            name=organisation.name,
            organisation_type=organisation.organisation_type.value,
            status=organisation.status.value,
            city=organisation.address.city if organisation.address else None,
            state=organisation.address.state if organisation.address else None,
            employee_strength=organisation.employee_strength,
            used_employee_strength=organisation.used_employee_strength,
            utilization_percentage=organisation.get_employee_utilization_percentage(),
            created_at=organisation.created_at.isoformat(),
            is_active=organisation.is_active()
        ) 