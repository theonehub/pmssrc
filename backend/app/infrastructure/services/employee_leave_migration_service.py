"""
Employee Leave Migration Service
Bridges SOLID-compliant employee leave system with legacy service functions
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from application.dto.employee_leave_dto import (
    EmployeeLeaveCreateRequestDTO,
    EmployeeLeaveApprovalRequestDTO,
    EmployeeLeaveSearchFiltersDTO,
    EmployeeLeaveResponseDTO,
    EmployeeLeaveBalanceDTO,
    LWPCalculationDTO
)
from api.controllers.employee_leave_controller import EmployeeLeaveController
from config.dependency_container import get_employee_leave_controller
from models.leave_model import EmployeeLeave as LegacyEmployeeLeave, LeaveStatus
from infrastructure.services.employee_leave_legacy_service import (
    apply_leave as legacy_apply_leave,
    leave_balance as legacy_leave_balance,
    get_user_leaves as legacy_get_user_leaves,
    get_pending_leaves as legacy_get_pending_leaves,
    update_leave_status as legacy_update_leave_status,
    get_all_employee_leaves as legacy_get_all_employee_leaves,
    get_leaves_by_month_for_user as legacy_get_leaves_by_month_for_user,
    calculate_lwp_for_month as legacy_calculate_lwp_for_month
)


class EmployeeLeaveServiceMigration:
    """
    Migration service that provides both legacy and SOLID interfaces.
    
    This service allows gradual migration from legacy employee leave service
    to SOLID-compliant architecture while maintaining backward compatibility.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._use_solid_architecture = True  # Flag to control which implementation to use
    
    def _get_controller(self) -> EmployeeLeaveController:
        """Get SOLID employee leave controller"""
        return get_employee_leave_controller()
    
    # Legacy interface methods (for backward compatibility)
    
    def apply_leave_legacy(self, leave: LegacyEmployeeLeave, hostname: str) -> Dict[str, Any]:
        """Legacy apply leave method"""
        try:
            if self._use_solid_architecture:
                return self._apply_leave_solid(leave, hostname)
            else:
                return legacy_apply_leave(leave, hostname)
        except Exception as e:
            self._logger.error(f"Error in apply_leave_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_apply_leave(leave, hostname)
    
    def get_leave_balance_legacy(self, emp_id: str, hostname: str) -> Dict[str, Any]:
        """Legacy get leave balance method"""
        try:
            if self._use_solid_architecture:
                return self._get_leave_balance_solid(emp_id, hostname)
            else:
                return legacy_leave_balance(emp_id, hostname)
        except Exception as e:
            self._logger.error(f"Error in get_leave_balance_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_leave_balance(emp_id, hostname)
    
    def get_user_leaves_legacy(self, emp_id: str, hostname: str) -> List[Dict[str, Any]]:
        """Legacy get user leaves method"""
        try:
            if self._use_solid_architecture:
                return self._get_user_leaves_solid(emp_id, hostname)
            else:
                return legacy_get_user_leaves(emp_id, hostname)
        except Exception as e:
            self._logger.error(f"Error in get_user_leaves_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_get_user_leaves(emp_id, hostname)
    
    def get_pending_leaves_legacy(self, manager_id: str, hostname: str) -> List[Dict[str, Any]]:
        """Legacy get pending leaves method"""
        try:
            if self._use_solid_architecture:
                return self._get_pending_leaves_solid(manager_id, hostname)
            else:
                return legacy_get_pending_leaves(manager_id, hostname)
        except Exception as e:
            self._logger.error(f"Error in get_pending_leaves_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_get_pending_leaves(manager_id, hostname)
    
    def update_leave_status_legacy(
        self, 
        leave_id: str, 
        status: LeaveStatus, 
        approved_by: str, 
        hostname: str
    ) -> Dict[str, Any]:
        """Legacy update leave status method"""
        try:
            if self._use_solid_architecture:
                return self._update_leave_status_solid(leave_id, status, approved_by, hostname)
            else:
                return legacy_update_leave_status(leave_id, status, approved_by, hostname)
        except Exception as e:
            self._logger.error(f"Error in update_leave_status_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_update_leave_status(leave_id, status, approved_by, hostname)
    
    def get_all_employee_leaves_legacy(
        self, 
        hostname: str, 
        manager_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Legacy get all employee leaves method"""
        try:
            if self._use_solid_architecture:
                return self._get_all_employee_leaves_solid(hostname, manager_id)
            else:
                return legacy_get_all_employee_leaves(hostname, manager_id)
        except Exception as e:
            self._logger.error(f"Error in get_all_employee_leaves_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_get_all_employee_leaves(hostname, manager_id)
    
    def get_leaves_by_month_for_user_legacy(
        self, 
        emp_id: str, 
        month: int, 
        year: int, 
        hostname: str
    ) -> List[Dict[str, Any]]:
        """Legacy get leaves by month method"""
        try:
            if self._use_solid_architecture:
                return self._get_leaves_by_month_solid(emp_id, month, year, hostname)
            else:
                return legacy_get_leaves_by_month_for_user(emp_id, month, year, hostname)
        except Exception as e:
            self._logger.error(f"Error in get_leaves_by_month_for_user_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_get_leaves_by_month_for_user(emp_id, month, year, hostname)
    
    def calculate_lwp_for_month_legacy(
        self, 
        emp_id: str, 
        month: int, 
        year: int, 
        hostname: str
    ) -> int:
        """Legacy calculate LWP method"""
        try:
            if self._use_solid_architecture:
                return self._calculate_lwp_solid(emp_id, month, year, hostname)
            else:
                return legacy_calculate_lwp_for_month(emp_id, month, year, hostname)
        except Exception as e:
            self._logger.error(f"Error in calculate_lwp_for_month_legacy: {e}")
            # Fallback to legacy implementation
            return legacy_calculate_lwp_for_month(emp_id, month, year, hostname)
    
    # SOLID implementation methods
    
    async def _apply_leave_solid(self, leave: LegacyEmployeeLeave, hostname: str) -> Dict[str, Any]:
        """Apply leave using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            # Convert legacy model to DTO
            request = EmployeeLeaveCreateRequestDTO(
                leave_type=leave.leave_name,
                start_date=leave.start_date,
                end_date=leave.end_date,
                reason=leave.reason
            )
            
            # Apply leave
            response = await controller.apply_leave(request, leave.emp_id, hostname)
            
            return {
                "msg": "Leave application submitted successfully",
                "inserted_id": response.leave_id
            }
            
        except Exception as e:
            self._logger.error(f"Error in SOLID apply leave: {e}")
            raise
    
    async def _get_leave_balance_solid(self, emp_id: str, hostname: str) -> Dict[str, Any]:
        """Get leave balance using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            response = await controller.get_leave_balance(emp_id)
            
            return response.leave_balances
            
        except Exception as e:
            self._logger.error(f"Error in SOLID get leave balance: {e}")
            raise
    
    async def _get_user_leaves_solid(self, emp_id: str, hostname: str) -> List[Dict[str, Any]]:
        """Get user leaves using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            responses = await controller.get_employee_leaves(emp_id)
            
            return [response.to_dict() for response in responses]
            
        except Exception as e:
            self._logger.error(f"Error in SOLID get user leaves: {e}")
            raise
    
    async def _get_pending_leaves_solid(self, manager_id: str, hostname: str) -> List[Dict[str, Any]]:
        """Get pending leaves using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            responses = await controller.get_pending_approvals(manager_id)
            
            return [response.to_dict() for response in responses]
            
        except Exception as e:
            self._logger.error(f"Error in SOLID get pending leaves: {e}")
            raise
    
    async def _update_leave_status_solid(
        self, 
        leave_id: str, 
        status: LeaveStatus, 
        approved_by: str, 
        hostname: str
    ) -> Dict[str, Any]:
        """Update leave status using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            # Convert status to approval request
            request = EmployeeLeaveApprovalRequestDTO(
                status=status,
                comments=None
            )
            
            response = await controller.approve_leave(leave_id, request, approved_by, hostname)
            
            return {"msg": "Leave status updated successfully"}
            
        except Exception as e:
            self._logger.error(f"Error in SOLID update leave status: {e}")
            raise
    
    async def _get_all_employee_leaves_solid(
        self, 
        hostname: str, 
        manager_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all employee leaves using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            if manager_id:
                responses = await controller.get_manager_leaves(manager_id)
            else:
                # For admin users, search all leaves
                filters = EmployeeLeaveSearchFiltersDTO()
                responses = await controller.search_leaves(filters)
            
            return [response.to_dict() for response in responses]
            
        except Exception as e:
            self._logger.error(f"Error in SOLID get all employee leaves: {e}")
            raise
    
    async def _get_leaves_by_month_solid(
        self, 
        emp_id: str, 
        month: int, 
        year: int, 
        hostname: str
    ) -> List[Dict[str, Any]]:
        """Get leaves by month using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            responses = await controller.get_monthly_leaves(emp_id, month, year)
            
            return [response.to_dict() for response in responses]
            
        except Exception as e:
            self._logger.error(f"Error in SOLID get leaves by month: {e}")
            raise
    
    async def _calculate_lwp_solid(
        self, 
        emp_id: str, 
        month: int, 
        year: int, 
        hostname: str
    ) -> int:
        """Calculate LWP using SOLID architecture"""
        try:
            controller = self._get_controller()
            
            response = await controller.calculate_lwp(emp_id, month, year)
            
            return response.lwp_days
            
        except Exception as e:
            self._logger.error(f"Error in SOLID calculate LWP: {e}")
            raise
    
    # Configuration methods
    
    def enable_solid_architecture(self):
        """Enable SOLID architecture implementation"""
        self._use_solid_architecture = True
        self._logger.info("Enabled SOLID architecture for employee leave service")
    
    def disable_solid_architecture(self):
        """Disable SOLID architecture implementation (use legacy)"""
        self._use_solid_architecture = False
        self._logger.info("Disabled SOLID architecture for employee leave service")
    
    def is_solid_enabled(self) -> bool:
        """Check if SOLID architecture is enabled"""
        return self._use_solid_architecture


# Global migration service instance
_migration_service: Optional[EmployeeLeaveServiceMigration] = None


def get_employee_leave_migration_service() -> EmployeeLeaveServiceMigration:
    """Get the global employee leave migration service instance"""
    global _migration_service
    if _migration_service is None:
        _migration_service = EmployeeLeaveServiceMigration()
    return _migration_service


# Legacy wrapper functions for backward compatibility
def apply_leave_migrated(leave: LegacyEmployeeLeave, hostname: str) -> Dict[str, Any]:
    """Migrated apply leave function"""
    service = get_employee_leave_migration_service()
    return service.apply_leave_legacy(leave, hostname)


def leave_balance_migrated(emp_id: str, hostname: str) -> Dict[str, Any]:
    """Migrated leave balance function"""
    service = get_employee_leave_migration_service()
    return service.get_leave_balance_legacy(emp_id, hostname)


def get_user_leaves_migrated(emp_id: str, hostname: str) -> List[Dict[str, Any]]:
    """Migrated get user leaves function"""
    service = get_employee_leave_migration_service()
    return service.get_user_leaves_legacy(emp_id, hostname)


def get_pending_leaves_migrated(manager_id: str, hostname: str) -> List[Dict[str, Any]]:
    """Migrated get pending leaves function"""
    service = get_employee_leave_migration_service()
    return service.get_pending_leaves_legacy(manager_id, hostname)


def update_leave_status_migrated(
    leave_id: str, 
    status: LeaveStatus, 
    approved_by: str, 
    hostname: str
) -> Dict[str, Any]:
    """Migrated update leave status function"""
    service = get_employee_leave_migration_service()
    return service.update_leave_status_legacy(leave_id, status, approved_by, hostname)


def get_all_employee_leaves_migrated(
    hostname: str, 
    manager_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Migrated get all employee leaves function"""
    service = get_employee_leave_migration_service()
    return service.get_all_employee_leaves_legacy(hostname, manager_id)


def get_leaves_by_month_for_user_migrated(
    emp_id: str, 
    month: int, 
    year: int, 
    hostname: str
) -> List[Dict[str, Any]]:
    """Migrated get leaves by month function"""
    service = get_employee_leave_migration_service()
    return service.get_leaves_by_month_for_user_legacy(emp_id, month, year, hostname)


def calculate_lwp_for_month_migrated(
    emp_id: str, 
    month: int, 
    year: int, 
    hostname: str
) -> int:
    """Migrated calculate LWP function"""
    service = get_employee_leave_migration_service()
    return service.calculate_lwp_for_month_legacy(emp_id, month, year, hostname) 