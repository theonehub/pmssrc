"""
Reporting Service Interface
Abstract service interface for reporting operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

from app.application.dto.reporting_dto import (
    CreateReportRequestDTO, UpdateReportRequestDTO, ReportSearchFiltersDTO,
    ReportResponseDTO, ReportListResponseDTO, DashboardAnalyticsDTO,
    UserAnalyticsDTO, AttendanceAnalyticsDTO, LeaveAnalyticsDTO,
    PayrollAnalyticsDTO, ReimbursementAnalyticsDTO, ConsolidatedAnalyticsDTO,
    ExportRequestDTO, ExportResponseDTO
)

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser


class ReportingService(ABC):
    """
    Abstract service interface for reporting operations.
    
    Follows SOLID principles:
    - SRP: Only handles reporting business logic
    - OCP: Can be extended with new implementations
    - LSP: All implementations must follow this contract
    - ISP: Focused interface for reporting operations
    - DIP: Depends on abstractions, not concretions
    """
    
    # Report Management Operations
    @abstractmethod
    async def create_report(
        self, 
        request: CreateReportRequestDTO, 
        current_user: "CurrentUser"
    ) -> ReportResponseDTO:
        """
        Create a new report.
        
        Args:
            request: Report creation request
            current_user: Current user context with organisation info
            
        Returns:
            Created report response
            
        Raises:
            ReportingValidationError: If validation fails
            ReportingBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def get_report_by_id(
        self, 
        report_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[ReportResponseDTO]:
        """
        Get report by ID.
        
        Args:
            report_id: Report ID to retrieve
            current_user: Current user context with organisation info
            
        Returns:
            Report response if found, None otherwise
            
        Raises:
            ReportingNotFoundError: If report not found
        """
        pass
    
    @abstractmethod
    async def list_reports(
        self, 
        filters: ReportSearchFiltersDTO, 
        current_user: "CurrentUser"
    ) -> ReportListResponseDTO:
        """
        List reports with filters and pagination.
        
        Args:
            filters: Search filters and pagination
            current_user: Current user context with organisation info
            
        Returns:
            Paginated list of reports
        """
        pass
    
    @abstractmethod
    async def update_report(
        self,
        report_id: str,
        request: UpdateReportRequestDTO,
        current_user: "CurrentUser"
    ) -> ReportResponseDTO:
        """
        Update an existing report.
        
        Args:
            report_id: Report ID to update
            request: Update request
            current_user: Current user context with organisation info
            
        Returns:
            Updated report response
            
        Raises:
            ReportingNotFoundError: If report not found
            ReportingValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    async def delete_report(
        self,
        report_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: Report ID to delete
            current_user: Current user context with organisation info
            
        Returns:
            True if deleted successfully
            
        Raises:
            ReportingNotFoundError: If report not found
        """
        pass
    
    # Analytics Operations
    @abstractmethod
    async def get_dashboard_analytics(
        self, 
        current_user: "CurrentUser"
    ) -> DashboardAnalyticsDTO:
        """
        Get consolidated dashboard analytics.
        
        Args:
            current_user: Current user context with organisation info
            
        Returns:
            Dashboard analytics data
        """
        pass
    
    @abstractmethod
    async def get_user_analytics(
        self, 
        current_user: "CurrentUser"
    ) -> UserAnalyticsDTO:
        """
        Get user analytics data.
        
        Args:
            current_user: Current user context with organisation info
            
        Returns:
            User analytics data
        """
        pass
    
    @abstractmethod
    async def get_attendance_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> AttendanceAnalyticsDTO:
        """
        Get attendance analytics data.
        
        Args:
            current_user: Current user context with organisation info
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Attendance analytics data
        """
        pass
    
    @abstractmethod
    async def get_leave_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> LeaveAnalyticsDTO:
        """
        Get leave analytics data.
        
        Args:
            current_user: Current user context with organisation info
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Leave analytics data
        """
        pass
    
    @abstractmethod
    async def get_payroll_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> PayrollAnalyticsDTO:
        """
        Get payroll analytics data.
        
        Args:
            current_user: Current user context with organisation info
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Payroll analytics data
        """
        pass
    
    @abstractmethod
    async def get_reimbursement_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ReimbursementAnalyticsDTO:
        """
        Get reimbursement analytics data.
        
        Args:
            current_user: Current user context with organisation info
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Reimbursement analytics data
        """
        pass
    
    @abstractmethod
    async def get_consolidated_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ConsolidatedAnalyticsDTO:
        """
        Get consolidated analytics from all modules.
        
        Args:
            current_user: Current user context with organisation info
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Consolidated analytics data
        """
        pass
    
    # Export Operations
    @abstractmethod
    async def export_report(
        self,
        request: ExportRequestDTO,
        current_user: "CurrentUser"
    ) -> ExportResponseDTO:
        """
        Export report data to file.
        
        Args:
            request: Export request with format and parameters
            current_user: Current user context with organisation info
            
        Returns:
            Export response with file information
            
        Raises:
            ReportingValidationError: If validation fails
        """
        pass
    
    # Utility Operations
    @abstractmethod
    async def cleanup_old_reports(
        self,
        current_user: "CurrentUser",
        days_old: int = 30
    ) -> Dict[str, Any]:
        """
        Clean up old reports.
        
        Args:
            current_user: Current user context with organisation info
            days_old: Number of days after which to clean up reports
            
        Returns:
            Cleanup statistics
        """
        pass 