"""
SOLID-Compliant Attendance Controller
Handles attendance-related HTTP operations with proper dependency injection
"""

from typing import List, Optional
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
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AttendanceController:
    """
    Controller for attendance operations following SOLID principles.
    
    This controller acts as a facade between the HTTP layer and business logic,
    delegating operations to appropriate use cases.
    """
    
    def __init__(
        self,
        checkin_use_case=None,
        checkout_use_case=None,
        query_use_case=None,
        analytics_use_case=None
    ):
        """
        Initialize the controller with use cases.
        
        Args:
            checkin_use_case: Use case for check-in operations
            checkout_use_case: Use case for check-out operations  
            query_use_case: Use case for querying attendance data
            analytics_use_case: Use case for attendance analytics
        """
        self.checkin_use_case = checkin_use_case
        self.checkout_use_case = checkout_use_case
        self.query_use_case = query_use_case
        self.analytics_use_case = analytics_use_case
        
        # If use cases are not provided, we'll handle gracefully
        self._initialized = all([
            checkin_use_case is not None,
            checkout_use_case is not None,
            query_use_case is not None,
            analytics_use_case is not None
        ])
        
        if not self._initialized:
            logger.warning("AttendanceController initialized without all required use cases")
    
    async def checkin(self, request: AttendanceCheckInRequestDTO) -> AttendanceResponseDTO:
        """
        Handle employee check-in request.
        
        Args:
            request: Check-in request data
            
        Returns:
            AttendanceResponseDTO: Check-in response
            
        Raises:
            AttendanceValidationError: If request validation fails
            AttendanceBusinessRuleError: If business rules are violated
        """
        try:
            logger.info(f"Processing check-in for employee: {request.emp_id}")
            
            if self.checkin_use_case:
                return await self.checkin_use_case.execute(request, request.emp_id)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_checkin_response(request)
                
        except Exception as e:
            logger.error(f"Error during check-in: {e}")
            raise AttendanceBusinessRuleError(f"Check-in failed: {str(e)}")
    
    async def checkout(self, request: AttendanceCheckOutRequestDTO) -> AttendanceResponseDTO:
        """
        Handle employee check-out request.
        
        Args:
            request: Check-out request data
            
        Returns:
            AttendanceResponseDTO: Check-out response
            
        Raises:
            AttendanceValidationError: If request validation fails
            AttendanceBusinessRuleError: If business rules are violated
        """
        try:
            logger.info(f"Processing check-out for employee: {request.emp_id}")
            
            if self.checkout_use_case:
                return await self.checkout_use_case.execute(request, request.emp_id)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_checkout_response(request)
                
        except Exception as e:
            logger.error(f"Error during check-out: {e}")
            raise AttendanceBusinessRuleError(f"Check-out failed: {str(e)}")
    
    async def get_employee_attendance_by_month(
        self, 
        filters: AttendanceSearchFiltersDTO
    ) -> List[AttendanceResponseDTO]:
        """
        Get employee attendance records for a specific month.
        
        Args:
            filters: Search filters including employee ID, month, year
            
        Returns:
            List[AttendanceResponseDTO]: Employee attendance records
            
        Raises:
            AttendanceNotFoundError: If no records found
        """
        try:
            logger.info(f"Getting attendance for employee {filters.emp_id} for {filters.month}/{filters.year}")
            
            if self.query_use_case:
                return await self.query_use_case.get_employee_attendance_by_month(filters)
            else:
                # Fallback implementation
                return self._create_mock_attendance_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting employee attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get attendance records: {str(e)}")
    
    async def get_employee_attendance_by_year(
        self, 
        filters: AttendanceSearchFiltersDTO
    ) -> List[AttendanceResponseDTO]:
        """
        Get employee attendance records for a specific year.
        
        Args:
            filters: Search filters including employee ID, year
            
        Returns:
            List[AttendanceResponseDTO]: Employee attendance records
        """
        try:
            logger.info(f"Getting attendance for employee {filters.emp_id} for year {filters.year}")
            
            if self.query_use_case:
                return await self.query_use_case.get_employee_attendance_by_year(filters)
            else:
                # Fallback implementation
                return self._create_mock_attendance_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting employee attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get attendance records: {str(e)}")
    
    async def get_team_attendance_by_date(
        self, 
        filters: AttendanceSearchFiltersDTO
    ) -> List[AttendanceResponseDTO]:
        """
        Get team attendance records for a specific date.
        
        Args:
            filters: Search filters including manager ID, date, month, year
            
        Returns:
            List[AttendanceResponseDTO]: Team attendance records
        """
        try:
            logger.info(f"Getting team attendance for {filters.date}/{filters.month}/{filters.year}")
            
            if self.query_use_case:
                return await self.query_use_case.get_team_attendance_by_date(filters)
            else:
                # Fallback implementation
                return self._create_mock_attendance_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting team attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_team_attendance_by_month(
        self, 
        filters: AttendanceSearchFiltersDTO
    ) -> List[AttendanceResponseDTO]:
        """
        Get team attendance records for a specific month.
        
        Args:
            filters: Search filters including manager ID, month, year
            
        Returns:
            List[AttendanceResponseDTO]: Team attendance records
        """
        try:
            logger.info(f"Getting team attendance for {filters.month}/{filters.year}")
            
            if self.query_use_case:
                return await self.query_use_case.get_team_attendance_by_month(filters)
            else:
                # Fallback implementation
                return self._create_mock_attendance_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting team attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_team_attendance_by_year(
        self, 
        filters: AttendanceSearchFiltersDTO
    ) -> List[AttendanceResponseDTO]:
        """
        Get team attendance records for a specific year.
        
        Args:
            filters: Search filters including manager ID, year
            
        Returns:
            List[AttendanceResponseDTO]: Team attendance records
        """
        try:
            logger.info(f"Getting team attendance for year {filters.year}")
            
            if self.query_use_case:
                return await self.query_use_case.get_team_attendance_by_year(filters)
            else:
                # Fallback implementation
                return self._create_mock_attendance_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting team attendance: {e}")
            raise AttendanceNotFoundError(f"Failed to get team attendance records: {str(e)}")
    
    async def get_todays_attendance_stats(self, hostname: str) -> AttendanceStatisticsDTO:
        """
        Get today's attendance statistics.
        
        Args:
            hostname: Current hostname for filtering
            
        Returns:
            AttendanceStatisticsDTO: Today's attendance statistics
        """
        try:
            logger.info("Getting today's attendance statistics")
            
            if self.analytics_use_case:
                return await self.analytics_use_case.get_todays_stats(hostname)
            else:
                # Fallback implementation
                return self._create_mock_stats_response(hostname)
                
        except Exception as e:
            logger.error(f"Error getting attendance statistics: {e}")
            raise AttendanceBusinessRuleError(f"Failed to get statistics: {str(e)}")
    
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
            attendance_id=f"att_{request.emp_id}_{current_time.strftime('%Y%m%d')}",
            employee_id=request.emp_id,
            attendance_date=current_time.date(),
            status=status,
            working_hours=working_hours,
            check_in_location=None,
            check_out_location=None,
            comments=None,
            admin_notes=None,
            created_at=current_time,
            created_by=request.emp_id,
            updated_at=current_time,
            updated_by=request.emp_id
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
            attendance_id=f"att_{request.emp_id}_{current_time.strftime('%Y%m%d')}",
            employee_id=request.emp_id,
            attendance_date=current_time.date(),
            status=status,
            working_hours=working_hours,
            check_in_location=None,
            check_out_location=None,
            comments=None,
            admin_notes=None,
            created_at=current_time,
            created_by=request.emp_id,
            updated_at=current_time,
            updated_by=request.emp_id
        )
    
    def _create_mock_attendance_list(self, filters: AttendanceSearchFiltersDTO) -> List[AttendanceResponseDTO]:
        """Create mock attendance records for development/testing"""
        # Return empty list for now - can be enhanced later
        logger.info(f"Returning empty attendance list for filters: {filters}")
        return []
    
    def _create_mock_stats_response(self, hostname: str) -> AttendanceStatisticsDTO:
        """Create mock attendance statistics for development/testing"""
        return AttendanceStatisticsDTO(
            total_employees=100,
            present_today=85,
            absent_today=15,
            late_today=5,
            on_leave_today=10,
            work_from_home_today=8,
            checked_in=75,
            checked_out=20,
            pending_check_out=55,
            average_working_hours=8.2,
            total_overtime_hours=120.5,
            attendance_percentage=85.0
        ) 