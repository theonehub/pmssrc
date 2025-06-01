"""
Check-In Use Case
Handles employee check-in operations with business rules and validation
"""

from datetime import datetime, date
from typing import Optional

from app.domain.entities.attendance import Attendance
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.attendance_status import AttendanceStatus, AttendanceMarkingType
from app.domain.value_objects.working_hours import WorkingHours
from app.application.dto.attendance_dto import (
    AttendanceCheckInRequestDTO,
    AttendanceResponseDTO,
    AttendanceValidationError,
    AttendanceBusinessRuleError,
    WorkingHoursResponseDTO,
    AttendanceStatusResponseDTO
)
from app.application.interfaces.repositories.attendance_repository import (
    AttendanceCommandRepository,
    AttendanceQueryRepository
)
from app.application.interfaces.repositories.employee_repository import EmployeeQueryRepository
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CheckInUseCase:
    """
    Use case for employee check-in operations.
    
    Follows SOLID principles:
    - SRP: Handles only check-in operations
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused repository interfaces
    - DIP: Depends on abstractions not concretions
    
    Business Rules:
    1. Employee must exist and be active
    2. Cannot check in if already checked in for the day
    3. Check-in time cannot be in the future
    4. Check-in time must be on the current date or specified date
    5. Creates attendance record if none exists for the date
    6. Updates existing attendance record if it exists
    """
    
    def __init__(
        self,
        attendance_command_repository: AttendanceCommandRepository,
        attendance_query_repository: AttendanceQueryRepository,
        employee_repository: EmployeeQueryRepository,
        event_publisher: EventPublisher,
        notification_service: Optional[NotificationService] = None
    ):
        self.attendance_command_repository = attendance_command_repository
        self.attendance_query_repository = attendance_query_repository
        self.employee_repository = employee_repository
        self.event_publisher = event_publisher
        self.notification_service = notification_service
    
    async def execute(
        self,
        request: AttendanceCheckInRequestDTO,
        checked_in_by: str
    ) -> AttendanceResponseDTO:
        """
        Execute check-in operation.
        
        Steps:
        1. Validate request data
        2. Verify employee exists and is active
        3. Check business rules
        4. Get or create attendance record
        5. Perform check-in
        6. Save attendance record
        7. Publish domain events
        8. Send notifications
        9. Return response
        """
        try:
            logger.info(f"Processing check-in for employee: {request.employee_id}")
            
            # Step 1: Validate request data
            await self._validate_request(request)
            
            # Step 2: Verify employee exists and is active
            employee = await self._verify_employee(request.employee_id)
            
            # Step 3: Check business rules
            check_in_time = request.check_in_time or datetime.now()
            attendance_date = check_in_time.date()
            
            await self._validate_business_rules(request.employee_id, attendance_date, check_in_time)
            
            # Step 4: Get or create attendance record
            attendance = await self._get_or_create_attendance(
                request.employee_id,
                attendance_date,
                checked_in_by
            )
            
            # Step 5: Perform check-in
            attendance.check_in(
                check_in_time=check_in_time,
                location=request.location,
                marked_by=checked_in_by
            )
            
            # Step 6: Save attendance record
            saved_attendance = await self.attendance_command_repository.save(attendance)
            
            # Step 7: Publish domain events
            await self._publish_events(saved_attendance)
            
            # Step 8: Send notifications
            await self._send_notifications(saved_attendance, employee)
            
            # Step 9: Return response
            response = self._create_response(saved_attendance)
            
            logger.info(f"Check-in completed successfully for employee: {request.employee_id}")
            return response
            
        except AttendanceValidationError:
            raise
        except AttendanceBusinessRuleError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during check-in: {e}")
            raise AttendanceBusinessRuleError(
                f"Failed to process check-in: {str(e)}",
                "CHECK_IN_FAILED"
            )
    
    async def _validate_request(self, request: AttendanceCheckInRequestDTO) -> None:
        """Validate the check-in request"""
        if not request.employee_id or not request.employee_id.strip():
            raise AttendanceValidationError(
                "Employee ID is required",
                "MISSING_EMPLOYEE_ID"
            )
        
        if request.check_in_time and request.check_in_time > datetime.now():
            raise AttendanceValidationError(
                "Check-in time cannot be in the future",
                "INVALID_CHECK_IN_TIME"
            )
    
    async def _verify_employee(self, employee_id: str) -> dict:
        """Verify employee exists and is active"""
        employee = await self.employee_repository.get_by_id(employee_id)
        
        if not employee:
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} not found",
                "EMPLOYEE_NOT_FOUND"
            )
        
        if not employee.get("is_active", True):
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} is not active",
                "EMPLOYEE_INACTIVE"
            )
        
        return employee
    
    async def _validate_business_rules(
        self,
        employee_id: str,
        attendance_date: date,
        check_in_time: datetime
    ) -> None:
        """Validate business rules for check-in"""
        
        # Check if employee is already checked in for the date
        existing_attendance = await self.attendance_query_repository.get_by_employee_and_date(
            employee_id, attendance_date
        )
        
        if existing_attendance and existing_attendance.working_hours.is_checked_in():
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} is already checked in for {attendance_date}",
                "ALREADY_CHECKED_IN"
            )
        
        # Check if check-in time is reasonable (not too far in the past)
        time_diff = datetime.utcnow() - check_in_time
        if time_diff.total_seconds() > 24 * 60 * 60:  # More than 24 hours ago
            raise AttendanceBusinessRuleError(
                "Check-in time cannot be more than 24 hours in the past",
                "CHECK_IN_TIME_TOO_OLD"
            )
    
    async def _get_or_create_attendance(
        self,
        employee_id: str,
        attendance_date: date,
        created_by: str
    ) -> Attendance:
        """Get existing attendance record or create new one"""
        
        # Try to get existing attendance record
        existing_attendance = await self.attendance_query_repository.get_by_employee_and_date(
            employee_id, attendance_date
        )
        
        if existing_attendance:
            return existing_attendance
        
        # Create new attendance record
        employee_id_vo = EmployeeId.from_string(employee_id)
        initial_status = AttendanceStatus.create_absent(AttendanceMarkingType.SYSTEM_AUTO)
        
        attendance = Attendance.create_new(
            employee_id=employee_id_vo,
            attendance_date=attendance_date,
            created_by=created_by,
            initial_status=initial_status
        )
        
        return attendance
    
    async def _publish_events(self, attendance: Attendance) -> None:
        """Publish domain events"""
        try:
            events = attendance.get_domain_events()
            for event in events:
                await self.event_publisher.publish(event)
            
            # Clear events after publishing
            attendance.clear_domain_events()
            
            logger.debug(f"Published {len(events)} domain events for attendance {attendance.attendance_id}")
            
        except Exception as e:
            logger.warning(f"Failed to publish domain events: {e}")
            # Don't fail the operation if event publishing fails
    
    async def _send_notifications(self, attendance: Attendance, employee: dict) -> None:
        """Send notifications for check-in"""
        if not self.notification_service:
            return
        
        try:
            # Send check-in confirmation to employee
            await self.notification_service.send_check_in_notification(
                employee_id=attendance.employee_id.value,
                employee_name=employee.get("name", "Employee"),
                check_in_time=attendance.working_hours.check_in_time,
                location=attendance.check_in_location
            )
            
            # Send notification to manager if late
            if attendance.is_late(employee.get("expected_start_time", "09:00")):
                manager_id = employee.get("manager_id")
                if manager_id:
                    await self.notification_service.send_late_arrival_notification(
                        manager_id=manager_id,
                        employee_id=attendance.employee_id.value,
                        employee_name=employee.get("name", "Employee"),
                        check_in_time=attendance.working_hours.check_in_time,
                        expected_time=employee.get("expected_start_time", "09:00")
                    )
            
            logger.debug(f"Sent check-in notifications for employee {attendance.employee_id.value}")
            
        except Exception as e:
            logger.warning(f"Failed to send notifications: {e}")
            # Don't fail the operation if notifications fail
    
    def _create_response(self, attendance: Attendance) -> AttendanceResponseDTO:
        """Create response DTO from attendance entity"""
        
        # Create working hours response
        working_hours_response = WorkingHoursResponseDTO(
            check_in_time=attendance.working_hours.check_in_time,
            check_out_time=attendance.working_hours.check_out_time,
            total_hours=float(attendance.working_hours.working_hours()),
            break_hours=float(attendance.working_hours.break_time_minutes() / 60),
            overtime_hours=float(attendance.working_hours.overtime_hours()),
            shortage_hours=float(attendance.working_hours.shortage_hours()),
            expected_hours=float(attendance.working_hours.expected_hours),
            is_complete_day=attendance.working_hours.is_complete_day(),
            is_full_day=attendance.working_hours.is_full_day(),
            is_half_day=attendance.working_hours.is_half_day()
        )
        
        # Create status response
        status_response = AttendanceStatusResponseDTO(
            status=attendance.status.status.value,
            marking_type=attendance.status.marking_type.value,
            is_regularized=attendance.status.is_regularized,
            regularization_reason=attendance.status.regularization_reason
        )
        
        # Create main response
        return AttendanceResponseDTO(
            attendance_id=attendance.attendance_id,
            employee_id=attendance.employee_id.value,
            attendance_date=attendance.attendance_date,
            status=status_response,
            working_hours=working_hours_response,
            check_in_location=attendance.check_in_location,
            check_out_location=attendance.check_out_location,
            comments=attendance.comments,
            admin_notes=attendance.admin_notes,
            created_at=attendance.created_at,
            created_by=attendance.created_by,
            updated_at=attendance.updated_at,
            updated_by=attendance.updated_by
        ) 