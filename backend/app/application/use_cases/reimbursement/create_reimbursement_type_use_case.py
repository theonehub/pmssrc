"""
Create Reimbursement Type Use Case
Business logic for creating reimbursement types
"""

import logging
from typing import Optional
from decimal import Decimal

from domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from domain.value_objects.reimbursement_type import (
    ReimbursementType as ReimbursementTypeVO,
    ReimbursementCategory,
    ReimbursementFrequency,
    ReimbursementApprovalLevel
)
from application.dto.reimbursement_dto import (
    ReimbursementTypeCreateRequestDTO,
    ReimbursementTypeResponseDTO,
    create_reimbursement_type_response_from_entity,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError
)
from application.interfaces.repositories.reimbursement_repository import (
    ReimbursementTypeCommandRepository,
    ReimbursementTypeQueryRepository
)
from application.interfaces.services.event_publisher import EventPublisher
from application.interfaces.services.notification_service import NotificationService


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
        created_by: str = "system"
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
        
        try:
            logger.info(f"Creating reimbursement type: {request.name} by {created_by}")
            
            # Step 1: Validate request data
            await self._validate_request(request)
            
            # Step 2: Check business rules
            await self._check_business_rules(request)
            
            # Step 3: Create domain objects
            reimbursement_type_entity = await self._create_domain_objects(request, created_by)
            
            # Step 4: Persist to repository
            saved_entity = await self._persist_entity(reimbursement_type_entity)
            
            # Step 5: Publish domain events
            await self._publish_events(saved_entity)
            
            # Step 6: Send notifications
            await self._send_notifications(saved_entity, created_by)
            
            # Step 7: Return response
            response = create_reimbursement_type_response_from_entity(saved_entity)
            
            logger.info(f"Successfully created reimbursement type: {saved_entity.type_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create reimbursement type: {str(e)}")
            raise
    
    async def _validate_request(self, request: ReimbursementTypeCreateRequestDTO):
        """Validate the request data"""
        
        # Basic validation is handled by Pydantic, but we can add custom validation here
        if not request.code or len(request.code.strip()) == 0:
            raise ReimbursementValidationError("Reimbursement type code cannot be empty", "code")
        
        if not request.name or len(request.name.strip()) == 0:
            raise ReimbursementValidationError("Reimbursement type name cannot be empty", "name")
        
        # Validate code format (alphanumeric and underscores only)
        if not request.code.replace('_', '').isalnum():
            raise ReimbursementValidationError(
                "Reimbursement type code can only contain letters, numbers, and underscores",
                "code"
            )
        
        # Validate max_limit if provided
        if request.max_limit is not None and request.max_limit <= 0:
            raise ReimbursementValidationError("Maximum limit must be positive", "max_limit")
        
        logger.debug("Request validation passed")
    
    async def _check_business_rules(self, request: ReimbursementTypeCreateRequestDTO):
        """Check business rules for reimbursement type creation"""
        
        # Rule 1: Code must be unique
        existing_type = await self.query_repository.get_by_code(request.code.upper())
        if existing_type:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement type with code '{request.code}' already exists",
                "unique_code"
            )
        
        # Rule 2: Validate category-specific rules
        if request.category == "medical" and request.max_limit and request.max_limit > Decimal('500000'):
            logger.warning(f"High medical reimbursement limit: {request.max_limit}")
        
        # Rule 3: Auto-approve types should have reasonable limits
        if request.approval_level == "auto_approve":
            if not request.max_limit:
                raise ReimbursementBusinessRuleError(
                    "Auto-approve reimbursement types must have a maximum limit",
                    "auto_approve_limit"
                )
            
            if request.max_limit > Decimal('10000'):
                raise ReimbursementBusinessRuleError(
                    "Auto-approve reimbursement types cannot have limits above ₹10,000",
                    "auto_approve_limit_exceeded"
                )
        
        # Rule 4: Receipt requirements for certain categories
        if request.category in ["medical", "training"] and not request.requires_receipt:
            logger.warning(f"Medical/Training reimbursements typically require receipts")
        
        logger.debug("Business rules validation passed")
    
    async def _create_domain_objects(
        self,
        request: ReimbursementTypeCreateRequestDTO,
        created_by: str
    ) -> ReimbursementTypeEntity:
        """Create domain objects from request"""
        
        # Create value object
        reimbursement_type_vo = ReimbursementTypeVO(
            code=request.code.upper(),
            name=request.name,
            category=ReimbursementCategory(request.category),
            description=request.description,
            max_limit=request.max_limit,
            frequency=ReimbursementFrequency(request.frequency),
            approval_level=ReimbursementApprovalLevel(request.approval_level),
            requires_receipt=request.requires_receipt,
            tax_applicable=request.tax_applicable
        )
        
        # Create entity using appropriate factory method
        if request.category == "travel":
            entity = ReimbursementTypeEntity.create_travel_type(
                name=request.name,
                max_limit=request.max_limit,
                created_by=created_by,
                description=request.description
            )
        elif request.category == "medical":
            entity = ReimbursementTypeEntity.create_medical_type(
                name=request.name,
                max_limit=request.max_limit,
                created_by=created_by,
                description=request.description
            )
        elif request.category == "food":
            entity = ReimbursementTypeEntity.create_food_type(
                name=request.name,
                max_limit=request.max_limit,
                created_by=created_by,
                description=request.description
            )
        elif request.category == "communication":
            entity = ReimbursementTypeEntity.create_communication_type(
                name=request.name,
                max_limit=request.max_limit,
                created_by=created_by,
                description=request.description
            )
        else:
            entity = ReimbursementTypeEntity.create_custom_type(
                reimbursement_type=reimbursement_type_vo,
                created_by=created_by
            )
        
        logger.debug(f"Created domain entity: {entity.type_id}")
        return entity
    
    async def _persist_entity(self, entity: ReimbursementTypeEntity) -> ReimbursementTypeEntity:
        """Persist entity to repository"""
        
        try:
            saved_entity = await self.command_repository.save(entity)
            logger.debug(f"Persisted entity: {saved_entity.type_id}")
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
            events = entity.get_domain_events()
            
            for event in events:
                await self.event_publisher.publish(event)
                logger.debug(f"Published event: {event.get_event_type()}")
            
            # Clear events after publishing
            entity.clear_domain_events()
            
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
                "reimbursement_type_id": entity.type_id,
                "reimbursement_type_name": entity.get_name(),
                "category": entity.get_category(),
                "created_by": created_by,
                "max_limit": str(entity.get_max_limit()) if entity.get_max_limit() else "No limit"
            }
            
            await self.notification_service.send_admin_notification(
                subject=f"New Reimbursement Type Created: {entity.get_name()}",
                template="reimbursement_type_created",
                data=notification_data
            )
            
            logger.debug("Sent creation notification")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}")
            # Don't fail the entire operation for notification errors 