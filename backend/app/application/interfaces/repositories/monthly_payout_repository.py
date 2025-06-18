"""
Monthly Payout Repository Interface
Repository interface for monthly payout operations with LWP integration
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.taxation.monthly_payout import MonthlyPayoutRecord, MonthlyPayoutStatus
from app.application.dto.payroll_dto import PayoutSearchFiltersDTO


class MonthlyPayoutRepository(ABC):
    """Repository interface for monthly payout operations."""
    
    @abstractmethod
    async def create_monthly_payout(
        self, 
        payout_record: MonthlyPayoutRecord, 
        organization_id: str
    ) -> MonthlyPayoutRecord:
        """
        Create a new monthly payout record.
        
        Args:
            payout_record: Monthly payout record to create
            organization_id: Organization ID
            
        Returns:
            Created payout record
            
        Raises:
            PayoutAlreadyExistsError: If payout already exists for employee/month/year
            ValidationError: If payout data is invalid
        """
        pass
    
    @abstractmethod
    async def get_monthly_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Optional[MonthlyPayoutRecord]:
        """
        Get monthly payout by employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            
        Returns:
            Monthly payout record if found
        """
        pass
    
    @abstractmethod
    async def update_monthly_payout(
        self, 
        payout_record: MonthlyPayoutRecord, 
        organization_id: str
    ) -> MonthlyPayoutRecord:
        """
        Update an existing monthly payout record.
        
        Args:
            payout_record: Updated payout record
            organization_id: Organization ID
            
        Returns:
            Updated payout record
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
            ValidationError: If update data is invalid
        """
        pass
    
    @abstractmethod
    async def delete_monthly_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> bool:
        """
        Delete a monthly payout record.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            organization_id: Organization ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
            PayoutCannotBeDeletedError: If payout is in non-deletable state
        """
        pass
    
    @abstractmethod
    async def get_monthly_payouts_by_period(
        self, 
        month: int, 
        year: int, 
        organization_id: str,
        status: Optional[MonthlyPayoutStatus] = None
    ) -> List[MonthlyPayoutRecord]:
        """
        Get all monthly payouts for a specific period.
        
        Args:
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            status: Optional status filter
            
        Returns:
            List of monthly payout records
        """
        pass
    
    @abstractmethod
    async def get_employee_payout_history(
        self, 
        employee_id: str, 
        year: int, 
        organization_id: str
    ) -> List[MonthlyPayoutRecord]:
        """
        Get payout history for an employee for a specific year.
        
        Args:
            employee_id: Employee ID
            year: Year
            organization_id: Organization ID
            
        Returns:
            List of monthly payout records for the year
        """
        pass
    
    @abstractmethod
    async def search_monthly_payouts(
        self, 
        filters: PayoutSearchFiltersDTO, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Search monthly payouts with filters and pagination.
        
        Args:
            filters: Search filters and pagination
            organization_id: Organization ID
            
        Returns:
            Dictionary with 'payouts', 'total_count', 'page', 'page_size'
        """
        pass
    
    @abstractmethod
    async def get_payouts_by_status(
        self, 
        status: MonthlyPayoutStatus, 
        organization_id: str,
        limit: Optional[int] = None
    ) -> List[MonthlyPayoutRecord]:
        """
        Get payouts by status.
        
        Args:
            status: Payout status
            organization_id: Organization ID
            limit: Optional limit on results
            
        Returns:
            List of payout records with the specified status
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        payout_ids: List[str], 
        new_status: MonthlyPayoutStatus, 
        organization_id: str,
        updated_by: str
    ) -> Dict[str, bool]:
        """
        Update status for multiple payouts.
        
        Args:
            payout_ids: List of payout IDs
            new_status: New status
            organization_id: Organization ID
            updated_by: User making the update
            
        Returns:
            Dictionary mapping payout_id to success status
        """
        pass
    
    @abstractmethod
    async def get_payout_summary(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get summary statistics for monthly payouts.
        
        Args:
            month: Month
            year: Year
            organization_id: Organization ID
            
        Returns:
            Summary statistics including totals and breakdowns
        """
        pass
    
    @abstractmethod
    async def get_lwp_analytics(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get LWP analytics for the specified period.
        
        Args:
            month: Month
            year: Year
            organization_id: Organization ID
            
        Returns:
            LWP analytics including impact analysis
        """
        pass
    
    @abstractmethod
    async def check_duplicate_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> bool:
        """
        Check if a payout already exists for employee/month/year.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            organization_id: Organization ID
            
        Returns:
            True if duplicate exists
        """
        pass
    
    @abstractmethod
    async def get_pending_approvals(
        self, 
        organization_id: str,
        approver_id: Optional[str] = None
    ) -> List[MonthlyPayoutRecord]:
        """
        Get payouts pending approval.
        
        Args:
            organization_id: Organization ID
            approver_id: Optional specific approver filter
            
        Returns:
            List of payouts pending approval
        """
        pass
    
    @abstractmethod
    async def get_department_wise_summary(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Get department-wise payout summary.
        
        Args:
            month: Month
            year: Year
            organization_id: Organization ID
            
        Returns:
            Department-wise breakdown of payouts
        """
        pass
    
    @abstractmethod
    async def get_compliance_metrics(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get compliance metrics for payouts.
        
        Args:
            month: Month
            year: Year
            organization_id: Organization ID
            
        Returns:
            Compliance metrics and analysis
        """
        pass
    
    @abstractmethod
    async def archive_old_payouts(
        self, 
        cutoff_date: datetime, 
        organization_id: str
    ) -> int:
        """
        Archive old payout records.
        
        Args:
            cutoff_date: Date before which payouts should be archived
            organization_id: Organization ID
            
        Returns:
            Number of records archived
        """
        pass 