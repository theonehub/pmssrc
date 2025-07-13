"""
LWP Calculation Service
Standardized service for calculating Leave Without Pay using the legacy approach
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from decimal import Decimal

from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.employee_leave_dto import LWPCalculationDTO
from app.application.dto.attendance_dto import AttendanceSearchFiltersDTO
from app.application.interfaces.services.attendance_service import AttendanceService
from app.application.interfaces.services.lwp_calculation_service import LWPCalculationServiceInterface
from app.application.interfaces.repositories.employee_leave_repository import EmployeeLeaveRepository
from app.application.interfaces.repositories.public_holiday_repository import PublicHolidayRepository
from app.domain.entities.employee_leave import EmployeeLeave
from app.application.dto.employee_leave_dto import LeaveStatus
from app.domain.entities.attendance import Attendance

logger = logging.getLogger(__name__)


class LWPCalculationService(LWPCalculationServiceInterface):
    """
    Standardized LWP calculation service using the legacy approach.
    
    LWP is calculated based on:
    1. Absent days without approved leave
    2. Days with pending or rejected leave
    3. Excludes weekends and public holidays
    """
    
    def __init__(
        self,
        attendance_service: AttendanceService,
        employee_leave_repository: EmployeeLeaveRepository,
        public_holiday_repository: PublicHolidayRepository
    ):
        self._attendance_service = attendance_service
        self._employee_leave_repository = employee_leave_repository
        self._public_holiday_repository = public_holiday_repository
    
    async def calculate_lwp_for_month(
        self,
        employee_id: str,
        month: int,
        year: int,
        organisation_id: str
    ) -> LWPCalculationDTO:
        """
        Calculate Leave Without Pay (LWP) for a specific month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            organisation_id: Organization identifier
            
        Returns:
            LWPCalculationDTO with LWP calculation details
        """
        try:
            logger.info(f"Calculating LWP for {employee_id} in {month}/{year} for org: {organisation_id}")
            
            # Validate inputs
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
            if not (2000 <= year <= 3000):
                raise ValueError("Year must be between 2000 and 3000")
            
            # Get month start and end dates
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Get attendance records for the month
            attendance_records = await self._get_attendance_records(
                employee_id, month, year, organisation_id
            )
            
            # Get leaves for the month
            leaves = await self._get_leave_records(
                employee_id, month_start, month_end, organisation_id
            )
            
            # Calculate LWP days
            lwp_days = await self._calculate_lwp_days(
                month_start, month_end, attendance_records, leaves, organisation_id
            )
            
            # Calculate working days in month
            working_days = await self._calculate_working_days_in_month(
                month_start, month_end, organisation_id
            )
            
            # Calculate LWP amount (placeholder - would need salary info)
            lwp_amount = 0.0
            
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=lwp_days,
                working_days=working_days,
                lwp_amount=lwp_amount,
                calculation_details={
                    "calculated_at": date.today().isoformat(),
                    "method": "legacy_standardized",
                    "total_attendance_records": len(attendance_records),
                    "total_leave_records": len(leaves),
                    "month_start": month_start.strftime("%Y-%m-%d"),
                    "month_end": month_end.strftime("%Y-%m-%d")
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating LWP for {employee_id}: {e}")
            raise Exception(f"Failed to calculate LWP: {str(e)}")
    
    async def _get_attendance_records(
        self,
        employee_id: str,
        month: int,
        year: int,
        organisation_id: str
    ) -> List[Dict[str, Any]]:
        """Get attendance records for the employee in the specified month."""
        try:
            # Create attendance search filters
            filters = AttendanceSearchFiltersDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                limit=1000
            )
            
            # Get attendance records using the attendance service
            attendance_records = await self._attendance_service.get_employee_attendance_by_month(
                filters, organisation_id  # current_user will be handled by the service
            )
            
            # Convert to simple format for LWP calculation
            records = []
            for record in attendance_records:
                if hasattr(record, 'checkin_time') and record.checkin_time:
                    records.append({
                        'checkin_time': record.checkin_time,
                        'date': record.checkin_time.date() if hasattr(record.checkin_time, 'date') else None
                    })
            
            return records
            
        except Exception as e:
            logger.warning(f"Error getting attendance records: {e}")
            return []
    
    async def _get_leave_records(
        self,
        employee_id: str,
        month_start: datetime,
        month_end: datetime,
        organisation_id: str
    ) -> List[EmployeeLeave]:
        """Get leave records for the employee in the specified month."""
        try:
            # Get leaves by date range
            leaves = await self._employee_leave_repository.get_by_date_range(
                start_date=month_start.date(),
                end_date=month_end.date(),
                employee_id=employee_id,
                organisation_id=organisation_id
            )
            
            return leaves
            
        except Exception as e:
            logger.warning(f"Error getting leave records: {e}")
            return []
    
    async def _calculate_lwp_days(
        self,
        month_start: datetime,
        month_end: datetime,
        attendance_records: List[Dict[str, Any]],
        leaves: List[EmployeeLeave],
        organisation_id: str
    ) -> int:
        """Calculate LWP days for the month."""
        lwp_days = 0
        current_date = month_start
        
        while current_date <= month_end:
            current_date_str = current_date.strftime("%Y-%m-%d")
            
            # Skip weekends and public holidays
            if await self._is_weekend_or_holiday(current_date, organisation_id):
                current_date += timedelta(days=1)
                continue
            
            # Check if present on this day
            is_present = any(
                record.get('date') == current_date.date()
                for record in attendance_records
            )
            
            if not is_present:
                # Check if on approved leave
                has_approved_leave = any(
                    datetime.strptime(leave.start_date, "%Y-%m-%d").date() <= current_date.date() <= 
                    datetime.strptime(leave.end_date, "%Y-%m-%d").date() and
                    leave.status == LeaveStatus.APPROVED
                    for leave in leaves
                )
                
                if not has_approved_leave:
                    # Check if day has pending or rejected leave
                    has_pending_rejected_leave = any(
                        datetime.strptime(leave.start_date, "%Y-%m-%d").date() <= current_date.date() <= 
                        datetime.strptime(leave.end_date, "%Y-%m-%d").date() and
                        leave.status in [LeaveStatus.PENDING, LeaveStatus.REJECTED]
                        for leave in leaves
                    )
                    
                    # Count as LWP if absent without approved leave
                    if not has_approved_leave or has_pending_rejected_leave:
                        lwp_days += 1
            
            current_date += timedelta(days=1)
        
        return lwp_days
    
    async def _is_weekend_or_holiday(self, date_obj: datetime, organisation_id: str) -> bool:
        """Check if a date is a weekend or public holiday."""
        # Check if weekend
        if date_obj.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            return True
        
                    # Check if public holiday
            try:
                date_str = date_obj.strftime("%Y-%m-%d")
                holidays = await self._public_holiday_repository.find_by_date_range(
                    start_date=date_obj.date(),
                    end_date=date_obj.date(),
                    hostname=organisation_id
                )
                return len(holidays) > 0
            except Exception as e:
                logger.warning(f"Error checking public holiday for {date_str}: {e}")
                return False
    
    async def _calculate_working_days_in_month(
        self,
        month_start: datetime,
        month_end: datetime,
        organisation_id: str
    ) -> int:
        """Calculate total working days in the month (excluding weekends and holidays)."""
        working_days = 0
        current_date = month_start
        
        while current_date <= month_end:
            if not await self._is_weekend_or_holiday(current_date, organisation_id):
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def calculate_lwp_factor(self, lwp_days: int, working_days: int) -> float:
        """
        Calculate the LWP factor (reduction factor for salary).
        
        Args:
            lwp_days: Number of LWP days
            working_days: Total working days in month
            
        Returns:
            float: Factor between 0 and 1 representing salary reduction
        """
        if lwp_days <= 0 or working_days <= 0:
            return 1.0  # No LWP
        
        if lwp_days >= working_days:
            return 0.0  # Full month LWP
        
        return 1.0 - (lwp_days / working_days)
    
    def calculate_paid_days(self, lwp_days: int, working_days: int) -> int:
        """Calculate number of paid days in the month."""
        return max(0, working_days - lwp_days) 