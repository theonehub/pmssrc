"""
Attendance Service Interface
Following Interface Segregation Principle for attendance business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.application.dto.attendance_dto import (
    CheckInRequestDTO,
    CheckOutRequestDTO,
    AttendanceResponseDTO,
    AttendanceListResponseDTO,
    AttendanceSearchFiltersDTO,
    AttendanceAnalyticsDTO
)


class AttendanceCommandService(ABC):
    """Service interface for attendance command operations."""
    
    @abstractmethod
    async def check_in(self, request: CheckInRequestDTO) -> AttendanceResponseDTO:
        """Process employee check-in."""
        pass
    
    @abstractmethod
    async def check_out(self, request: CheckOutRequestDTO) -> AttendanceResponseDTO:
        """Process employee check-out."""
        pass


class AttendanceQueryService(ABC):
    """Service interface for attendance query operations."""
    
    @abstractmethod
    async def get_attendance_by_id(self, attendance_id: str) -> Optional[AttendanceResponseDTO]:
        """Get attendance record by ID."""
        pass
    
    @abstractmethod
    async def list_attendance(self, filters: Optional[AttendanceSearchFiltersDTO] = None) -> AttendanceListResponseDTO:
        """List attendance records with optional filters."""
        pass


class AttendanceAnalyticsService(ABC):
    """Service interface for attendance analytics operations."""
    
    @abstractmethod
    async def get_attendance_analytics(self, employee_id: str, start_date: date, end_date: date) -> AttendanceAnalyticsDTO:
        """Get attendance analytics for an employee."""
        pass


class AttendanceValidationService(ABC):
    """Service interface for attendance validation operations."""
    
    @abstractmethod
    async def validate_check_in(self, request: CheckInRequestDTO) -> List[str]:
        """Validate check-in request."""
        pass
    
    @abstractmethod
    async def validate_check_out(self, request: CheckOutRequestDTO) -> List[str]:
        """Validate check-out request."""
        pass


class AttendanceService(
    AttendanceCommandService,
    AttendanceQueryService,
    AttendanceAnalyticsService,
    AttendanceValidationService
):
    """Combined attendance service interface."""
    pass 