"""
Attendance Analytics Use Case
Handles attendance analytics and statistics operations
"""

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from app.application.dto.attendance_dto import (
    AttendanceStatisticsDTO,
    AttendanceBusinessRuleError
)
from app.application.interfaces.repositories.attendance_repository import AttendanceQueryRepository
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.utils.logger import get_logger

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = get_logger(__name__)


class AttendanceAnalyticsUseCase:
    """
    Use case for attendance analytics operations.
    
    Follows SOLID principles:
    - SRP: Handles only analytics operations
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
    
    async def get_todays_attendance_stats(self, current_user: "CurrentUser") -> AttendanceStatisticsDTO:
        """Get today's attendance statistics for the organisation"""
        try:
            logger.info(f"Getting today's attendance statistics for organisation: {current_user.hostname}")
            
            today = date.today()
            
            # Get total employees in organisation
            total_employees = await self._get_total_employees(current_user)
            
            # Get today's attendance statistics
            stats = await self._calculate_todays_stats(today, current_user)
            
            # Create response DTO
            response = AttendanceStatisticsDTO(
                total_employees=total_employees,
                present_today=stats.get("present_today", 0),
                absent_today=stats.get("absent_today", 0),
                late_today=stats.get("late_today", 0),
                on_leave_today=stats.get("on_leave_today", 0),
                work_from_home_today=stats.get("work_from_home_today", 0),
                checked_in=stats.get("checked_in", 0),
                checked_out=stats.get("checked_out", 0),
                pending_check_out=stats.get("pending_check_out", 0),
                average_working_hours=stats.get("average_working_hours", 0.0),
                total_overtime_hours=stats.get("total_overtime_hours", 0.0),
                attendance_percentage=stats.get("attendance_percentage", 0.0)
            )
            
            logger.info(f"Generated attendance statistics for {total_employees} employees")
            return response
            
        except Exception as e:
            logger.error(f"Error getting today's attendance statistics for organisation {current_user.hostname}: {e}")
            raise AttendanceBusinessRuleError(f"Failed to get attendance statistics: {str(e)}")
    
    async def _get_total_employees(self, current_user: "CurrentUser") -> int:
        """Get total number of active employees in organisation"""
        try:
            employees = await self.employee_repository.get_all_active(current_user.hostname)
            return len(employees) if employees else 0
        except Exception as e:
            logger.warning(f"Error getting total employees: {e}")
            return 0
    
    async def _calculate_todays_stats(self, today: date, current_user: "CurrentUser") -> dict:
        """Calculate today's attendance statistics"""
        try:
            # Get all attendance records for today
            todays_attendances = await self.attendance_query_repository.get_by_date(today, current_user.hostname)
            
            if not todays_attendances:
                return self._get_empty_stats()
            
            stats = {
                "present_today": 0,
                "absent_today": 0,
                "late_today": 0,
                "on_leave_today": 0,
                "work_from_home_today": 0,
                "checked_in": 0,
                "checked_out": 0,
                "pending_check_out": 0,
                "total_working_hours": 0.0,
                "total_overtime_hours": 0.0
            }
            
            for attendance in todays_attendances:
                # Count by status
                status = attendance.status.status.value.lower()
                if status == "present":
                    stats["present_today"] += 1
                elif status == "absent":
                    stats["absent_today"] += 1
                elif status == "late":
                    stats["late_today"] += 1
                elif status == "on_leave":
                    stats["on_leave_today"] += 1
                elif status == "work_from_home":
                    stats["work_from_home_today"] += 1
                
                # Count check-in/check-out status
                if attendance.working_hours.is_checked_in():
                    stats["checked_in"] += 1
                    
                    if attendance.working_hours.is_checked_out():
                        stats["checked_out"] += 1
                        stats["total_working_hours"] += attendance.working_hours.total_hours
                        stats["total_overtime_hours"] += attendance.working_hours.overtime_hours
                    else:
                        stats["pending_check_out"] += 1
            
            # Calculate averages
            total_employees_with_attendance = len(todays_attendances)
            if total_employees_with_attendance > 0:
                stats["average_working_hours"] = stats["total_working_hours"] / total_employees_with_attendance
                stats["attendance_percentage"] = (stats["present_today"] / total_employees_with_attendance) * 100
            else:
                stats["average_working_hours"] = 0.0
                stats["attendance_percentage"] = 0.0
            
            return stats
            
        except Exception as e:
            logger.warning(f"Error calculating today's stats: {e}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> dict:
        """Get empty statistics structure"""
        return {
            "present_today": 0,
            "absent_today": 0,
            "late_today": 0,
            "on_leave_today": 0,
            "work_from_home_today": 0,
            "checked_in": 0,
            "checked_out": 0,
            "pending_check_out": 0,
            "average_working_hours": 0.0,
            "total_overtime_hours": 0.0,
            "attendance_percentage": 0.0
        } 