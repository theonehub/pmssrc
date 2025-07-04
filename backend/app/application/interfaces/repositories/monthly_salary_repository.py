"""
Monthly Salary Repository Interface
Abstract repository interface for monthly salary operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.entities.taxation.monthly_salary import MonthlySalary


class MonthlySalaryRepository(ABC):
    """
    Abstract repository interface for monthly salary operations.
    
    Defines the contract for persistence operations on monthly salary records.
    """
    
    @abstractmethod
    async def save(self, monthly_salary: MonthlySalary, organization_id: str) -> MonthlySalary:
        """
        Save or update a monthly salary record.
        
        Args:
            monthly_salary: Monthly salary record to save
            organization_id: Organization ID for multi-tenancy
            
        Returns:
            MonthlySalary: Saved monthly salary record
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, monthly_salary_id: str, organization_id: str) -> Optional[MonthlySalary]:
        """
        Get monthly salary record by ID.
        
        Args:
            monthly_salary_id: Monthly salary record ID
            organization_id: Organization ID
            
        Returns:
            Optional[MonthlySalary]: Monthly salary record if found
        """
        pass
    
    @abstractmethod
    async def get_by_employee_month_year(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Optional[MonthlySalary]:
        """
        Get monthly salary record by employee ID, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            
        Returns:
            Optional[MonthlySalary]: Monthly salary record if found
        """
        pass
    
    @abstractmethod
    async def get_by_employee(
        self, 
        employee_id: EmployeeId, 
        organization_id: str,
        limit: int = 12,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get all monthly salary records for an employee.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[MonthlySalary]: List of monthly salary records
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
        Get all monthly salary records for a specific month and year.
        
        Args:
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[MonthlySalary]: List of monthly salary records
        """
        pass
    
    @abstractmethod
    async def get_by_tax_year(
        self, 
        tax_year: TaxYear,
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get all monthly salary records for a tax year.
        
        Args:
            tax_year: Tax year
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[MonthlySalary]: List of monthly salary records
        """
        pass
    
    @abstractmethod
    async def search(
        self, 
        organization_id: str,
        employee_id: Optional[EmployeeId] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        tax_year: Optional[TaxYear] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Search monthly salary records with filters.
        
        Args:
            organization_id: Organization ID
            employee_id: Optional employee ID filter
            month: Optional month filter (1-12)
            year: Optional year filter
            tax_year: Optional tax year filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[MonthlySalary]: List of matching monthly salary records
        """
        pass
    
    @abstractmethod
    async def count(
        self, 
        organization_id: str,
        employee_id: Optional[EmployeeId] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        tax_year: Optional[TaxYear] = None
    ) -> int:
        """
        Count monthly salary records with filters.
        
        Args:
            organization_id: Organization ID
            employee_id: Optional employee ID filter
            month: Optional month filter
            year: Optional year filter
            tax_year: Optional tax year filter
            
        Returns:
            int: Number of matching records
        """
        pass
    
    @abstractmethod
    async def delete(self, monthly_salary_id: str, organization_id: str) -> bool:
        """
        Delete a monthly salary record.
        
        Args:
            monthly_salary_id: Monthly salary record ID
            organization_id: Organization ID
            
        Returns:
            bool: True if record was deleted
        """
        pass
    
    @abstractmethod
    async def exists(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int,
        organization_id: str
    ) -> bool:
        """
        Check if monthly salary record exists for employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            
        Returns:
            bool: True if record exists
        """
        pass
    
    @abstractmethod
    async def get_by_employee_and_period(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> Optional[MonthlySalary]:
        """Get monthly salary by employee and period."""
        pass
    
    @abstractmethod
    async def get_by_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str,
        status: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MonthlySalary]:
        """Get monthly salaries for a period with optional filtering."""
        pass
    
    @abstractmethod
    async def get_summary_by_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> dict:
        """Get summary statistics for a period."""
        pass
    
    @abstractmethod
    async def get_all_employees_for_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> List[str]:
        """Get all employee IDs that should have salary records for a period."""
        pass
    
    @abstractmethod
    async def bulk_save(
        self, 
        monthly_salaries: List[MonthlySalary], 
        organisation_id: str
    ) -> List[MonthlySalary]:
        """Save multiple monthly salary records."""
        pass
    
    @abstractmethod
    async def update_status(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Optional[MonthlySalary]:
        """Update the status of a monthly salary record."""
        pass
    
    @abstractmethod
    async def mark_payment(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        payment_type: str,
        payment_reference: Optional[str] = None,
        payment_notes: Optional[str] = None,
        paid_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Optional[MonthlySalary]:
        """Mark payment for a monthly salary record."""
        pass
    
    @abstractmethod
    async def delete(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> bool:
        """Delete a monthly salary record."""
        pass
    
    @abstractmethod
    async def exists(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> bool:
        """Check if a monthly salary record exists."""
        pass 