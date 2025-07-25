"""
Attendance Query Use Case
Handles attendance query operations with proper filtering and pagination
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, TYPE_CHECKING

from app.domain.entities.attendance import Attendance
from app.application.dto.attendance_dto import (
    AttendanceSearchFiltersDTO,
    AttendanceResponseDTO,
    AttendanceNotFoundError,
    AttendanceValidationError,
    WorkingHoursResponseDTO,
    AttendanceStatusResponseDTO,
    AttendanceStatusEnum,
    AttendanceMarkingTypeEnum
)
from app.application.interfaces.repositories.attendance_repository import AttendanceQueryRepository
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.utils.logger import get_logger

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = get_logger(__name__)


class AttendanceQueryUseCase:
    """
    Use case for attendance query operations.
    
    Follows SOLID principles:
    - SRP: Handles only query operations
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused repository interfaces
    - DIP: Depends on abstractions not concretions
    """
    
    def __init__(
        self,
        attendance_query_repository: AttendanceQueryRepository,
        employee_repository: UserQueryRepository
    ):
        self.attendance_query_repository = attendance_query_repository
        self.employee_repository = employee_repository
    
    async def get_employee_attendance_by_month(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"  # Organisation context is always provided via current_user
    ) -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific month (organisation context from current_user)"""
        try:
            logger.info(f"Getting employee attendance for {filters.employee_id} for {filters.month}/{filters.year} in organisation {current_user.hostname}")
            
            # Validate filters
            self._validate_month_filters(filters)
            
            # Get attendance records
            attendances = await self.attendance_query_repository.get_by_employee_and_month(
                employee_id=filters.employee_id,
                month=filters.month,
                year=filters.year,
                hostname=current_user.hostname
            )
            
            # Convert to response DTOs
            response_dtos = [self._create_response_dto(attendance) for attendance in attendances]
            
            logger.info(f"Found {len(response_dtos)} attendance records for employee {filters.employee_id}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error getting employee attendance by month: {e}")
            raise AttendanceNotFoundError(f"Failed to get attendance records: {str(e)}")
    
    async def get_employee_attendance_by_year(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"
    ) -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific year"""
        try:
            logger.info(f"Getting employee attendance for {filters.employee_id} for year {filters.year} in organisation {current_user.hostname}")
            
            # Validate filters
            self._validate_year_filters(filters)
            
            # Get attendance records
            attendances = await self.attendance_query_repository.get_by_employee_and_year(
                employee_id=filters.employee_id,
                year=filters.year,
                hostname=current_user.hostname
            )
            
            # Convert to response DTOs
            response_dtos = [self._create_response_dto(attendance) for attendance in attendances]
            
            logger.info(f"Found {len(response_dtos)} attendance records for employee {filters.employee_id}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error getting employee attendance by year: {e}")
            raise AttendanceNotFoundError(f"Failed to get attendance records: {str(e)}")
    
    async def get_team_attendance_by_date(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"  # Organisation context is always provided via current_user
    ) -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific date (organisation context from current_user)"""
        try:
            logger.info(f"Getting team attendance for {filters.date}/{filters.month}/{filters.year} in organisation {current_user.hostname}")
            
            # Validate filters
            self._validate_date_filters(filters)
            
            # Get team members
            team_members = await self._get_team_members(filters.manager_id, current_user)
            
            # Get attendance records for all team members
            attendances = []
            for member in team_members:
                member_attendance = await self.attendance_query_repository.get_by_employee_and_date(
                    employee_id=member.employee_id,
                    attendance_date=date(filters.year, filters.month, filters.date),
                    hostname=current_user.hostname
                )
                if member_attendance:
                    attendances.append(member_attendance)
            
            # Convert to response DTOs
            response_dtos = [self._create_response_dto(attendance) for attendance in attendances]
            
            logger.info(f"Found {len(response_dtos)} team attendance records")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error getting team attendance by date: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_team_attendance_by_month(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"  # Organisation context is always provided via current_user
    ) -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific month (organisation context from current_user)"""
        try:
            logger.info(f"Getting team attendance for {filters.month}/{filters.year} in organisation {current_user.hostname}")
            
            # Validate filters
            self._validate_month_filters(filters)
            
            # Get team members
            team_members = await self._get_team_members(filters.manager_id, current_user)
            
            # Get attendance records for all team members
            attendances = []
            for member in team_members:
                member_attendances = await self.attendance_query_repository.get_by_employee_and_month(
                    employee_id=member.employee_id,
                    month=filters.month,
                    year=filters.year,
                    hostname=current_user.hostname
                )
                attendances.extend(member_attendances)
            
            # Convert to response DTOs
            response_dtos = [self._create_response_dto(attendance) for attendance in attendances]
            
            logger.info(f"Found {len(response_dtos)} team attendance records")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error getting team attendance by month: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_team_attendance_by_year(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"  # Organisation context is always provided via current_user
    ) -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific year (organisation context from current_user)"""
        try:
            logger.info(f"Getting team attendance for year {filters.year} in organisation {current_user.hostname}")
            
            # Validate filters
            self._validate_year_filters(filters)
            
            # Get team members
            team_members = await self._get_team_members(filters.manager_id, current_user)
            
            # Get attendance records for all team members
            attendances = []
            for member in team_members:
                member_attendances = await self.attendance_query_repository.get_by_employee_and_year(
                    employee_id=member.employee_id,
                    year=filters.year,
                    hostname=current_user.hostname
                )
                attendances.extend(member_attendances)
            
            # Convert to response DTOs
            response_dtos = [self._create_response_dto(attendance) for attendance in attendances]
            
            logger.info(f"Found {len(response_dtos)} team attendance records")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error getting team attendance by year: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    def _validate_month_filters(self, filters: AttendanceSearchFiltersDTO) -> None:
        """Validate month-based filters"""
        if not filters.month or not filters.year:
            raise AttendanceValidationError("Month and year are required")
        
        if filters.month < 1 or filters.month > 12:
            raise AttendanceValidationError("Month must be between 1 and 12")
        
        if filters.year < 2000 or filters.year > 3000:
            raise AttendanceValidationError("Year must be between 2000 and 3000")
    
    def _validate_year_filters(self, filters: AttendanceSearchFiltersDTO) -> None:
        """Validate year-based filters"""
        if not filters.year:
            raise AttendanceValidationError("Year is required")
        
        if filters.year < 2000 or filters.year > 3000:
            raise AttendanceValidationError("Year must be between 2000 and 3000")
    
    def _validate_date_filters(self, filters: AttendanceSearchFiltersDTO) -> None:
        """Validate date-based filters"""
        if not filters.date or not filters.month or not filters.year:
            raise AttendanceValidationError("Date, month and year are required")
        
        if filters.date < 1 or filters.date > 31:
            raise AttendanceValidationError("Date must be between 1 and 31")
        
        if filters.month < 1 or filters.month > 12:
            raise AttendanceValidationError("Month must be between 1 and 12")
        
        if filters.year < 2000 or filters.year > 3000:
            raise AttendanceValidationError("Year must be between 2000 and 3000")
    
    async def _get_team_members(self, manager_id: str, current_user: "CurrentUser") -> List:
        """Get team members for a manager"""
        try:
            team_members = await self.employee_repository.get_by_manager_id(manager_id, current_user.hostname)
            return team_members or []
        except Exception as e:
            logger.warning(f"Error getting team members for manager {manager_id}: {e}")
            return []
    
    def _create_response_dto(self, attendance: Attendance) -> AttendanceResponseDTO:
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
            employee_id=attendance.employee_id.value if hasattr(attendance.employee_id, 'value') else str(attendance.employee_id),
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