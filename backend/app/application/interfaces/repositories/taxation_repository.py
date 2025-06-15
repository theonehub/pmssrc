"""
Taxation Repository Interface
Abstract repository interface for taxation operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.entities.taxation_record import TaxationRecord


class TaxationRepository(ABC):
    """
    Abstract repository interface for taxation operations.
    
    Defines the contract for persistence operations on taxation records.
    """
    
    @abstractmethod
    async def save(self, taxation_record: TaxationRecord, organization_id: str) -> TaxationRecord:
        """
        Save or update a taxation record.
        
        Args:
            taxation_record: Taxation record to save
            
        Returns:
            TaxationRecord: Saved taxation record
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, taxation_id: str, organization_id: str) -> Optional[TaxationRecord]:
        """
        Get taxation record by ID.
        
        Args:
            taxation_id: Taxation record ID
            organization_id: Organization ID
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found
        """
        pass
    
    @abstractmethod
    async def get_by_user_and_year(self, 
                                 user_id: EmployeeId, 
                                 tax_year: TaxYear,
                                 organization_id: str) -> Optional[TaxationRecord]:
        """
        Get taxation record by user and tax year.
        
        Args:
            user_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found
        """
        pass
    
    @abstractmethod
    async def get_by_user(self, 
                        user_id: EmployeeId, 
                        organization_id: str,
                        limit: int = 10,
                        offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for a user.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_by_tax_year(self, 
                            tax_year: TaxYear,
                            organization_id: str,
                            limit: int = 100,
                            offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for a tax year.
        
        Args:
            tax_year: Tax year
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_by_organization(self, 
                                organization_id: str,
                                limit: int = 100,
                                offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for an organization.
        
        Args:
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def search(self, 
                   organization_id: str,
                   user_id: Optional[EmployeeId] = None,
                   tax_year: Optional[TaxYear] = None,
                   regime: Optional[str] = None,
                   is_final: Optional[bool] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[TaxationRecord]:
        """
        Search taxation records with filters.
        
        Args:
            organization_id: Organization ID
            user_id: Optional user ID filter
            tax_year: Optional tax year filter
            regime: Optional regime filter ('old' or 'new')
            is_final: Optional finalization status filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of matching taxation records
        """
        pass
    
    @abstractmethod
    async def count(self, 
                  organization_id: str,
                  user_id: Optional[EmployeeId] = None,
                  tax_year: Optional[TaxYear] = None,
                  regime: Optional[str] = None,
                  is_final: Optional[bool] = None) -> int:
        """
        Count taxation records with filters.
        
        Args:
            organization_id: Organization ID
            user_id: Optional user ID filter
            tax_year: Optional tax year filter
            regime: Optional regime filter
            is_final: Optional finalization status filter
            
        Returns:
            int: Number of matching records
        """
        pass
    
    @abstractmethod
    async def delete(self, taxation_id: str, organization_id: str) -> bool:
        """
        Delete a taxation record.
        
        Args:
            taxation_id: Taxation record ID
            organization_id: Organization ID
            
        Returns:
            bool: True if record was deleted
        """
        pass
    
    @abstractmethod
    async def exists(self, 
                   user_id: EmployeeId, 
                   tax_year: TaxYear,
                   organization_id: str) -> bool:
        """
        Check if taxation record exists for user and tax year.
        
        Args:
            user_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            bool: True if record exists
        """
        pass 