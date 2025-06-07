"""
Get Employee Leaves Use Case
Business workflow for retrieving employee leave applications
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date

from app.application.dto.employee_leave_dto import (
    EmployeeLeaveSearchFiltersDTO,
    EmployeeLeaveResponseDTO,
    EmployeeLeaveBalanceDTO,
    EmployeeLeaveAnalyticsDTO,
    LWPCalculationDTO
)
from app.application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveQueryRepository,
    EmployeeLeaveAnalyticsRepository
)
from app.domain.entities.employee_leave import EmployeeLeave
from app.application.dto.employee_leave_dto import LeaveStatus
from datetime import date
from app.domain.value_objects.employee_id import EmployeeId


class GetEmployeeLeavesUseCase:
    """
    Use case for retrieving employee leave applications.
    
    Follows SOLID principles:
    - SRP: Only handles employee leave retrieval operations
    - OCP: Can be extended with new filtering options
    - LSP: Can be substituted with other query use cases
    - ISP: Depends only on required query interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        query_repository: EmployeeLeaveQueryRepository,
        analytics_repository: Optional[EmployeeLeaveAnalyticsRepository] = None
    ):
        self._query_repository = query_repository
        self._analytics_repository = analytics_repository
        self._logger = logging.getLogger(__name__)
    
    def get_employee_leave_by_id(self, leave_id: str) -> Optional[EmployeeLeaveResponseDTO]:
        """
        Get employee leave by ID.
        
        Args:
            leave_id: Leave application identifier
            
        Returns:
            EmployeeLeaveResponseDTO if found, None otherwise
        """
        
        try:
            self._logger.info(f"Retrieving employee leave: {leave_id}")
            
            employee_leave = self._query_repository.get_by_id(leave_id)
            
            if employee_leave:
                return EmployeeLeaveResponseDTO.from_entity(employee_leave)
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve employee leave {leave_id}: {str(e)}")
            raise Exception(f"Failed to retrieve employee leave: {str(e)}")
    
    def get_employee_leaves_by_employee_id(
        self, 
        employee_id: str,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get employee leaves by employee ID.
        
        Args:
            employee_id: Employee identifier
            status_filter: Optional status filter
            limit: Optional limit on results
            
        Returns:
            List of EmployeeLeaveResponseDTO
        """
        
        try:
            self._logger.info(f"Retrieving leaves for employee: {employee_id}")
            
            employee_id = EmployeeId(employee_id)
            employee_leaves = self._query_repository.get_by_employee_id(
                employee_id, status_filter, limit
            )
            
            return [
                EmployeeLeaveResponseDTO.from_entity(leave)
                for leave in employee_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve leaves for employee {employee_id}: {str(e)}")
            raise Exception(f"Failed to retrieve employee leaves: {str(e)}")
    
    def get_employee_leaves_by_manager_id(
        self, 
        manager_id: str,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get employee leaves by manager ID.
        
        Args:
            manager_id: Manager identifier
            status_filter: Optional status filter
            limit: Optional limit on results
            
        Returns:
            List of EmployeeLeaveResponseDTO for employees under the manager
        """
        
        try:
            self._logger.info(f"Retrieving leaves for manager: {manager_id}")
            
            employee_leaves = self._query_repository.get_by_manager_id(
                manager_id, status_filter, limit
            )
            
            return [
                EmployeeLeaveResponseDTO.from_entity(leave)
                for leave in employee_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve leaves for manager {manager_id}: {str(e)}")
            raise Exception(f"Failed to retrieve manager leaves: {str(e)}")
    
    def get_pending_approvals(
        self, 
        manager_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get pending leave approvals.
        
        Args:
            manager_id: Optional manager filter
            limit: Optional limit on results
            
        Returns:
            List of pending EmployeeLeaveResponseDTO
        """
        
        try:
            self._logger.info(f"Retrieving pending approvals for manager: {manager_id}")
            
            employee_leaves = self._query_repository.get_pending_approvals(manager_id, limit)
            
            return [
                EmployeeLeaveResponseDTO.from_entity(leave)
                for leave in employee_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve pending approvals: {str(e)}")
            raise Exception(f"Failed to retrieve pending approvals: {str(e)}")
    
    def search_employee_leaves(
        self, 
        filters: EmployeeLeaveSearchFiltersDTO
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Search employee leaves with filters.
        
        Args:
            filters: Search filters
            
        Returns:
            List of matching EmployeeLeaveResponseDTO
        """
        
        try:
            self._logger.info(f"Searching employee leaves with filters")
            
            # Convert filters to repository parameters
            employee_id = EmployeeId(filters.employee_id) if filters.employee_id else None
            start_date = date.fromisoformat(filters.start_date) if filters.start_date else None
            end_date = date.fromisoformat(filters.end_date) if filters.end_date else None
            
            employee_leaves = self._query_repository.search(
                employee_id=employee_id,
                manager_id=filters.manager_id,
                leave_type=filters.leave_type,
                status=filters.status,
                start_date=start_date,
                end_date=end_date,
                month=filters.month,
                year=filters.year,
                skip=filters.skip,
                limit=filters.limit
            )
            
            return [
                EmployeeLeaveResponseDTO.from_entity(leave)
                for leave in employee_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to search employee leaves: {str(e)}")
            raise Exception(f"Failed to search employee leaves: {str(e)}")
    
    async def get_employee_leaves_by_month(
        self, 
        employee_id: str,
        month: int,
        year: int
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get employee leaves for a specific month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            
        Returns:
            List of EmployeeLeaveResponseDTO for the month
        """
        
        try:
            self._logger.info(f"Retrieving leaves for employee {employee_id} in {month}/{year}")
            
            # Call the repository method directly with string employee_id
            employee_leaves = await self._query_repository.get_by_month(employee_id, month, year)
            
            return [
                EmployeeLeaveResponseDTO.from_entity(leave)
                for leave in employee_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve monthly leaves: {str(e)}")
            raise Exception(f"Failed to retrieve monthly leaves: {str(e)}")
    
    def get_leave_balance(self, employee_id: str) -> EmployeeLeaveBalanceDTO:
        """
        Get leave balance for an employee.
        
        Args:
            employee_id: Employee identifier
            
        Returns:
            EmployeeLeaveBalanceDTO with leave balances
        """
        
        try:
            self._logger.info(f"Retrieving leave balance for employee: {employee_id}")
            
            # Balance repository not available in current implementation
            raise Exception("Leave balance functionality not implemented")
            
            return EmployeeLeaveBalanceDTO(
                employee_id=employee_id,
                leave_balances=leave_balances
            )
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave balance for {employee_id}: {str(e)}")
            raise Exception(f"Failed to retrieve leave balance: {str(e)}")
    
    def get_leave_analytics(
        self,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> EmployeeLeaveAnalyticsDTO:
        """
        Get leave analytics.
        
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            year: Optional year filter
            
        Returns:
            EmployeeLeaveAnalyticsDTO with analytics data
        """
        
        try:
            self._logger.info(f"Retrieving leave analytics")
            
            if not self._analytics_repository:
                raise Exception("Analytics repository not available")
            
            employee_id = EmployeeId(employee_id) if employee_id else None
            
            # Get basic statistics
            stats = self._analytics_repository.get_leave_statistics(employee_id, manager_id, year)
            
            # Get leave type breakdown
            type_breakdown = self._analytics_repository.get_leave_type_breakdown(
                employee_id, manager_id, year
            )
            
            # Get monthly trends
            monthly_trends = self._analytics_repository.get_monthly_leave_trends(
                employee_id, manager_id, year
            )
            
            return EmployeeLeaveAnalyticsDTO(
                total_applications=stats.get("total_applications", 0),
                approved_applications=stats.get("approved_applications", 0),
                rejected_applications=stats.get("rejected_applications", 0),
                pending_applications=stats.get("pending_applications", 0),
                total_days_taken=stats.get("total_days_taken", 0),
                leave_type_breakdown=type_breakdown,
                monthly_breakdown=monthly_trends
            )
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave analytics: {str(e)}")
            raise Exception(f"Failed to retrieve leave analytics: {str(e)}")
    
    async def calculate_lwp_for_month(
        self,
        employee_id: str,
        month: int,
        year: int
    ) -> LWPCalculationDTO:
        """
        Calculate Leave Without Pay (LWP) for a specific month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            
        Returns:
            LWPCalculationDTO with LWP calculation details
        """
        
        try:
            self._logger.info(f"Calculating LWP for employee {employee_id} in {month}/{year}")
            
            if not self._analytics_repository:
                raise Exception("Analytics repository not available")
            
            employee_id = EmployeeId(employee_id)
            lwp_days = self._analytics_repository.calculate_lwp_for_employee(employee_id, month, year)
            
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=lwp_days,
                calculation_details={
                    "calculated_at": date.today().isoformat(),
                    "method": "working_days_calculation"
                }
            )
            
        except Exception as e:
            self._logger.error(f"Failed to calculate LWP: {str(e)}")
            raise Exception(f"Failed to calculate LWP: {str(e)}")
    
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
        
        try:
            self._logger.info(f"Retrieving team leave summary for manager: {manager_id}")
            
            if not self._analytics_repository:
                raise Exception("Analytics repository not available")
            
            team_summary = self._analytics_repository.get_team_leave_summary(
                manager_id, month, year
            )
            
            return team_summary
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve team leave summary: {str(e)}")
            raise Exception(f"Failed to retrieve team leave summary: {str(e)}")
    
    def count_employee_leaves(
        self, 
        filters: EmployeeLeaveSearchFiltersDTO
    ) -> int:
        """
        Count employee leaves matching filters.
        
        Args:
            filters: Search filters
            
        Returns:
            Count of matching records
        """
        
        try:
            self._logger.info(f"Counting employee leaves with filters")
            
            # Convert filters to repository parameters
            employee_id = EmployeeId(filters.employee_id) if filters.employee_id else None
            start_date = date.fromisoformat(filters.start_date) if filters.start_date else None
            end_date = date.fromisoformat(filters.end_date) if filters.end_date else None
            
            count = self._query_repository.count_by_filters(
                employee_id=employee_id,
                manager_id=filters.manager_id,
                leave_type=filters.leave_type,
                status=filters.status,
                start_date=start_date,
                end_date=end_date,
                month=filters.month,
                year=filters.year
            )
            
            return count
            
        except Exception as e:
            self._logger.error(f"Failed to count employee leaves: {str(e)}")
            raise Exception(f"Failed to count employee leaves: {str(e)}") 