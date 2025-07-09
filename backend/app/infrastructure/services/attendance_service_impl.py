"""
Attendance Service Implementation
SOLID-compliant implementation of attendance service interfaces
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

from app.application.interfaces.services.attendance_service import AttendanceService
from app.application.interfaces.repositories.attendance_repository import AttendanceRepository
from app.application.dto.attendance_dto import (
    AttendanceCheckInRequestDTO,
    AttendanceCheckOutRequestDTO,
    AttendanceResponseDTO,
    AttendanceSearchFiltersDTO,
    AttendanceStatisticsDTO
)
from app.infrastructure.services.notification_service import NotificationService
from app.utils.logger import get_logger

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = get_logger(__name__)


class AttendanceServiceImpl(AttendanceService):
    """
    Concrete implementation of attendance services.
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (repository, notification service)
    """
    
    def __init__(
        self,
        repository: AttendanceRepository,
        notification_service: Optional[NotificationService] = None,
        checkin_use_case=None,
        checkout_use_case=None,
        query_use_case=None,
        analytics_use_case=None,
        punch_use_case=None
    ):
        self.repository = repository
        self.notification_service = notification_service
        self.checkin_use_case = checkin_use_case
        self.checkout_use_case = checkout_use_case
        self.query_use_case = query_use_case
        self.analytics_use_case = analytics_use_case
        self.punch_use_case = punch_use_case
        self.logger = get_logger(__name__)
    
    # ==================== COMMAND OPERATIONS ====================
    
    async def check_in(self, request: AttendanceCheckInRequestDTO, current_user: "CurrentUser") -> AttendanceResponseDTO:
        """Process employee check-in"""
        try:
            self.logger.info(f"Processing check-in for employee {request.employee_id} in organisation {current_user.hostname}")
            
            if self.checkin_use_case:
                return await self.checkin_use_case.execute(request, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Check-in use case not available, using fallback implementation")
                return self._create_mock_checkin_response(request)
                
        except Exception as e:
            self.logger.error(f"Error processing check-in for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def check_out(self, request: AttendanceCheckOutRequestDTO, current_user: "CurrentUser") -> AttendanceResponseDTO:
        """Process employee check-out"""
        try:
            self.logger.info(f"Processing check-out for employee {request.employee_id} in organisation {current_user.hostname}")
            
            if self.checkout_use_case:
                return await self.checkout_use_case.execute(request, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Check-out use case not available, using fallback implementation")
                return self._create_mock_checkout_response(request)
                
        except Exception as e:
            self.logger.error(f"Error processing check-out for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise

    async def record_punch(self, employee_id: str, current_user: "CurrentUser") -> AttendanceResponseDTO:
        """Process employee punch (check-in or check-out)"""
        try:
            self.logger.info(f"Processing punch for employee {employee_id} in organisation {current_user.hostname}")
            
            if self.punch_use_case:
                return await self.punch_use_case.execute(employee_id, current_user)
            else:
                self.logger.warning("Punch use case not available, using fallback implementation")
                # Fallback logic or raise error
                raise NotImplementedError("Punch functionality not fully implemented")
                
        except Exception as e:
            self.logger.error(f"Error processing punch for employee {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_employee_attendance_by_month(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific month"""
        try:
            self.logger.info(f"Getting employee attendance for {filters.employee_id} for {filters.month}/{filters.year} in organisation {current_user.hostname}")
            
            if self.query_use_case:
                return await self.query_use_case.get_employee_attendance_by_month(filters, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Query use case not available, returning empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting employee attendance for {filters.employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_employee_attendance_by_year(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get employee attendance records for a specific year"""
        try:
            self.logger.info(f"Getting employee attendance for {filters.employee_id} for year {filters.year} in organisation {current_user.hostname}")
            
            if self.query_use_case:
                return await self.query_use_case.get_employee_attendance_by_year(filters, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Query use case not available, returning empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting employee attendance for {filters.employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_team_attendance_by_date(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific date"""
        try:
            self.logger.info(f"Getting team attendance for {filters.date}/{filters.month}/{filters.year} in organisation {current_user.hostname}")
            
            if self.query_use_case:
                return await self.query_use_case.get_team_attendance_by_date(filters, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Query use case not available, returning empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting team attendance in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_team_attendance_by_month(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific month"""
        try:
            self.logger.info(f"Getting team attendance for {filters.month}/{filters.year} in organisation {current_user.hostname}")
            
            if self.query_use_case:
                return await self.query_use_case.get_team_attendance_by_month(filters, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Query use case not available, returning empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting team attendance in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_team_attendance_by_year(self, filters: AttendanceSearchFiltersDTO, current_user: "CurrentUser") -> List[AttendanceResponseDTO]:
        """Get team attendance records for a specific year"""
        try:
            self.logger.info(f"Getting team attendance for year {filters.year} in organisation {current_user.hostname}")
            
            if self.query_use_case:
                return await self.query_use_case.get_team_attendance_by_year(filters, current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Query use case not available, returning empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting team attendance in organisation {current_user.hostname}: {e}")
            raise
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_todays_attendance_stats(self, current_user: "CurrentUser") -> AttendanceStatisticsDTO:
        """Get today's attendance statistics"""
        try:
            self.logger.info(f"Getting today's attendance statistics for organisation {current_user.hostname}")
            
            if self.analytics_use_case:
                return await self.analytics_use_case.get_todays_attendance_stats(current_user)
            else:
                # Fallback implementation for development
                self.logger.warning("Analytics use case not available, returning mock statistics")
                return self._create_mock_statistics()
                
        except Exception as e:
            self.logger.error(f"Error getting attendance statistics for organisation {current_user.hostname}: {e}")
            raise
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    def _create_mock_statistics(self) -> AttendanceStatisticsDTO:
        """Create mock statistics for development/testing"""
        return AttendanceStatisticsDTO(
            total_employees=50,
            present_today=45,
            absent_today=5,
            late_today=3,
            on_leave_today=2,
            work_from_home_today=8,
            checked_in=40,
            checked_out=35,
            pending_check_out=5,
            average_working_hours=8.2,
            total_overtime_hours=15.5,
            attendance_percentage=90.0
        )
    
    # Private helper methods for fallback implementations
    
    def _create_mock_checkin_response(self, request: AttendanceCheckInRequestDTO) -> AttendanceResponseDTO:
        """Create a mock check-in response for development/testing"""
        from app.application.dto.attendance_dto import (
            AttendanceStatusResponseDTO, 
            WorkingHoursResponseDTO,
            AttendanceStatusEnum,
            AttendanceMarkingTypeEnum
        )
        
        current_time = datetime.now()
        
        status = AttendanceStatusResponseDTO(
            status=AttendanceStatusEnum.PRESENT,
            marking_type=AttendanceMarkingTypeEnum.WEB_APP,
            is_regularized=False,
            regularization_reason=None
        )
        
        working_hours = WorkingHoursResponseDTO(
            check_in_time=current_time,
            check_out_time=None,
            total_hours=0.0,
            break_hours=0.0,
            overtime_hours=0.0,
            shortage_hours=0.0,
            expected_hours=8.0,
            is_complete_day=False,
            is_full_day=False,
            is_half_day=False
        )
        
        return AttendanceResponseDTO(
            attendance_id=f"att_{request.employee_id}_{current_time.strftime('%Y%m%d')}",
            employee_id=request.employee_id,
            attendance_date=current_time.date(),
            status=status,
            working_hours=working_hours,
            check_in_location=request.location,
            check_out_location=None,
            comments=None,
            admin_notes=None,
            created_at=current_time,
            created_by=request.employee_id,
            updated_at=current_time,
            updated_by=request.employee_id
        )
    
    def _create_mock_checkout_response(self, request: AttendanceCheckOutRequestDTO) -> AttendanceResponseDTO:
        """Create a mock check-out response for development/testing"""
        from app.application.dto.attendance_dto import (
            AttendanceStatusResponseDTO, 
            WorkingHoursResponseDTO,
            AttendanceStatusEnum,
            AttendanceMarkingTypeEnum
        )
        
        current_time = datetime.now()
        start_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
        total_hours = (current_time - start_time).total_seconds() / 3600
        
        status = AttendanceStatusResponseDTO(
            status=AttendanceStatusEnum.PRESENT,
            marking_type=AttendanceMarkingTypeEnum.WEB_APP,
            is_regularized=False,
            regularization_reason=None
        )
        
        working_hours = WorkingHoursResponseDTO(
            check_in_time=start_time,
            check_out_time=current_time,
            total_hours=total_hours,
            break_hours=0.0,
            overtime_hours=max(0.0, total_hours - 8.0),
            shortage_hours=max(0.0, 8.0 - total_hours),
            expected_hours=8.0,
            is_complete_day=total_hours >= 8.0,
            is_full_day=total_hours >= 8.0,
            is_half_day=4.0 <= total_hours < 8.0
        )
        
        return AttendanceResponseDTO(
            attendance_id=f"att_{request.employee_id}_{current_time.strftime('%Y%m%d')}",
            employee_id=request.employee_id,
            attendance_date=current_time.date(),
            status=status,
            working_hours=working_hours,
            check_in_location=None,
            check_out_location=request.location,
            comments=None,
            admin_notes=None,
            created_at=current_time,
            created_by=request.employee_id,
            updated_at=current_time,
            updated_by=request.employee_id
        ) 