"""
Delete Company Leave Use Case
Business workflow for deleting company leave policies
"""

import logging
from typing import Optional

from app.application.dto.company_leave_dto import (
    CompanyLeaveNotFoundError,
    CompanyLeaveBusinessRuleError
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveCommandRepository,
    CompanyLeaveQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.domain.entities.company_leave import CompanyLeave


logger = logging.getLogger(__name__)


class DeleteCompanyLeaveUseCase:
    """
    Use case for deleting company leave policies.
    
    Follows SOLID principles:
    - SRP: Only handles company leave deletion workflow
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        command_repository: CompanyLeaveCommandRepository,
        query_repository: CompanyLeaveQueryRepository,
        event_publisher: EventPublisher
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._event_publisher = event_publisher
    
    async def execute(
        self, 
        company_leave_id: str, 
        force: bool, 
        deleted_by: str
    ) -> bool:
        """
        Execute company leave deletion workflow.
        
        Business Rules:
        1. Company leave must exist
        2. Check if deletion is allowed (unless forced)
        3. Events must be published for downstream processing
        
        Args:
            company_leave_id: ID of company leave to delete
            force: Whether to force deletion even if business rules prevent it
            deleted_by: User performing the deletion
            
        Returns:
            True if deletion successful
            
        Raises:
            CompanyLeaveNotFoundError: If company leave doesn't exist
            CompanyLeaveBusinessRuleError: If deletion violates business rules
            Exception: If deletion fails
        """
        
        try:
            logger.info(f"Deleting company leave: {company_leave_id} by {deleted_by} (force: {force})")
            
            # Step 1: Get existing company leave
            company_leave = await self._query_repository.get_by_id(company_leave_id)
            if not company_leave:
                raise CompanyLeaveNotFoundError(f"Company leave {company_leave_id} not found")
            
            # Step 2: Check business rules (unless forced)
            if not force:
                await self._validate_deletion_rules(company_leave)
            
            # Step 3: Perform soft delete (deactivate)
            company_leave.is_active = False
            company_leave.updated_by = deleted_by
            
            success = await self._command_repository.update(company_leave)
            if not success:
                raise Exception("Failed to delete company leave in database")
            
            # Step 4: Publish domain events
            await self._publish_domain_events(company_leave, deleted_by)
            
            logger.info(f"Successfully deleted company leave: {company_leave_id}")
            return True
            
        except CompanyLeaveNotFoundError:
            logger.warning(f"Company leave not found for deletion: {company_leave_id}")
            raise
        except CompanyLeaveBusinessRuleError:
            logger.warning(f"Business rule violation in company leave deletion: {company_leave_id}")
            raise
        except Exception as e:
            logger.error(f"Failed to delete company leave: {str(e)}")
            raise Exception(f"Company leave deletion failed: {str(e)}")
    
    async def _validate_deletion_rules(self, company_leave: CompanyLeave):
        """Validate business rules for company leave deletion"""
        
        # Example: Check if company leave is being used by employees
        # This would depend on your business logic
        
        # For now, we'll allow deletion if it's not active
        if not company_leave.is_active:
            raise CompanyLeaveBusinessRuleError(
                f"Company leave {company_leave.company_leave_id} is already inactive"
            )
    
    async def _publish_domain_events(self, company_leave: CompanyLeave, deleted_by: str):
        """Publish domain events for company leave deletion"""
        try:
            event_data = {
                'company_leave_id': company_leave.company_leave_id,
                'accrual_type': company_leave.accrual_type,
                'deleted_by': deleted_by,
                'deleted_at': company_leave.updated_at.isoformat()
            }
            
            await self._event_publisher.publish('company_leave_deleted', event_data)
            logger.info(f"Published company_leave_deleted event for {company_leave.company_leave_id}")
            
        except Exception as e:
            logger.warning(f"Failed to publish events for company leave {company_leave.company_leave_id}: {e}")


class DeleteCompanyLeaveUseCaseError(Exception):
    """Base exception for delete company leave use case"""
    pass 