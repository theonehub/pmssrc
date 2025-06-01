"""
Employee Leave Repository Interfaces
Repository abstractions for employee leave data access following SOLID principles
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.domain.entities.employee_leave import EmployeeLeave
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.date_range import DateRange
from models.leave_model import LeaveStatus


class EmployeeLeaveCommandRepository(ABC):
    """
    Command repository interface for employee leave write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new write operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    def save(self, employee_leave: EmployeeLeave) -> bool:
        """
        Save employee leave application.
        
        Args:
            employee_leave: Employee leave entity to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update(self, employee_leave: EmployeeLeave) -> bool:
        """
        Update existing employee leave application.
        
        Args:
            employee_leave: Employee leave entity to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, leave_id: str) -> bool:
        """
        Delete employee leave application.
        
        Args:
            leave_id: Leave application identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update_status(
        self, 
        leave_id: str, 
        status: LeaveStatus, 
        approved_by: str,
        comments: Optional[str] = None
    ) -> bool:
        """
        Update leave application status.
        
        Args:
            leave_id: Leave application identifier
            status: New status
            approved_by: User who approved/rejected
            comments: Approval/rejection comments
            
        Returns:
            True if successful, False otherwise
        """
        pass


class EmployeeLeaveQueryRepository(ABC):
    """
    Query repository interface for employee leave read operations.
    """
    
    @abstractmethod
    def get_by_id(self, leave_id: str) -> Optional[EmployeeLeave]:
        """
        Get employee leave by ID.
        
        Args:
            leave_id: Leave application identifier
            
        Returns:
            EmployeeLeave entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_employee_id(
        self, 
        employee_id: EmployeeId,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """
        Get employee leaves by employee ID.
        
        Args:
            employee_id: Employee identifier
            status_filter: Optional status filter
            limit: Optional limit on results
            
        Returns:
            List of EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    def get_by_manager_id(
        self, 
        manager_id: str,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """
        Get employee leaves by manager ID.
        
        Args:
            manager_id: Manager identifier
            status_filter: Optional status filter
            limit: Optional limit on results
            
        Returns:
            List of EmployeeLeave entities for employees under the manager
        """
        pass
    
    @abstractmethod
    def get_by_date_range(
        self, 
        date_range: DateRange,
        employee_id: Optional[EmployeeId] = None,
        status_filter: Optional[LeaveStatus] = None
    ) -> List[EmployeeLeave]:
        """
        Get employee leaves by date range.
        
        Args:
            date_range: Date range to search
            employee_id: Optional employee filter
            status_filter: Optional status filter
            
        Returns:
            List of EmployeeLeave entities within the date range
        """
        pass
    
    @abstractmethod
    def get_by_month(
        self, 
        employee_id: EmployeeId,
        month: int,
        year: int
    ) -> List[EmployeeLeave]:
        """
        Get employee leaves for a specific month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            
        Returns:
            List of EmployeeLeave entities for the month
        """
        pass
    
    @abstractmethod
    def get_overlapping_leaves(
        self, 
        employee_id: EmployeeId,
        date_range: DateRange,
        exclude_leave_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """
        Get leaves that overlap with the given date range.
        
        Args:
            employee_id: Employee identifier
            date_range: Date range to check for overlaps
            exclude_leave_id: Optional leave ID to exclude from results
            
        Returns:
            List of overlapping EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    def get_pending_approvals(
        self, 
        manager_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """
        Get pending leave approvals.
        
        Args:
            manager_id: Optional manager filter
            limit: Optional limit on results
            
        Returns:
            List of pending EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    def search(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        leave_type: Optional[str] = None,
        status: Optional[LeaveStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeLeave]:
        """
        Search employee leaves with filters.
        
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            leave_type: Optional leave type filter
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            month: Optional month filter
            year: Optional year filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    def count_by_filters(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        leave_type: Optional[str] = None,
        status: Optional[LeaveStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> int:
        """
        Count employee leaves matching filters.
        
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            leave_type: Optional leave type filter
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            Count of matching records
        """
        pass


class EmployeeLeaveAnalyticsRepository(ABC):
    """
    Analytics repository interface for employee leave reporting and analytics.
    """
    
    @abstractmethod
    def get_leave_statistics(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get leave statistics.
        
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            year: Optional year filter
            
        Returns:
            Dictionary containing leave statistics
        """
        pass
    
    @abstractmethod
    def get_leave_type_breakdown(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get leave type breakdown.
        
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            year: Optional year filter
            
        Returns:
            Dictionary mapping leave types to counts
        """
        pass
    
    @abstractmethod
    def get_monthly_leave_trends(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get monthly leave trends.
        
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            year: Optional year filter
            
        Returns:
            Dictionary mapping months to leave counts
        """
        pass
    
    @abstractmethod
    def get_team_leave_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get team leave summary for a manager.
        
        Args:
            manager_id: Manager identifier
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            List of team member leave summaries
        """
        pass
    
    @abstractmethod
    def calculate_lwp_for_employee(
        self,
        employee_id: EmployeeId,
        month: int,
        year: int
    ) -> int:
        """
        Calculate Leave Without Pay (LWP) for an employee.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            
        Returns:
            Number of LWP days
        """
        pass


class EmployeeLeaveBalanceRepository(ABC):
    """
    Repository interface for employee leave balance operations.
    """
    
    @abstractmethod
    def get_leave_balance(self, employee_id: EmployeeId) -> Dict[str, int]:
        """
        Get leave balance for an employee.
        
        Args:
            employee_id: Employee identifier
            
        Returns:
            Dictionary mapping leave types to balances
        """
        pass
    
    @abstractmethod
    def update_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_type: str, 
        balance_change: int
    ) -> bool:
        """
        Update leave balance for an employee.
        
        Args:
            employee_id: Employee identifier
            leave_type: Leave type
            balance_change: Change in balance (positive or negative)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def set_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_balances: Dict[str, int]
    ) -> bool:
        """
        Set leave balances for an employee.
        
        Args:
            employee_id: Employee identifier
            leave_balances: Dictionary mapping leave types to balances
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_team_leave_balances(self, manager_id: str) -> List[Dict[str, Any]]:
        """
        Get leave balances for all team members under a manager.
        
        Args:
            manager_id: Manager identifier
            
        Returns:
            List of employee leave balance summaries
        """
        pass 