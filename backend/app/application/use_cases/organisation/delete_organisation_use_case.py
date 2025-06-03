"""
Delete Organisation Use Case
Handles the business logic for deleting an organisation
"""

import logging
from typing import Optional

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.application.dto.organisation_dto import (
    OrganisationNotFoundError, OrganisationBusinessRuleError
)
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationCommandRepository, OrganisationQueryRepository
)
from app.application.interfaces.services.organisation_service import OrganisationNotificationService


logger = logging.getLogger(__name__)


class DeleteOrganisationUseCase:
    """
    Use case for deleting an organisation.
    
    Follows SOLID principles:
    - SRP: Only handles organisation deletion logic
    - OCP: Can be extended with new deletion rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Organisation must exist to be deleted
    2. Cannot delete organisation with active employees
    3. Must provide deletion reason
    4. Deletion triggers domain events for cleanup
    5. Soft deletion is preferred over hard deletion
    """
    
    def __init__(
        self,
        command_repository: OrganisationCommandRepository,
        query_repository: OrganisationQueryRepository,
        notification_service: OrganisationNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.notification_service = notification_service
    
    async def execute(
        self, 
        organisation_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Execute the delete organisation use case.
        
        Args:
            organisation_id: ID of organisation to delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            OrganisationNotFoundError: If organisation not found
            OrganisationBusinessRuleError: If deletion is not allowed
        """
        logger.info(f"Deleting organisation: {organisation_id}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing organisation
        organisation = await self._get_existing_organisation(organisation_id)
        
        # Step 3: Validate deletion rules
        await self._validate_deletion_rules(organisation)
        
        # Step 4: Perform soft deletion (mark as deleted)
        organisation.delete(deletion_reason, deleted_by)
        
        # Step 5: Save organisation with deletion event
        await self.command_repository.save(organisation)
        
        # Step 6: Perform hard deletion from repository
        deletion_success = await self.command_repository.delete(organisation.organisation_id)
        
        # Step 7: Send notifications (non-blocking)
        if deletion_success:
            try:
                # Note: The organisation.delete() method already publishes OrganisationDeleted event
                # Additional notifications can be sent here if needed
                logger.info(f"Organisation deletion notifications triggered for: {organisation_id}")
            except Exception as e:
                logger.warning(f"Failed to send organisation deletion notifications: {e}")
        
        logger.info(f"Organisation deleted successfully: {organisation_id}")
        return deletion_success
    
    async def execute_soft_delete(
        self, 
        organisation_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Execute soft deletion (mark as deleted without removing from database).
        
        Args:
            organisation_id: ID of organisation to soft delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if soft deleted successfully
            
        Raises:
            OrganisationNotFoundError: If organisation not found
            OrganisationBusinessRuleError: If deletion is not allowed
        """
        logger.info(f"Soft deleting organisation: {organisation_id}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing organisation
        organisation = await self._get_existing_organisation(organisation_id)
        
        # Step 3: Validate deletion rules
        await self._validate_deletion_rules(organisation)
        
        # Step 4: Perform soft deletion
        organisation.delete(deletion_reason, deleted_by)
        
        # Step 5: Deactivate organisation
        if organisation.is_active():
            organisation.deactivate(f"Deleted: {deletion_reason}", deleted_by)
        
        # Step 6: Save organisation
        await self.command_repository.save(organisation)
        
        logger.info(f"Organisation soft deleted successfully: {organisation_id}")
        return True
    
    async def execute_force_delete(
        self, 
        organisation_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Execute force deletion (bypass some business rules).
        
        Args:
            organisation_id: ID of organisation to force delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if force deleted successfully
            
        Raises:
            OrganisationNotFoundError: If organisation not found
        """
        logger.warning(f"Force deleting organisation: {organisation_id}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing organisation
        organisation = await self._get_existing_organisation(organisation_id)
        
        # Step 3: Perform deletion (bypass some rules)
        organisation.delete(f"FORCE DELETE: {deletion_reason}", deleted_by)
        
        # Step 4: Save organisation with deletion event
        await self.command_repository.save(organisation)
        
        # Step 5: Perform hard deletion
        deletion_success = await self.command_repository.delete(organisation.organisation_id)
        
        logger.warning(f"Organisation force deleted: {organisation_id}")
        return deletion_success
    
    def _validate_inputs(self, deletion_reason: str) -> None:
        """Validate input parameters"""
        if not deletion_reason or not deletion_reason.strip():
            raise OrganisationBusinessRuleError(
                "Deletion reason is required",
                "deletion_reason_required"
            )
        
        if len(deletion_reason.strip()) < 10:
            raise OrganisationBusinessRuleError(
                "Deletion reason must be at least 10 characters",
                "deletion_reason_too_short"
            )
    
    async def _get_existing_organisation(self, organisation_id: str) -> Organisation:
        """Get existing organisation"""
        org_id = OrganisationId.from_string(organisation_id)
        organisation = await self.query_repository.get_by_id(org_id)
        
        if not organisation:
            raise OrganisationNotFoundError(organisation_id)
        
        return organisation
    
    async def _validate_deletion_rules(self, organisation: Organisation) -> None:
        """Validate business rules for deletion"""
        
        # Rule 1: Cannot delete organisation with active employees
        if organisation.used_employee_strength > 0:
            raise OrganisationBusinessRuleError(
                f"Cannot delete organisation with {organisation.used_employee_strength} active employees. "
                f"Please remove all employees before deletion.",
                "has_active_employees"
            )
        
        # Rule 2: Cannot delete if organisation has critical dependencies
        # This would be implemented based on specific business requirements
        # For example, checking for active contracts, pending transactions, etc.
        
        # Rule 3: Additional validation can be added here
        # For example, checking user permissions, organisation status, etc.
        
        logger.info(f"Deletion validation passed for organisation: {organisation.organisation_id}")
    
    async def check_deletion_eligibility(self, organisation_id: str) -> dict:
        """
        Check if organisation is eligible for deletion.
        
        Args:
            organisation_id: ID of organisation to check
            
        Returns:
            Dictionary with eligibility status and reasons
        """
        try:
            organisation = await self._get_existing_organisation(organisation_id)
            
            eligibility = {
                "eligible": True,
                "reasons": [],
                "warnings": [],
                "organisation_name": organisation.name,
                "employee_count": organisation.used_employee_strength
            }
            
            # Check for blocking conditions
            if organisation.used_employee_strength > 0:
                eligibility["eligible"] = False
                eligibility["reasons"].append(
                    f"Organisation has {organisation.used_employee_strength} active employees"
                )
            
            # Check for warning conditions
            if organisation.is_active():
                eligibility["warnings"].append("Organisation is currently active")
            
            if organisation.is_gst_registered():
                eligibility["warnings"].append("Organisation is GST registered")
            
            return eligibility
            
        except OrganisationNotFoundError:
            return {
                "eligible": False,
                "reasons": ["Organisation not found"],
                "warnings": [],
                "organisation_name": None,
                "employee_count": 0
            } 