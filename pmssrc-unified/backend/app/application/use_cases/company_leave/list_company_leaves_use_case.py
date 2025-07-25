"""
List Company Leaves Use Case
Business workflow for listing company leave policies with filtering and pagination
"""

import logging
from typing import List
import math

from app.application.dto.company_leave_dto import (
    CompanyLeaveSearchFiltersDTO,
    CompanyLeaveResponseDTO,
    CompanyLeaveListResponseDTO
)
from app.application.interfaces.repositories.company_leave_repository import CompanyLeaveQueryRepository
from app.domain.entities.company_leave import CompanyLeave


logger = logging.getLogger(__name__)


class ListCompanyLeavesUseCase:
    """
    Use case for listing company leave policies.
    
    Follows SOLID principles:
    - SRP: Only handles company leave listing workflow
    - OCP: Can be extended with new filtering methods
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(self, query_repository: CompanyLeaveQueryRepository):
        self._query_repository = query_repository
    
    async def execute(self, filters: CompanyLeaveSearchFiltersDTO) -> CompanyLeaveListResponseDTO:
        """
        List company leaves with optional filters and pagination.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            CompanyLeaveListResponseDTO with paginated results
            
        Raises:
            Exception: If listing fails
        """
        
        try:
            logger.info(f"Listing company leaves with filters: {filters.to_dict()}")
            
            # Get total count for pagination
            total_count = await self._query_repository.count_with_filters(filters)
            
            # Calculate pagination
            total_pages = math.ceil(total_count / filters.page_size) if total_count > 0 else 0
            
            # Get paginated results
            company_leaves = await self._query_repository.list_with_filters(filters)
            
            # Convert to DTOs
            leave_dtos = [
                CompanyLeaveResponseDTO.from_entity(leave) 
                for leave in company_leaves
            ]
            
            response = CompanyLeaveListResponseDTO(
                items=leave_dtos,
                total=total_count,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages
            )
            
            logger.info(f"Successfully listed {len(leave_dtos)} company leaves (total: {total_count})")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list company leaves: {str(e)}")
            raise Exception(f"Company leave listing failed: {str(e)}")


class ListCompanyLeavesUseCaseError(Exception):
    """Base exception for list company leaves use case"""
    pass 