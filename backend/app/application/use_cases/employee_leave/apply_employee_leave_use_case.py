"""
Apply Employee Leave Use Case
Business workflow for applying employee leave requests
"""

import logging
from typing import Optional
from datetime import datetime, date

from app.application.dto.employee_leave_dto import (
    EmployeeLeaveCreateRequestDTO, 
    EmployeeLeaveResponseDTO,
    EmployeeLeaveValidationError,
    EmployeeLeaveBusinessRuleError,
    InsufficientLeaveBalanceError
)
from app.application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveCommandRepository,
    EmployeeLeaveQueryRepository,
    EmployeeLeaveBalanceRepository
)
from app.application.interfaces.repositories.company_leave_repository import CompanyLeaveQueryRepository
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.email_service import EmailService
from app.domain.entities.employee_leave import EmployeeLeave
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.leave_type import LeaveType, LeaveCategory
from app.domain.value_objects.date_range import DateRange
from app.infrastructure.services.legacy_migration_service import (
    get_user_by_employee_id, is_public_holiday_sync
)


class ApplyEmployeeLeaveUseCase:
    """
    Use case for applying employee leave requests.
    
    Follows SOLID principles:
    - SRP: Only handles employee leave application workflow
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        command_repository: EmployeeLeaveCommandRepository,
        query_repository: EmployeeLeaveQueryRepository,
        balance_repository: EmployeeLeaveBalanceRepository,
        company_leave_repository: CompanyLeaveQueryRepository,
        event_publisher: EventPublisher,
        email_service: Optional[EmailService] = None
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._balance_repository = balance_repository
        self._company_leave_repository = company_leave_repository
        self._event_publisher = event_publisher
        self._email_service = email_service
        self._logger = logging.getLogger(__name__)
    
    async def execute(
        self, 
        request: EmployeeLeaveCreateRequestDTO, 
        employee_id: str,
        hostname: str
    ) -> EmployeeLeaveResponseDTO:
        """
        Execute employee leave application workflow.
        
        Business Rules:
        1. Employee must exist and be active
        2. Leave type must be valid and available
        3. Employee must have sufficient leave balance
        4. No overlapping leave applications
        5. Working days calculation excludes weekends and holidays
        6. Events must be published for downstream processing
        
        Args:
            request: Employee leave application request
            employee_id: Employee applying for leave
            hostname: Organisation hostname
            
        Returns:
            EmployeeLeaveResponseDTO with created leave details
            
        Raises:
            EmployeeLeaveValidationError: If request data is invalid
            EmployeeLeaveBusinessRuleError: If business rules are violated
            InsufficientLeaveBalanceError: If insufficient leave balance
            Exception: If application fails
        """
        
        try:
            # Step 1: Validate request data
            self._logger.info(f"Applying leave for employee {employee_id}: {request.leave_type}")
            validation_errors = request.validate()
            if validation_errors:
                raise EmployeeLeaveValidationError(validation_errors)
            
            # Step 2: Validate employee and get details
            employee_details = await self._validate_employee(employee_id, hostname)
            
            # Step 3: Validate leave type and get company leave policy
            company_leave = await self._validate_leave_type(request.leave_type, hostname)
            
            # Step 4: Create domain objects
            employee_id = EmployeeId(employee_id)
            leave_type = LeaveType(
                code=request.leave_type,
                name=company_leave.leave_type.name if company_leave else request.leave_type,
                category=company_leave.leave_type.category if company_leave else LeaveCategory.GENERAL,
                description=f"{request.leave_type} leave"
            )
            
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            # Step 5: Calculate working days
            working_days = self._calculate_working_days(
                request.start_date, request.end_date, hostname
            )
            
            # Step 6: Validate business rules
            await self._validate_business_rules(
                employee_id, leave_type, date_range, working_days, hostname
            )
            
            # Step 7: Check leave balance
            await self._validate_leave_balance(employee_id, request.leave_type, working_days)
            
            # Step 8: Create employee leave entity
            employee_leave = EmployeeLeave.create_new_leave_application(
                employee_id=employee_id,
                leave_type=leave_type,
                date_range=date_range,
                working_days_count=working_days,
                reason=request.reason,
                employee_name=employee_details.get("name"),
                employee_email=employee_details.get("email")
            )
            
            # Step 9: Persist to database
            success = self._command_repository.save(employee_leave)
            if not success:
                raise Exception("Failed to save employee leave application")
            
            # Step 10: Publish domain events
            await self._publish_domain_events(employee_leave)
            
            # Step 11: Send notifications (if email service available)
            if self._email_service:
                await self._send_application_notifications(employee_leave, employee_details)
            
            # Step 12: Return response
            response = EmployeeLeaveResponseDTO.from_entity(employee_leave)
            self._logger.info(f"Successfully applied leave: {employee_leave.leave_id}")
            
            return response
            
        except EmployeeLeaveValidationError:
            self._logger.warning(f"Validation failed for leave application: {employee_id}")
            raise
        except EmployeeLeaveBusinessRuleError:
            self._logger.warning(f"Business rule violation in leave application: {employee_id}")
            raise
        except InsufficientLeaveBalanceError:
            self._logger.warning(f"Insufficient leave balance for: {employee_id}")
            raise
        except Exception as e:
            self._logger.error(f"Failed to apply leave for {employee_id}: {str(e)}")
            raise Exception(f"Leave application failed: {str(e)}")
    
    async def _validate_employee(self, employee_id: str, hostname: str) -> dict:
        """Validate employee exists and is active"""
        
        employee = await get_user_by_employee_id(employee_id, hostname)
        if not employee:
            raise EmployeeLeaveBusinessRuleError(f"Employee not found: {employee_id}")
        
        if not employee.get("is_active", False):
            raise EmployeeLeaveBusinessRuleError(f"Employee is not active: {employee_id}")
        
        return employee
    
    async def _validate_leave_type(self, leave_type: str, hostname: str):
        """Validate leave type exists and is available"""
        
        company_leave = self._company_leave_repository.get_by_leave_type_code(leave_type)
        if not company_leave:
            self._logger.warning(f"Company leave policy not found for type: {leave_type}")
            # Allow application but log warning - some organisations might not have formal policies
            return None
        
        if not company_leave.is_active:
            raise EmployeeLeaveBusinessRuleError(f"Leave type is not active: {leave_type}")
        
        return company_leave
    
    def _calculate_working_days(self, start_date: str, end_date: str, hostname: str) -> int:
        """Calculate working days excluding weekends and public holidays"""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        working_days = 0
        current_date = start
        
        while current_date <= end:
            # Check if the current day is not a weekend and not a public holiday
            if not self._is_weekend(current_date) and not is_public_holiday_sync(
                current_date.strftime("%Y-%m-%d"), hostname
            ):
                working_days += 1
            
            current_date += datetime.timedelta(days=1)
        
        return working_days
    
    def _is_weekend(self, date_obj: datetime) -> bool:
        """Check if a date is a weekend (Saturday or Sunday)"""
        return date_obj.weekday() >= 5  # 5 is Saturday, 6 is Sunday
    
    async def _validate_business_rules(
        self, 
        employee_id: EmployeeId, 
        leave_type: LeaveType, 
        date_range: DateRange, 
        working_days: int,
        hostname: str
    ):
        """Validate business rules for leave application"""
        
        # Check if start date is in the future (allow same day applications)
        if date_range.start_date < date.today():
            raise EmployeeLeaveBusinessRuleError("Cannot apply for leave in the past")
        
        # Check for overlapping leave applications
        overlapping_leaves = self._query_repository.get_overlapping_leaves(
            employee_id, date_range
        )
        
        if overlapping_leaves:
            overlapping_leave = overlapping_leaves[0]
            raise EmployeeLeaveBusinessRuleError(
                f"Leave application overlaps with existing leave: {overlapping_leave.leave_id}"
            )
        
        # Validate minimum working days
        if working_days <= 0:
            raise EmployeeLeaveBusinessRuleError("Leave application must include at least one working day")
        
        # Validate maximum continuous days (if company policy exists)
        # This would be implemented based on company leave policy
        
        # Additional business rules can be added here
    
    async def _validate_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_type: str, 
        required_days: int
    ):
        """Validate employee has sufficient leave balance"""
        
        leave_balances = self._balance_repository.get_leave_balance(employee_id)
        available_balance = leave_balances.get(leave_type, 0)
        
        if available_balance < required_days:
            raise InsufficientLeaveBalanceError(
                leave_type=leave_type,
                required=required_days,
                available=available_balance
            )
    
    async def _publish_domain_events(self, employee_leave: EmployeeLeave):
        """Publish domain events for the leave application"""
        
        try:
            events = employee_leave.get_domain_events()
            for event in events:
                await self._event_publisher.publish(event)
            
            employee_leave.clear_domain_events()
            self._logger.info(f"Published {len(events)} domain events for leave: {employee_leave.leave_id}")
            
        except Exception as e:
            self._logger.error(f"Failed to publish domain events: {str(e)}")
            # Don't fail the entire operation for event publishing failures
    
    async def _send_application_notifications(
        self, 
        employee_leave: EmployeeLeave, 
        employee_details: dict
    ):
        """Send email notifications for leave application"""
        
        try:
            if self._email_service:
                # Send confirmation to employee
                await self._email_service.send_leave_application_confirmation(
                    employee_email=employee_details.get("email"),
                    employee_name=employee_details.get("name"),
                    leave_type=employee_leave.leave_type.name,
                    start_date=employee_leave.date_range.start_date,
                    end_date=employee_leave.date_range.end_date,
                    working_days=employee_leave.working_days_count
                )
                
                # Send notification to manager (if manager exists)
                manager_id = employee_details.get("manager_id")
                if manager_id:
                    await self._email_service.send_leave_approval_request(
                        manager_id=manager_id,
                        employee_name=employee_details.get("name"),
                        leave_type=employee_leave.leave_type.name,
                        start_date=employee_leave.date_range.start_date,
                        end_date=employee_leave.date_range.end_date,
                        working_days=employee_leave.working_days_count,
                        reason=employee_leave.reason
                    )
                
                self._logger.info(f"Sent application notifications for leave: {employee_leave.leave_id}")
                
        except Exception as e:
            self._logger.error(f"Failed to send application notifications: {str(e)}")
            # Don't fail the entire operation for notification failures 