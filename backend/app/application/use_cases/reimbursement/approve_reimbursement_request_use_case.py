"""
Approve Reimbursement Request Use Case
Business logic for approving reimbursement requests
"""

import logging
from typing import Optional
from decimal import Decimal

from domain.entities.reimbursement import Reimbursement
from domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from domain.value_objects.reimbursement_amount import ReimbursementAmount
from application.dto.reimbursement_dto import (
    ReimbursementApprovalDTO,
    ReimbursementResponseDTO,
    create_reimbursement_response_from_entity,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError
)
from application.interfaces.repositories.reimbursement_repository import (
    ReimbursementCommandRepository,
    ReimbursementQueryRepository,
    ReimbursementTypeQueryRepository
)
from application.interfaces.repositories.employee_repository import EmployeeQueryRepository
from application.interfaces.services.event_publisher import EventPublisher
from application.interfaces.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class ApproveReimbursementRequestUseCase:
    """
    Use case for approving reimbursement requests.
    
    Follows SOLID principles:
    - SRP: Handles only reimbursement request approval
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
        request_id: str,
        approval_request: ReimbursementApprovalDTO,
        approved_by: str
    ) -> ReimbursementResponseDTO:
        """
        Execute reimbursement request approval workflow.
        
        Steps:
        1. Validate request data
        2. Check business rules
        3. Update domain objects
        4. Persist to repository
        5. Publish domain events
        6. Send notifications
        7. Return response
        """
        
        try:
            logger.info(f"Approving reimbursement request: {request_id} by {approved_by}")
            
            # Step 1: Validate request data
            await self._validate_request(approval_request, approved_by)
            
            # Step 2: Check business rules and get entities
            reimbursement, reimbursement_type, employee = await self._check_business_rules(
                request_id, approval_request, approved_by
            )
            
            # Step 3: Update domain objects
            await self._update_domain_objects(reimbursement, approval_request, approved_by)
            
            # Step 4: Persist to repository
            saved_reimbursement = await self._persist_entity(reimbursement)
            
            # Step 5: Publish domain events
            await self._publish_events(saved_reimbursement)
            
            # Step 6: Send notifications
            await self._send_notifications(saved_reimbursement, employee, reimbursement_type, approved_by)
            
            # Step 7: Return response
            response = create_reimbursement_response_from_entity(saved_reimbursement, reimbursement_type)
            
            logger.info(f"Successfully approved reimbursement request: {saved_reimbursement.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to approve reimbursement request: {str(e)}")
            raise
    
    async def _validate_request(self, approval_request: ReimbursementApprovalDTO, approved_by: str):
        """Validate the approval request data"""
        
        if not approved_by or len(approved_by.strip()) == 0:
            raise ReimbursementValidationError("Approved by cannot be empty", "approved_by")
        
        if approval_request.approved_amount is not None:
            if approval_request.approved_amount <= 0:
                raise ReimbursementValidationError("Approved amount must be positive", "approved_amount")
            
            if approval_request.approved_amount > Decimal('9999999.99'):
                raise ReimbursementValidationError("Approved amount cannot exceed ₹99,99,999.99", "approved_amount")
        
        logger.debug("Approval request validation passed")
    
    async def _check_business_rules(
        self,
        request_id: str,
        approval_request: ReimbursementApprovalDTO,
        approved_by: str
    ):
        """Check business rules for reimbursement request approval"""
        
        # Rule 1: Reimbursement request must exist
        reimbursement = await self.query_repository.get_by_id(request_id)
        if not reimbursement:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement request with ID '{request_id}' not found",
                "reimbursement_not_found"
            )
        
        # Rule 2: Request must be in approvable status
        if not reimbursement.is_pending_approval():
            raise ReimbursementBusinessRuleError(
                f"Reimbursement request is in '{reimbursement.status.value}' status and cannot be approved",
                "invalid_status_for_approval"
            )
        
        # Rule 3: Get reimbursement type for validation
        reimbursement_type = await self.reimbursement_type_repository.get_by_code(
            reimbursement.reimbursement_type.code
        )
        if not reimbursement_type:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement type '{reimbursement.reimbursement_type.code}' not found",
                "reimbursement_type_not_found"
            )
        
        # Rule 4: Check approval authority
        await self._check_approval_authority(reimbursement_type, approved_by, approval_request.approval_level)
        
        # Rule 5: Validate approved amount
        if approval_request.approved_amount is not None:
            approved_amount = ReimbursementAmount(approval_request.approved_amount, reimbursement.amount.currency)
            
            # Check if approved amount exceeds original request
            if approved_amount.is_greater_than(reimbursement.amount):
                raise ReimbursementBusinessRuleError(
                    f"Approved amount {approved_amount} cannot exceed requested amount {reimbursement.amount}",
                    "approved_amount_exceeds_request"
                )
            
            # Check if approved amount is within type limits
            if not reimbursement_type.validate_amount(approved_amount):
                limit_display = reimbursement_type.reimbursement_type.get_limit_display()
                raise ReimbursementBusinessRuleError(
                    f"Approved amount {approved_amount} exceeds the limit of {limit_display}",
                    "approved_amount_exceeds_limit"
                )
        
        # Rule 6: Get employee for notifications
        employee = await self.employee_repository.get_by_id(reimbursement.employee_id)
        if not employee:
            raise ReimbursementBusinessRuleError(
                f"Employee with ID '{reimbursement.employee_id.value}' not found",
                "employee_not_found"
            )
        
        logger.debug("Business rules validation passed")
        return reimbursement, reimbursement_type, employee
    
    async def _check_approval_authority(
        self,
        reimbursement_type: ReimbursementTypeEntity,
        approved_by: str,
        approval_level: str
    ):
        """Check if the approver has the required authority"""
        
        # Get approver details
        approver = await self.employee_repository.get_by_id_string(approved_by)
        if not approver:
            raise ReimbursementBusinessRuleError(
                f"Approver with ID '{approved_by}' not found",
                "approver_not_found"
            )
        
        # Check approval level requirements
        required_approval = reimbursement_type.reimbursement_type.approval_level
        
        if required_approval.value == "manager" and approval_level not in ["manager", "admin", "finance"]:
            raise ReimbursementBusinessRuleError(
                "Manager level approval or higher is required for this reimbursement type",
                "insufficient_approval_authority"
            )
        
        if required_approval.value == "admin" and approval_level not in ["admin", "finance"]:
            raise ReimbursementBusinessRuleError(
                "Admin level approval or higher is required for this reimbursement type",
                "insufficient_approval_authority"
            )
        
        if required_approval.value == "finance" and approval_level != "finance":
            raise ReimbursementBusinessRuleError(
                "Finance level approval is required for this reimbursement type",
                "insufficient_approval_authority"
            )
        
        # Additional business rule: Check if approver is not the same as requester
        # This would require getting the original requester information
        # For now, we'll skip this check but it could be added based on business requirements
    
    async def _update_domain_objects(
        self,
        reimbursement: Reimbursement,
        approval_request: ReimbursementApprovalDTO,
        approved_by: str
    ):
        """Update domain objects with approval information"""
        
        # Determine approved amount
        approved_amount = None
        if approval_request.approved_amount is not None:
            approved_amount = ReimbursementAmount(
                approval_request.approved_amount,
                reimbursement.amount.currency
            )
        
        # Approve the request
        reimbursement.approve_request(
            approved_by=approved_by,
            approved_amount=approved_amount,
            approval_level=approval_request.approval_level,
            comments=approval_request.comments
        )
        
        logger.debug(f"Updated domain object with approval: {reimbursement.request_id}")
    
    async def _persist_entity(self, reimbursement: Reimbursement) -> Reimbursement:
        """Persist entity to repository"""
        
        try:
            saved_reimbursement = await self.command_repository.update(reimbursement)
            logger.debug(f"Persisted approved entity: {saved_reimbursement.request_id}")
            return saved_reimbursement
            
        except Exception as e:
            logger.error(f"Failed to persist entity: {str(e)}")
            raise ReimbursementBusinessRuleError(
                f"Failed to save approved reimbursement request: {str(e)}",
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
        approved_by: str
    ):
        """Send notifications for reimbursement request approval"""
        
        if not self.notification_service:
            return
        
        try:
            # Get final approved amount
            final_amount = reimbursement.get_final_amount()
            
            # Notify employee about approval
            notification_data = {
                "type": "reimbursement_request_approved",
                "request_id": reimbursement.request_id,
                "employee_id": reimbursement.employee_id.value,
                "reimbursement_type": reimbursement_type.get_name(),
                "requested_amount": str(reimbursement.amount),
                "approved_amount": str(final_amount),
                "approved_by": approved_by,
                "approval_level": reimbursement.approval.approval_level if reimbursement.approval else "unknown",
                "comments": reimbursement.approval.comments if reimbursement.approval else None,
                "status": reimbursement.status.value
            }
            
            # Send notification to employee
            await self.notification_service.send_employee_notification(
                employee_id=reimbursement.employee_id.value,
                subject=f"Reimbursement Request Approved: {reimbursement_type.get_name()}",
                template="reimbursement_request_approved",
                data=notification_data
            )
            
            # Notify finance team for payment processing
            await self.notification_service.send_finance_notification(
                subject=f"Reimbursement Ready for Payment: {reimbursement_type.get_name()}",
                template="reimbursement_payment_required",
                data=notification_data
            )
            
            # Notify approver about successful approval
            await self.notification_service.send_employee_notification(
                employee_id=approved_by,
                subject=f"Reimbursement Request Approved Successfully: {reimbursement_type.get_name()}",
                template="reimbursement_approval_confirmation",
                data=notification_data
            )
            
            logger.debug("Sent approval notifications")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}")
            # Don't fail the entire operation for notification errors 