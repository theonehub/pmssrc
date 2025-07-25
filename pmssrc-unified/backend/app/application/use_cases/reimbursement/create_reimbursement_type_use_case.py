"""
Create Reimbursement Type Use Case
Business logic for creating reimbursement types
"""

import logging
from typing import Optional
from decimal import Decimal
import uuid

from app.domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from app.domain.value_objects.reimbursement_type import (
    ReimbursementType as ReimbursementTypeVO
)
from app.application.dto.reimbursement_dto import (
    ReimbursementTypeCreateRequestDTO,
    ReimbursementTypeResponseDTO,
    create_reimbursement_type_response_from_entity,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError
)
from app.application.interfaces.repositories.reimbursement_repository import (
    ReimbursementTypeCommandRepository,
    ReimbursementTypeQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.auth.auth_dependencies import CurrentUser


logger = logging.getLogger(__name__)


class CreateReimbursementTypeUseCase:
    """
    Use case for creating reimbursement types.
    
    Follows SOLID principles:
    - SRP: Handles only reimbursement type creation
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        command_repository: ReimbursementTypeCommandRepository,
        query_repository: ReimbursementTypeQueryRepository,
        event_publisher: EventPublisher,
        notification_service: Optional[NotificationService] = None
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.event_publisher = event_publisher
        self.notification_service = notification_service
    
    async def execute(
        self,
        request: ReimbursementTypeCreateRequestDTO,
        current_user: CurrentUser
    ) -> ReimbursementTypeResponseDTO:
        """
        Execute reimbursement type creation workflow.
        
        Steps:
        1. Validate request data
        2. Check business rules
        3. Create domain objects
        4. Persist to repository
        5. Publish domain events
        6. Send notifications
        7. Return response
        """
        
        created_by = current_user.username
        
        try:
            logger.info(f"Creating reimbursement type: {request.category_name} by {created_by}")
            
            # Step 1: Validate request data
            await self._validate_request(request)
            
            # Step 2: Check business rules
            await self._check_business_rules(request, current_user)
            
            # Step 3: Create domain objects
            reimbursement_type_entity = await self._create_domain_objects(request, created_by)
            
            # Step 4: Persist to repository
            saved_entity = await self._persist_entity(reimbursement_type_entity, current_user)
            
            # Step 5: Publish domain events
            await self._publish_events(saved_entity)
            
            # Step 6: Send notifications
            await self._send_notifications(saved_entity, created_by)
            
            # Step 7: Return response
            response = create_reimbursement_type_response_from_entity(saved_entity)
            
            logger.info(f"Successfully created reimbursement type: {saved_entity.reimbursement_type_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create reimbursement type: {str(e)}")
            raise
    
    async def _validate_request(self, request: ReimbursementTypeCreateRequestDTO):
        """Validate the request data"""
        
        # Basic validation is handled by Pydantic, but we can add custom validation here
        if not request.category_name or len(request.category_name.strip()) == 0:
            raise ReimbursementValidationError("Reimbursement type category_name cannot be empty")
        
        # Validate max_limit if provided
        if request.max_limit is not None and request.max_limit <= 0:
            raise ReimbursementValidationError("Maximum limit must be positive", "max_limit")
        
        logger.info("Request validation passed")
    
    async def _check_business_rules(self, request: ReimbursementTypeCreateRequestDTO, current_user: CurrentUser):
        """Check business rules for reimbursement type creation"""
        
        # Rule 1: Code must be unique
        existing_type = await self.query_repository.get_by_code(request.category_name, current_user)
        if existing_type:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement type with category_name '{request.category_name}' already exists"
            )
        
        # Rule 3: Auto-approve types should have reasonable limits
        if request.is_approval_required == False:
            if not request.max_limit:
                raise ReimbursementBusinessRuleError(
                    "Auto-approve reimbursement types must have a maximum limit"
                )
        
        logger.info("Business rules validation passed")
    
    async def _create_domain_objects(
        self,
        request: ReimbursementTypeCreateRequestDTO,
        created_by: str
    ) -> ReimbursementTypeEntity:
        """Create domain objects from request"""
        
        # Create entity directly with aligned fields
        entity = ReimbursementTypeEntity(
            reimbursement_type_id=str(uuid.uuid4()),
            category_name=request.category_name,
            description=request.description,
            max_limit=request.max_limit,
            is_approval_required=request.is_approval_required,
            is_receipt_required=request.is_receipt_required,
            is_active=True,
            created_by=created_by,
            updated_by=created_by
        )
        
        logger.info(f"Created domain entity: {entity.reimbursement_type_id}")
        return entity
    
    async def _persist_entity(self, entity: ReimbursementTypeEntity, current_user: CurrentUser) -> ReimbursementTypeEntity:
        """Persist entity to repository"""
        
        try:
            saved_entity = await self.command_repository.save(entity, current_user.hostname)
            logger.info(f"Persisted entity: {saved_entity.reimbursement_type_id}")
            return saved_entity
            
        except Exception as e:
            logger.error(f"Failed to persist entity: {str(e)}")
            raise ReimbursementBusinessRuleError(
                f"Failed to save reimbursement type: {str(e)}",
                "persistence_error"
            )
    
    async def _publish_events(self, entity: ReimbursementTypeEntity):
        """Publish domain events"""
        
        try:
            # For now, we don't have domain events on the entity
            # This can be extended in the future if domain events are added
            logger.info("Domain events publishing skipped - not implemented on entity")
            
        except Exception as e:
            logger.error(f"Failed to publish events: {str(e)}")
            # Don't fail the entire operation for event publishing errors
    
    async def _send_notifications(self, entity: ReimbursementTypeEntity, created_by: str):
        """Send notifications for reimbursement type creation"""
        
        if not self.notification_service:
            return
        
        try:
            # Notify administrators about new reimbursement type
            notification_data = {
                "type": "reimbursement_type_created",
                "reimbursement_type_id": entity.reimbursement_type_id,
                "category_name": entity.category_name,
                "category": entity.category_name,
                "created_by": created_by,
                "max_limit": str(entity.max_limit) if entity.max_limit else "No limit"
            }
            
            await self.notification_service.send_admin_notification(
                subject=f"New Reimbursement Type Created: {entity.category_name}",
                template="reimbursement_type_created",
                data=notification_data
            )
            
            logger.info("Sent creation notification")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}")
            # Don't fail the entire operation for notification errors 