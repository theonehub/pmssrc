"""
Process Reimbursement Payment Use Case
Business logic for processing reimbursement payments
"""

import logging
from typing import Optional

from app.domain.entities.reimbursement import Reimbursement, PaymentMethod
from app.domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from app.application.dto.reimbursement_dto import (
    ReimbursementPaymentDTO,
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
from app.application.interfaces.services.payment_service import PaymentService


logger = logging.getLogger(__name__)


class ProcessReimbursementPaymentUseCase:
    """
    Use case for processing reimbursement payments.
    
    Follows SOLID principles:
    - SRP: Handles only reimbursement payment processing
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
        payment_service: Optional[PaymentService] = None,
        notification_service: Optional[NotificationService] = None
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.reimbursement_type_repository = reimbursement_type_repository
        self.employee_repository = employee_repository
        self.event_publisher = event_publisher
        self.payment_service = payment_service
        self.notification_service = notification_service
    
    async def execute(
        self,
        request_id: str,
        payment_request: ReimbursementPaymentDTO,
        processed_by: str,
        hostname: str
    ) -> ReimbursementResponseDTO:
        """
        Execute reimbursement payment processing workflow.
        
        Steps:
        1. Validate request data
        2. Check business rules
        3. Process payment (if payment service available)
        4. Update domain objects
        5. Persist to repository
        6. Publish domain events
        7. Send notifications
        8. Return response
        """
        
        try:
            logger.info(f"Processing payment for reimbursement request: {request_id} by {processed_by}")
            
            # Step 1: Validate request data
            await self._validate_request(payment_request, processed_by)
            
            # Step 2: Check business rules and get entities
            reimbursement, reimbursement_type, employee = await self._check_business_rules(
                request_id, payment_request, processed_by, hostname
            )
            
            # Step 3: Process payment (if payment service available)
            payment_reference = await self._process_external_payment(
                reimbursement, employee, payment_request
            )
            
            # Step 4: Update domain objects
            await self._update_domain_objects(
                reimbursement, payment_request, processed_by, payment_reference
            )
            
            # Step 5: Persist to repository
            saved_reimbursement = await self._persist_entity(reimbursement, hostname)
            
            # Step 6: Publish domain events
            await self._publish_events(saved_reimbursement)
            
            # Step 7: Send notifications
            await self._send_notifications(saved_reimbursement, employee, reimbursement_type, processed_by)
            
            # Step 8: Return response
            response = create_reimbursement_response_from_entity(saved_reimbursement, reimbursement_type)
            
            logger.info(f"Successfully processed payment for reimbursement request: {saved_reimbursement.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process payment for reimbursement request: {str(e)}")
            raise
    
    async def _validate_request(self, payment_request: ReimbursementPaymentDTO, processed_by: str):
        """Validate the payment request data"""
        
        if not processed_by or len(processed_by.strip()) == 0:
            raise ReimbursementValidationError("Processed by cannot be empty", "processed_by")
        
        # Validate payment method
        valid_methods = ["bank_transfer", "cash", "cheque", "digital_wallet"]
        if payment_request.payment_method not in valid_methods:
            raise ReimbursementValidationError(
                f"Invalid payment method. Must be one of: {', '.join(valid_methods)}",
                "payment_method"
            )
        
        # Validate payment reference for certain methods
        if payment_request.payment_method in ["bank_transfer", "cheque", "digital_wallet"]:
            if not payment_request.payment_reference:
                raise ReimbursementValidationError(
                    f"Payment reference is required for {payment_request.payment_method}",
                    "payment_reference"
                )
        
        logger.debug("Payment request validation passed")
    
    async def _check_business_rules(
        self,
        request_id: str,
        payment_request: ReimbursementPaymentDTO,
        processed_by: str,
        hostname: str
    ):
        """Check business rules for reimbursement payment processing"""
        
        # Rule 1: Reimbursement request must exist
        reimbursement = await self.query_repository.get_by_id(request_id, hostname)
        if not reimbursement:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement request with ID '{request_id}' not found",
                "reimbursement_not_found"
            )
        
        # Rule 2: Request must be approved
        if not reimbursement.is_approved():
            raise ReimbursementBusinessRuleError(
                f"Reimbursement request is in '{reimbursement.status.value}' status and cannot be paid. Must be approved first.",
                "invalid_status_for_payment"
            )
        
        # Rule 3: Request must not already be paid
        if reimbursement.is_paid():
            raise ReimbursementBusinessRuleError(
                "Reimbursement request has already been paid",
                "already_paid"
            )
        
        # Rule 4: Get reimbursement type for validation
        reimbursement_type = await self.reimbursement_type_repository.get_by_code(
            reimbursement.reimbursement_type.code, hostname
        )
        if not reimbursement_type:
            raise ReimbursementBusinessRuleError(
                f"Reimbursement type '{reimbursement.reimbursement_type.code}' not found",
                "reimbursement_type_not_found"
            )
        
        # Rule 5: Check payment authority
        await self._check_payment_authority(processed_by, hostname)
        
        # Rule 6: Get employee for payment processing
        employee = await self.employee_repository.get_by_id(reimbursement.employee_id, hostname)
        if not employee:
            raise ReimbursementBusinessRuleError(
                f"Employee with ID '{reimbursement.employee_id.value}' not found",
                "employee_not_found"
            )
        
        # Rule 7: Validate employee bank details for bank transfers
        if payment_request.payment_method == "bank_transfer":
            if not employee.has_bank_details():
                raise ReimbursementBusinessRuleError(
                    "Employee bank details are required for bank transfer payments",
                    "missing_bank_details"
                )
        
        logger.debug("Business rules validation passed")
        return reimbursement, reimbursement_type, employee
    
    async def _check_payment_authority(self, processed_by: str, hostname: str):
        """Check if the processor has the required authority"""
        
        # Get processor details
        processor = await self.employee_repository.get_by_id_string(processed_by, hostname)
        if not processor:
            raise ReimbursementBusinessRuleError(
                f"Processor with ID '{processed_by}' not found",
                "processor_not_found"
            )
        
        # Check if processor has finance role or admin privileges
        if not processor.has_finance_role() and not processor.is_admin():
            raise ReimbursementBusinessRuleError(
                "Only finance team members or administrators can process payments",
                "insufficient_payment_authority"
            )
    
    async def _process_external_payment(
        self,
        reimbursement: Reimbursement,
        employee,
        payment_request: ReimbursementPaymentDTO
    ) -> Optional[str]:
        """Process payment through external payment service"""
        
        if not self.payment_service:
            logger.info("No payment service configured, skipping external payment processing")
            return payment_request.payment_reference
        
        try:
            # Get final amount to be paid
            final_amount = reimbursement.get_final_amount()
            
            # Prepare payment data
            payment_data = {
                "reimbursement_id": reimbursement.request_id,
                "employee_id": reimbursement.employee_id.value,
                "amount": final_amount.amount,
                "currency": final_amount.currency,
                "payment_method": payment_request.payment_method,
                "employee_bank_details": employee.get_bank_details() if payment_request.payment_method == "bank_transfer" else None,
                "description": f"Reimbursement payment for {reimbursement.reimbursement_type.name}"
            }
            
            # Process payment
            payment_result = await self.payment_service.process_payment(payment_data)
            
            if payment_result.success:
                logger.info(f"External payment processed successfully: {payment_result.reference}")
                return payment_result.reference
            else:
                raise ReimbursementBusinessRuleError(
                    f"Payment processing failed: {payment_result.error_message}",
                    "payment_processing_failed"
                )
                
        except Exception as e:
            logger.error(f"External payment processing failed: {str(e)}")
            raise ReimbursementBusinessRuleError(
                f"Payment processing failed: {str(e)}",
                "payment_processing_error"
            )
    
    async def _update_domain_objects(
        self,
        reimbursement: Reimbursement,
        payment_request: ReimbursementPaymentDTO,
        processed_by: str,
        payment_reference: Optional[str]
    ):
        """Update domain objects with payment information"""
        
        # Convert payment method string to enum
        payment_method = PaymentMethod(payment_request.payment_method)
        
        # Process the payment
        reimbursement.process_payment(
            paid_by=processed_by,
            payment_method=payment_method,
            payment_reference=payment_reference or payment_request.payment_reference,
            bank_details=payment_request.bank_details
        )
        
        logger.debug(f"Updated domain object with payment: {reimbursement.request_id}")
    
    async def _persist_entity(self, reimbursement: Reimbursement, hostname: str) -> Reimbursement:
        """Persist entity to repository"""
        
        try:
            saved_reimbursement = await self.command_repository.update(reimbursement, hostname)
            logger.debug(f"Persisted paid entity: {saved_reimbursement.request_id}")
            return saved_reimbursement
            
        except Exception as e:
            logger.error(f"Failed to persist entity: {str(e)}")
            raise ReimbursementBusinessRuleError(
                f"Failed to save paid reimbursement request: {str(e)}",
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
        processed_by: str
    ):
        """Send notifications for reimbursement payment processing"""
        
        if not self.notification_service:
            return
        
        try:
            # Get final paid amount
            final_amount = reimbursement.get_final_amount()
            
            # Notify employee about payment
            notification_data = {
                "type": "reimbursement_payment_processed",
                "request_id": reimbursement.request_id,
                "employee_id": reimbursement.employee_id.value,
                "reimbursement_type": reimbursement_type.get_category_name(),
                "paid_amount": str(final_amount),
                "payment_method": reimbursement.payment.payment_method.value if reimbursement.payment else "unknown",
                "payment_reference": reimbursement.payment.payment_reference if reimbursement.payment else None,
                "processed_by": processed_by,
                "status": reimbursement.status.value
            }
            
            # Send notification to employee
            await self.notification_service.send_employee_notification(
                employee_id=reimbursement.employee_id.value,
                subject=f"Reimbursement Payment Processed: {reimbursement_type.get_category_name()}",
                template="reimbursement_payment_processed",
                data=notification_data
            )
            
            # Notify finance team about successful payment
            await self.notification_service.send_finance_notification(
                subject=f"Reimbursement Payment Completed: {reimbursement_type.get_category_name()}",
                template="reimbursement_payment_completed",
                data=notification_data
            )
            
            # Notify processor about successful payment
            await self.notification_service.send_employee_notification(
                employee_id=processed_by,
                subject=f"Reimbursement Payment Processed Successfully: {reimbursement_type.get_category_name()}",
                template="reimbursement_payment_confirmation",
                data=notification_data
            )
            
            logger.debug("Sent payment notifications")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}")
            # Don't fail the entire operation for notification errors 