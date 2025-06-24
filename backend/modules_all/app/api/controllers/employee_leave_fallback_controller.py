"""
Employee Leave Fallback Controller
Provides basic employee leave functionality when full SOLID architecture is not available
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.application.dto.employee_leave_dto import (
    EmployeeLeaveResponseDTO,
    EmployeeLeaveBalanceDTO,
    LWPCalculationDTO
)
from app.infrastructure.services.employee_leave_legacy_service import (
    get_leaves_by_month_for_user as legacy_get_leaves_by_month,
    calculate_lwp_for_month as legacy_calculate_lwp
)


class EmployeeLeaveFallbackController:
    """
    Fallback employee leave controller that uses legacy services.
    
    This controller provides basic functionality when the full SOLID architecture
    is not available or has dependency issues.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    async def get_monthly_leaves(
        self, 
        employee_id: str,
        month: int,
        year: int
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get employee leaves for a specific month using legacy service.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            
        Returns:
            List of EmployeeLeaveResponseDTO for the month
        """
        
        try:
            self._logger.info(f"Retrieving monthly leaves for {employee_id}: {month}/{year} (fallback)")
            
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
            
            if not (2000 <= year <= 3000):
                raise ValueError("Year must be between 2000 and 3000")
            
            # Use legacy service to get leaves
            hostname = "default"  # Default hostname for now
            legacy_leaves = legacy_get_leaves_by_month(employee_id, month, year, hostname)
            
            # Convert legacy format to DTO format
            response_leaves = []
            for leave_dict in legacy_leaves:
                # Create a basic EmployeeLeaveResponseDTO from legacy data
                response_leave = EmployeeLeaveResponseDTO(
                    leave_id=leave_dict.get('leave_id', ''),
                    employee_id=leave_dict.get('employee_id', employee_id),
                    leave_type_name=leave_dict.get('leave_name', ''),
                    start_date=datetime.strptime(leave_dict.get('start_date', ''), '%Y-%m-%d').date() if leave_dict.get('start_date') else date.today(),
                    end_date=datetime.strptime(leave_dict.get('end_date', ''), '%Y-%m-%d').date() if leave_dict.get('end_date') else date.today(),
                    reason=leave_dict.get('reason', ''),
                    status=leave_dict.get('status', 'pending'),
                    working_days=leave_dict.get('leave_count', 0),
                    applied_at=datetime.now(),
                    days_in_current_month=leave_dict.get('leave_count', 0)
                )
                response_leaves.append(response_leave)
            
            return response_leaves
            
        except Exception as e:
            self._logger.error(f"Error retrieving monthly leaves (fallback): {e}")
            # Return empty list instead of raising exception to prevent 404
            return []
    
    async def calculate_lwp(
        self,
        employee_id: str,
        month: int,
        year: int
    ) -> LWPCalculationDTO:
        """
        Calculate Leave Without Pay (LWP) for a specific month using legacy service.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            
        Returns:
            LWPCalculationDTO with LWP calculation details
        """
        
        try:
            self._logger.info(f"Calculating LWP for {employee_id}: {month}/{year} (fallback)")
            
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
            
            if not (2000 <= year <= 3000):
                raise ValueError("Year must be between 2000 and 3000")
            
            # Use legacy service to calculate LWP
            hostname = "default"  # Default hostname for now
            lwp_days = legacy_calculate_lwp(employee_id, month, year, hostname)
            
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=lwp_days,
                calculation_details={
                    "calculated_at": date.today().isoformat(),
                    "method": "legacy_calculation"
                }
            )
            
        except Exception as e:
            self._logger.error(f"Error calculating LWP (fallback): {e}")
            # Return zero LWP instead of raising exception
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=0,
                calculation_details={
                    "calculated_at": date.today().isoformat(),
                    "method": "fallback_zero",
                    "error": str(e)
                }
            )
    
    # Placeholder methods for other functionality
    async def apply_leave(self, *args, **kwargs):
        """Placeholder for apply leave functionality."""
        raise NotImplementedError("Apply leave not implemented in fallback controller")
    
    async def approve_leave(self, *args, **kwargs):
        """Placeholder for approve leave functionality."""
        raise NotImplementedError("Approve leave not implemented in fallback controller")
    
    async def get_leave_by_id(self, *args, **kwargs):
        """Placeholder for get leave by ID functionality."""
        raise NotImplementedError("Get leave by ID not implemented in fallback controller")
    
    async def get_employee_leaves(self, *args, **kwargs):
        """Placeholder for get employee leaves functionality."""
        raise NotImplementedError("Get employee leaves not implemented in fallback controller")
    
    async def get_manager_leaves(self, *args, **kwargs):
        """Placeholder for get manager leaves functionality."""
        raise NotImplementedError("Get manager leaves not implemented in fallback controller")
    
    async def get_pending_approvals(self, *args, **kwargs):
        """Placeholder for get pending approvals functionality."""
        raise NotImplementedError("Get pending approvals not implemented in fallback controller")
    
    async def search_leaves(self, *args, **kwargs):
        """Placeholder for search leaves functionality."""
        raise NotImplementedError("Search leaves not implemented in fallback controller")
    
    async def get_leave_balance(self, *args, **kwargs):
        """Placeholder for get leave balance functionality."""
        raise NotImplementedError("Get leave balance not implemented in fallback controller")
    
    async def get_leave_analytics(self, *args, **kwargs):
        """Placeholder for get leave analytics functionality."""
        raise NotImplementedError("Get leave analytics not implemented in fallback controller")
    
    async def get_team_summary(self, *args, **kwargs):
        """Placeholder for get team summary functionality."""
        raise NotImplementedError("Get team summary not implemented in fallback controller")
    
    async def count_leaves(self, *args, **kwargs):
        """Placeholder for count leaves functionality."""
        raise NotImplementedError("Count leaves not implemented in fallback controller") 