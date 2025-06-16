"""
Payout Repository Interfaces
Repository interfaces for payout operations following CQRS pattern
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from app.domain.entities.taxation.payout import PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus
from app.application.dto.payroll_dto import PayoutSearchFiltersDTO


class PayoutCommandRepository(ABC):
    """Command repository interface for payout write operations"""
    
    @abstractmethod
    async def create_payout(self, payout: PayoutCreate, hostname: str) -> PayoutInDB:
        """
        Create a new payout record
        
        Args:
            payout: Payout data to create
            hostname: Organisation hostname
            
        Returns:
            Created payout record
            
        Raises:
            PayoutAlreadyExistsError: If payout already exists for the period
            ValidationError: If payout data is invalid
        """
        pass
    
    @abstractmethod
    async def update_payout(self, payout_id: str, update: PayoutUpdate, 
                           hostname: str, updated_by: str) -> PayoutInDB:
        """
        Update an existing payout record
        
        Args:
            payout_id: ID of payout to update
            update: Update data
            hostname: Organisation hostname
            updated_by: User making the update
            
        Returns:
            Updated payout record
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
            ValidationError: If update data is invalid
        """
        pass
    
    @abstractmethod
    async def update_payout_status(self, payout_id: str, status: PayoutStatus,
                                  hostname: str, updated_by: str, 
                                  reason: Optional[str] = None) -> bool:
        """
        Update payout status
        
        Args:
            payout_id: ID of payout to update
            status: New status
            hostname: Organisation hostname
            updated_by: User making the update
            reason: Optional reason for status change
            
        Returns:
            True if successful
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
            InvalidStatusTransitionError: If status transition is invalid
        """
        pass
    
    @abstractmethod
    async def bulk_create_payouts(self, payouts: List[PayoutCreate], 
                                 hostname: str, created_by: str) -> List[PayoutInDB]:
        """
        Create multiple payout records in bulk
        
        Args:
            payouts: List of payout data to create
            hostname: Organisation hostname
            created_by: User creating the payouts
            
        Returns:
            List of created payout records
            
        Raises:
            BulkOperationError: If some creations fail
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(self, payout_ids: List[str], status: PayoutStatus,
                                hostname: str, updated_by: str) -> Dict[str, bool]:
        """
        Update status for multiple payouts
        
        Args:
            payout_ids: List of payout IDs to update
            status: New status
            hostname: Organisation hostname
            updated_by: User making the update
            
        Returns:
            Dictionary mapping payout_id to success status
        """
        pass
    
    @abstractmethod
    async def delete_payout(self, payout_id: str, hostname: str, 
                           deleted_by: str) -> bool:
        """
        Soft delete a payout record
        
        Args:
            payout_id: ID of payout to delete
            hostname: Organisation hostname
            deleted_by: User deleting the payout
            
        Returns:
            True if successful
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
            PayoutCannotBeDeletedError: If payout is in non-deletable state
        """
        pass


