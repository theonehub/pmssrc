"""
Salary Package Repository Interface
Abstract repository interface for salary package operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.entities.taxation.taxation_record import SalaryPackageRecord


class SalaryPackageRepository(ABC):
    """
    Abstract repository interface for salary package operations.
    
    Defines the contract for persistence operations on salary package records.
    """
    
    @abstractmethod
    async def save(self, salary_package_record: SalaryPackageRecord, organization_id: str) -> SalaryPackageRecord:
        """
        Save or update a salary package record.
        
        Args:
            salary_package_record: Salary package record to save
            
        Returns:
            SalaryPackageRecord: Saved salary package record
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, salary_package_id: str, organization_id: str) -> Optional[SalaryPackageRecord]:
        """
        Get salary package record by ID.
        
        Args:
            salary_package_id: Salary package record ID
            organization_id: Organization ID
            
        Returns:
            Optional[SalaryPackageRecord]: Salary package record if found
        """
        pass
    
    @abstractmethod
    async def get_salary_package_record(self, employee_id: str, tax_year: str, organization_id: str) -> Optional[SalaryPackageRecord]:
        """
        Get salary package record by employee ID and tax year.
        
        Args:
            employee_id: Employee ID as string
            tax_year: Tax year as string
            organization_id: Organization ID
            
        Returns:
            Optional[SalaryPackageRecord]: Salary package record if found
        """
        pass
    
    @abstractmethod
    async def get_by_user_and_year(self, 
                                 employee_id: EmployeeId, 
                                 tax_year: TaxYear,
                                 organization_id: str) -> Optional[SalaryPackageRecord]:
        """
        Get salary package record by user and tax year.
        
        Args:
            employee_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            Optional[SalaryPackageRecord]: Salary package record if found
        """
        pass
    
    @abstractmethod
    async def get_by_user(self, 
                        employee_id: EmployeeId, 
                        organization_id: str,
                        limit: int = 10,
                        offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Get all salary package records for a user.
        
        Args:
            employee_id: User ID
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of salary package records
        """
        pass
    
    @abstractmethod
    async def get_by_tax_year(self, 
                            tax_year: TaxYear,
                            organization_id: str,
                            limit: int = 100,
                            offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Get all salary package records for a tax year.
        
        Args:
            tax_year: Tax year
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of salary package records
        """
        pass
    
    @abstractmethod
    async def get_by_organization(self, 
                                organization_id: str,
                                limit: int = 100,
                                offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Get all salary package records for an organization.
        
        Args:
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of salary package records
        """
        pass
    
    @abstractmethod
    async def search(self, 
                   organization_id: str,
                   employee_id: Optional[EmployeeId] = None,
                   tax_year: Optional[TaxYear] = None,
                   regime: Optional[str] = None,
                   is_final: Optional[bool] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Search salary package records with filters.
        
        Args:
            organization_id: Organization ID
            employee_id: Optional user ID filter
            tax_year: Optional tax year filter
            regime: Optional regime filter ('old' or 'new')
            is_final: Optional finalization status filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of matching salary package records
        """
        pass
    
    @abstractmethod
    async def count(self, 
                  organization_id: str,
                  employee_id: Optional[EmployeeId] = None,
                  tax_year: Optional[TaxYear] = None,
                  regime: Optional[str] = None,
                  is_final: Optional[bool] = None) -> int:
        """
        Count salary package records with filters.
        
        Args:
            organization_id: Organization ID
            employee_id: Optional user ID filter
            tax_year: Optional tax year filter
            regime: Optional regime filter
            is_final: Optional finalization status filter
            
        Returns:
            int: Number of matching records
        """
        pass
    
    @abstractmethod
    async def delete(self, salary_package_id: str, organization_id: str) -> bool:
        """
        Delete a salary package record.
        
        Args:
            salary_package_id: Salary package record ID
            organization_id: Organization ID
            
        Returns:
            bool: True if record was deleted
        """
        pass
    
    @abstractmethod
    async def exists(self, 
                   employee_id: EmployeeId, 
                   tax_year: TaxYear,
                   organization_id: str) -> bool:
        """
        Check if salary package record exists for user and tax year.
        
        Args:
            employee_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            bool: True if record exists
        """
        pass 