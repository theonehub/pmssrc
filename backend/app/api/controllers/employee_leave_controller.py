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
        employee_id: str,
        hostname: str
    ) -> EmployeeLeaveResponseDTO:
        """
        Apply for employee leave.
        
        Args:
            request: Leave application request
            employee_id: Employee applying for leave
            hostname: Organisation hostname
            
        Returns:
            EmployeeLeaveResponseDTO with created leave details
            
        Raises:
            EmployeeLeaveValidationError: If request data is invalid
            EmployeeLeaveBusinessRuleError: If business rules are violated
            InsufficientLeaveBalanceError: If insufficient leave balance
        """
        
        try:
            self._logger.info(f"Processing leave application for employee: {employee_id}")
            
            response = await self._apply_use_case.execute(request, employee_id, hostname)
            
            self._logger.info(f"Successfully processed leave application: {response.leave_id}")
            return response
            
        except (EmployeeLeaveValidationError, EmployeeLeaveBusinessRuleError, 
                InsufficientLeaveBalanceError):
            # Re-raise known exceptions
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in leave application: {e}")
            raise Exception(f"Failed to process leave application: {str(e)}")
    
    async def approve_leave(
        self, 
        leave_id: str,
        request: EmployeeLeaveApprovalRequestDTO, 
        approver_id: str,
        hostname: str
    ) -> EmployeeLeaveResponseDTO:
        """
        Approve or reject employee leave.
        
        Args:
            leave_id: Leave application identifier
            request: Approval/rejection request
            approver_id: User approving/rejecting the leave
            hostname: Organisation hostname
            
        Returns:
            EmployeeLeaveResponseDTO with updated leave details
            
        Raises:
            EmployeeLeaveNotFoundError: If leave application not found
            EmployeeLeaveValidationError: If request data is invalid
            EmployeeLeaveBusinessRuleError: If business rules are violated
        """
        
        try:
            self._logger.info(f"Processing leave approval: {leave_id} by {approver_id}")
            
            response = await self._approve_use_case.execute(
                leave_id, request, approver_id, hostname
            )
            
            self._logger.info(f"Successfully processed leave approval: {leave_id}")
            return response
            
        except (EmployeeLeaveNotFoundError, EmployeeLeaveValidationError, 
                EmployeeLeaveBusinessRuleError):
            # Re-raise known exceptions
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in leave approval: {e}")
            raise Exception(f"Failed to process leave approval: {str(e)}")
    
    async def get_leave_by_id(self, leave_id: str) -> Optional[EmployeeLeaveResponseDTO]:
        """
        Get employee leave by ID.
        
        Args:
            leave_id: Leave application identifier
            
        Returns:
            EmployeeLeaveResponseDTO if found, None otherwise
        """
        
        try:
            self._logger.info(f"Retrieving leave: {leave_id}")
            
            response = self._query_use_case.get_employee_leave_by_id(leave_id)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error retrieving leave {leave_id}: {e}")
            raise Exception(f"Failed to retrieve leave: {str(e)}")
    
    async def get_employee_leaves(
        self, 
        employee_id: str,
        status_filter: Optional[str] = None,
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
            
            status = None
            if status_filter:
                try:
                    status = LeaveStatus(status_filter.upper())
                except ValueError:
                    raise EmployeeLeaveValidationError([f"Invalid status: {status_filter}"])
            
            response = self._query_use_case.get_employee_leaves_by_employee_id(
                employee_id, status, limit
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
            
            response = self._query_use_case.get_pending_approvals(manager_id, limit)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error retrieving pending approvals: {e}")
            raise Exception(f"Failed to retrieve pending approvals: {str(e)}")
    
    async def search_leaves(
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
            self._logger.info(f"Searching employee leaves")
            
            response = self._query_use_case.search_employee_leaves(filters)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error searching employee leaves: {e}")
            raise Exception(f"Failed to search employee leaves: {str(e)}")
    
    async def get_monthly_leaves(
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
            self._logger.info(f"Retrieving monthly leaves for {employee_id}: {month}/{year}")
            
            if not (1 <= month <= 12):
                raise EmployeeLeaveValidationError(["Month must be between 1 and 12"])
            
            if not (2000 <= year <= 3000):
                raise EmployeeLeaveValidationError(["Year must be between 2000 and 3000"])
            
            # Try to use the query use case if available
            if self._query_use_case:
                response = await self._query_use_case.get_employee_leaves_by_month(
                    employee_id, month, year
                )
                return response
            else:
                # Fallback to legacy service
                return await self._get_monthly_leaves_fallback(employee_id, month, year)
            
        except EmployeeLeaveValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error retrieving monthly leaves: {e}")
            # Try fallback on error
            try:
                return await self._get_monthly_leaves_fallback(employee_id, month, year)
            except Exception as fallback_error:
                self._logger.error(f"Fallback also failed: {fallback_error}")
                return []  # Return empty list instead of raising exception
    
    async def _get_monthly_leaves_fallback(
        self, 
        employee_id: str,
        month: int,
        year: int
    ) -> List[EmployeeLeaveResponseDTO]:
        """Fallback method using legacy service."""
        from app.infrastructure.services.employee_leave_legacy_service import get_leaves_by_month_for_user
        from datetime import datetime, date
        
        try:
            hostname = "default"  # Default hostname for now
            legacy_leaves = get_leaves_by_month_for_user(employee_id, month, year, hostname)
            
            # Convert legacy format to DTO format
            response_leaves = []
            for leave_dict in legacy_leaves:
                # Create a basic EmployeeLeaveResponseDTO from legacy data
                response_leave = EmployeeLeaveResponseDTO(
                    leave_id=leave_dict.get('leave_id', ''),
                    employee_id=leave_dict.get('employee_id', employee_id),
                    leave_type_name=leave_dict.get('leave_name', ''),
                    start_date=datetime.strptime(leave_dict.get('start_date', ''), '%Y-%m-%d').date() if leave_dict.get('start_date') else date.today(),
                    end_date=datetime.strptime(leave_dict.get('end_date', ''), '%Y-%m-%d').date() if leave_dict.get('end_date') else date.today(),
                    reason=leave_dict.get('reason', ''),
                    status=leave_dict.get('status', 'pending'),
                    working_days=leave_dict.get('leave_count', 0),
                    applied_at=datetime.now(),
                    days_in_current_month=leave_dict.get('leave_count', 0)
                )
                response_leaves.append(response_leave)
            
            return response_leaves
            
        except Exception as e:
            self._logger.error(f"Legacy fallback failed: {e}")
            return []
    
    async def get_leave_balance(self, employee_id: str) -> EmployeeLeaveBalanceDTO:
        """
        Get leave balance for an employee.
        
        Args:
            employee_id: Employee identifier
            
        Returns:
            EmployeeLeaveBalanceDTO with leave balances
        """
        
        try:
            self._logger.info(f"Retrieving leave balance for: {employee_id}")
            
            response = self._query_use_case.get_leave_balance(employee_id)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error retrieving leave balance: {e}")
            raise Exception(f"Failed to retrieve leave balance: {str(e)}")
    
    async def get_leave_analytics(
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
            
            if year and not (2000 <= year <= 3000):
                raise EmployeeLeaveValidationError(["Year must be between 2000 and 3000"])
            
            response = self._query_use_case.get_leave_analytics(
                employee_id, manager_id, year
            )
            
            return response
            
        except EmployeeLeaveValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error retrieving leave analytics: {e}")
            raise Exception(f"Failed to retrieve leave analytics: {str(e)}")
    
    async def calculate_lwp(
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
            self._logger.info(f"Calculating LWP for {employee_id}: {month}/{year}")
            
            if not (1 <= month <= 12):
                raise EmployeeLeaveValidationError(["Month must be between 1 and 12"])
            
            if not (2000 <= year <= 3000):
                raise EmployeeLeaveValidationError(["Year must be between 2000 and 3000"])
            
            # Try to use the query use case if available
            if self._query_use_case:
                response = await self._query_use_case.calculate_lwp_for_month(
                    employee_id, month, year
                )
                return response
            else:
                # Fallback to legacy service
                return await self._calculate_lwp_fallback(employee_id, month, year)
            
        except EmployeeLeaveValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error calculating LWP: {e}")
            # Try fallback on error
            try:
                return await self._calculate_lwp_fallback(employee_id, month, year)
            except Exception as fallback_error:
                self._logger.error(f"LWP fallback also failed: {fallback_error}")
                # Return zero LWP instead of raising exception
                return LWPCalculationDTO(
                    employee_id=employee_id,
                    month=month,
                    year=year,
                    lwp_days=0,
                    calculation_details={
                        "calculated_at": date.today().isoformat(),
                        "method": "fallback_zero",
                        "error": str(fallback_error)
                    }
                )
    
    async def _calculate_lwp_fallback(
        self,
        employee_id: str,
        month: int,
        year: int
    ) -> LWPCalculationDTO:
        """Fallback method for LWP calculation using legacy service."""
        from app.infrastructure.services.employee_leave_legacy_service import calculate_lwp_for_month
        from datetime import date
        
        try:
            hostname = "default"  # Default hostname for now
            lwp_days = calculate_lwp_for_month(employee_id, month, year, hostname)
            
            return LWPCalculationDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                lwp_days=lwp_days,
                calculation_details={
                    "calculated_at": date.today().isoformat(),
                    "method": "legacy_calculation"
                }
            )
            
        except Exception as e:
            self._logger.error(f"Legacy LWP calculation failed: {e}")
            raise
    
    async def get_team_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[dict]:
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
            self._logger.info(f"Retrieving team summary for manager: {manager_id}")
            
            if month and not (1 <= month <= 12):
                raise EmployeeLeaveValidationError(["Month must be between 1 and 12"])
            
            if year and not (2000 <= year <= 3000):
                raise EmployeeLeaveValidationError(["Year must be between 2000 and 3000"])
            
            response = self._query_use_case.get_team_leave_summary(
                manager_id, month, year
            )
            
            return response
            
        except EmployeeLeaveValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error retrieving team summary: {e}")
            raise Exception(f"Failed to retrieve team summary: {str(e)}")
    
    async def count_leaves(
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
            self._logger.info(f"Counting employee leaves")
            
            count = self._query_use_case.count_employee_leaves(filters)
            
            return count
            
        except Exception as e:
            self._logger.error(f"Error counting employee leaves: {e}")
            raise Exception(f"Failed to count employee leaves: {str(e)}") 