class PayoutQueryRepository(ABC):
    """Query repository interface for payout read operations"""
    
    @abstractmethod
    async def get_by_id(self, payout_id: str, hostname: str) -> Optional[PayoutInDB]:
        """
        Get payout by ID
        
        Args:
            payout_id: ID of payout to retrieve
            hostname: Organisation hostname
            
        Returns:
            Payout record if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_employee_payouts(self, employee_id: str, hostname: str,
                                  year: Optional[int] = None,
                                  month: Optional[int] = None) -> List[PayoutInDB]:
        """
        Get payouts for a specific employee
        
        Args:
            employee_id: Employee ID
            hostname: Organisation hostname
            year: Optional year filter
            month: Optional month filter
            
        Returns:
            List of payout records
        """
        pass
    
    @abstractmethod
    async def get_monthly_payouts(self, month: int, year: int, hostname: str,
                                 status: Optional[PayoutStatus] = None) -> List[PayoutInDB]:
        """
        Get all payouts for a specific month
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            status: Optional status filter
            
        Returns:
            List of payout records
        """
        pass
    
    @abstractmethod
    async def search_payouts(self, filters: PayoutSearchFiltersDTO,
                           hostname: str) -> Dict[str, Any]:
        """
        Search payouts with filters and pagination
        
        Args:
            filters: Search filters and pagination
            hostname: Organisation hostname
            
        Returns:
            Dictionary with 'payouts', 'total_count', 'page', 'page_size'
        """
        pass
    
    @abstractmethod
    async def check_duplicate_payout(self, employee_id: str, pay_period_start: date,
                                   pay_period_end: date, hostname: str) -> bool:
        """
        Check if payout already exists for employee and period
        
        Args:
            employee_id: Employee ID
            pay_period_start: Start of pay period
            pay_period_end: End of pay period
            hostname: Organisation hostname
            
        Returns:
            True if duplicate exists
        """
        pass
    
    @abstractmethod
    async def get_payout_summary(self, month: int, year: int, 
                                hostname: str) -> Dict[str, Any]:
        """
        Get payout summary for a month
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Summary statistics
        """
        pass
    
    @abstractmethod
    async def get_employee_payout_history(self, employee_id: str, year: int,
                                        hostname: str) -> Dict[str, Any]:
        """
        Get comprehensive payout history for employee
        
        Args:
            employee_id: Employee ID
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Payout history with statistics
        """
        pass
    
    @abstractmethod
    async def get_payouts_by_status(self, status: PayoutStatus, hostname: str,
                                   limit: Optional[int] = None) -> List[PayoutInDB]:
        """
        Get payouts by status
        
        Args:
            status: Payout status
            hostname: Organisation hostname
            limit: Optional limit on results
            
        Returns:
            List of payout records
        """
        pass
    
    @abstractmethod
    async def get_pending_approvals(self, hostname: str, 
                                   approver_id: Optional[str] = None) -> List[PayoutInDB]:
        """
        Get payouts pending approval
        
        Args:
            hostname: Organisation hostname
            approver_id: Optional approver filter
            
        Returns:
            List of payouts pending approval
        """
        pass


class PayoutAnalyticsRepository(ABC):
    """Analytics repository interface for payout reporting and analytics"""
    
    @abstractmethod
    async def get_department_wise_summary(self, month: int, year: int,
                                        hostname: str) -> Dict[str, Dict[str, float]]:
        """
        Get department-wise payout summary
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Department-wise breakdown
        """
        pass
    
    @abstractmethod
    async def get_monthly_trends(self, start_month: int, start_year: int,
                               end_month: int, end_year: int,
                               hostname: str) -> List[Dict[str, Any]]:
        """
        Get monthly payout trends
        
        Args:
            start_month: Start month
            start_year: Start year
            end_month: End month
            end_year: End year
            hostname: Organisation hostname
            
        Returns:
            Monthly trend data
        """
        pass
    
    @abstractmethod
    async def get_salary_distribution(self, month: int, year: int,
                                    hostname: str) -> Dict[str, Any]:
        """
        Get salary distribution analytics
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Salary distribution data
        """
        pass
    
    @abstractmethod
    async def get_top_earners(self, month: int, year: int, hostname: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top earners for a month
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            limit: Number of top earners to return
            
        Returns:
            List of top earners
        """
        pass
    
    @abstractmethod
    async def get_deduction_analysis(self, month: int, year: int,
                                   hostname: str) -> Dict[str, float]:
        """
        Get deduction analysis
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Deduction breakdown
        """
        pass
    
    @abstractmethod
    async def get_compliance_metrics(self, month: int, year: int,
                                   hostname: str) -> Dict[str, Any]:
        """
        Get compliance metrics
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Compliance metrics
        """
        pass


class PayoutScheduleRepository(ABC):
    """Repository interface for payout schedule operations"""
    
    @abstractmethod
    async def create_schedule(self, schedule_data: Dict[str, Any],
                            hostname: str, created_by: str) -> str:
        """
        Create payout schedule
        
        Args:
            schedule_data: Schedule configuration
            hostname: Organisation hostname
            created_by: User creating the schedule
            
        Returns:
            Schedule ID
        """
        pass
    
    @abstractmethod
    async def get_schedule(self, month: int, year: int,
                         hostname: str) -> Optional[Dict[str, Any]]:
        """
        Get payout schedule for month/year
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Schedule data if exists
        """
        pass
    
    @abstractmethod
    async def update_schedule(self, schedule_id: str, update_data: Dict[str, Any],
                            hostname: str, updated_by: str) -> bool:
        """
        Update payout schedule
        
        Args:
            schedule_id: Schedule ID
            update_data: Update data
            hostname: Organisation hostname
            updated_by: User making the update
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_active_schedules(self, hostname: str) -> List[Dict[str, Any]]:
        """
        Get all active payout schedules
        
        Args:
            hostname: Organisation hostname
            
        Returns:
            List of active schedules
        """
        pass


class PayoutAuditRepository(ABC):
    """Repository interface for payout audit operations"""
    
    @abstractmethod
    async def log_audit_event(self, event_data: Dict[str, Any],
                            hostname: str) -> str:
        """
        Log audit event
        
        Args:
            event_data: Audit event data
            hostname: Organisation hostname
            
        Returns:
            Audit record ID
        """
        pass
    
    @abstractmethod
    async def get_payout_audit_trail(self, payout_id: str,
                                   hostname: str) -> List[Dict[str, Any]]:
        """
        Get audit trail for a payout
        
        Args:
            payout_id: Payout ID
            hostname: Organisation hostname
            
        Returns:
            List of audit events
        """
        pass
    
    @abstractmethod
    async def get_user_audit_trail(self, employee_id: str, hostname: str,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get audit trail for a user
        
        Args:
            employee_id: User ID
            hostname: Organisation hostname
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of audit events
        """
        pass 