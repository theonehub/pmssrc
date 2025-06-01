"""
Approve Employee Leave Use Case
Business workflow for approving/rejecting employee leave requests
"""

import logging
from typing import Optional

from app.application.dto.employee_leave_dto import (
    EmployeeLeaveApprovalRequestDTO, 
    EmployeeLeaveResponseDTO,
    EmployeeLeaveValidationError,
    EmployeeLeaveBusinessRuleError,
    EmployeeLeaveNotFoundError
)
from app.application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveCommandRepository,
    EmployeeLeaveQueryRepository,
    EmployeeLeaveBalanceRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.email_service import EmailService
from app.domain.entities.employee_leave import EmployeeLeave, LeaveStatus
from app.infrastructure.services.legacy_migration_service import (
    get_user_by_employee_id, update_user_leave_balance
)


class ApproveEmployeeLeaveUseCase:
    """
    Use case for approving/rejecting employee leave requests.
    
    Follows SOLID principles:
    - SRP: Only handles employee leave approval workflow
    - OCP: Can be extended with new approval rules
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        command_repository: EmployeeLeaveCommandRepository,
        query_repository: EmployeeLeaveQueryRepository,
        balance_repository: EmployeeLeaveBalanceRepository,
        event_publisher: EventPublisher,
        email_service: Optional[EmailService] = None
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._balance_repository = balance_repository
        self._event_publisher = event_publisher
        self._email_service = email_service
        self._logger = logging.getLogger(__name__)
    
    async def execute(
        self, 
        leave_id: str,
        request: EmployeeLeaveApprovalRequestDTO, 
        approver_id: str,
        hostname: str
    ) -> EmployeeLeaveResponseDTO:
        """
        Execute employee leave approval/rejection workflow.
        
        Business Rules:
        1. Leave application must exist and be in pending status
        2. Approver must have permission to approve this leave
        3. For approvals: Deduct leave balance from employee
        4. For rejections: Reason must be provided
        5. Events must be published for downstream processing
        
        Args:
            leave_id: Leave application identifier
            request: Approval/rejection request
            approver_id: User approving/rejecting the leave
            hostname: Organization hostname
            
        Returns:
            EmployeeLeaveResponseDTO with updated leave details
            
        Raises:
            EmployeeLeaveNotFoundError: If leave application not found
            EmployeeLeaveValidationError: If request data is invalid
            EmployeeLeaveBusinessRuleError: If business rules are violated
            Exception: If approval/rejection fails
        """
        
        try:
            # Step 1: Validate request data
            self._logger.info(f"Processing leave approval: {leave_id} by {approver_id}")
            validation_errors = self._validate_request(request)
            if validation_errors:
                raise EmployeeLeaveValidationError(validation_errors)
            
            # Step 2: Get leave application
            employee_leave = self._query_repository.get_by_id(leave_id)
            if not employee_leave:
                raise EmployeeLeaveNotFoundError(leave_id)
            
            # Step 3: Validate business rules
            await self._validate_business_rules(employee_leave, approver_id, hostname)
            
            # Step 4: Process approval or rejection
            if request.status == LeaveStatus.APPROVED:
                await self._approve_leave(employee_leave, approver_id, request.comments, hostname)
            elif request.status == LeaveStatus.REJECTED:
                await self._reject_leave(employee_leave, approver_id, request.comments or "No reason provided")
            
            # Step 5: Update in database
            success = self._command_repository.update(employee_leave)
            if not success:
                raise Exception("Failed to update employee leave application")
            
            # Step 6: Publish domain events
            await self._publish_domain_events(employee_leave)
            
            # Step 7: Send notifications (if email service available)
            if self._email_service:
                await self._send_approval_notifications(employee_leave, hostname)
            
            # Step 8: Return response
            response = EmployeeLeaveResponseDTO.from_entity(employee_leave)
            self._logger.info(f"Successfully processed leave approval: {leave_id}")
            
            return response
            
        except EmployeeLeaveNotFoundError:
            self._logger.warning(f"Leave application not found: {leave_id}")
            raise
        except EmployeeLeaveValidationError:
            self._logger.warning(f"Validation failed for leave approval: {leave_id}")
            raise
        except EmployeeLeaveBusinessRuleError:
            self._logger.warning(f"Business rule violation in leave approval: {leave_id}")
            raise
        except Exception as e:
            self._logger.error(f"Failed to process leave approval {leave_id}: {str(e)}")
            raise Exception(f"Leave approval failed: {str(e)}")
    
    def _validate_request(self, request: EmployeeLeaveApprovalRequestDTO) -> list:
        """Validate approval request"""
        errors = []
        
        if request.status not in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
            errors.append("Status must be either APPROVED or REJECTED")
        
        if request.status == LeaveStatus.REJECTED and not request.comments:
            errors.append("Comments are required for rejection")
        
        return errors
    
    async def _validate_business_rules(
        self, 
        employee_leave: EmployeeLeave, 
        approver_id: str, 
        hostname: str
    ):
        """Validate business rules for leave approval"""
        
        # Check if leave is in pending status
        if employee_leave.status != LeaveStatus.PENDING:
            raise EmployeeLeaveBusinessRuleError(
                f"Cannot approve/reject leave in {employee_leave.status} status"
            )
        
        # Check if approver has permission (basic check - can be enhanced)
        approver = await get_user_by_employee_id(approver_id, hostname)
        if not approver:
            raise EmployeeLeaveBusinessRuleError(f"Approver not found: {approver_id}")
        
        # Check if approver has appropriate role
        approver_role = approver.get("role", "").lower()
        if approver_role not in ["manager", "admin", "superadmin"]:
            raise EmployeeLeaveBusinessRuleError(
                f"User does not have permission to approve leaves: {approver_id}"
            )
        
        # For managers, check if they manage the employee (simplified check)
        if approver_role == "manager":
            employee = await get_user_by_employee_id(str(employee_leave.employee_id), hostname)
            if employee and employee.get("manager_id") != approver_id:
                raise EmployeeLeaveBusinessRuleError(
                    f"Manager can only approve leaves for their team members"
                )
        
        # Check if leave has already started (optional business rule)
        # if employee_leave.date_range.start_date <= date.today():
        #     raise EmployeeLeaveBusinessRuleError("Cannot approve/reject leave that has already started")
    
    async def _approve_leave(
        self, 
        employee_leave: EmployeeLeave, 
        approver_id: str, 
        comments: Optional[str],
        hostname: str
    ):
        """Approve the leave application"""
        
        # Approve the leave (this will update status and raise domain events)
        employee_leave.approve(approver_id, comments)
        
        # Deduct leave balance from employee
        await self._deduct_leave_balance(employee_leave, hostname)
        
        self._logger.info(f"Approved leave: {employee_leave.leave_id}")
    
    async def _reject_leave(
        self, 
        employee_leave: EmployeeLeave, 
        approver_id: str, 
        reason: str
    ):
        """Reject the leave application"""
        
        # Reject the leave (this will update status and raise domain events)
        employee_leave.reject(approver_id, reason)
        
        self._logger.info(f"Rejected leave: {employee_leave.leave_id}")
    
    async def _deduct_leave_balance(self, employee_leave: EmployeeLeave, hostname: str):
        """Deduct leave balance from employee"""
        
        try:
            # Update leave balance using legacy service
            success = await update_user_leave_balance(
                str(employee_leave.employee_id),
                employee_leave.leave_type.code,
                -employee_leave.working_days_count,  # Negative to deduct
                hostname
            )
            
            if not success:
                self._logger.warning(f"Failed to update leave balance for employee: {employee_leave.employee_id}")
            else:
                self._logger.info(
                    f"Deducted {employee_leave.working_days_count} {employee_leave.leave_type.code} "
                    f"days from employee: {employee_leave.employee_id}"
                )
                
        except Exception as e:
            self._logger.error(f"Error updating leave balance: {str(e)}")
            # Don't fail the approval for balance update failures
    
    async def _publish_domain_events(self, employee_leave: EmployeeLeave):
        """Publish domain events for the leave approval/rejection"""
        
        try:
            events = employee_leave.get_domain_events()
            for event in events:
                await self._event_publisher.publish(event)
            
            employee_leave.clear_domain_events()
            self._logger.info(f"Published {len(events)} domain events for leave: {employee_leave.leave_id}")
            
        except Exception as e:
            self._logger.error(f"Failed to publish domain events: {str(e)}")
            # Don't fail the entire operation for event publishing failures
    
    async def _send_approval_notifications(self, employee_leave: EmployeeLeave, hostname: str):
        """Send email notifications for leave approval/rejection"""
        
        try:
            if self._email_service:
                # Get employee details
                employee = await get_user_by_employee_id(str(employee_leave.employee_id), hostname)
                if not employee:
                    return
                
                if employee_leave.status == LeaveStatus.APPROVED:
                    # Send approval notification to employee
                    await self._email_service.send_leave_approval_notification(
                        employee_email=employee.get("email"),
                        employee_name=employee.get("name"),
                        leave_type=employee_leave.leave_type.name,
                        start_date=employee_leave.date_range.start_date,
                        end_date=employee_leave.date_range.end_date,
                        working_days=employee_leave.working_days_count,
                        approved_by=employee_leave.approved_by,
                        comments=employee_leave.approval_comments
                    )
                    
                elif employee_leave.status == LeaveStatus.REJECTED:
                    # Send rejection notification to employee
                    await self._email_service.send_leave_rejection_notification(
                        employee_email=employee.get("email"),
                        employee_name=employee.get("name"),
                        leave_type=employee_leave.leave_type.name,
                        start_date=employee_leave.date_range.start_date,
                        end_date=employee_leave.date_range.end_date,
                        rejected_by=employee_leave.approved_by,
                        reason=employee_leave.approval_comments
                    )
                
                self._logger.info(f"Sent approval notifications for leave: {employee_leave.leave_id}")
                
        except Exception as e:
            self._logger.error(f"Failed to send approval notifications: {str(e)}")
            # Don't fail the entire operation for notification failures 