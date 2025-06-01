"""
Create Reimbursement Request Use Case
Business logic for creating reimbursement requests
"""

import logging
from typing import Optional
from decimal import Decimal

from app.domain.entities.reimbursement import Reimbursement
from app.domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.reimbursement_amount import ReimbursementAmount
from app.application.dto.reimbursement_dto import (
    ReimbursementRequestCreateDTO,
    ReimbursementResponseDTO,
    create_reimbursement_response_from_entity,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError
)
from app.application.interfaces.repositories.reimbursement_repository import (
    ReimbursementCommandRepository,
    ReimbursementQueryRepository,
    ReimbursementTypeQueryRepository
)
from app.application.interfaces.repositories.employee_repository import EmployeeQueryRepository
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class CreateReimbursementRequestUseCase:
    """
    Use case for creating reimbursement requests.
    
    Follows SOLID principles:
    - SRP: Handles only reimbursement request creation
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        command_repository: ReimbursementCommandRepository,
        query_repository: ReimbursementQueryRepository,
        reimbursement_type_repository: ReimbursementTypeQueryRepository,
        employee_repository: EmployeeQueryRepository,
        event_publisher: EventPublisher,
        notification_service: Optional[NotificationService] = None
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.reimbursement_type_repository = reimbursement_type_repository
        self.employee_repository = employee_repository
        self.event_publisher = event_publisher
        self.notification_service = notification_service
    
    async def execute(
        self,
        request: ReimbursementRequestCreateDTO,
        created_by: str = "system"
    ) -> ReimbursementResponseDTO:
        """
        Execute reimbursement request creation workflow.
        
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
            logger.info(f"Creating reimbursement request for employee: {request.employee_id} by {created_by}")
            
            # Step 1: Validate request data
            await self._validate_request(request)
            
            # Step 2: Check business rules
            employee, reimbursement_type = await self._check_business_rules(request)
            
            # Step 3: Create domain objects
            reimbursement = await self._create_domain_objects(request, created_by)
            
            # Step 4: Persist to repository
            saved_reimbursement = await self._persist_entity(reimbursement)
            
            # Step 5: Publish domain events
            await self._publish_events(saved_reimbursement)
            
            # Step 6: Send notifications
            await self._send_notifications(saved_reimbursement, employee, reimbursement_type, created_by)
            
            # Step 7: Return response
            response = create_reimbursement_response_from_entity(saved_reimbursement, reimbursement_type)
            
            logger.info(f"Successfully created reimbursement request: {saved_reimbursement.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create reimbursement request: {str(e)}")
            raise
    
    async def _validate_request(self, request: ReimbursementRequestCreateDTO):
        """Validate the request data"""
        
        if not request.employee_id or len(request.employee_id.strip()) == 0:
            raise ReimbursementValidationError("Employee ID cannot be empty", "employee_id")
        
        if not request.reimbursement_type_id or len(request.reimbursement_type_id.strip()) == 0:
            raise ReimbursementValidationError("Reimbursement type ID cannot be empty", "reimbursement_type_id")
        
        if request.amount <= 0:
            raise ReimbursementValidationError("Amount must be positive", "amount")
        
        if request.amount > Decimal('9999999.99'):
            raise ReimbursementValidationError("Amount cannot exceed ₹99,99,999.99", "amount")
        
        logger.debug("Request validation passed")
    
    async def _check_business_rules(self, request: ReimbursementRequestCreateDTO):
        """Check business rules for reimbursement request creation"""
        
        # Rule 1: Employee must exist and be active
        employee_id = EmployeeId.from_string(request.employee_id)
        employee = await self.employee_repository.get_by_id(employee_id)
        if not employee:
            raise ReimbursementBusinessRuleError(
                f"Employee with ID '{request.employee_id}' not found",
                "employee_not_found"
            )
        
        if not employee.is_active():
            raise ReimbursementBusinessRuleError(
                f"Employee '{request.employee_id}' is not active",
                "employee_inactive"
            )
        
        # Rule 2: Reimbursement type must exist and be active
        reimbursement_type = await self.reimbursement_type_repository.get_by_id(request.reimbursement_type_id)
        if not reimbursement_type:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement type with ID '{request.reimbursement_type_id}' not found",
                "reimbursement_type_not_found"
            )
        
        if not reimbursement_type.is_active:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement type '{request.reimbursement_type_id}' is not active",
                "reimbursement_type_inactive"
            )
        
        # Rule 3: Check amount limits
        amount = ReimbursementAmount(request.amount, request.currency)
        if not reimbursement_type.validate_amount(amount):
            limit_display = reimbursement_type.reimbursement_type.get_limit_display()
            raise ReimbursementBusinessRuleError(
                f"Amount {amount} exceeds the limit of {limit_display}",
                "amount_exceeds_limit"
            )
        
        # Rule 4: Check period-based limits (if applicable)
        await self._check_period_limits(employee_id, reimbursement_type, amount)
        
        logger.debug("Business rules validation passed")
        return employee, reimbursement_type
    
    async def _check_period_limits(
        self,
        employee_id: EmployeeId,
        reimbursement_type: ReimbursementTypeEntity,
        amount: ReimbursementAmount
    ):
        """Check period-based spending limits"""
        
        if not reimbursement_type.reimbursement_type.has_limit():
            return
        
        from datetime import datetime, timedelta
        
        # Calculate period start based on frequency
        frequency = reimbursement_type.reimbursement_type.frequency
        now = datetime.utcnow()
        
        if frequency.value == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif frequency.value == "weekly":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif frequency.value == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif frequency.value == "quarterly":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif frequency.value == "annually":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return  # No period limit for unlimited frequency
        
        # Get total spent in this period
        total_spent = await self.query_repository.get_total_amount_by_employee_and_type(
            employee_id.value,
            reimbursement_type.type_id,
            start_date,
            now
        )
        
        # Check if new amount would exceed limit
        limit_amount = ReimbursementAmount(reimbursement_type.reimbursement_type.max_limit, amount.currency)
        current_spent = ReimbursementAmount(total_spent, amount.currency)
        total_with_new = current_spent.add(amount)
        
        if total_with_new.is_greater_than(limit_amount):
            raise ReimbursementBusinessRuleError(
                f"Adding this amount would exceed the {frequency.value} limit of {limit_amount}. "
                f"Current spent: {current_spent}, Requested: {amount}",
                "period_limit_exceeded"
            )
    
    async def _create_domain_objects(
        self,
        request: ReimbursementRequestCreateDTO,
        created_by: str
    ) -> Reimbursement:
        """Create domain objects from request"""
        
        employee_id = EmployeeId.from_string(request.employee_id)
        
        # Get reimbursement type for domain object creation
        reimbursement_type = await self.reimbursement_type_repository.get_by_id(request.reimbursement_type_id)
        
        amount = ReimbursementAmount(request.amount, request.currency)
        
        # Create reimbursement entity
        reimbursement = Reimbursement.create_request(
            employee_id=employee_id,
            reimbursement_type=reimbursement_type.reimbursement_type,
            amount=amount,
            description=request.description,
            created_by=created_by
        )
        
        logger.debug(f"Created domain entity: {reimbursement.request_id}")
        return reimbursement
    
    async def _persist_entity(self, reimbursement: Reimbursement) -> Reimbursement:
        """Persist entity to repository"""
        
        try:
            saved_reimbursement = await self.command_repository.save(reimbursement)
            logger.debug(f"Persisted entity: {saved_reimbursement.request_id}")
            return saved_reimbursement
            
        except Exception as e:
            logger.error(f"Failed to persist entity: {str(e)}")
            raise ReimbursementBusinessRuleError(
                f"Failed to save reimbursement request: {str(e)}",
                "persistence_error"
            )
    
    async def _publish_events(self, reimbursement: Reimbursement):
        """Publish domain events"""
        
        try:
            events = reimbursement.get_domain_events()
            
            for event in events:
                await self.event_publisher.publish(event)
                logger.debug(f"Published event: {event.get_event_type()}")
            
            # Clear events after publishing
            reimbursement.clear_domain_events()
            
        except Exception as e:
            logger.error(f"Failed to publish events: {str(e)}")
            # Don't fail the entire operation for event publishing errors
    
    async def _send_notifications(
        self,
        reimbursement: Reimbursement,
        employee,
        reimbursement_type: ReimbursementTypeEntity,
        created_by: str
    ):
        """Send notifications for reimbursement request creation"""
        
        if not self.notification_service:
            return
        
        try:
            # Notify employee about request creation
            notification_data = {
                "type": "reimbursement_request_created",
                "request_id": reimbursement.request_id,
                "employee_id": reimbursement.employee_id.value,
                "reimbursement_type": reimbursement_type.get_name(),
                "amount": str(reimbursement.amount),
                "status": reimbursement.status.value,
                "created_by": created_by,
                "requires_receipt": reimbursement_type.requires_receipt(),
                "auto_approved": reimbursement_type.is_auto_approved()
            }
            
            # Send notification to employee
            await self.notification_service.send_employee_notification(
                employee_id=reimbursement.employee_id.value,
                subject=f"Reimbursement Request Created: {reimbursement_type.get_name()}",
                template="reimbursement_request_created",
                data=notification_data
            )
            
            # If requires approval, notify managers
            if reimbursement_type.requires_manager_approval() or reimbursement_type.requires_admin_approval():
                await self.notification_service.send_manager_notification(
                    employee_id=reimbursement.employee_id.value,
                    subject=f"Reimbursement Request Pending Approval: {reimbursement_type.get_name()}",
                    template="reimbursement_approval_required",
                    data=notification_data
                )
            
            logger.debug("Sent creation notifications")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}")
            # Don't fail the entire operation for notification errors 