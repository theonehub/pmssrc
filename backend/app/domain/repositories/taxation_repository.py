"""
Taxation Repository Interface
Defines the contract for taxation data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from app.domain.entities.taxation.taxation_record import TaxationRecord
from app.domain.value_objects.taxation.tax_regime import TaxRegimeType


class TaxationRepository(ABC):
    """Repository interface for taxation data access."""
    
    @abstractmethod
    async def save_taxation_record(self, record: TaxationRecord, organization_id: str) -> None:
        """
        Save a taxation record.
        
        Args:
            record: Taxation record to save
            organization_id: Organization ID
        """
        pass
    
    @abstractmethod
    async def get_taxation_record(self, 
                                employee_id: str,
                                tax_year: str,
                                organization_id: str) -> Optional[TaxationRecord]:
        """
        Get a taxation record.
        
        Args:
            employee_id: Employee ID
            tax_year: Tax year
            organization_id: Organization ID
        Returns:
            Optional[TaxationRecord]: Taxation record if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_taxation_records(self,
                                 employee_id: str,
                                 tax_year: str,
                                 organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records for an employee.
        
        Args:
            employee_id: Employee ID
            tax_year: Tax year
            organization_id: Organization ID
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_regime(self,
                                           regime: TaxRegimeType,
                                           tax_year: str,
                                           organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by regime.
        
        Args:
            regime: Tax regime
            tax_year: Tax year
            organization_id: Organization ID
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    
    @abstractmethod
    async def delete_taxation_record(self,
                                   employee_id: str,
                                   tax_year: str,
                                   organization_id: str) -> None:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee ID
            tax_year: Tax year
            organization_id: Organization ID
        """
        pass
    
    @abstractmethod
    async def update_taxation_record(self, record: TaxationRecord, organization_id: str) -> None:
        """
        Update a taxation record.
        
        Args:
            record: Taxation record to update
            organization_id: Organization ID
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_date_range(self,
                                               start_date: date,
                                               end_date: date,
                                               organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_tax_liability_range(self,
                                                        min_tax: float,
                                                        max_tax: float,
                                                        tax_year: str,
                                                        organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by tax liability range.
        
        Args:
            min_tax: Minimum tax liability
            max_tax: Maximum tax liability
            tax_year: Tax year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_income_range(self,
                                                 min_income: float,
                                                 max_income: float,
                                                 tax_year: str,
                                                 organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by income range.
        
        Args:
            min_income: Minimum income
            max_income: Maximum income
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_deduction_range(self,
                                                    min_deduction: float,
                                                    max_deduction: float,
                                                    tax_year: str,
                                                    organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by deduction range.
        
        Args:
            min_deduction: Minimum deduction
            max_deduction: Maximum deduction
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_exemption_range(self,
                                                    min_exemption: float,
                                                    max_exemption: float,
                                                    tax_year: str,
                                                    organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by exemption range.
        
        Args:
            min_exemption: Minimum exemption
            max_exemption: Maximum exemption
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass 