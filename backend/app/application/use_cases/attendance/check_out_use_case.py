"""
Check-Out Use Case
Handles employee check-out operations with business rules and validation
"""

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from decimal import Decimal

from app.domain.entities.attendance import Attendance
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.attendance_status import AttendanceStatus, AttendanceMarkingType
from app.domain.value_objects.working_hours import WorkingHours
from app.application.dto.attendance_dto import (
    AttendanceCheckOutRequestDTO,
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

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = get_logger(__name__)


class CheckOutUseCase:
    """
    Use case for employee check-out operations.
    
    Follows SOLID principles:
    - SRP: Handles only check-out operations
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused repository interfaces
    - DIP: Depends on abstractions not concretions
    
    Business Rules:
    1. Employee must exist and be active
    2. Must be checked in before checking out
    3. Check-out time cannot be in the future
    4. Check-out time must be after check-in time
    5. Check-out time must be on the same date as attendance date
    6. Updates existing attendance record
    7. Calculates working hours and overtime
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
        request: AttendanceCheckOutRequestDTO,
        current_user: "CurrentUser"
    ) -> AttendanceResponseDTO:
        """
        Execute check-out operation.
        
        Steps:
        1. Validate request data
        2. Verify employee exists and is active
        3. Get existing attendance record
        4. Check business rules
        5. Perform check-out
        6. Save attendance record
        7. Publish domain events
        8. Send notifications
        9. Return response
        """
        try:
            logger.info(f"Processing check-out for employee: {request.employee_id} in organisation: {current_user.hostname}")
            
            # Step 1: Validate request data
            await self._validate_request(request)
            
            # Step 2: Verify employee exists and is active
            employee = await self._verify_employee(request.employee_id, current_user)
            
            # Step 3: Get existing attendance record
            check_out_time = request.check_out_time or datetime.now()
            attendance_date = check_out_time.date()
            
            attendance = await self._get_attendance_record(request.employee_id, attendance_date, current_user)
            
            # Step 4: Check business rules
            await self._validate_business_rules(attendance, check_out_time)
            
            # Step 5: Perform check-out
            attendance.check_out(
                check_out_time=check_out_time,
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
            
            logger.info(f"Check-out completed successfully for employee: {request.employee_id} in organisation: {current_user.hostname}")
            return response
            
        except AttendanceValidationError:
            raise
        except AttendanceBusinessRuleError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during check-out: {e}")
            raise AttendanceBusinessRuleError(
                f"Failed to process check-out: {str(e)}",
                "CHECK_OUT_FAILED"
            )
    
    async def _validate_request(self, request: AttendanceCheckOutRequestDTO) -> None:
        """Validate the check-out request"""
        if not request.employee_id or not request.employee_id.strip():
            raise AttendanceValidationError(
                "Employee ID is required",
                "MISSING_EMPLOYEE_ID"
            )
        
        if request.check_out_time and request.check_out_time > datetime.now():
            raise AttendanceValidationError(
                "Check-out time cannot be in the future",
                "INVALID_CHECK_OUT_TIME"
            )
    
    async def _verify_employee(self, employee_id: str, current_user: "CurrentUser") -> dict:
        """Verify employee exists and is active"""
        employee = await self.employee_repository.get_by_id(employee_id, current_user.hostname)
        
        if not employee:
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} not found in organisation {current_user.hostname}",
                "EMPLOYEE_NOT_FOUND"
            )
        
        if hasattr(employee, 'is_active') and not employee.is_active:
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} is not active",
                "EMPLOYEE_INACTIVE"
            )
        elif isinstance(employee, dict) and not employee.get("is_active", True):
            raise AttendanceBusinessRuleError(
                f"Employee {employee_id} is not active",
                "EMPLOYEE_INACTIVE"
            )
        
        return employee
    
    async def _get_attendance_record(
        self,
        employee_id: str,
        attendance_date: date,
        current_user: "CurrentUser"
    ) -> Attendance:
        """Get existing attendance record"""
        attendance = await self.attendance_query_repository.get_by_employee_and_date(
            employee_id, attendance_date, current_user.hostname
        )
        
        if not attendance:
            raise AttendanceBusinessRuleError(
                f"No attendance record found for employee {employee_id} on {attendance_date}",
                "ATTENDANCE_NOT_FOUND"
            )
        
        return attendance
    
    async def _validate_business_rules(
        self,
        attendance: Attendance,
        check_out_time: datetime
    ) -> None:
        """Validate business rules for check-out"""
        
        # Check if employee is checked in
        if not attendance.working_hours.is_checked_in():
            raise AttendanceBusinessRuleError(
                f"Employee {attendance.employee_id.value} is not checked in",
                "NOT_CHECKED_IN"
            )
        
        # Check if already checked out
        if attendance.working_hours.is_checked_out():
            raise AttendanceBusinessRuleError(
                f"Employee {attendance.employee_id.value} is already checked out",
                "ALREADY_CHECKED_OUT"
            )
        
        # Check if check-out time is after check-in time
        if check_out_time <= attendance.working_hours.check_in_time:
            raise AttendanceBusinessRuleError(
                "Check-out time must be after check-in time",
                "INVALID_CHECK_OUT_TIME"
            )
        
        # Check if check-out time is on the same date
        if check_out_time.date() != attendance.attendance_date:
            raise AttendanceBusinessRuleError(
                "Check-out time must be on the same date as attendance date",
                "INVALID_CHECK_OUT_DATE"
            )
        
        # Check if check-out time is reasonable (not too far in the future)
        # Allow for timezone differences and clock skew
        time_diff = check_out_time - datetime.utcnow()
        if time_diff.total_seconds() > 6 * 60 * 60:  # More than 6 hours in the future
            raise AttendanceBusinessRuleError(
                "Check-out time cannot be more than 6 hours in the future",
                "CHECK_OUT_TIME_TOO_FUTURE"
            )
    
    async def _publish_events(self, attendance: Attendance) -> None:
        """Publish domain events"""
        try:
            if self.event_publisher:
                # Publish check-out event
                await self.event_publisher.publish({
                    "event_type": "attendance.checked_out",
                    "employee_id": attendance.employee_id.value,
                    "attendance_date": attendance.attendance_date.isoformat(),
                    "check_out_time": attendance.working_hours.check_out_time.isoformat(),
                    "total_hours": float(attendance.working_hours.working_hours()),
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            logger.warning(f"Failed to publish check-out event: {e}")
    
    async def _send_notifications(self, attendance: Attendance, employee: dict) -> None:
        """Send notifications for check-out"""
        try:
            if self.notification_service:
                # Send notification for overtime if applicable
                if attendance.working_hours.overtime_hours > 0:
                    employee_name = getattr(employee, 'name', None) or (employee.get("name", "Unknown") if isinstance(employee, dict) else "Unknown")
                    manager_id = getattr(employee, 'manager_id', None) or (employee.get("manager_id") if isinstance(employee, dict) else None)
                    
                    await self.notification_service.send_overtime_notification(
                        employee_id=attendance.employee_id.value,
                        employee_name=employee_name,
                        overtime_hours=attendance.working_hours.overtime_hours,
                        manager_id=manager_id
                    )
        except Exception as e:
            logger.warning(f"Failed to send check-out notifications: {e}")
    
    def _create_response(self, attendance: Attendance) -> AttendanceResponseDTO:
        """Create response DTO from attendance entity"""
        from app.application.dto.attendance_dto import (
            AttendanceStatusEnum,
            AttendanceMarkingTypeEnum
        )
        
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
            break_hours=float(Decimal(attendance.working_hours.break_time_minutes()) / Decimal(60)),
            overtime_hours=float(attendance.working_hours.overtime_hours()),
            shortage_hours=float(attendance.working_hours.shortage_hours()),
            expected_hours=attendance.working_hours.expected_hours,
            is_complete_day=attendance.working_hours.is_complete_day,
            is_full_day=attendance.working_hours.is_full_day,
            is_half_day=attendance.working_hours.is_half_day
        )
        
        return AttendanceResponseDTO(
            attendance_id=attendance.attendance_id.value,
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