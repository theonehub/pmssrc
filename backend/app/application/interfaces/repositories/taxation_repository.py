"""
Taxation Repository Interfaces
Repository abstractions for taxation data access operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from application.dto.taxation_dto import (
    TaxationCreateRequestDTO,
    TaxationUpdateRequestDTO,
    TaxationResponseDTO,
    TaxSearchFiltersDTO,
    TaxStatisticsDTO,
    TaxProjectionDTO,
    TaxComparisonDTO,
    LWPAdjustmentRequestDTO
)


class TaxationCommandRepository(ABC):
    """
    Command repository for taxation write operations.
    
    Follows SOLID principles:
    - SRP: Only handles taxation write operations
    - OCP: Can be extended with new implementations
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    async def create_taxation(
        self,
        request: TaxationCreateRequestDTO,
        hostname: str
    ) -> TaxationResponseDTO:
        """
        Create a new taxation record.
        
        Args:
            request: Taxation creation request
            hostname: Organization hostname
            
        Returns:
            Created taxation response
        """
        pass
    
    @abstractmethod
    async def update_taxation(
        self,
        employee_id: str,
        request: TaxationUpdateRequestDTO,
        hostname: str
    ) -> TaxationResponseDTO:
        """
        Update an existing taxation record.
        
        Args:
            employee_id: Employee identifier
            request: Taxation update request
            hostname: Organization hostname
            
        Returns:
            Updated taxation response
        """
        pass
    
    @abstractmethod
    async def delete_taxation(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> bool:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def update_tax_calculation(
        self,
        employee_id: str,
        tax_year: str,
        calculation_result: Dict[str, Any],
        hostname: str
    ) -> bool:
        """
        Update taxation record with calculation results.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            calculation_result: Tax calculation results
            hostname: Organization hostname
            
        Returns:
            True if updated successfully
        """
        pass
    
    @abstractmethod
    async def update_filing_status(
        self,
        employee_id: str,
        tax_year: str,
        filing_status: str,
        hostname: str,
        updated_by: str
    ) -> bool:
        """
        Update taxation filing status.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            filing_status: New filing status
            hostname: Organization hostname
            updated_by: User making the update
            
        Returns:
            True if updated successfully
        """
        pass
    
    @abstractmethod
    async def save_lwp_adjustment(
        self,
        employee_id: str,
        tax_year: str,
        adjustment_data: Dict[str, Any],
        hostname: str
    ) -> bool:
        """
        Save LWP (Leave Without Pay) adjustment.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            adjustment_data: LWP adjustment data
            hostname: Organization hostname
            
        Returns:
            True if saved successfully
        """
        pass


class TaxationQueryRepository(ABC):
    """
    Query repository for taxation read operations.
    
    Follows SOLID principles:
    - SRP: Only handles taxation read operations
    - OCP: Can be extended with new implementations
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    async def get_taxation_by_employee(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> Optional[TaxationResponseDTO]:
        """
        Get taxation record by employee and tax year.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Taxation response or None if not found
        """
        pass
    
    @abstractmethod
    async def get_current_taxation(
        self,
        employee_id: str,
        hostname: str
    ) -> Optional[TaxationResponseDTO]:
        """
        Get current year taxation record for an employee.
        
        Args:
            employee_id: Employee identifier
            hostname: Organization hostname
            
        Returns:
            Current taxation response or None if not found
        """
        pass
    
    @abstractmethod
    async def search_taxation_records(
        self,
        filters: TaxSearchFiltersDTO,
        hostname: str
    ) -> List[TaxationResponseDTO]:
        """
        Search taxation records with filters.
        
        Args:
            filters: Search filters
            hostname: Organization hostname
            
        Returns:
            List of matching taxation records
        """
        pass
    
    @abstractmethod
    async def get_employee_tax_history(
        self,
        employee_id: str,
        hostname: str
    ) -> List[TaxationResponseDTO]:
        """
        Get tax history for an employee across all years.
        
        Args:
            employee_id: Employee identifier
            hostname: Organization hostname
            
        Returns:
            List of taxation records for the employee
        """
        pass
    
    @abstractmethod
    async def get_taxation_by_regime(
        self,
        regime: str,
        tax_year: str,
        hostname: str
    ) -> List[TaxationResponseDTO]:
        """
        Get taxation records by regime and tax year.
        
        Args:
            regime: Tax regime ('old' or 'new')
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            List of taxation records for the regime
        """
        pass
    
    @abstractmethod
    async def get_taxation_by_department(
        self,
        department: str,
        tax_year: str,
        hostname: str
    ) -> List[TaxationResponseDTO]:
        """
        Get taxation records by department and tax year.
        
        Args:
            department: Department name
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            List of taxation records for the department
        """
        pass
    
    @abstractmethod
    async def exists_taxation(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> bool:
        """
        Check if taxation record exists.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            True if taxation record exists
        """
        pass


class TaxationCalculationRepository(ABC):
    """
    Repository for taxation calculation operations.
    
    Handles complex tax calculations and projections.
    """
    
    @abstractmethod
    async def calculate_tax(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate tax for an employee.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            force_recalculate: Force recalculation even if already calculated
            
        Returns:
            Tax calculation results
        """
        pass
    
    @abstractmethod
    async def calculate_tax_comparison(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> TaxComparisonDTO:
        """
        Calculate tax comparison between old and new regime.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Tax comparison between regimes
        """
        pass
    
    @abstractmethod
    async def calculate_tax_projection(
        self,
        employee_id: str,
        projection_period: str,
        hostname: str
    ) -> TaxProjectionDTO:
        """
        Calculate tax projection for future periods.
        
        Args:
            employee_id: Employee identifier
            projection_period: Projection period (monthly, quarterly, annual)
            hostname: Organization hostname
            
        Returns:
            Tax projection data
        """
        pass
    
    @abstractmethod
    async def calculate_lwp_adjustment(
        self,
        employee_id: str,
        tax_year: str,
        lwp_days: int,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Calculate LWP tax adjustment.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            lwp_days: Number of LWP days
            hostname: Organization hostname
            
        Returns:
            LWP adjustment calculation results
        """
        pass
    
    @abstractmethod
    async def get_salary_projection(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get salary projection considering mid-year changes.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Salary projection data or None if not available
        """
        pass


class TaxationAnalyticsRepository(ABC):
    """
    Repository for taxation analytics and reporting.
    
    Handles aggregation and statistical operations.
    """
    
    @abstractmethod
    async def get_tax_statistics(
        self,
        tax_year: str,
        hostname: str,
        department: Optional[str] = None
    ) -> TaxStatisticsDTO:
        """
        Get tax statistics for a tax year.
        
        Args:
            tax_year: Tax year
            hostname: Organization hostname
            department: Optional department filter
            
        Returns:
            Tax statistics
        """
        pass
    
    @abstractmethod
    async def get_regime_adoption_stats(
        self,
        tax_year: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Get tax regime adoption statistics.
        
        Args:
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Regime adoption statistics
        """
        pass
    
    @abstractmethod
    async def get_top_taxpayers(
        self,
        tax_year: str,
        hostname: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top taxpayers for a tax year.
        
        Args:
            tax_year: Tax year
            hostname: Organization hostname
            limit: Number of top taxpayers to return
            
        Returns:
            List of top taxpayers
        """
        pass
    
    @abstractmethod
    async def get_department_tax_summary(
        self,
        tax_year: str,
        hostname: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get department-wise tax summary.
        
        Args:
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Department-wise tax summary
        """
        pass
    
    @abstractmethod
    async def get_tax_trend_analysis(
        self,
        employee_id: str,
        hostname: str,
        years: int = 3
    ) -> Dict[str, Any]:
        """
        Get tax trend analysis for an employee.
        
        Args:
            employee_id: Employee identifier
            hostname: Organization hostname
            years: Number of years for trend analysis
            
        Returns:
            Tax trend analysis data
        """
        pass
    
    @abstractmethod
    async def get_compliance_metrics(
        self,
        tax_year: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Get tax compliance metrics.
        
        Args:
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Compliance metrics
        """
        pass


class TaxationAuditRepository(ABC):
    """
    Repository for taxation audit and tracking operations.
    """
    
    @abstractmethod
    async def log_calculation_event(
        self,
        employee_id: str,
        tax_year: str,
        event_type: str,
        event_data: Dict[str, Any],
        hostname: str,
        user_id: str
    ) -> bool:
        """
        Log taxation calculation event for audit.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            event_type: Type of event
            event_data: Event data
            hostname: Organization hostname
            user_id: User performing the action
            
        Returns:
            True if logged successfully
        """
        pass
    
    @abstractmethod
    async def get_calculation_history(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> List[Dict[str, Any]]:
        """
        Get calculation history for audit trail.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            List of calculation events
        """
        pass
    
    @abstractmethod
    async def track_regime_changes(
        self,
        employee_id: str,
        tax_year: str,
        old_regime: str,
        new_regime: str,
        hostname: str,
        changed_by: str
    ) -> bool:
        """
        Track tax regime changes for audit.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            old_regime: Previous regime
            new_regime: New regime
            hostname: Organization hostname
            changed_by: User making the change
            
        Returns:
            True if tracked successfully
        """
        pass 