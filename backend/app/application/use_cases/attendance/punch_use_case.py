"""
Punch Use Case
Handles combined check-in and check-out operations for attendance devices.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from app.domain.entities.attendance import Attendance
from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.attendance_dto import (
    AttendanceResponseDTO,
    AttendanceValidationError,
    AttendanceBusinessRuleError
)
from app.application.interfaces.repositories.attendance_repository import (
    AttendanceCommandRepository,
    AttendanceQueryRepository
)
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.application.use_cases.attendance.check_in_use_case import CheckInUseCase
from app.application.use_cases.attendance.check_out_use_case import CheckOutUseCase
from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = get_logger(__name__)


class PunchUseCase:
    """
    Use case for handling a single punch event, which can be a check-in or check-out.
    """
    
    def __init__(
        self,
        attendance_command_repository: AttendanceCommandRepository,
        attendance_query_repository: AttendanceQueryRepository,
        employee_repository: UserQueryRepository,
        check_in_use_case: CheckInUseCase,
        check_out_use_case: CheckOutUseCase
    ):
        self.attendance_command_repository = attendance_command_repository
        self.attendance_query_repository = attendance_query_repository
        self.employee_repository = employee_repository
        self.check_in_use_case = check_in_use_case
        self.check_out_use_case = check_out_use_case

    async def execute(
        self,
        employee_id: str,
        current_user: "CurrentUser"  # Organisation context is always provided via current_user
    ) -> AttendanceResponseDTO:
        """
        Execute the punch operation (organisation context from current_user).
        
        If no attendance record exists for the day, it's a check-in.
        If a record exists, it's a check-out.
        """
        logger.info(f"Processing punch for employee: {employee_id}")
        
        punch_time = datetime.now()
        attendance_date = punch_time.date()
        
        existing_attendance = await self.attendance_query_repository.get_by_employee_and_date(
            employee_id, attendance_date, current_user.hostname
        )
        
        if not existing_attendance:
            # This is a Check-in
            logger.info(f"No existing attendance found for {employee_id} on {attendance_date}. Treating as check-in.")
            from app.application.dto.attendance_dto import AttendanceCheckInRequestDTO
            check_in_request = AttendanceCheckInRequestDTO(
                employee_id=employee_id,
                check_in_time=punch_time
            )
            return await self.check_in_use_case.execute(check_in_request, current_user)
        else:
            # This is a Check-out
            logger.info(f"Existing attendance found for {employee_id} on {attendance_date}. Treating as check-out.")
            from app.application.dto.attendance_dto import AttendanceCheckOutRequestDTO
            check_out_request = AttendanceCheckOutRequestDTO(
                employee_id=employee_id,
                check_out_time=punch_time
            )
            return await self.check_out_use_case.execute(check_out_request, current_user)
