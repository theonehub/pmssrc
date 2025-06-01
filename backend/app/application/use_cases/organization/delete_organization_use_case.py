"""
Delete Organization Use Case
Handles the business logic for deleting an organization
"""

import logging
from typing import Optional

from app.domain.entities.organization import Organization
from app.domain.value_objects.organization_id import OrganizationId
from app.application.dto.organization_dto import (
    OrganizationNotFoundError, OrganizationBusinessRuleError
)
from app.application.interfaces.repositories.organization_repository import (
    OrganizationCommandRepository, OrganizationQueryRepository
)
from app.application.interfaces.services.organization_service import OrganizationNotificationService


logger = logging.getLogger(__name__)


class DeleteOrganizationUseCase:
    """
    Use case for deleting an organization.
    
    Follows SOLID principles:
    - SRP: Only handles organization deletion logic
    - OCP: Can be extended with new deletion rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Organization must exist to be deleted
    2. Cannot delete organization with active employees
    3. Must provide deletion reason
    4. Deletion triggers domain events for cleanup
    5. Soft deletion is preferred over hard deletion
    """
    
    def __init__(
        self,
        command_repository: OrganizationCommandRepository,
        query_repository: OrganizationQueryRepository,
        notification_service: OrganizationNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.notification_service = notification_service
    
    async def execute(
        self, 
        organization_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Execute the delete organization use case.
        
        Args:
            organization_id: ID of organization to delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationBusinessRuleError: If deletion is not allowed
        """
        logger.info(f"Deleting organization: {organization_id}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing organization
        organization = await self._get_existing_organization(organization_id)
        
        # Step 3: Validate deletion rules
        await self._validate_deletion_rules(organization)
        
        # Step 4: Perform soft deletion (mark as deleted)
        organization.delete(deletion_reason, deleted_by)
        
        # Step 5: Save organization with deletion event
        await self.command_repository.save(organization)
        
        # Step 6: Perform hard deletion from repository
        deletion_success = await self.command_repository.delete(organization.organization_id)
        
        # Step 7: Send notifications (non-blocking)
        if deletion_success:
            try:
                # Note: The organization.delete() method already publishes OrganizationDeleted event
                # Additional notifications can be sent here if needed
                logger.info(f"Organization deletion notifications triggered for: {organization_id}")
            except Exception as e:
                logger.warning(f"Failed to send organization deletion notifications: {e}")
        
        logger.info(f"Organization deleted successfully: {organization_id}")
        return deletion_success
    
    async def execute_soft_delete(
        self, 
        organization_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Execute soft deletion (mark as deleted without removing from database).
        
        Args:
            organization_id: ID of organization to soft delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if soft deleted successfully
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationBusinessRuleError: If deletion is not allowed
        """
        logger.info(f"Soft deleting organization: {organization_id}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing organization
        organization = await self._get_existing_organization(organization_id)
        
        # Step 3: Validate deletion rules
        await self._validate_deletion_rules(organization)
        
        # Step 4: Perform soft deletion
        organization.delete(deletion_reason, deleted_by)
        
        # Step 5: Deactivate organization
        if organization.is_active():
            organization.deactivate(f"Deleted: {deletion_reason}", deleted_by)
        
        # Step 6: Save organization
        await self.command_repository.save(organization)
        
        logger.info(f"Organization soft deleted successfully: {organization_id}")
        return True
    
    async def execute_force_delete(
        self, 
        organization_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Execute force deletion (bypass some business rules).
        
        Args:
            organization_id: ID of organization to force delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if force deleted successfully
            
        Raises:
            OrganizationNotFoundError: If organization not found
        """
        logger.warning(f"Force deleting organization: {organization_id}")
        
        # Step 1: Validate inputs
        self._validate_inputs(deletion_reason)
        
        # Step 2: Get existing organization
        organization = await self._get_existing_organization(organization_id)
        
        # Step 3: Perform deletion (bypass some rules)
        organization.delete(f"FORCE DELETE: {deletion_reason}", deleted_by)
        
        # Step 4: Save organization with deletion event
        await self.command_repository.save(organization)
        
        # Step 5: Perform hard deletion
        deletion_success = await self.command_repository.delete(organization.organization_id)
        
        logger.warning(f"Organization force deleted: {organization_id}")
        return deletion_success
    
    def _validate_inputs(self, deletion_reason: str) -> None:
        """Validate input parameters"""
        if not deletion_reason or not deletion_reason.strip():
            raise OrganizationBusinessRuleError(
                "Deletion reason is required",
                "deletion_reason_required"
            )
        
        if len(deletion_reason.strip()) < 10:
            raise OrganizationBusinessRuleError(
                "Deletion reason must be at least 10 characters",
                "deletion_reason_too_short"
            )
    
    async def _get_existing_organization(self, organization_id: str) -> Organization:
        """Get existing organization"""
        org_id = OrganizationId.from_string(organization_id)
        organization = await self.query_repository.get_by_id(org_id)
        
        if not organization:
            raise OrganizationNotFoundError(organization_id)
        
        return organization
    
    async def _validate_deletion_rules(self, organization: Organization) -> None:
        """Validate business rules for deletion"""
        
        # Rule 1: Cannot delete organization with active employees
        if organization.used_employee_strength > 0:
            raise OrganizationBusinessRuleError(
                f"Cannot delete organization with {organization.used_employee_strength} active employees. "
                f"Please remove all employees before deletion.",
                "has_active_employees"
            )
        
        # Rule 2: Cannot delete if organization has critical dependencies
        # This would be implemented based on specific business requirements
        # For example, checking for active contracts, pending transactions, etc.
        
        # Rule 3: Additional validation can be added here
        # For example, checking user permissions, organization status, etc.
        
        logger.info(f"Deletion validation passed for organization: {organization.organization_id}")
    
    async def check_deletion_eligibility(self, organization_id: str) -> dict:
        """
        Check if organization is eligible for deletion.
        
        Args:
            organization_id: ID of organization to check
            
        Returns:
            Dictionary with eligibility status and reasons
        """
        try:
            organization = await self._get_existing_organization(organization_id)
            
            eligibility = {
                "eligible": True,
                "reasons": [],
                "warnings": [],
                "organization_name": organization.name,
                "employee_count": organization.used_employee_strength
            }
            
            # Check for blocking conditions
            if organization.used_employee_strength > 0:
                eligibility["eligible"] = False
                eligibility["reasons"].append(
                    f"Organization has {organization.used_employee_strength} active employees"
                )
            
            # Check for warning conditions
            if organization.is_active():
                eligibility["warnings"].append("Organization is currently active")
            
            if organization.is_gst_registered():
                eligibility["warnings"].append("Organization is GST registered")
            
            return eligibility
            
        except OrganizationNotFoundError:
            return {
                "eligible": False,
                "reasons": ["Organization not found"],
                "warnings": [],
                "organization_name": None,
                "employee_count": 0
            } 