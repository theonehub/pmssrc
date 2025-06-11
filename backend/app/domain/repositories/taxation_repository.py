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
    async def save_taxation_record(self, record: TaxationRecord) -> None:
        """
        Save a taxation record.
        
        Args:
            record: Taxation record to save
        """
        pass
    
    @abstractmethod
    async def get_taxation_record(self, 
                                employee_id: str,
                                financial_year: int) -> Optional[TaxationRecord]:
        """
        Get a taxation record.
        
        Args:
            employee_id: Employee ID
            financial_year: Financial year
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_taxation_records(self,
                                 employee_id: str,
                                 start_year: Optional[int] = None,
                                 end_year: Optional[int] = None) -> List[TaxationRecord]:
        """
        Get taxation records for an employee.
        
        Args:
            employee_id: Employee ID
            start_year: Start financial year (optional)
            end_year: End financial year (optional)
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_regime(self,
                                           regime: TaxRegimeType,
                                           financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by regime.
        
        Args:
            regime: Tax regime
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_organisation(self,
                                                 organisation_id: str,
                                                 financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by organisation.
        
        Args:
            organisation_id: Organisation ID
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def delete_taxation_record(self,
                                   employee_id: str,
                                   financial_year: int) -> None:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee ID
            financial_year: Financial year
        """
        pass
    
    @abstractmethod
    async def update_taxation_record(self, record: TaxationRecord) -> None:
        """
        Update a taxation record.
        
        Args:
            record: Taxation record to update
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_date_range(self,
                                               start_date: date,
                                               end_date: date) -> List[TaxationRecord]:
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
                                                        financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by tax liability range.
        
        Args:
            min_tax: Minimum tax liability
            max_tax: Maximum tax liability
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_income_range(self,
                                                 min_income: float,
                                                 max_income: float,
                                                 financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by income range.
        
        Args:
            min_income: Minimum income
            max_income: Maximum income
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_deduction_range(self,
                                                    min_deduction: float,
                                                    max_deduction: float,
                                                    financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by deduction range.
        
        Args:
            min_deduction: Minimum deduction
            max_deduction: Maximum deduction
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass
    
    @abstractmethod
    async def get_taxation_records_by_exemption_range(self,
                                                    min_exemption: float,
                                                    max_exemption: float,
                                                    financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by exemption range.
        
        Args:
            min_exemption: Minimum exemption
            max_exemption: Maximum exemption
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        pass 