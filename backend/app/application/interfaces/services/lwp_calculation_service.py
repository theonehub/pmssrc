"""
LWP Calculation Service Interface
Abstract interface for LWP calculation services
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.application.dto.employee_leave_dto import LWPCalculationDTO


class LWPCalculationServiceInterface(ABC):
    """Abstract interface for LWP calculation services."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def calculate_lwp_factor(self, lwp_days: int, working_days: int) -> float:
        """
        Calculate the LWP factor (reduction factor for salary).
        
        Args:
            lwp_days: Number of LWP days
            working_days: Total working days in month
            
        Returns:
            float: Factor between 0 and 1 representing salary reduction
        """
        pass
    
    @abstractmethod
    def calculate_paid_days(self, lwp_days: int, working_days: int) -> int:
        """
        Calculate number of paid days in the month.
        
        Args:
            lwp_days: Number of LWP days
            working_days: Total working days in month
            
        Returns:
            int: Number of paid days
        """
        pass 