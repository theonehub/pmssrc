"""
Attendance Service Interface
Following Interface Segregation Principle for attendance business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

from app.application.dto.attendance_dto import (
    AttendanceCheckInRequestDTO,
    AttendanceCheckOutRequestDTO,
    AttendanceResponseDTO,
    AttendanceSearchFiltersDTO,
    AttendanceStatisticsDTO
)

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser


class AttendanceCommandService(ABC):
    """Service interface for attendance command operations."""
    
    @abstractmethod
    async def check_in(self, request: AttendanceCheckInRequestDTO, current_user: "CurrentUser") -> AttendanceResponseDTO:
        """Process employee check-in."""
        pass
    
    @abstractmethod
    async def check_out(self, request: AttendanceCheckOutRequestDTO, current_user: "CurrentUser") -> AttendanceResponseDTO:
        """Process employee check-out."""
        pass


class AttendanceQueryService(ABC):
    """Service interface for attendance query operations."""
    
    @abstractmethod
    async def get_employee_attendance_by_month(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific month."""
        pass
    
    @abstractmethod
    async def get_employee_attendance_by_year(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific year."""
        pass
    
    @abstractmethod
    async def get_team_attendance_by_date(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific date."""
        pass
    
    @abstractmethod
    async def get_team_attendance_by_month(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific month."""
        pass
    
    @abstractmethod
    async def get_team_attendance_by_year(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific year."""
        pass


class AttendanceAnalyticsService(ABC):
    """Service interface for attendance analytics operations."""
    
    @abstractmethod
    async def get_todays_attendance_stats(self, current_user: "CurrentUser") -> AttendanceStatisticsDTO:
        """Get today's attendance statistics."""
        pass


class AttendanceService(
    AttendanceCommandService,
    AttendanceQueryService,
    AttendanceAnalyticsService
):
    """Combined attendance service interface."""
    pass 