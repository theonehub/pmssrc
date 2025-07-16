"""
Employee Leave API Controller
FastAPI controller for employee leave management endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date

from app.application.use_cases.employee_leave.apply_employee_leave_use_case import ApplyEmployeeLeaveUseCase
from app.application.use_cases.employee_leave.approve_employee_leave_use_case import ApproveEmployeeLeaveUseCase
from app.application.use_cases.employee_leave.get_employee_leaves_use_case import GetEmployeeLeavesUseCase
from app.application.dto.employee_leave_dto import (
    EmployeeLeaveCreateRequestDTO,
    EmployeeLeaveUpdateRequestDTO,
    EmployeeLeaveApprovalRequestDTO,
    EmployeeLeaveSearchFiltersDTO,
    EmployeeLeaveResponseDTO,
    EmployeeLeaveBalanceDTO,
    EmployeeLeaveAnalyticsDTO,
    LWPCalculationDTO,
    EmployeeLeaveValidationError,
    EmployeeLeaveBusinessRuleError,
    EmployeeLeaveNotFoundError,
    InsufficientLeaveBalanceError
)
from app.application.dto.employee_leave_dto import LeaveStatus
from app.auth.auth_dependencies import CurrentUser


class EmployeeLeaveController:
    """
    Employee Leave controller following SOLID principles.
    
    Follows SOLID principles:
    - SRP: Only handles HTTP request/response for employee leave operations
    - OCP: Can be extended with new endpoints without modification
    - LSP: Can be substituted with other controllers
    - ISP: Provides focused employee leave operations
    - DIP: Depends on use case abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        apply_use_case: Optional[ApplyEmployeeLeaveUseCase] = None,
        approve_use_case: Optional[ApproveEmployeeLeaveUseCase] = None,
        query_use_case: Optional[GetEmployeeLeavesUseCase] = None
    ):
        self._apply_use_case = apply_use_case
        self._approve_use_case = approve_use_case
        self._query_use_case = query_use_case
        self._logger = logging.getLogger(__name__)
    
    async def apply_leave(
        self, 
        request: EmployeeLeaveCreateRequestDTO, 
        current_user: CurrentUser
    ) -> EmployeeLeaveResponseDTO:
        """
        Apply for employee leave.
        
        Args:
            request: Leave application request
            current_user: Current user applying for leave (provides organization context)
        Returns:
            EmployeeLeaveResponseDTO with created leave details
        Raises:
            EmployeeLeaveValidationError: If request data is invalid
            EmployeeLeaveBusinessRuleError: If business rules are violated
            InsufficientLeaveBalanceError: If insufficient leave balance
        """
        try:
            self._logger.info(f"Processing leave application for employee: {current_user.employee_id} in org: {current_user.hostname}")
            response = await self._apply_use_case.execute(request, current_user)
            self._logger.info(f"Successfully processed leave application: {response.leave_id}")
            return response
        except (EmployeeLeaveValidationError, EmployeeLeaveBusinessRuleError, 
                InsufficientLeaveBalanceError):
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in leave application: {e}")
            raise Exception(f"Failed to process leave application: {str(e)}")
    
    async def approve_leave(
        self, 
        leave_id: str,
        request: EmployeeLeaveApprovalRequestDTO, 
        current_user: CurrentUser
    ) -> EmployeeLeaveResponseDTO:
        """
        Approve or reject employee leave.
        Args:
            leave_id: Leave application identifier
            request: Approval/rejection request
            current_user: User approving/rejecting the leave (organization context)
        Returns:
            EmployeeLeaveResponseDTO with updated leave details
        Raises:
            EmployeeLeaveNotFoundError: If leave application not found
            EmployeeLeaveValidationError: If request data is invalid
            EmployeeLeaveBusinessRuleError: If business rules are violated
        """
        try:
            self._logger.info(f"Processing leave approval: {leave_id} by {current_user.employee_id} in org: {current_user.hostname}")
            response = await self._approve_use_case.execute(leave_id, request, current_user)
            self._logger.info(f"Leave approval Processed: {response}")
            return response
        except (EmployeeLeaveNotFoundError, EmployeeLeaveValidationError, EmployeeLeaveBusinessRuleError):
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in leave approval: {e}")
            raise Exception(f"Failed to process leave approval: {str(e)}")
    
    async def get_leave_by_id(self, leave_id: str, current_user: CurrentUser) -> Optional[EmployeeLeaveResponseDTO]:
        """
        Get employee leave by ID.
        Args:
            leave_id: Leave application identifier
            current_user: Current user context (organization context)
        Returns:
            EmployeeLeaveResponseDTO if found, None otherwise
        """
        try:
            self._logger.info(f"Retrieving leave: {leave_id} in org: {current_user.hostname}")
            response = await self._query_use_case.get_employee_leave_by_id(leave_id, current_user)
            return response
        except Exception as e:
            self._logger.error(f"Error retrieving leave {leave_id}: {e}")
            raise Exception(f"Failed to retrieve leave: {str(e)}")
    
    async def get_employee_leaves(
        self, 
        employee_id: str,
        status_filter: Optional[str] = None,
        limit: Optional[int] = None,
        current_user: CurrentUser = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get employee leaves by employee ID.
        Args:
            employee_id: Employee identifier
            status_filter: Optional status filter
            limit: Optional limit on results
            current_user: Current user context for organization
        Returns:
            List of EmployeeLeaveResponseDTO
        """
        try:
            self._logger.info(f"Retrieving leaves for employee: {employee_id} in org: {current_user.hostname if current_user else 'unknown'}")
            status = None
            if status_filter:
                try:
                    status = LeaveStatus(status_filter.upper())
                except ValueError:
                    raise EmployeeLeaveValidationError([f"Invalid status: {status_filter}"])
            response = await self._query_use_case.get_employee_leaves_by_employee_id(
                employee_id, current_user
            )
            return response
        except EmployeeLeaveValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error retrieving employee leaves: {e}")
            raise Exception(f"Failed to retrieve employee leaves: {str(e)}")
    
    async def get_manager_leaves(
        self, 
        manager_id: str,
        status_filter: Optional[str] = None,
        limit: Optional[int] = None,
        current_user: CurrentUser = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get leaves for manager's team.
        
        Args:
            manager_id: Manager identifier
            status_filter: Optional status filter
            limit: Optional limit on results
            current_user: Current user context for organization
            
        Returns:
            List of EmployeeLeaveResponseDTO
        """
        
        try:
            self._logger.info(f"Retrieving leaves for manager: {manager_id} in org: {current_user.hostname if current_user else 'unknown'}")
            
            status = None
            if status_filter:
                try:
                    status = LeaveStatus(status_filter.upper())
                except ValueError:
                    raise EmployeeLeaveValidationError([f"Invalid status: {status_filter}"])
            
            response = self._query_use_case.get_employee_leaves_by_manager_id(
                manager_id, status, limit
            )
            
            return response
            
        except EmployeeLeaveValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error retrieving manager leaves: {e}")
            raise Exception(f"Failed to retrieve manager leaves: {str(e)}")
    
    async def get_pending_approvals(
        self, 
        manager_id: Optional[str] = None,
        limit: Optional[int] = None,
        current_user: CurrentUser = None
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get pending leave approvals.
        Args:
            manager_id: Optional manager filter
            limit: Optional limit on results
            current_user: Current user context (organization context)
        Returns:
            List of pending EmployeeLeaveResponseDTO
        """
        try:
            self._logger.info(f"Retrieving pending approvals for manager: {manager_id} in org: {current_user.hostname if current_user else 'unknown'}")
            response = await self._query_use_case.get_pending_approvals(manager_id, limit, current_user)
            return response
        except Exception as e:
            self._logger.error(f"Failed to retrieve pending approvals: {str(e)}")
            raise Exception(f"Failed to retrieve pending approvals: {str(e)}")
    
    async def search_leaves(
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
            response = await self._query_use_case.search_employee_leaves(filters, current_user)
            return response
        except Exception as e:
            self._logger.error(f"Error searching employee leaves: {e}")
            raise Exception(f"Failed to search employee leaves: {str(e)}")
    
    async def get_monthly_leaves(
        self, 
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Get monthly leaves for an employee.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            current_user: Current user context for organization
            
        Returns:
            List of EmployeeLeaveResponseDTO for the specified month
        """
        
        try:
            self._logger.info(f"Retrieving monthly leaves for {employee_id} ({month}/{year}) in org: {current_user.hostname}")
            
            if self._query_use_case and hasattr(self._query_use_case, 'get_employee_leaves_by_month'):
                response = await self._query_use_case.get_employee_leaves_by_month(
                    employee_id, month, year
                )
            else:
                # Fallback implementation
                response = await self._get_monthly_leaves_fallback(employee_id, month, year, current_user)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error retrieving monthly leaves: {e}")
            raise Exception(f"Failed to retrieve monthly leaves: {str(e)}")
    
    async def _get_monthly_leaves_fallback(
        self, 
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> List[EmployeeLeaveResponseDTO]:
        """
        Fallback implementation for monthly leaves.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            current_user: Current user context for organization
            
        Returns:
            List of EmployeeLeaveResponseDTO for the specified month
        """
        
        try:
            # Create date range for the month
            from datetime import date
            start_date = date(year, month, 1)
            
            # Get last day of month
            if month == 12:
                end_date = date(year + 1, 1, 1) - date.resolution
            else:
                end_date = date(year, month + 1, 1) - date.resolution
            
            # Create search filters for the date range
            filters = EmployeeLeaveSearchFiltersDTO(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date,
                limit=100
            )
            
            return await self.search_leaves(filters, current_user)
            
        except Exception as e:
            self._logger.error(f"Error in monthly leaves fallback: {e}")
            return []
    
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
            response = await self._query_use_case.get_leave_balance(employee_id, current_user)
            return response
        except Exception as e:
            self._logger.error(f"Error retrieving leave balance: {e}")
            raise Exception(f"Failed to retrieve leave balance: {str(e)}")
    
    async def get_leave_analytics(
        self,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        current_user: CurrentUser = None
    ) -> EmployeeLeaveAnalyticsDTO:
        """
        Get leave analytics.
        Args:
            employee_id: Optional employee filter
            manager_id: Optional manager filter
            year: Optional year filter
            current_user: Current user context (organization context)
        Returns:
            EmployeeLeaveAnalyticsDTO with analytics data
        """
        try:
            self._logger.info(f"Retrieving leave analytics for org: {current_user.hostname if current_user else 'unknown'}")
            response = await self._query_use_case.get_leave_analytics(current_user, employee_id, manager_id, year)
            return response
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave analytics: {str(e)}")
            raise Exception(f"Failed to retrieve leave analytics: {str(e)}")
    
    async def calculate_lwp(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> LWPCalculationDTO:
        """
        Calculate Loss of Pay (LWP) for an employee.
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            current_user: Current user context for organization
        Returns:
            LWPCalculationDTO with LWP calculation details
        """
        try:
            self._logger.info(f"Calculating LWP for {employee_id} ({month}/{year}) in org: {current_user.hostname}")
            from app.config.dependency_container import get_dependency_container
            container = get_dependency_container()
            lwp_service = container.get_lwp_calculation_service()
            response = await lwp_service.calculate_lwp_for_month(
                employee_id, month, year, current_user
            )
            return response
        except Exception as e:
            self._logger.error(f"Error calculating LWP: {e}")
            return await self._calculate_lwp_fallback(employee_id, month, year, current_user)
    
    async def _calculate_lwp_fallback(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> LWPCalculationDTO:
        """
        Fallback implementation for LWP calculation.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            current_user: Current user context for organization
            
        Returns:
            LWPCalculationDTO with basic LWP calculation
        """
        
        try:
            # Get monthly leaves
            monthly_leaves = await self.get_monthly_leaves(employee_id, month, year, current_user)
            
            # Calculate LWP days (simplified logic)
            lwp_days = 0
            for leave in monthly_leaves:
                if hasattr(leave, 'leave_type') and leave.leave_type.lower() == 'lwp':
                    lwp_days += leave.days_requested if hasattr(leave, 'days_requested') else 1
            
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=lwp_days,
                working_days=22,  # Assumed working days
                lwp_amount=0.0,  # Would need salary info
                calculation_details={
                    "total_leaves": len(monthly_leaves),
                    "lwp_leaves": lwp_days,
                    "calculation_method": "fallback"
                }
            )
            
        except Exception as e:
            self._logger.error(f"Error in LWP calculation fallback: {e}")
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=0,
                working_days=22,
                lwp_amount=0.0,
                calculation_details={"error": str(e)}
            )
    
    async def get_team_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
        current_user: CurrentUser = None
    ) -> List[dict]:
        """
        Get team leave summary for a manager.
        
        Args:
            manager_id: Manager identifier
            month: Optional month filter
            year: Optional year filter
            current_user: Current user context for organization
            
        Returns:
            List of team member leave summaries
        """
        
        try:
            self._logger.info(f"Retrieving team summary for manager: {manager_id} in org: {current_user.hostname if current_user else 'unknown'}")
            
            # Get manager's team leaves
            team_leaves = await self.get_manager_leaves(manager_id, None, None, current_user)
            
            # Group by employee and summarize
            team_summary = {}
            for leave in team_leaves:
                emp_id = leave.employee_id
                if emp_id not in team_summary:
                    team_summary[emp_id] = {
                        "employee_id": emp_id,
                        "employee_name": getattr(leave, 'employee_name', 'Unknown'),
                        "total_leaves": 0,
                        "pending_leaves": 0,
                        "approved_leaves": 0,
                        "rejected_leaves": 0
                    }
                
                team_summary[emp_id]["total_leaves"] += 1
                if leave.status.lower() == "pending":
                    team_summary[emp_id]["pending_leaves"] += 1
                elif leave.status.lower() == "approved":
                    team_summary[emp_id]["approved_leaves"] += 1
                elif leave.status.lower() == "rejected":
                    team_summary[emp_id]["rejected_leaves"] += 1
            
            return list(team_summary.values())
            
        except Exception as e:
            self._logger.error(f"Error retrieving team summary: {e}")
            return []
    
    async def count_leaves(
        self, 
        filters: EmployeeLeaveSearchFiltersDTO,
        current_user: CurrentUser
    ) -> int:
        """
        Count leaves matching filters.
        
        Args:
            filters: Search filters
            current_user: Current user context for organization
            
        Returns:
            Count of matching leaves
        """
        
        try:
            self._logger.info(f"Counting leaves with filters in org: {current_user.hostname}")
            
            if self._query_use_case and hasattr(self._query_use_case, 'count_leaves'):
                count = self._query_use_case.count_employee_leaves(filters)
            else:
                # Fallback - search and count
                leaves = await self.search_leaves(filters, current_user)
                count = len(leaves)
            
            return count
            
        except Exception as e:
            self._logger.error(f"Error counting leaves: {e}")
            return 0
    
    async def update_leave(
        self,
        leave_id: str,
        request: EmployeeLeaveUpdateRequestDTO,
        current_user: CurrentUser
    ) -> EmployeeLeaveResponseDTO:
        """
        Update leave application.
        Args:
            leave_id: Leave application identifier
            request: Update request
            current_user: Current user context (organization context)
        Returns:
            EmployeeLeaveResponseDTO with updated leave details
        """
        try:
            self._logger.info(f"Updating leave {leave_id} for org: {current_user.hostname}")
            response = await self._query_use_case.update_leave(leave_id, request, current_user)
            return response
        except Exception as e:
            self._logger.error(f"Failed to update leave {leave_id}: {str(e)}")
            raise Exception(f"Failed to update leave: {str(e)}")

    async def get_user_leave_summary(
        self,
        employee_id: str,
        year: int,
        current_user: CurrentUser
    ) -> dict:
        """Get user leave summary for a specific year"""
        try:
            self._logger.info(f"Getting leave summary for employee {employee_id} for year {year} in organisation: {current_user.hostname}")
            
            # Get leave balance
            leave_balance = await self.get_leave_balance(employee_id, current_user)
            
            # Get all leaves for the year
            from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
            filters = EmployeeLeaveSearchFiltersDTO(
                employee_id=employee_id,
                year=year
            )
            
            leaves = await self.search_leaves(filters, current_user)
            
            # Calculate summary statistics
            total_casual_leaves = leave_balance.casual_leaves.total if leave_balance.casual_leaves else 0
            used_casual_leaves = leave_balance.casual_leaves.used if leave_balance.casual_leaves else 0
            
            total_sick_leaves = leave_balance.sick_leaves.total if leave_balance.sick_leaves else 0
            used_sick_leaves = leave_balance.sick_leaves.used if leave_balance.sick_leaves else 0
            
            total_earned_leaves = leave_balance.earned_leaves.total if leave_balance.earned_leaves else 0
            used_earned_leaves = leave_balance.earned_leaves.used if leave_balance.earned_leaves else 0
            
            # Count pending leave requests
            pending_leave_requests = len([leave for leave in leaves if leave.status == "PENDING"])
            
            return {
                "total_casual_leaves": total_casual_leaves,
                "used_casual_leaves": used_casual_leaves,
                "total_sick_leaves": total_sick_leaves,
                "used_sick_leaves": used_sick_leaves,
                "total_earned_leaves": total_earned_leaves,
                "used_earned_leaves": used_earned_leaves,
                "pending_leave_requests": pending_leave_requests
            }
            
        except Exception as e:
            self._logger.error(f"Error getting leave summary for employee {employee_id}: {e}")
            raise Exception(f"Failed to get leave summary: {str(e)}") 