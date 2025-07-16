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
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.domain.entities.employee_leave import EmployeeLeave
from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.employee_leave_dto import LeaveStatus
from datetime import date
from app.auth.auth_dependencies import CurrentUser


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
        user_query_repository: UserQueryRepository,
        analytics_repository: Optional[EmployeeLeaveAnalyticsRepository] = None
    ):
        self._query_repository = query_repository
        self._user_query_repository = user_query_repository
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
    
    async def get_employee_leaves_by_employee_id(
        self, 
        employee_id: str,
        current_user: CurrentUser,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get employee leaves by employee ID.
        Args:
            employee_id: Employee identifier
            current_user: Current user context for organization
            status_filter: Optional status filter
            limit: Optional limit on results
        Returns:
            List of EmployeeLeaveResponseDTO
        """
        try:
            self._logger.info(f"Retrieving leaves for employee: {employee_id} in org: {current_user.hostname}")
            employee_leaves = await self._query_repository.get_by_employee_id(
                employee_id, current_user.hostname
            )
            if status_filter:
                filter_value = status_filter.value if hasattr(status_filter, 'value') else str(status_filter)
                employee_leaves = [leave for leave in employee_leaves if leave.status == filter_value]
            if limit:
                employee_leaves = employee_leaves[:limit]
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
    
    async def search_employee_leaves(
        self, 
        filters: EmployeeLeaveSearchFiltersDTO,
        current_user: CurrentUser
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Search employee leaves with filters.
        Args:
            filters: Search filters
            current_user: Current user context for organization
        Returns:
            List of matching EmployeeLeaveResponseDTO
        """
        try:
            self._logger.info(f"Searching employee leaves with filters for org: {current_user.hostname}")
            employee_leaves = await self._query_repository.search(filters, current_user.hostname)
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
    
    async def get_leave_balance(self, employee_id: str, current_user: CurrentUser) -> EmployeeLeaveBalanceDTO:
        """
        Get leave balance for an employee.
        Args:
            employee_id: Employee identifier
            current_user: Current user context for organization
        Returns:
            EmployeeLeaveBalanceDTO with leave balances
        """
        try:
            self._logger.info(f"Retrieving leave balance for employee: {employee_id} in org: {current_user.hostname}")
            employee_id_obj = EmployeeId(employee_id)
            user = await self._user_query_repository.get_by_id(employee_id_obj, current_user.hostname)
            if not user:
                self._logger.warning(f"User not found: {employee_id}")
                return EmployeeLeaveBalanceDTO(
                    employee_id=employee_id,
                    balances={
                        "casual_leave": 12.0,
                        "sick_leave": 12.0,
                        "earned_leave": 21.0,
                        "maternity_leave": 180.0,
                        "paternity_leave": 15.0
                    }
                )
            leave_balances = getattr(user, 'leave_balance', {})
            float_balances = {k: float(v) for k, v in leave_balances.items() if v is not None}
            return EmployeeLeaveBalanceDTO(
                employee_id=employee_id,
                balances=float_balances
            )
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave balance for employee {employee_id}: {str(e)}")
            raise Exception(f"Failed to retrieve employee leave balance: {str(e)}")
    
    async def get_leave_analytics(
        self,
        current_user: CurrentUser,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> EmployeeLeaveAnalyticsDTO:
        """
        Get leave analytics for the organization.
        Args:
            current_user: Current user context for organization
            employee_id: Optional employee identifier
            manager_id: Optional manager identifier
            year: Optional year
        Returns:
            EmployeeLeaveAnalyticsDTO
        """
        try:
            self._logger.info(f"Retrieving leave analytics for org: {current_user.hostname}")
            analytics = await self._analytics_repository.get_leave_statistics(
                employee_id=employee_id,
                manager_id=manager_id,
                year=year,
                organisation_id=current_user.hostname
            )
            return EmployeeLeaveAnalyticsDTO(**analytics)
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave analytics: {str(e)}")
            raise Exception(f"Failed to retrieve leave analytics: {str(e)}")
    
    async def calculate_lwp_for_month(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> LWPCalculationDTO:
        """
        Calculate Leave Without Pay (LWP) for a specific month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            current_user: Current user object
            
        Returns:
            LWPCalculationDTO with LWP calculation details
        """
        
        try:
            self._logger.info(f"Calculating LWP for employee {employee_id} in {month}/{year}")
            
            # Use standardized LWP calculation service from dependency container
            from app.config.dependency_container import get_dependency_container
            container = get_dependency_container()
            lwp_service = container.get_lwp_calculation_service()
            
            # Calculate LWP using standardized method
            response = await lwp_service.calculate_lwp_for_month(
                employee_id, month, year, current_user
            )
            
            return response
            
        except Exception as e:
            self._logger.error(f"Failed to calculate LWP: {str(e)}")
            # Fallback to analytics repository if available
            if self._analytics_repository:
                try:
                    employee_id_obj = EmployeeId(employee_id)
                    lwp_days = self._analytics_repository.calculate_lwp_for_employee(employee_id_obj, month, year)
                    
                    return LWPCalculationDTO(
                        employee_id=employee_id,
                        month=month,
                        year=year,
                        lwp_days=lwp_days,
                        calculation_details={
                            "calculated_at": date.today().isoformat(),
                            "method": "analytics_repository_fallback"
                        }
                    )
                except Exception as fallback_error:
                    self._logger.error(f"Fallback LWP calculation also failed: {fallback_error}")
            
            # Return zero LWP if all methods fail
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=0,
                calculation_details={
                    "calculated_at": date.today().isoformat(),
                    "method": "zero_fallback",
                    "error": str(e)
                }
            )
    
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