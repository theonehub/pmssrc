"""
Delete User Use Case
Handles the business logic for deleting a user
"""

import logging
from typing import Optional

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.user_dto import (
    UserNotFoundError, UserBusinessRuleError, UserResponseDTO
)
from app.application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository
)
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationQueryRepository, OrganisationCommandRepository
)
from app.application.interfaces.services.user_service import (
    UserNotificationService
)
from app.auth.auth_dependencies import CurrentUser


logger = logging.getLogger(__name__)


class DeleteUserUseCase:
    """
    Use case for deleting a user.
    
    Follows SOLID principles:
    - SRP: Only handles user deletion logic
    - OCP: Can be extended with new deletion rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. User must exist to be deleted
    2. Cannot delete if user has active sessions
    3. Must provide deletion reason
    4. Deletion triggers domain events for cleanup
    5. Soft deletion is preferred over hard deletion
    6. Must decrement organisation employee strength
    """
    
    def __init__(
        self,
        command_repository: UserCommandRepository,
        query_repository: UserQueryRepository,
        organisation_query_repository: OrganisationQueryRepository,
        organisation_command_repository: OrganisationCommandRepository,
        notification_service: UserNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.organisation_query_repository = organisation_query_repository
        self.organisation_command_repository = organisation_command_repository
        self.notification_service = notification_service
    
    async def execute(
        self, 
        employee_id: str,
        deletion_reason: str,
        current_user: CurrentUser,
        deleted_by: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Execute the delete user use case.
        Args:
            employee_id: ID of user to delete
            deletion_reason: Reason for deletion
            current_user: Current authenticated user with organisation context (organisation_id is current_user.hostname)
            deleted_by: User performing the deletion
            soft_delete: Whether to soft delete (mark as deleted) or hard delete
        Returns:
            True if deleted successfully
        Raises:
            UserNotFoundError: If user not found
            UserBusinessRuleError: If deletion is not allowed
        """
        logger.info(f"Deleting user: {employee_id} in organisation: {current_user.hostname}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing user
        user = await self._get_existing_user(employee_id, current_user)
        
        # Step 3: Validate deletion rules
        await self._validate_deletion_rules(user)
        
        # Step 4: Perform user deletion
        deletion_success = await self.command_repository.delete(
            EmployeeId(employee_id), 
            soft_delete, 
            current_user.hostname
        )
        
        if not deletion_success:
            raise UserBusinessRuleError(
                f"Failed to delete user {employee_id}",
                "deletion_failed"
            )
        
        # Step 5: Decrement organisation used employee strength
        await self._decrement_organisation_employee_strength(current_user)
        
        # Step 6: Send notifications (non-blocking)
        try:
            await self.notification_service.send_user_deleted_notification(user, deletion_reason)
        except Exception as e:
            logger.warning(f"Failed to send user deleted notification: {e}")
        
        logger.info(f"User deleted successfully: {employee_id}")
        return True
    
    def _validate_inputs(self, deletion_reason: str) -> None:
        """Validate input parameters"""
        if not deletion_reason or not deletion_reason.strip():
            raise UserBusinessRuleError(
                "Deletion reason is required",
                "deletion_reason_required"
            )
        
        if len(deletion_reason.strip()) < 5:
            raise UserBusinessRuleError(
                "Deletion reason must be at least 5 characters",
                "deletion_reason_too_short"
            )
    
    async def _get_existing_user(self, employee_id: str, current_user: CurrentUser) -> User:
        """Get existing user using current_user for organisation context."""
        user = await self.query_repository.get_by_id(
            EmployeeId(employee_id), 
            current_user.hostname
        )
        
        if not user:
            raise UserNotFoundError(employee_id)
        
        return user
    
    async def _validate_deletion_rules(self, user: User) -> None:
        """Validate business rules for deletion"""
        
        # Rule 1: Cannot delete if user is already deleted
        if user.is_deleted:
            raise UserBusinessRuleError(
                f"User {user.employee_id} is already deleted",
                "already_deleted"
            )
        
        # Rule 2: Cannot delete if user has active sessions (business rule)
        # This would be implemented based on session management system
        # For now, we'll skip this check
        
        # Rule 3: Additional validation can be added here
        # For example, checking user permissions, user status, etc.
        
        logger.info(f"Deletion validation passed for user: {user.employee_id}")
    
    async def _decrement_organisation_employee_strength(self, current_user: CurrentUser) -> None:
        """
        Decrement organisation used employee strength.
        Args:
            hostname: Hostname of the organisation
        """
        try:
            # Get organisation by hostname
            organisation = await self.organisation_query_repository.get_by_hostname(current_user.hostname)
            
            if organisation:
                # Use the dedicated decrement method from command repository
                success = await self.organisation_command_repository.decrement_used_employee_strength(organisation.organisation_id)
                
                if success:
                    logger.info(f"Decremented organisation employee strength for organisation: {organisation.organisation_id}")
                else:
                    logger.warning(f"Could not decrement organisation employee strength for organisation: {organisation.organisation_id} - may be at zero")
            else:
                logger.warning(f"Organisation not found for hostname: {current_user.hostname}")
                
        except Exception as e:
            logger.error(f"Error decrementing organisation employee strength: {e}")
            # Don't fail user deletion if this fails, but log the error
            # This is a non-critical operation 