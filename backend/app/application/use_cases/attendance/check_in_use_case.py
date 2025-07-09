"""
Check-In Use Case
Handles employee check-in operations with business rules and validation
"""

from datetime import datetime, date, time
from typing import Optional, TYPE_CHECKING

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
    AttendanceStatusResponseDTO,
    AttendanceStatusEnum,
    AttendanceMarkingTypeEnum
)
from app.application.interfaces.repositories.attendance_repository import (
    AttendanceCommandRepository,
    AttendanceQueryRepository
)
from app.application.interfaces.repositories.employee_repository import EmployeeQueryRepository
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.utils.logger import get_logger

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

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
        current_user: "CurrentUser"
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
            logger.info(f"Processing check-in for employee: {request.employee_id} in organisation: {current_user.hostname}")
            
            # Step 1: Validate request data
            await self._validate_request(request)
            
            # Step 2: Verify employee exists and is active
            employee = await self._verify_employee(request.employee_id, current_user)
            
            # Step 3: Check business rules
            check_in_time = request.check_in_time or datetime.now()
            attendance_date = check_in_time.date()
            # Convert attendance_date to datetime for repository
            attendance_date_dt = self._date_to_datetime_midnight(attendance_date)
            await self._validate_business_rules(request.employee_id, attendance_date_dt, check_in_time, current_user)
            
            # Step 4: Get or create attendance record
            attendance = await self._get_or_create_attendance(
                request.employee_id,
                attendance_date_dt,
                current_user.employee_id,
                current_user
            )
            
            # Step 5: Perform check-in
            attendance.check_in(
                check_in_time=check_in_time,
                location=request.location,
                marked_by=current_user.employee_id
            )
            
            # Step 6: Save attendance record
            saved_attendance = await self.attendance_command_repository.save(attendance, current_user.hostname)
            
            # Step 7: Publish domain events
            await self._publish_events(saved_attendance)
            
            # Step 8: Send notifications
            await self._send_notifications(saved_attendance, employee)
            
            # Step 9: Return response
            response = self._create_response(saved_attendance)
            
            logger.info(f"Check-in completed successfully for employee: {request.employee_id} in organisation: {current_user.hostname}")
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
    
    async def _verify_employee(self, employee_id: str, current_user: "CurrentUser"):
        """Verify employee exists and is active"""
        employee = await self.employee_repository.get_by_id(employee_id, current_user.hostname)
        
        if not employee:
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} not found in organisation {current_user.hostname}",
                "EMPLOYEE_NOT_FOUND"
            )
        
        # Check if employee is active - handle both dict and object formats
        is_active = True
        if hasattr(employee, 'is_active') and callable(getattr(employee, 'is_active')):
            is_active = employee.is_active()
        elif hasattr(employee, 'is_active'):
            is_active = employee.is_active
        elif isinstance(employee, dict):
            is_active = employee.get("is_active", True)
        
        if not is_active:
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} is not active",
                "EMPLOYEE_INACTIVE"
            )
        
        return employee
    
    async def _validate_business_rules(
        self,
        employee_id: str,
        attendance_date: datetime,  # now datetime
        check_in_time: datetime,
        current_user: "CurrentUser"
    ) -> None:
        """Validate business rules for check-in"""
        
        # Check if employee is already checked in for the date
        existing_attendance = await self.attendance_query_repository.get_by_employee_and_date(
            employee_id, attendance_date, current_user.hostname
        )
        
        if existing_attendance and existing_attendance.working_hours.is_checked_in():
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} is already checked in for {attendance_date.date()}",
                "ALREADY_CHECKED_IN"
            )
        
        # # Check if check-in time is reasonable (not too far in the past)
        # time_diff = datetime.utcnow() - check_in_time
        # if time_diff.total_seconds() > 24 * 60 * 60:  # More than 24 hours ago
        #     raise AttendanceBusinessRuleError(
        #         "Check-in time cannot be more than 24 hours in the past",
        #         "CHECK_IN_TIME_TOO_OLD"
        #     )
    
    async def _get_or_create_attendance(
        self,
        employee_id: str,
        attendance_date: datetime,  # now datetime
        created_by: str,
        current_user: "CurrentUser"
    ) -> Attendance:
        """Get existing attendance record or create new one"""
        
        # Try to get existing attendance record
        attendance = await self.attendance_query_repository.get_by_employee_and_date(
            employee_id, attendance_date, current_user.hostname
        )
        
        if attendance:
            return attendance
        
        # Create new attendance record
        attendance = Attendance.create_new(
            employee_id=EmployeeId(employee_id),
            attendance_date=attendance_date.date() if isinstance(attendance_date, datetime) else attendance_date,
            created_by=created_by
        )
        
        return attendance
    
    async def _publish_events(self, attendance: Attendance) -> None:
        """Publish domain events"""
        try:
            if self.event_publisher:
                # Publish check-in event
                await self.event_publisher.publish({
                    "event_type": "attendance.checked_in",
                    "employee_id": attendance.employee_id.value,
                    "attendance_date": attendance.attendance_date.isoformat(),
                    "check_in_time": attendance.working_hours.check_in_time.isoformat(),
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            logger.warning(f"Failed to publish check-in event: {e}")
    
    async def _send_notifications(self, attendance: Attendance, employee) -> None:
        """Send notifications for check-in"""
        try:
            if self.notification_service:
                # Send notification to manager if late
                if attendance.status.status.value == "late":
                    # Handle both dict and object formats for employee
                    employee_name = "Unknown"
                    manager_id = None
                    
                    if isinstance(employee, dict):
                        employee_name = employee.get("name", "Unknown")
                        manager_id = employee.get("manager_id")
                    else:
                        # Handle object format
                        employee_name = getattr(employee, 'name', "Unknown")
                        manager_id = getattr(employee, 'manager_id', None)
                        if hasattr(manager_id, 'value'):
                            manager_id = manager_id.value
                    
                    await self.notification_service.send_late_arrival_notification(
                        employee_id=attendance.employee_id.value,
                        employee_name=employee_name,
                        check_in_time=attendance.working_hours.check_in_time,
                        manager_id=manager_id
                    )
        except Exception as e:
            logger.warning(f"Failed to send check-in notifications: {e}")
    
    def _create_response(self, attendance: Attendance) -> AttendanceResponseDTO:
        """Create response DTO from attendance entity"""
        
        # Map domain enums to DTO enums
        status_mapping = {
            "present": AttendanceStatusEnum.PRESENT,
            "absent": AttendanceStatusEnum.ABSENT,
            "late": AttendanceStatusEnum.LATE,
            "half_day": AttendanceStatusEnum.HALF_DAY,
            "work_from_home": AttendanceStatusEnum.WORK_FROM_HOME,
            "on_leave": AttendanceStatusEnum.ON_LEAVE,
            "holiday": AttendanceStatusEnum.HOLIDAY,
            "weekend": AttendanceStatusEnum.WEEKEND
        }
        
        marking_type_mapping = {
            "manual": AttendanceMarkingTypeEnum.MANUAL,
            "biometric": AttendanceMarkingTypeEnum.BIOMETRIC,
            "mobile_app": AttendanceMarkingTypeEnum.MOBILE_APP,
            "web_app": AttendanceMarkingTypeEnum.WEB_APP,
            "system_auto": AttendanceMarkingTypeEnum.SYSTEM_AUTO,
            "admin_override": AttendanceMarkingTypeEnum.ADMIN_OVERRIDE
        }
        
        status = AttendanceStatusResponseDTO(
            status=status_mapping.get(attendance.status.status.value, AttendanceStatusEnum.PRESENT),
            marking_type=marking_type_mapping.get(attendance.status.marking_type.value, AttendanceMarkingTypeEnum.WEB_APP),
            is_regularized=attendance.status.is_regularized,
            regularization_reason=attendance.status.regularization_reason
        )
        
        working_hours = WorkingHoursResponseDTO(
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
        
        return AttendanceResponseDTO(
            attendance_id=attendance.attendance_id,
            employee_id=attendance.employee_id.value,
            attendance_date=attendance.attendance_date,
            status=status,
            working_hours=working_hours,
            check_in_location=attendance.check_in_location,
            check_out_location=attendance.check_out_location,
            comments=attendance.comments,
            admin_notes=attendance.admin_notes,
            created_at=attendance.created_at,
            created_by=attendance.created_by,
            updated_at=attendance.updated_at,
            updated_by=attendance.updated_by
        ) 

    # Utility function to convert date to datetime at midnight
    @staticmethod
    def _date_to_datetime_midnight(d: date) -> datetime:
        return datetime.combine(d, time.min) 