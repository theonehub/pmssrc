"""
Apply Employee Leave Use Case
Business workflow for employee leave application
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import uuid4

from app.application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveCommandRepository, EmployeeLeaveQueryRepository
)
from app.application.interfaces.repositories.company_leave_repository import CompanyLeaveQueryRepository
from app.application.interfaces.services.notification_service import NotificationService
from app.application.dto.employee_leave_dto import (
    ApplyEmployeeLeaveRequestDTO, EmployeeLeaveResponseDTO
)
from app.domain.entities.employee_leave import EmployeeLeave
from app.domain.entities.user import User


logger = logging.getLogger(__name__)


class ApplyEmployeeLeaveUseCase:
    """
    Use case for applying employee leave.
    
    Follows SOLID principles:
    - SRP: Only handles employee leave application workflow
    - OCP: Can be extended with new leave types without modification
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        leave_command_repository: EmployeeLeaveCommandRepository,
        leave_query_repository: EmployeeLeaveQueryRepository,
        company_leave_repository: CompanyLeaveQueryRepository,
        notification_service: NotificationService
    ):
        self._leave_command_repository = leave_command_repository
        self._leave_query_repository = leave_query_repository
        self._company_leave_repository = company_leave_repository
        self._notification_service = notification_service
        self._logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        request: ApplyEmployeeLeaveRequestDTO,
        current_user: User,
        organisation_id: Optional[str] = None
    ) -> EmployeeLeaveResponseDTO:
        """
        Execute employee leave application.
        
        Args:
            request: Leave application request data
            current_user: Current user applying for leave
            organisation_id: Organisation ID for leave policies
            
        Returns:
            EmployeeLeaveResponseDTO with application details
            
        Raises:
            ValueError: If validation fails
            Exception: If application fails
        """
        
        try:
            self._logger.info(f"Processing leave application for employee {current_user.employee_id}")
            
            # Validate request
            await self._validate_leave_request(request, current_user, organisation_id)
            
            # Create employee leave entity
            employee_leave = EmployeeLeave.create(
                employee_id=current_user.employee_id,
                organisation_id=organisation_id or current_user.hostname,
                leave_name=request.leave_name,
                start_date=request.start_date,
                end_date=request.end_date,
                reason=request.reason,
                is_half_day=request.is_half_day,
                is_compensatory=request.is_compensatory,
                compensatory_work_date=request.compensatory_work_date,
                created_by=current_user.employee_id
            )
            
            # Save the leave application
            saved_leave = await self._leave_command_repository.save(employee_leave, organisation_id)
            
            # Send notifications
            await self._send_application_notifications(saved_leave, current_user)
            
            # Create response
            response = EmployeeLeaveResponseDTO.from_entity(saved_leave)
            
            self._logger.info(f"Leave application submitted successfully: {saved_leave.leave_id}")
            return response
            
        except Exception as e:
            self._logger.error(f"Failed to apply employee leave: {str(e)}")
            raise Exception(f"Leave application failed: {str(e)}")
    
    async def _validate_leave_request(
        self,
        request: ApplyEmployeeLeaveRequestDTO,
        current_user: User,
        organisation_id: Optional[str] = None
    ) -> None:
        """
        Validate the leave application request.
        
        Args:
            request: Leave application request
            current_user: Current user
            organisation_id: Organisation ID
            
        Raises:
            ValueError: If validation fails
        """
        
        # Basic validation
        errors = request.validate()
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")
        
        # Check if leave type exists and is active
        company_leave = await self._company_leave_repository.get_by_leave_name(
            request.leave_name, 
            organisation_id
        )
        
        if not company_leave:
            raise ValueError(f"Leave type '{request.leave_name}' not found")
        
        if not company_leave.is_active:
            raise ValueError(f"Leave type '{request.leave_name}' is not active")
        
        # Check date validation
        if request.start_date > request.end_date:
            raise ValueError("Start date cannot be after end date")
        
        if request.start_date < date.today():
            raise ValueError("Cannot apply for past dates")
        
        # Check for overlapping leaves
        await self._check_overlapping_leaves(request, current_user.employee_id, organisation_id)
        
        # Check leave balance (simplified - in real implementation would check balances)
        await self._check_leave_balance(request, current_user, organisation_id)
        
        # Check business rules
        await self._validate_business_rules(request, current_user, company_leave, organisation_id)
    
    async def _check_overlapping_leaves(
        self,
        request: ApplyEmployeeLeaveRequestDTO,
        employee_id: str,
        organisation_id: Optional[str] = None
    ) -> None:
        """
        Check for overlapping leave applications.
        
        Args:
            request: Leave request
            employee_id: Employee ID
            organisation_id: Organisation ID
            
        Raises:
            ValueError: If overlapping leaves found
        """
        
        try:
            # Get leaves in the date range
            overlapping_leaves = await self._leave_query_repository.get_by_date_range(
                request.start_date,
                request.end_date,
                organisation_id
            )
            
            # Filter for same employee and active status
            employee_overlaps = [
                leave for leave in overlapping_leaves
                if leave.employee_id == employee_id and leave.status in ["pending", "approved"]
            ]
            
            if employee_overlaps:
                raise ValueError("You already have leave applications for overlapping dates")
                
        except Exception as e:
            if "overlapping dates" in str(e):
                raise
            self._logger.warning(f"Could not check overlapping leaves: {e}")
            # Continue processing - don't fail application due to check failure
    
    async def _check_leave_balance(
        self,
        request: ApplyEmployeeLeaveRequestDTO,
        current_user: User,
        organisation_id: Optional[str] = None
    ) -> None:
        """
        Check if employee has sufficient leave balance.
        
        Args:
            request: Leave request
            current_user: Current user
            organisation_id: Organisation ID
            
        Raises:
            ValueError: If insufficient balance
        """
        
        try:
            # Get user's leave balance
            leave_balance = current_user.leave_balance.get(request.leave_name, 0)
            
            # Calculate requested days
            requested_days = (request.end_date - request.start_date).days + 1
            if request.is_half_day:
                requested_days = 0.5
            
            if leave_balance < requested_days:
                raise ValueError(f"Insufficient {request.leave_name} balance. Available: {leave_balance}, Requested: {requested_days}")
                
        except Exception as e:
            if "Insufficient" in str(e):
                raise
            self._logger.warning(f"Could not check leave balance: {e}")
            # Continue processing - don't fail application due to check failure
    
    async def _validate_business_rules(
        self,
        request: ApplyEmployeeLeaveRequestDTO,
        current_user: User,
        company_leave: Any,
        organisation_id: Optional[str] = None
    ) -> None:
        """
        Validate business rules for leave application.
        
        Args:
            request: Leave request
            current_user: Current user
            company_leave: Company leave policy
            organisation_id: Organisation ID
            
        Raises:
            ValueError: If business rules violated
        """
        
        # Check probation restrictions
        if hasattr(company_leave, 'policy') and hasattr(company_leave.policy, 'available_during_probation'):
            if not company_leave.policy.available_during_probation and current_user.is_on_probation():
                raise ValueError(f"{request.leave_name} is not allowed during probation period")
        
        # Check minimum notice period
        if hasattr(company_leave, 'policy') and hasattr(company_leave.policy, 'minimum_notice_days'):
            notice_days = (request.start_date - date.today()).days
            if notice_days < company_leave.policy.minimum_notice_days:
                raise ValueError(f"Minimum {company_leave.policy.minimum_notice_days} days notice required for {request.leave_name}")
        
        # Check maximum days per application
        if hasattr(company_leave, 'policy') and hasattr(company_leave.policy, 'max_days_per_application'):
            requested_days = (request.end_date - request.start_date).days + 1
            if requested_days > company_leave.policy.max_days_per_application:
                raise ValueError(f"Maximum {company_leave.policy.max_days_per_application} days allowed per {request.leave_name} application")
        
        # Compensatory leave validation
        if request.is_compensatory:
            if not request.compensatory_work_date:
                raise ValueError("Compensatory work date is required for compensatory leave")
            
            if request.compensatory_work_date >= request.start_date:
                raise ValueError("Compensatory work date must be before the leave start date")
    
    async def _send_application_notifications(
        self,
        employee_leave: EmployeeLeave,
        current_user: User
    ) -> None:
        """
        Send notifications for leave application.
        
        Args:
            employee_leave: Applied leave
            current_user: Current user
        """
        
        try:
            # Notification to employee
            await self._notification_service.send_notification(
                recipient_id=current_user.employee_id,
                subject="Leave Application Submitted",
                message=f"Your {employee_leave.leave_name} application from {employee_leave.start_date} to {employee_leave.end_date} has been submitted successfully.",
                notification_type="leave_application"
            )
            
            # Notification to manager (if configured)
            if hasattr(current_user, 'manager_id') and current_user.manager_id:
                await self._notification_service.send_notification(
                    recipient_id=current_user.manager_id,
                    subject="Leave Application Pending Approval",
                    message=f"{current_user.name} has applied for {employee_leave.leave_name} from {employee_leave.start_date} to {employee_leave.end_date}. Please review and approve.",
                    notification_type="leave_approval_pending"
                )
            
            self._logger.info(f"Leave application notifications sent for: {employee_leave.leave_id}")
            
        except Exception as e:
            self._logger.warning(f"Failed to send leave application notifications: {e}")
            # Don't fail the application due to notification failure


class ApplyEmployeeLeaveUseCaseError(Exception):
    """Base exception for apply employee leave use case"""
    pass


class InvalidLeaveRequestError(ApplyEmployeeLeaveUseCaseError):
    """Exception raised when leave request is invalid"""
    
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field} '{value}': {reason}")


class InsufficientLeaveBalanceError(ApplyEmployeeLeaveUseCaseError):
    """Exception raised when employee has insufficient leave balance"""
    
    def __init__(self, leave_name: str, available: float, requested: float):
        self.leave_name = leave_name
        self.available = available
        self.requested = requested
        super().__init__(f"Insufficient {leave_name} balance. Available: {available}, Requested: {requested}")


class OverlappingLeaveError(ApplyEmployeeLeaveUseCaseError):
    """Exception raised when leave dates overlap with existing applications"""
    
    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(f"Leave dates {start_date} to {end_date} overlap with existing applications") 