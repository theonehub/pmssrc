"""
Company Leave Service Interface
Following Interface Segregation Principle for company leave business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

from app.application.dto.company_leave_dto import (
    CreateCompanyLeaveRequestDTO,
    UpdateCompanyLeaveRequestDTO,
    CompanyLeaveResponseDTO,
    CompanyLeaveListResponseDTO,
    CompanyLeaveSearchFiltersDTO,
    BulkCompanyLeaveUpdateDTO,
    BulkCompanyLeaveUpdateResultDTO,
    CompanyLeaveStatisticsDTO,
    CompanyLeaveAnalyticsDTO
)

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser


class CompanyLeaveCommandService(ABC):
    """
    Service interface for company leave command operations.
    
    Follows SOLID principles:
    - SRP: Only handles command operations
    - OCP: Can be extended with new command operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def create_company_leave(
        self, 
        request: CreateCompanyLeaveRequestDTO, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """
        Create a new company leave policy.
        
        Args:
            request: Company leave creation request DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Created company leave response DTO
            
        Raises:
            CompanyLeaveValidationError: If request data is invalid
            CompanyLeaveConflictError: If leave policy already exists
            CompanyLeaveBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_company_leave(
        self, 
        leave_id: str, 
        request: UpdateCompanyLeaveRequestDTO,
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """
        Update an existing company leave policy.
        
        Args:
            leave_id: ID of leave policy to update
            request: Company leave update request DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Updated company leave response DTO
            
        Raises:
            CompanyLeaveNotFoundError: If leave policy not found
            CompanyLeaveValidationError: If request data is invalid
            CompanyLeaveBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def delete_company_leave(
        self, 
        leave_id: str, 
        deletion_reason: str,
        current_user: "CurrentUser",
        deleted_by: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a company leave policy.
        
        Args:
            leave_id: ID of leave policy to delete
            deletion_reason: Reason for deletion
            current_user: Current authenticated user with organisation context
            deleted_by: User performing the deletion
            soft_delete: Whether to perform soft delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            CompanyLeaveNotFoundError: If leave policy not found
            CompanyLeaveBusinessRuleError: If deletion is not allowed
        """
        pass
    
    @abstractmethod
    async def activate_company_leave(
        self, 
        leave_id: str, 
        activated_by: str,
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """
        Activate a company leave policy.
        
        Args:
            leave_id: ID of leave policy to activate
            activated_by: User activating the policy
            current_user: Current authenticated user with organisation context
            
        Returns:
            Updated company leave response DTO
        """
        pass
    
    @abstractmethod
    async def deactivate_company_leave(
        self, 
        leave_id: str, 
        deactivated_by: str,
        reason: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> CompanyLeaveResponseDTO:
        """
        Deactivate a company leave policy.
        
        Args:
            leave_id: ID of leave policy to deactivate
            deactivated_by: User deactivating the policy
            reason: Reason for deactivation
            current_user: Current authenticated user with organisation context
            
        Returns:
            Updated company leave response DTO
        """
        pass


class CompanyLeaveQueryService(ABC):
    """
    Service interface for company leave query operations.
    """
    
    @abstractmethod
    async def get_company_leave_by_id(
        self, 
        leave_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[CompanyLeaveResponseDTO]:
        """
        Get company leave by ID.
        
        Args:
            leave_id: Company leave ID to search for
            current_user: Current authenticated user with organisation context
            
        Returns:
            Company leave response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_company_leave_by_type(
        self, 
        leave_type: str, 
        current_user: "CurrentUser"
    ) -> Optional[CompanyLeaveResponseDTO]:
        """
        Get company leave by type.
        
        Args:
            leave_type: Leave type to search for
            current_user: Current authenticated user with organisation context
            
        Returns:
            Company leave response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_company_leaves(
        self, 
        filters: Optional[CompanyLeaveSearchFiltersDTO] = None,
        current_user: "CurrentUser" = None
    ) -> CompanyLeaveListResponseDTO:
        """
        List company leaves with optional filters.
        
        Args:
            filters: Search filters and pagination parameters
            current_user: Current authenticated user with organisation context
            
        Returns:
            Paginated list of company leave response DTOs matching filters
        """
        pass
    
    @abstractmethod
    async def get_active_leaves(
        self, 
        current_user: "CurrentUser"
    ) -> List[CompanyLeaveResponseDTO]:
        """
        Get all active company leave policies.
        
        Args:
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of active company leave policies
        """
        pass
    
    @abstractmethod
    async def get_leaves_by_category(
        self, 
        category: str, 
        current_user: "CurrentUser"
    ) -> List[CompanyLeaveResponseDTO]:
        """
        Get company leaves by category.
        
        Args:
            category: Leave category to filter by
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of company leaves in specified category
        """
        pass
    
    @abstractmethod
    async def check_leave_exists(
        self, 
        leave_type: str,
        exclude_id: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> bool:
        """
        Check if leave type already exists.
        
        Args:
            leave_type: Leave type to check
            exclude_id: Leave ID to exclude from check
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if leave type exists, False otherwise
        """
        pass


class CompanyLeaveValidationService(ABC):
    """
    Service interface for company leave validation operations.
    """
    
    @abstractmethod
    async def validate_leave_request(
        self, 
        request: CreateCompanyLeaveRequestDTO,
        current_user: "CurrentUser"
    ) -> List[str]:
        """
        Validate company leave creation request.
        
        Args:
            request: Company leave creation request DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_leave_update(
        self, 
        leave_id: str, 
        request: UpdateCompanyLeaveRequestDTO,
        current_user: "CurrentUser"
    ) -> List[str]:
        """
        Validate company leave update request.
        
        Args:
            leave_id: Leave ID being updated
            request: Company leave update request DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_business_rules(
        self, 
        leave_data: Dict[str, Any],
        current_user: "CurrentUser"
    ) -> List[str]:
        """
        Validate company leave business rules.
        
        Args:
            leave_data: Leave data to validate
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of business rule violations (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_leave_conflicts(
        self, 
        request: CreateCompanyLeaveRequestDTO,
        exclude_id: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> List[str]:
        """
        Validate leave type conflicts.
        
        Args:
            request: Company leave request to validate
            exclude_id: Leave ID to exclude from conflict check
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of conflict errors (empty if no conflicts)
        """
        pass


class CompanyLeaveNotificationService(ABC):
    """
    Service interface for company leave notification operations.
    """
    
    @abstractmethod
    async def notify_leave_created(
        self, 
        company_leave: CompanyLeaveResponseDTO,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Notify about company leave creation.
        
        Args:
            company_leave: Created company leave
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def notify_leave_updated(
        self, 
        company_leave: CompanyLeaveResponseDTO,
        changes: Dict[str, Any],
        current_user: "CurrentUser"
    ) -> bool:
        """
        Notify about company leave update.
        
        Args:
            company_leave: Updated company leave
            changes: Dictionary of changes made
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def notify_leave_deleted(
        self, 
        leave_id: str, 
        leave_type: str,
        deleted_by: str,
        reason: str,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Notify about company leave deletion.
        
        Args:
            leave_id: ID of deleted leave
            leave_type: Type of deleted leave
            deleted_by: User who deleted the leave
            reason: Reason for deletion
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def notify_leave_status_changed(
        self, 
        company_leave: CompanyLeaveResponseDTO,
        old_status: str,
        new_status: str,
        changed_by: str,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Notify about company leave status change.
        
        Args:
            company_leave: Company leave with status change
            old_status: Previous status
            new_status: New status
            changed_by: User who changed the status
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if notification sent successfully
        """
        pass


class CompanyLeaveAnalyticsService(ABC):
    """
    Service interface for company leave analytics and reporting.
    """
    
    @abstractmethod
    async def get_leave_statistics(
        self, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveStatisticsDTO:
        """
        Get comprehensive leave statistics.
        
        Args:
            current_user: Current authenticated user with organisation context
            
        Returns:
            Leave statistics including counts, distributions, and trends
        """
        pass
    
    @abstractmethod
    async def get_leave_analytics(
        self, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveAnalyticsDTO:
        """
        Get detailed leave analytics.
        
        Args:
            current_user: Current authenticated user with organisation context
            
        Returns:
            Leave analytics including usage patterns and insights
        """
        pass
    
    @abstractmethod
    async def get_leave_usage_report(
        self, 
        start_date: date, 
        end_date: date,
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """
        Get leave usage report for a date range.
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            current_user: Current authenticated user with organisation context
            
        Returns:
            Leave usage report with trends and patterns
        """
        pass
    
    @abstractmethod
    async def get_leave_type_distribution(
        self, 
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """
        Get leave type distribution report.
        
        Args:
            current_user: Current authenticated user with organisation context
            
        Returns:
            Leave type distribution statistics
        """
        pass


class CompanyLeaveBulkOperationsService(ABC):
    """
    Service interface for bulk company leave operations.
    """
    
    @abstractmethod
    async def bulk_update_leaves(
        self, 
        updates: List[BulkCompanyLeaveUpdateDTO],
        updated_by: str,
        current_user: "CurrentUser"
    ) -> BulkCompanyLeaveUpdateResultDTO:
        """
        Bulk update multiple company leaves.
        
        Args:
            updates: List of update requests
            updated_by: User performing the updates
            current_user: Current authenticated user with organisation context
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_activate_leaves(
        self, 
        leave_ids: List[str],
        activated_by: str,
        current_user: "CurrentUser"
    ) -> BulkCompanyLeaveUpdateResultDTO:
        """
        Bulk activate company leaves.
        
        Args:
            leave_ids: List of leave IDs to activate
            activated_by: User performing the activation
            current_user: Current authenticated user with organisation context
            
        Returns:
            Results of bulk activation operation
        """
        pass
    
    @abstractmethod
    async def bulk_deactivate_leaves(
        self, 
        leave_ids: List[str],
        deactivated_by: str,
        reason: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> BulkCompanyLeaveUpdateResultDTO:
        """
        Bulk deactivate company leaves.
        
        Args:
            leave_ids: List of leave IDs to deactivate
            deactivated_by: User performing the deactivation
            reason: Reason for deactivation
            current_user: Current authenticated user with organisation context
            
        Returns:
            Results of bulk deactivation operation
        """
        pass
    
    @abstractmethod
    async def bulk_export_leaves(
        self, 
        leave_ids: Optional[List[str]] = None,
        format: str = "csv",
        current_user: "CurrentUser" = None
    ) -> bytes:
        """
        Bulk export company leave data.
        
        Args:
            leave_ids: List of leave IDs to export (None for all)
            format: Export format (csv, xlsx, json)
            current_user: Current authenticated user with organisation context
            
        Returns:
            Exported data as bytes
        """
        pass


class CompanyLeaveService(
    CompanyLeaveCommandService,
    CompanyLeaveQueryService,
    CompanyLeaveValidationService,
    CompanyLeaveNotificationService,
    CompanyLeaveAnalyticsService,
    CompanyLeaveBulkOperationsService
):
    """
    Combined company leave service interface.
    
    Aggregates all company leave service interfaces for convenience
    when a single implementation handles all operations.
    """
    pass
