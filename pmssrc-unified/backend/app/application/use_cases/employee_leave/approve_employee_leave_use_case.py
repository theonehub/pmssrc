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
    EmployeeLeaveQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.email_service import EmailService
from app.domain.entities.employee_leave import EmployeeLeave
from app.application.dto.employee_leave_dto import LeaveStatus
from app.auth.auth_dependencies import CurrentUser
from app.application.interfaces.repositories.user_repository import UserQueryRepository, UserCommandRepository
from app.domain.value_objects.employee_id import EmployeeId


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
        user_query_repository: UserQueryRepository,
        user_command_repository: UserCommandRepository,
        event_publisher: Optional[EventPublisher] = None,
        email_service: Optional[EmailService] = None
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._user_query_repository = user_query_repository
        self._user_command_repository = user_command_repository
        self._event_publisher = event_publisher
        self._email_service = email_service
        self._logger = logging.getLogger(__name__)
    
    async def execute(
        self, 
        leave_id: str,
        request: EmployeeLeaveApprovalRequestDTO, 
        current_user: CurrentUser
    ) -> EmployeeLeaveResponseDTO:
        """
        Execute employee leave approval/rejection workflow.
        Args:
            leave_id: Leave application identifier
            request: Approval/rejection request
            current_user: User approving/rejecting the leave (provides organization context)
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
            self._logger.info(f"Processing leave approval: {leave_id} by {current_user.employee_id}")
            validation_errors = self._validate_request(request, current_user)
            if validation_errors:
                raise EmployeeLeaveValidationError(validation_errors)
            
            # Step 2: Get leave application
            employee_leave = await self._query_repository.get_by_id(leave_id, current_user.hostname)
            if not employee_leave:
                raise EmployeeLeaveNotFoundError(leave_id)
            
            # Step 3: Validate business rules
            await self._validate_business_rules(employee_leave, current_user)
            
            # Step 4: Process approval or rejection
            if request.status == LeaveStatus.APPROVED:
                status = await self._approve_leave(employee_leave, current_user.employee_id, request.comments, current_user.hostname)
            elif request.status == LeaveStatus.REJECTED:
                status = await self._reject_leave(employee_leave, current_user.employee_id, request.comments or "No reason provided", current_user.hostname)
            
            # Step 5: Update in database
            updated_leave = await self._command_repository.update(employee_leave, current_user.hostname)
            if not updated_leave:
                raise Exception("Failed to update employee leave application")
            employee_leave = updated_leave
            # Step 6: Publish domain events
            await self._publish_domain_events(employee_leave)
            
            # Step 7: Send notifications (if email service available)
            if self._email_service:
                await self._send_approval_notifications(employee_leave, current_user.hostname)
            
            # Step 8: Return response
            response = EmployeeLeaveResponseDTO.from_entity(employee_leave)
            self._logger.info(f"Leave approval: {status} for {leave_id}")
            
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
    
    def _validate_request(self, request: EmployeeLeaveApprovalRequestDTO, current_user: CurrentUser) -> list:
        """Validate approval request"""
        errors = []
        
        if request.status not in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
            errors.append("Status must be either APPROVED or REJECTED")
        
        if request.status == LeaveStatus.REJECTED and not request.comments:
            errors.append("Comments are required for rejection")
        
        if request.status == LeaveStatus.APPROVED and not current_user.role in ["manager", "admin", "superadmin"]:
            errors.append("Only managers can approve leaves")
        
        return errors
    
    async def _validate_business_rules(
        self, 
        employee_leave: EmployeeLeave, 
        current_user: CurrentUser
    ):
        """Validate business rules for leave approval"""
        
        # Check if leave is in pending status
        if employee_leave.status != LeaveStatus.PENDING:
            raise EmployeeLeaveBusinessRuleError(
                f"Cannot approve/reject leave in {employee_leave.status} status"
            )
        
        # Check if approver has appropriate role
        if current_user.role not in ["manager", "admin", "superadmin"]:
            raise EmployeeLeaveBusinessRuleError(
                f"User does not have permission to approve leaves: {current_user.employee_id} {current_user.role}"
            )
        
        
    async def _approve_leave(
        self, 
        employee_leave: EmployeeLeave, 
        approver_id: str, 
        comments: Optional[str],
        hostname: str
    ):
        """Approve the leave application and deduct leave balance"""
        # Approve the leave (this will update status and raise domain events)
        employee_leave.approve(approver_id)
        # Deduct leave balance from user
        try:
            employee_id_obj = EmployeeId(employee_leave.employee_id)
            user = await self._user_query_repository.get_by_id(employee_id_obj, hostname)
            if user:
                leave_type = employee_leave.leave_name
                current_balance = user.leave_balance.get(leave_type, 0)
                days_to_deduct = employee_leave.approved_days or employee_leave.applied_days or 0
                if days_to_deduct > current_balance:
                    employee_leave.status = LeaveStatus.LOW_BALANCE
                    self._logger.info(f"Days to deduct {days_to_deduct} is greater than current balance {current_balance} for user {employee_leave.employee_id}, leave_type {leave_type}")
                # Ensure both are floats
                try:
                    current_balance_f = float(current_balance)
                except Exception:
                    self._logger.error(f"Could not convert current_balance '{current_balance}' to float for user {employee_leave.employee_id}, leave_type {leave_type}")
                    current_balance_f = 0.0
                try:
                    days_to_deduct_f = float(days_to_deduct)
                except Exception:
                    self._logger.error(f"Could not convert days_to_deduct '{days_to_deduct}' to float for user {employee_leave.employee_id}, leave_type {leave_type}")
                    days_to_deduct_f = 0.0
                self._logger.info(f"Deducting leave: current_balance={current_balance_f} (type {type(current_balance_f)}), days_to_deduct={days_to_deduct_f} (type {type(days_to_deduct_f)})")
                new_balance = current_balance_f - days_to_deduct_f
                if new_balance < 0:
                    new_balance = 0.0
                user.update_leave_balance(leave_type, new_balance)
                await self._user_command_repository.save(user, hostname)
                self._logger.info(f"Deducted {days_to_deduct_f} days from {leave_type} for user {employee_leave.employee_id}. New balance: {new_balance}")
            else:
                self._logger.warning(f"User not found for leave balance deduction: {employee_leave.employee_id}")
        except Exception as e:
            self._logger.error(f"Error deducting leave balance: {e}")
        self._logger.info(f"Approved leave: {employee_leave.leave_id}")
    
    
    async def _reject_leave(
        self, 
        employee_leave: EmployeeLeave, 
        approver_id: str, 
        reason: str,
        hostname: str
    ):
        """Reject the leave application and restore leave balance if previously approved"""
        # If the leave was previously approved, restore the balance
        try:
            if employee_leave.status == LeaveStatus.APPROVED:
                employee_id_obj = EmployeeId(employee_leave.employee_id)
                user = await self._user_query_repository.get_by_id(employee_id_obj, hostname)
                if user:
                    leave_type = employee_leave.leave_name
                    current_balance = user.leave_balance.get(leave_type, 0)
                    days_to_restore = employee_leave.approved_days or employee_leave.applied_days or 0
                    # Ensure both are floats
                    try:
                        current_balance_f = float(current_balance)
                    except Exception:
                        self._logger.error(f"Could not convert current_balance '{current_balance}' to float for user {employee_leave.employee_id}, leave_type {leave_type}")
                        current_balance_f = 0.0
                    try:
                        days_to_restore_f = float(days_to_restore)
                    except Exception:
                        self._logger.error(f"Could not convert days_to_restore '{days_to_restore}' to float for user {employee_leave.employee_id}, leave_type {leave_type}")
                        days_to_restore_f = 0.0
                    self._logger.info(f"Restoring leave: current_balance={current_balance_f} (type {type(current_balance_f)}), days_to_restore={days_to_restore_f} (type {type(days_to_restore_f)})")
                    new_balance = current_balance_f + days_to_restore_f
                    user.update_leave_balance(leave_type, new_balance)
                    await self._user_command_repository.save(user, hostname)
                    self._logger.info(f"Restored {days_to_restore_f} days to {leave_type} for user {employee_leave.employee_id}. New balance: {new_balance}")
                else:
                    self._logger.warning(f"User not found for leave balance restoration: {employee_leave.employee_id}")
        except Exception as e:
            self._logger.error(f"Error restoring leave balance: {e}")
        # Reject the leave (this will update status and raise domain events)
        employee_leave.reject(approver_id, reason)
        self._logger.info(f"Rejected leave: {employee_leave.leave_id}")

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