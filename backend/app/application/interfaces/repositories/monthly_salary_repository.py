"""
Monthly Salary Repository Interface
Abstract repository interface for monthly salary operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.monthly_salary import MonthlySalary
from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.taxation_dto import MonthlySalaryResponseDTO


class MonthlySalaryCommandRepository(ABC):
    """
    Repository interface for monthly salary write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def save(self, monthly_salary: MonthlySalary, organization_id: str) -> MonthlySalary:
        """
        Save monthly salary to organisation-specific database.
        
        Args:
            monthly_salary: Monthly salary entity to save
            organization_id: Organization ID for database selection
            
        Returns:
            Saved monthly salary entity
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def save_batch(self, monthly_salaries: List[MonthlySalary], organization_id: str) -> List[MonthlySalary]:
        """
        Save multiple monthly salaries in a batch operation.
        
        Args:
            monthly_salaries: List of monthly salary entities to save
            organization_id: Organization ID for database selection
            
        Returns:
            List of saved monthly salary entities
            
        Raises:
            RepositoryError: If batch save operation fails
        """
        pass
    
    @abstractmethod
    async def update(self, monthly_salary: MonthlySalary, organization_id: str) -> MonthlySalary:
        """
        Update existing monthly salary.
        
        Args:
            monthly_salary: Monthly salary entity to update
            organization_id: Organization ID for database selection
            
        Returns:
            Updated monthly salary entity
            
        Raises:
            RepositoryError: If update operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, employee_id: str, month: int, year: int, organization_id: str) -> bool:
        """
        Delete monthly salary record.
        
        Args:
            employee_id: Employee ID
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class MonthlySalaryQueryRepository(ABC):
    """
    Repository interface for monthly salary read operations.
    
    Follows SOLID principles:
    - SRP: Only handles read operations
    - OCP: Can be extended with new query methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_by_employee_month_year(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Optional[MonthlySalary]:
        """
        Get monthly salary by employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            Monthly salary entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_employee(
        self, 
        employee_id: str, 
        organization_id: str,
        limit: int = 12,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries for an employee.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        pass
    
    @abstractmethod
    async def get_by_month_year(
        self, 
        month: int, 
        year: int, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get all monthly salaries for a specific month and year.
        
        Args:
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        pass
    
    @abstractmethod
    async def get_by_tax_year(
        self, 
        tax_year: str, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get all monthly salaries for a specific tax year.
        
        Args:
            tax_year: Tax year string (e.g., "2024-25")
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        pass
    
    @abstractmethod
    async def get_monthly_salaries_for_period(
        self,
        month: int,
        year: int,
        organization_id: str,
        status: Optional[str] = None,
        department: Optional[str] = None,
        employee_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries for a period with optional filters.
        
        Args:
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            status: Optional status filter
            department: Optional department filter
            employee_id: Optional employee ID filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        pass
    
    @abstractmethod
    async def exists(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> bool:
        """
        Check if monthly salary exists for employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            True if exists, False otherwise
        """
        pass


class MonthlySalaryAnalyticsRepository(ABC):
    """
    Repository interface for monthly salary analytics operations.
    
    Follows SOLID principles:
    - SRP: Only handles analytics operations
    - OCP: Can be extended with new analytics methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for analytics operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_monthly_summary(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get monthly salary summary for a specific month and year.
        
        Args:
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            Dictionary containing summary statistics
        """
        pass
    
    @abstractmethod
    async def get_employee_salary_history(
        self, 
        employee_id: str, 
        organization_id: str,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get salary history for an employee.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID for database selection
            months: Number of months to retrieve
            
        Returns:
            List of salary history records
        """
        pass
    
    @abstractmethod
    async def get_payroll_summary(
        self, 
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get payroll summary for a date range.
        
        Args:
            organization_id: Organization ID for database selection
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary containing payroll summary
        """
        pass


class MonthlySalaryRepository(
    MonthlySalaryCommandRepository,
    MonthlySalaryQueryRepository,
    MonthlySalaryAnalyticsRepository
):
    """
    Composite repository interface combining all monthly salary repository interfaces.
    
    This interface can be used when you need access to all repository operations
    in a single interface. Individual interfaces should be preferred when possible
    to follow the Interface Segregation Principle.
    
    Follows SOLID principles:
    - SRP: Combines related repository operations
    - OCP: Can be extended through composition
    - LSP: All implementations must be substitutable
    - ISP: Composed of focused interfaces
    - DIP: Depends on abstractions
    """
    pass 