"""
Monthly Salary Repository Interface
Repository interface for monthly salary data operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.entities.monthly_salary import MonthlySalary
from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.monthly_salary_dto import MonthlySalaryFilterDTO


class MonthlySalaryRepository(ABC):
    """Repository interface for monthly salary operations."""
    
    @abstractmethod
    async def save(self, monthly_salary: MonthlySalary, hostname: str) -> MonthlySalary:
        """
        Save or update monthly salary record.
        
        Args:
            monthly_salary: Monthly salary entity
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            MonthlySalary: Saved monthly salary entity
        """
        pass
    
    @abstractmethod
    async def get_by_employee_month_year(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Optional[MonthlySalary]:
        """
        Get monthly salary by employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            Optional[MonthlySalary]: Monthly salary if found
        """
        pass
    
    @abstractmethod
    async def get_by_employee_tax_year(
        self, 
        employee_id: EmployeeId, 
        tax_year: str, 
        hostname: str
    ) -> List[MonthlySalary]:
        """
        Get all monthly salaries for an employee in a tax year.
        
        Args:
            employee_id: Employee ID
            tax_year: Tax year (e.g., '2023-24')
            hostname: Organization hostname
            
        Returns:
            List[MonthlySalary]: List of monthly salaries
        """
        pass
    
    @abstractmethod
    async def get_by_month_year(
        self, 
        month: int, 
        year: int, 
        hostname: str,
        filters: Optional[MonthlySalaryFilterDTO] = None
    ) -> List[MonthlySalary]:
        """
        Get all monthly salaries for a specific month/year.
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            filters: Additional filters
            
        Returns:
            List[MonthlySalary]: List of monthly salaries
        """
        pass
    
    @abstractmethod
    async def get_by_status(
        self, 
        status: str, 
        hostname: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries by status.
        
        Args:
            status: Processing status
            hostname: Organization hostname
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            List[MonthlySalary]: List of monthly salaries
        """
        pass
    
    @abstractmethod
    async def get_summary_by_month_year(
        self, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a month/year.
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        pass
    
    @abstractmethod
    async def delete_by_employee_month_year(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> bool:
        """
        Delete monthly salary record.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            bool: True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def exists(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> bool:
        """
        Check if monthly salary record exists.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            bool: True if exists
        """
        pass
    
    @abstractmethod
    async def count_by_filters(
        self, 
        filters: MonthlySalaryFilterDTO, 
        hostname: str
    ) -> int:
        """
        Count monthly salary records by filters.
        
        Args:
            filters: Filter criteria
            hostname: Organization hostname
            
        Returns:
            int: Count of records
        """
        pass
    
    @abstractmethod
    async def get_employees_without_salary(
        self, 
        month: int, 
        year: int, 
        hostname: str
    ) -> List[str]:
        """
        Get list of employee IDs without monthly salary for given month/year.
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            List[str]: List of employee IDs
        """
        pass


class MonthlySalaryQueryRepository(ABC):
    """Query-specific repository interface for monthly salary read operations."""
    
    @abstractmethod
    async def get_monthly_salary_with_employee_details(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get monthly salary with employee details.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            Optional[Dict[str, Any]]: Monthly salary with employee info
        """
        pass
    
    @abstractmethod
    async def get_payroll_summary_by_department(
        self, 
        month: int, 
        year: int, 
        hostname: str
    ) -> List[Dict[str, Any]]:
        """
        Get payroll summary grouped by department.
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organization hostname
            
        Returns:
            List[Dict[str, Any]]: Department-wise payroll summary
        """
        pass
    
    @abstractmethod
    async def get_monthly_salary_trends(
        self, 
        employee_id: EmployeeId, 
        months: int, 
        hostname: str
    ) -> List[Dict[str, Any]]:
        """
        Get monthly salary trends for an employee.
        
        Args:
            employee_id: Employee ID
            months: Number of months to look back
            hostname: Organization hostname
            
        Returns:
            List[Dict[str, Any]]: Monthly salary trend data
        """
        pass 