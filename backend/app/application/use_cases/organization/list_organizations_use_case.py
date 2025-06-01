"""
List Organizations Use Case
Handles the business logic for listing and searching organizations
"""

import logging
import math
from typing import List

from app.domain.entities.organization import Organization
from app.domain.value_objects.organization_details import OrganizationType, OrganizationStatus
from app.application.dto.organization_dto import (
    OrganizationSearchFiltersDTO, OrganizationListResponseDTO,
    OrganizationSummaryDTO, OrganizationValidationError
)
from app.application.interfaces.repositories.organization_repository import OrganizationQueryRepository


logger = logging.getLogger(__name__)


class ListOrganizationsUseCase:
    """
    Use case for listing and searching organizations.
    
    Follows SOLID principles:
    - SRP: Only handles organization listing logic
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
    
    def __init__(self, query_repository: OrganizationQueryRepository):
        self.query_repository = query_repository
    
    async def execute(self, filters: OrganizationSearchFiltersDTO) -> OrganizationListResponseDTO:
        """
        Execute the list organizations use case.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            Paginated list of organization summaries
            
        Raises:
            OrganizationValidationError: If filters are invalid
        """
        logger.info(f"Listing organizations with filters: {filters}")
        
        # Step 1: Validate filters
        await self._validate_filters(filters)
        
        # Step 2: Get organizations from repository
        organizations = await self.query_repository.search(filters)
        
        # Step 3: Get total count for pagination
        total_count = await self._get_total_count(filters)
        
        # Step 4: Convert to summary DTOs
        organization_summaries = [
            self._convert_to_summary_dto(org) for org in organizations
        ]
        
        # Step 5: Calculate pagination metadata
        total_pages = math.ceil(total_count / filters.page_size) if total_count > 0 else 0
        has_next = filters.page < total_pages
        has_previous = filters.page > 1
        
        # Step 6: Create response DTO
        response = OrganizationListResponseDTO(
            organizations=organization_summaries,
            total_count=total_count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        logger.info(f"Listed {len(organization_summaries)} organizations (total: {total_count})")
        return response
    
    async def execute_simple(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> OrganizationListResponseDTO:
        """
        Execute simple organization listing without complex filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive organizations
            
        Returns:
            Paginated list of organization summaries
        """
        logger.info(f"Simple listing organizations: skip={skip}, limit={limit}")
        
        # Step 1: Get organizations from repository
        organizations = await self.query_repository.get_all(
            skip=skip, 
            limit=limit, 
            include_inactive=include_inactive
        )
        
        # Step 2: Get total count
        total_count = await self.query_repository.count_total()
        if not include_inactive:
            active_count = await self.query_repository.count_by_status(OrganizationStatus.ACTIVE)
            total_count = active_count
        
        # Step 3: Convert to summary DTOs
        organization_summaries = [
            self._convert_to_summary_dto(org) for org in organizations
        ]
        
        # Step 4: Calculate pagination metadata
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total_count / limit) if total_count > 0 and limit > 0 else 0
        has_next = skip + limit < total_count
        has_previous = skip > 0
        
        # Step 5: Create response DTO
        response = OrganizationListResponseDTO(
            organizations=organization_summaries,
            total_count=total_count,
            page=page,
            page_size=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        logger.info(f"Simple listed {len(organization_summaries)} organizations (total: {total_count})")
        return response
    
    async def execute_by_status(self, status: str) -> List[OrganizationSummaryDTO]:
        """
        Execute organization listing by status.
        
        Args:
            status: Organization status to filter by
            
        Returns:
            List of organization summaries with specified status
        """
        logger.info(f"Listing organizations by status: {status}")
        
        try:
            organization_status = OrganizationStatus(status)
        except ValueError:
            raise OrganizationValidationError(f"Invalid organization status: {status}")
        
        organizations = await self.query_repository.get_by_status(organization_status)
        
        organization_summaries = [
            self._convert_to_summary_dto(org) for org in organizations
        ]
        
        logger.info(f"Listed {len(organization_summaries)} organizations with status: {status}")
        return organization_summaries
    
    async def execute_by_type(self, organization_type: str) -> List[OrganizationSummaryDTO]:
        """
        Execute organization listing by type.
        
        Args:
            organization_type: Organization type to filter by
            
        Returns:
            List of organization summaries with specified type
        """
        logger.info(f"Listing organizations by type: {organization_type}")
        
        try:
            org_type = OrganizationType(organization_type)
        except ValueError:
            raise OrganizationValidationError(f"Invalid organization type: {organization_type}")
        
        organizations = await self.query_repository.get_by_type(org_type)
        
        organization_summaries = [
            self._convert_to_summary_dto(org) for org in organizations
        ]
        
        logger.info(f"Listed {len(organization_summaries)} organizations with type: {organization_type}")
        return organization_summaries
    
    async def execute_by_location(
        self, 
        city: str = None, 
        state: str = None, 
        country: str = None
    ) -> List[OrganizationSummaryDTO]:
        """
        Execute organization listing by location.
        
        Args:
            city: City to filter by
            state: State to filter by
            country: Country to filter by
            
        Returns:
            List of organization summaries in specified location
        """
        logger.info(f"Listing organizations by location: city={city}, state={state}, country={country}")
        
        organizations = await self.query_repository.get_by_location(
            city=city, 
            state=state, 
            country=country
        )
        
        organization_summaries = [
            self._convert_to_summary_dto(org) for org in organizations
        ]
        
        logger.info(f"Listed {len(organization_summaries)} organizations by location")
        return organization_summaries
    
    async def _validate_filters(self, filters: OrganizationSearchFiltersDTO) -> None:
        """Validate search filters"""
        validation_errors = filters.validate()
        
        if validation_errors:
            raise OrganizationValidationError(
                "Invalid search filters",
                validation_errors
            )
    
    async def _get_total_count(self, filters: OrganizationSearchFiltersDTO) -> int:
        """Get total count of organizations matching filters"""
        # For now, return total count
        # In a real implementation, this would apply the same filters
        # but only count records instead of retrieving them
        return await self.query_repository.count_total()
    
    def _convert_to_summary_dto(self, organization: Organization) -> OrganizationSummaryDTO:
        """Convert organization entity to summary DTO"""
        return OrganizationSummaryDTO(
            organization_id=str(organization.organization_id),
            name=organization.name,
            organization_type=organization.organization_type.value,
            status=organization.status.value,
            city=organization.address.city if organization.address else None,
            state=organization.address.state if organization.address else None,
            employee_strength=organization.employee_strength,
            used_employee_strength=organization.used_employee_strength,
            utilization_percentage=organization.get_employee_utilization_percentage(),
            created_at=organization.created_at.isoformat(),
            is_active=organization.is_active()
        ) 