"""
Taxation Repository Interfaces
Defines contracts for taxation data persistence operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from domain.entities.taxation import Taxation
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.tax_regime import TaxRegime


class TaxationCommandRepository(ABC):
    """
    Command repository interface for taxation write operations.
    
    Follows SOLID principles:
    - SRP: Only handles taxation write operations
    - OCP: Can be implemented by different storage systems
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    def save(self, taxation: Taxation) -> bool:
        """
        Save taxation record.
        
        Args:
            taxation: Taxation entity to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def update(self, taxation: Taxation) -> bool:
        """
        Update existing taxation record.
        
        Args:
            taxation: Taxation entity to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, employee_id: EmployeeId, tax_year: str) -> bool:
        """
        Delete taxation record.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class TaxationQueryRepository(ABC):
    """
    Query repository interface for taxation read operations.
    """
    
    @abstractmethod
    def get_by_employee_and_year(
        self, 
        employee_id: EmployeeId, 
        tax_year: str
    ) -> Optional[Taxation]:
        """
        Get taxation record by employee ID and tax year.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            
        Returns:
            Taxation entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_employee(self, employee_id: EmployeeId) -> List[Taxation]:
        """
        Get all taxation records for an employee.
        
        Args:
            employee_id: Employee identifier
            
        Returns:
            List of taxation entities
        """
        pass
    
    @abstractmethod
    def get_by_tax_year(self, tax_year: str) -> List[Taxation]:
        """
        Get all taxation records for a tax year.
        
        Args:
            tax_year: Tax year
            
        Returns:
            List of taxation entities
        """
        pass
    
    @abstractmethod
    def exists(self, employee_id: EmployeeId, tax_year: str) -> bool:
        """
        Check if taxation record exists.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            
        Returns:
            True if record exists, False otherwise
        """
        pass 