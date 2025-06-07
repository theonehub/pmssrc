"""
Employee Leave Repository Wrapper
Adapts repository implementations to handle hostname and match interface signatures
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date

from app.application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveCommandRepository,
    EmployeeLeaveQueryRepository,
    EmployeeLeaveAnalyticsRepository,
    EmployeeLeaveBalanceRepository
)
from app.domain.entities.employee_leave import EmployeeLeave
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.date_range import DateRange
from app.application.dto.employee_leave_dto import LeaveStatus
from app.infrastructure.repositories.employee_leave_repository_impl import (
    EmployeeLeaveCommandRepositoryImpl,
    EmployeeLeaveQueryRepositoryImpl,
    EmployeeLeaveAnalyticsRepositoryImpl,
    EmployeeLeaveBalanceRepositoryImpl
)


class EmployeeLeaveCommandRepositoryWrapper(EmployeeLeaveCommandRepository):
    """Wrapper for command repository that handles hostname"""
    
    def __init__(self, database_connector, hostname: str = "default"):
        self._impl = EmployeeLeaveCommandRepositoryImpl(database_connector)
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
    
    def save(self, employee_leave: EmployeeLeave) -> bool:
        """Save employee leave application"""
        # Temporarily modify the implementation to use our hostname
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.save(employee_leave)
        finally:
            self._impl._get_collection = original_get_collection
    
    def update(self, employee_leave: EmployeeLeave) -> bool:
        """Update existing employee leave application"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.update(employee_leave)
        finally:
            self._impl._get_collection = original_get_collection
    
    def delete(self, leave_id: str) -> bool:
        """Delete employee leave application"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.delete(leave_id)
        finally:
            self._impl._get_collection = original_get_collection
    
    def update_status(
        self, 
        leave_id: str, 
        status: LeaveStatus, 
        approved_by: str,
        comments: Optional[str] = None
    ) -> bool:
        """Update leave application status"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.update_status(leave_id, status, approved_by, comments)
        finally:
            self._impl._get_collection = original_get_collection


class EmployeeLeaveQueryRepositoryWrapper(EmployeeLeaveQueryRepository):
    """Wrapper for query repository that handles hostname"""
    
    def __init__(self, database_connector, hostname: str = "default"):
        self._impl = EmployeeLeaveQueryRepositoryImpl(database_connector)
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
    
    def get_by_id(self, leave_id: str) -> Optional[EmployeeLeave]:
        """Get employee leave by ID"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_by_id(leave_id)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_by_employee_id(
        self, 
        employee_id: EmployeeId,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """Get employee leaves by employee ID"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_by_employee_id(employee_id, status_filter, limit, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_by_manager_id(
        self, 
        manager_id: str,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """Get employee leaves by manager ID"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_by_manager_id(manager_id, status_filter, limit, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_by_date_range(
        self, 
        date_range: DateRange,
        employee_id: Optional[EmployeeId] = None,
        status_filter: Optional[LeaveStatus] = None
    ) -> List[EmployeeLeave]:
        """Get employee leaves by date range"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_by_date_range(date_range, employee_id, status_filter, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_by_month(
        self, 
        employee_id: EmployeeId,
        month: int,
        year: int
    ) -> List[EmployeeLeave]:
        """Get employee leaves for a specific month"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_by_month(employee_id, month, year, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_overlapping_leaves(
        self, 
        employee_id: EmployeeId,
        date_range: DateRange,
        exclude_leave_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """Get leaves that overlap with the given date range"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_overlapping_leaves(employee_id, date_range, exclude_leave_id, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_pending_approvals(
        self, 
        manager_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """Get pending leave approvals"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_pending_approvals(manager_id, limit, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
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
        """Search employee leaves with filters"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.search(
                employee_id, manager_id, leave_type, status, start_date, end_date,
                month, year, skip, limit, self._hostname
            )
        finally:
            self._impl._get_collection = original_get_collection
    
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
        """Count employee leaves matching filters"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.count_by_filters(
                employee_id, manager_id, leave_type, status, start_date, end_date,
                month, year, self._hostname
            )
        finally:
            self._impl._get_collection = original_get_collection


class EmployeeLeaveAnalyticsRepositoryWrapper(EmployeeLeaveAnalyticsRepository):
    """Wrapper for analytics repository that handles hostname"""
    
    def __init__(self, database_connector, hostname: str = "default"):
        self._impl = EmployeeLeaveAnalyticsRepositoryImpl(database_connector)
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
    
    def get_leave_statistics(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get leave statistics"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_leave_statistics(employee_id, manager_id, year, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_leave_type_breakdown(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """Get leave type breakdown"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_leave_type_breakdown(employee_id, manager_id, year, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_monthly_leave_trends(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """Get monthly leave trends"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_monthly_leave_trends(employee_id, manager_id, year, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def get_team_leave_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get team leave summary for a manager"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.get_team_leave_summary(manager_id, month, year, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection
    
    def calculate_lwp_for_employee(
        self,
        employee_id: EmployeeId,
        month: int,
        year: int
    ) -> int:
        """Calculate Leave Without Pay (LWP) for an employee"""
        original_get_collection = self._impl._get_collection
        self._impl._get_collection = lambda h: original_get_collection(self._hostname)
        try:
            return self._impl.calculate_lwp_for_employee(employee_id, month, year, self._hostname)
        finally:
            self._impl._get_collection = original_get_collection


class EmployeeLeaveBalanceRepositoryWrapper(EmployeeLeaveBalanceRepository):
    """Wrapper for balance repository that handles hostname"""
    
    def __init__(self, database_connector, hostname: str = "default"):
        self._impl = EmployeeLeaveBalanceRepositoryImpl(database_connector)
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
    
    def get_leave_balance(self, employee_id: EmployeeId) -> Dict[str, int]:
        """Get leave balance for an employee"""
        original_get_user_collection = self._impl._get_user_collection
        self._impl._get_user_collection = lambda h: original_get_user_collection(self._hostname)
        try:
            return self._impl.get_leave_balance(employee_id, self._hostname)
        finally:
            self._impl._get_user_collection = original_get_user_collection
    
    def update_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_type: str, 
        balance_change: int
    ) -> bool:
        """Update leave balance for an employee"""
        original_get_user_collection = self._impl._get_user_collection
        self._impl._get_user_collection = lambda h: original_get_user_collection(self._hostname)
        try:
            return self._impl.update_leave_balance(employee_id, leave_type, balance_change, self._hostname)
        finally:
            self._impl._get_user_collection = original_get_user_collection
    
    def set_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_balances: Dict[str, int]
    ) -> bool:
        """Set leave balances for an employee"""
        original_get_user_collection = self._impl._get_user_collection
        self._impl._get_user_collection = lambda h: original_get_user_collection(self._hostname)
        try:
            return self._impl.set_leave_balance(employee_id, leave_balances, self._hostname)
        finally:
            self._impl._get_user_collection = original_get_user_collection
    
    def get_team_leave_balances(self, manager_id: str) -> List[Dict[str, Any]]:
        """Get leave balances for all team members under a manager"""
        original_get_user_collection = self._impl._get_user_collection
        self._impl._get_user_collection = lambda h: original_get_user_collection(self._hostname)
        try:
            return self._impl.get_team_leave_balances(manager_id, self._hostname)
        finally:
            self._impl._get_user_collection = original_get_user_collection 