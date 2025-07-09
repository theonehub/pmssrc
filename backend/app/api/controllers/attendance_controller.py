"""
SOLID-Compliant Attendance Controller
Handles attendance-related HTTP operations with proper dependency injection
"""

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from app.application.dto.attendance_dto import (
    AttendanceCheckInRequestDTO,
    AttendanceCheckOutRequestDTO,
    AttendanceSearchFiltersDTO,
    AttendanceResponseDTO,
    AttendanceStatisticsDTO,
    AttendanceValidationError,
    AttendanceBusinessRuleError,
    AttendanceNotFoundError
)
from app.infrastructure.services.attendance_service_impl import AttendanceServiceImpl
from app.utils.logger import get_logger

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = get_logger(__name__)


class AttendanceController:
    """
    Controller for attendance operations following SOLID principles.
    
    This controller acts as a facade between the HTTP layer and business logic,
    delegating operations to the attendance service.
    
    Follows SOLID principles:
    - SRP: Only handles HTTP request/response concerns
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with other controllers
    - ISP: Focused interface for attendance HTTP operations
    - DIP: Depends on abstractions (AttendanceService)
    """
    
    def __init__(self, attendance_service: AttendanceServiceImpl):
        """
        Initialize the controller with attendance service.
        
        Args:
            attendance_service: Service for attendance business operations
        """
        self.attendance_service = attendance_service
    
    async def checkin(
        self,
        request: AttendanceCheckInRequestDTO,
        current_user: "CurrentUser"
    ) -> AttendanceResponseDTO:
        """Handle employee check-in request"""
        try:
            logger.info(f"Check-in request for employee: {request.employee_id} in organisation: {current_user.hostname}")
            return await self.attendance_service.check_in(request, current_user)
            
        except AttendanceValidationError as e:
            logger.warning(f"Validation error during check-in: {e}")
            raise
        except AttendanceBusinessRuleError as e:
            logger.warning(f"Business rule error during check-in: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during check-in: {e}")
            raise AttendanceBusinessRuleError(f"Check-in failed: {str(e)}")
    
    async def checkout(
        self,
        request: AttendanceCheckOutRequestDTO,
        current_user: "CurrentUser"
    ) -> AttendanceResponseDTO:
        """Handle employee check-out request"""
        try:
            logger.info(f"Check-out request for employee: {request.employee_id} in organisation: {current_user.hostname}")
            return await self.attendance_service.check_out(request, current_user)
            
        except AttendanceValidationError as e:
            logger.warning(f"Validation error during check-out: {e}")
            raise
        except AttendanceBusinessRuleError as e:
            logger.warning(f"Business rule error during check-out: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during check-out: {e}")
            raise AttendanceBusinessRuleError(f"Check-out failed: {str(e)}")

    async def punch(
        self,
        employee_id: str,
        current_user: "CurrentUser"
    ) -> AttendanceResponseDTO:
        """Handle employee punch (check-in or check-out)"""
        try:
            logger.info(f"Punch request for employee: {employee_id} in organisation: {current_user.hostname}")
            return await self.attendance_service.record_punch(employee_id, current_user)
            
        except AttendanceValidationError as e:
            logger.warning(f"Validation error during punch: {e}")
            raise
        except AttendanceBusinessRuleError as e:
            logger.warning(f"Business rule error during punch: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during punch: {e}")
            raise AttendanceBusinessRuleError(f"Punch failed: {str(e)}")
    
    async def get_employee_attendance_by_month(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"
    ) -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific month"""
        try:
            logger.info(f"Getting attendance for employee {filters.employee_id} for {filters.month}/{filters.year} in organisation: {current_user.hostname}")
            return await self.attendance_service.get_employee_attendance_by_month(filters, current_user)
            
        except AttendanceNotFoundError as e:
            logger.warning(f"Attendance not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting employee attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get attendance records: {str(e)}")
    
    async def get_employee_attendance_by_year(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"
    ) -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific year"""
        try:
            logger.info(f"Getting attendance for employee {filters.employee_id} for year {filters.year} in organisation: {current_user.hostname}")
            return await self.attendance_service.get_employee_attendance_by_year(filters, current_user)
            
        except AttendanceNotFoundError as e:
            logger.warning(f"Attendance not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting employee attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get attendance records: {str(e)}")
    
    async def get_team_attendance_by_date(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"
    ) -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific date"""
        try:
            logger.info(f"Getting team attendance for {filters.date}/{filters.month}/{filters.year} in organisation: {current_user.hostname}")
            return await self.attendance_service.get_team_attendance_by_date(filters, current_user)
            
        except AttendanceNotFoundError as e:
            logger.warning(f"Team attendance not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting team attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_team_attendance_by_month(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"
    ) -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific month"""
        try:
            logger.info(f"Getting team attendance for {filters.month}/{filters.year} in organisation: {current_user.hostname}")
            return await self.attendance_service.get_team_attendance_by_month(filters, current_user)
            
        except AttendanceNotFoundError as e:
            logger.warning(f"Team attendance not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting team attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_team_attendance_by_year(
        self, 
        filters: AttendanceSearchFiltersDTO,
        current_user: "CurrentUser"
    ) -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific year"""
        try:
            logger.info(f"Getting team attendance for year {filters.year} in organisation: {current_user.hostname}")
            return await self.attendance_service.get_team_attendance_by_year(filters, current_user)
            
        except AttendanceNotFoundError as e:
            logger.warning(f"Team attendance not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting team attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_todays_attendance_stats(self, current_user: "CurrentUser") -> AttendanceStatisticsDTO:
        """Get today's attendance statistics"""
        try:
            logger.info(f"Getting today's attendance statistics for organisation: {current_user.hostname}")
            return await self.attendance_service.get_todays_attendance_stats(current_user)
            
        except Exception as e:
            logger.error(f"Error getting attendance statistics: {e}")
            raise AttendanceBusinessRuleError(f"Failed to get statistics: {str(e)}")

    async def get_user_attendance_summary(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: "CurrentUser"
    ) -> dict:
        """Get user attendance summary for a specific month"""
        try:
            logger.info(f"Getting attendance summary for employee {employee_id} for {month}/{year} in organisation: {current_user.hostname}")
            
            # Create filters for the month
            from app.application.dto.attendance_dto import AttendanceSearchFiltersDTO
            filters = AttendanceSearchFiltersDTO(
                employee_id=employee_id,
                month=month,
                year=year
            )
            
            # Get attendance records for the month
            attendance_records = await self.attendance_service.get_employee_attendance_by_month(filters, current_user)
            
            # Calculate summary statistics
            total_working_days = 0
            present_days = 0
            absent_days = 0
            half_days = 0
            late_arrivals = 0
            early_departures = 0
            overtime_hours = 0
            
            for record in attendance_records:
                if record.status == "present":
                    present_days += 1
                elif record.status == "absent":
                    absent_days += 1
                elif record.status == "half_day":
                    half_days += 1
                
                if record.is_late:
                    late_arrivals += 1
                if record.is_early_departure:
                    early_departures += 1
                
                if record.overtime_hours:
                    overtime_hours += record.overtime_hours
            
            # Calculate total working days (assuming 22 working days per month)
            total_working_days = 22
            
            # Calculate attendance percentage
            attendance_percentage = (present_days / total_working_days * 100) if total_working_days > 0 else 0
            
            return {
                "total_working_days": total_working_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "half_days": half_days,
                "late_arrivals": late_arrivals,
                "early_departures": early_departures,
                "overtime_hours": overtime_hours,
                "attendance_percentage": round(attendance_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting attendance summary for employee {employee_id}: {e}")
            raise AttendanceBusinessRuleError(f"Failed to get attendance summary: {str(e)}") 