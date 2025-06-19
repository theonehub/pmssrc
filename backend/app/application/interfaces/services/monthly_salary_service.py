"""
Monthly Salary Service Interface
Service interface for monthly salary business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from app.application.dto.monthly_salary_dto import (
    MonthlySalaryRequestDTO,
    MonthlySalaryResponseDTO,
    MonthlySalaryListResponseDTO,
    MonthlySalaryFilterDTO,
    MonthlySalaryComputeRequestDTO,
    MonthlySalaryBulkComputeRequestDTO,
    MonthlySalaryBulkComputeResponseDTO,
    MonthlySalaryStatusUpdateRequestDTO,
    MonthlySalarySummaryDTO
)

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser


class MonthlySalaryService(ABC):
    """Service interface for monthly salary operations."""
    
    @abstractmethod
    async def get_monthly_salary(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        current_user: "CurrentUser"
    ) -> Optional[MonthlySalaryResponseDTO]:
        """
        Get monthly salary for an employee.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            current_user: Current user context
            
        Returns:
            Optional[MonthlySalaryResponseDTO]: Monthly salary if found
        """
        pass
    
    @abstractmethod
    async def get_monthly_salaries_for_period(
        self, 
        month: int, 
        year: int, 
        current_user: "CurrentUser",
        filters: Optional[MonthlySalaryFilterDTO] = None
    ) -> MonthlySalaryListResponseDTO:
        """
        Get all monthly salaries for a period.
        
        Args:
            month: Month (1-12)
            year: Year
            current_user: Current user context
            filters: Optional filters
            
        Returns:
            MonthlySalaryListResponseDTO: List of monthly salaries
        """
        pass
    
    @abstractmethod
    async def compute_monthly_salary(
        self, 
        request: MonthlySalaryComputeRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryResponseDTO:
        """
        Compute monthly salary for an employee.
        
        Args:
            request: Compute request data
            current_user: Current user context
            
        Returns:
            MonthlySalaryResponseDTO: Computed monthly salary
        """
        pass
    
    @abstractmethod
    async def bulk_compute_monthly_salaries(
        self, 
        request: MonthlySalaryBulkComputeRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryBulkComputeResponseDTO:
        """
        Bulk compute monthly salaries.
        
        Args:
            request: Bulk compute request data
            current_user: Current user context
            
        Returns:
            MonthlySalaryBulkComputeResponseDTO: Bulk compute results
        """
        pass
    
    @abstractmethod
    async def update_monthly_salary_status(
        self, 
        request: MonthlySalaryStatusUpdateRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryResponseDTO:
        """
        Update monthly salary status.
        
        Args:
            request: Status update request data
            current_user: Current user context
            
        Returns:
            MonthlySalaryResponseDTO: Updated monthly salary
        """
        pass
    
    @abstractmethod
    async def get_monthly_salary_summary(
        self, 
        month: int, 
        year: int, 
        current_user: "CurrentUser"
    ) -> MonthlySalarySummaryDTO:
        """
        Get monthly salary summary for a period.
        
        Args:
            month: Month (1-12)
            year: Year
            current_user: Current user context
            
        Returns:
            MonthlySalarySummaryDTO: Summary data
        """
        pass
    
    @abstractmethod
    async def delete_monthly_salary(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        current_user: "CurrentUser"
    ) -> bool:
        """
        Delete monthly salary record.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            current_user: Current user context
            
        Returns:
            bool: True if deleted successfully
        """
        pass 