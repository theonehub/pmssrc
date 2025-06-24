"""
Company Leave Controller Implementation
SOLID-compliant controller for company leave HTTP operations
"""

import logging
from typing import Optional, TYPE_CHECKING

from app.application.interfaces.services.company_leaves_service import CompanyLeaveService
from app.application.dto.company_leave_dto import (
    CreateCompanyLeaveRequestDTO,
    UpdateCompanyLeaveRequestDTO,
    CompanyLeaveSearchFiltersDTO,
    CompanyLeaveResponseDTO,
    CompanyLeaveListResponseDTO
)

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class CompanyLeaveController:
    """
    Controller for company leave management operations.
    
    Follows SOLID principles:
    - SRP: Each method handles a single operation
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused on company leave operations
    - DIP: Depends on service abstractions
    """
    
    def __init__(self, company_leave_service: CompanyLeaveService):
        """
        Initialize controller with company leave service.
        
        Args:
            company_leave_service: Service for company leave operations
        """
        self.service = company_leave_service
        self.logger = logging.getLogger(__name__)

    async def create_company_leave(
        self, 
        request: CreateCompanyLeaveRequestDTO, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """Create a new company leave"""
        self.logger.info(f"Creating company leave with name: {request.leave_name} by {current_user.hostname}")
        return await self.service.create_company_leave(request, current_user)

    async def list_company_leaves(
        self, 
        filters: Optional[CompanyLeaveSearchFiltersDTO] = None,
        current_user: "CurrentUser" = None
    ) -> CompanyLeaveListResponseDTO:
        """List company leaves with optional filters and pagination"""
        self.logger.info("Listing company leaves with filters")
        return await self.service.list_company_leaves(filters, current_user)

    async def get_company_leave_by_id(
        self, 
        company_leave_id: str,
        current_user: "CurrentUser"
    ) -> Optional[CompanyLeaveResponseDTO]:
        """Get company leave by ID"""
        self.logger.info(f"Getting company leave: {company_leave_id}")
        return await self.service.get_company_leave_by_id(company_leave_id, current_user)

    async def update_company_leave(
        self, 
        company_leave_id: str, 
        request: UpdateCompanyLeaveRequestDTO, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """Update an existing company leave"""
        self.logger.info(f"Updating company leave: {company_leave_id} by {current_user.hostname}")
        return await self.service.update_company_leave(company_leave_id, request, current_user)

    async def delete_company_leave(
        self, 
        company_leave_id: str, 
        deletion_reason: str,
        current_user: "CurrentUser",
        deleted_by: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """Delete a company leave"""
        self.logger.info(f"Deleting company leave: {company_leave_id} by {current_user.hostname} (soft: {soft_delete})")
        return await self.service.delete_company_leave(
            company_leave_id, 
            deletion_reason, 
            current_user, 
            deleted_by, 
            soft_delete
        ) 