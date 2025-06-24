"""
Reimbursement Service Interfaces
Following Interface Segregation Principle for reimbursement business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

from app.application.dto.reimbursement_dto import (
    ReimbursementTypeCreateRequestDTO,
    ReimbursementTypeUpdateRequestDTO,
    ReimbursementRequestCreateDTO,
    ReimbursementRequestUpdateDTO,
    ReimbursementApprovalDTO,
    ReimbursementRejectionDTO,
    ReimbursementPaymentDTO,
    ReimbursementSearchFiltersDTO,
    ReimbursementTypeResponseDTO,
    ReimbursementResponseDTO,
    ReimbursementSummaryDTO,
    ReimbursementListResponseDTO,
    ReimbursementStatisticsDTO,
    ReimbursementTypeOptionsDTO
)

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser


class ReimbursementTypeCommandService(ABC):
    """
    Service interface for reimbursement type command operations.
    
    Follows SOLID principles:
    - SRP: Only handles command operations for reimbursement types
    - OCP: Can be extended with new command operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def create_reimbursement_type(
        self, 
        request: ReimbursementTypeCreateRequestDTO, 
        current_user: "CurrentUser"
    ) -> ReimbursementTypeResponseDTO:
        """
        Create a new reimbursement type.
        
        Args:
            request: Reimbursement type creation request DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Created reimbursement type response DTO
            
        Raises:
            ReimbursementValidationError: If request data is invalid
            ReimbursementBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_reimbursement_type(
        self,
        type_id: str,
        request: ReimbursementTypeUpdateRequestDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementTypeResponseDTO:
        """
        Update an existing reimbursement type.
        
        Args:
            type_id: ID of reimbursement type to update
            request: Reimbursement type update request DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Updated reimbursement type response DTO
            
        Raises:
            ReimbursementNotFoundError: If reimbursement type not found
            ReimbursementValidationError: If request data is invalid
            ReimbursementBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def delete_reimbursement_type(
        self,
        type_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Delete (deactivate) a reimbursement type.
        
        Args:
            type_id: ID of reimbursement type to delete
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if deleted successfully
            
        Raises:
            ReimbursementNotFoundError: If reimbursement type not found
            ReimbursementBusinessRuleError: If deletion is not allowed
        """
        pass


class ReimbursementRequestCommandService(ABC):
    """
    Service interface for reimbursement request command operations.
    
    Follows SOLID principles:
    - SRP: Only handles command operations for reimbursement requests
    - OCP: Can be extended with new command operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def create_reimbursement_request(
        self, 
        request: ReimbursementRequestCreateDTO, 
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """
        Create a new reimbursement request.
        
        Args:
            request: Reimbursement request creation DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Created reimbursement request response DTO
            
        Raises:
            ReimbursementValidationError: If request data is invalid
            ReimbursementBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_reimbursement_request(
        self,
        request_id: str,
        request: ReimbursementRequestUpdateDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """
        Update an existing reimbursement request.
        
        Args:
            request_id: ID of reimbursement request to update
            request: Reimbursement request update DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Updated reimbursement request response DTO
            
        Raises:
            ReimbursementNotFoundError: If reimbursement request not found
            ReimbursementValidationError: If request data is invalid
            ReimbursementBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def approve_reimbursement_request(
        self,
        request_id: str,
        approval: ReimbursementApprovalDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """
        Approve a reimbursement request.
        
        Args:
            request_id: ID of reimbursement request to approve
            approval: Approval details DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Approved reimbursement request response DTO
            
        Raises:
            ReimbursementNotFoundError: If reimbursement request not found
            ReimbursementValidationError: If approval data is invalid
            ReimbursementBusinessRuleError: If approval is not allowed
        """
        pass
    
    @abstractmethod
    async def reject_reimbursement_request(
        self,
        request_id: str,
        rejection: ReimbursementRejectionDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """
        Reject a reimbursement request.
        
        Args:
            request_id: ID of reimbursement request to reject
            rejection: Rejection details DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Rejected reimbursement request response DTO
            
        Raises:
            ReimbursementNotFoundError: If reimbursement request not found
            ReimbursementValidationError: If rejection data is invalid
            ReimbursementBusinessRuleError: If rejection is not allowed
        """
        pass
    
    @abstractmethod
    async def process_reimbursement_payment(
        self,
        request_id: str,
        payment: ReimbursementPaymentDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """
        Process payment for a reimbursement request.
        
        Args:
            request_id: ID of reimbursement request to process payment
            payment: Payment details DTO
            current_user: Current authenticated user with organisation context
            
        Returns:
            Processed reimbursement request response DTO
            
        Raises:
            ReimbursementNotFoundError: If reimbursement request not found
            ReimbursementValidationError: If payment data is invalid
            ReimbursementBusinessRuleError: If payment processing is not allowed
        """
        pass
    
    @abstractmethod
    async def delete_reimbursement_request(
        self,
        request_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Delete a reimbursement request.
        
        Args:
            request_id: ID of reimbursement request to delete
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if deletion was successful, False otherwise
            
        Raises:
            ReimbursementNotFoundError: If reimbursement request not found
            ReimbursementBusinessRuleError: If deletion is not allowed
        """
        pass

    @abstractmethod
    async def attach_receipt_to_request(
        self,
        request_id: str,
        file_path: str,
        file_name: str,
        file_size: int,
        uploaded_by: str,
        current_user: "CurrentUser"
    ) -> bool:
        """
        Attach a receipt to an existing reimbursement request.
        
        Args:
            request_id: ID of reimbursement request
            file_path: Path to the uploaded receipt file
            file_name: Name of the receipt file
            file_size: Size of the receipt file in bytes
            uploaded_by: ID of user who uploaded the receipt
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if receipt was attached successfully, False otherwise
            
        Raises:
            ReimbursementNotFoundError: If reimbursement request not found
            ReimbursementBusinessRuleError: If receipt attachment is not allowed
        """
        pass


class ReimbursementQueryService(ABC):
    """
    Service interface for reimbursement query operations.
    
    Follows SOLID principles:
    - SRP: Only handles query operations
    - OCP: Can be extended with new query operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_reimbursement_type_by_id(
        self, 
        type_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[ReimbursementTypeResponseDTO]:
        """
        Get reimbursement type by ID.
        
        Args:
            type_id: Reimbursement type ID to search for
            current_user: Current authenticated user with organisation context
            
        Returns:
            Reimbursement type response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_reimbursement_request_by_id(
        self, 
        request_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[ReimbursementResponseDTO]:
        """
        Get reimbursement request by ID.
        
        Args:
            request_id: Reimbursement request ID to search for
            current_user: Current authenticated user with organisation context
            
        Returns:
            Reimbursement request response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_reimbursement_types(
        self,
        include_inactive: bool = False,
        current_user: "CurrentUser" = None
    ) -> List[ReimbursementTypeOptionsDTO]:
        """
        List all reimbursement types.
        
        Args:
            include_inactive: Whether to include inactive types
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of reimbursement type option DTOs
        """
        pass
    
    @abstractmethod
    async def list_reimbursement_requests(
        self, 
        filters: Optional[ReimbursementSearchFiltersDTO] = None,
        current_user: "CurrentUser" = None
    ) -> ReimbursementListResponseDTO:
        """
        List reimbursement requests with optional filters.
        
        Args:
            filters: Search filters and pagination parameters
            current_user: Current authenticated user with organisation context
            
        Returns:
            Paginated list of reimbursement request summary DTOs
        """
        pass
    
    @abstractmethod
    async def get_reimbursement_requests_by_employee(
        self,
        employee_id: str,
        current_user: "CurrentUser"
    ) -> List[ReimbursementSummaryDTO]:
        """
        Get reimbursement requests for a specific employee.
        
        Args:
            employee_id: Employee ID to filter by
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of reimbursement request summary DTOs
        """
        pass
    
    @abstractmethod
    async def get_pending_approvals(
        self,
        approver_id: str,
        current_user: "CurrentUser"
    ) -> List[ReimbursementSummaryDTO]:
        """
        Get reimbursement requests pending approval by a specific approver.
        
        Args:
            approver_id: Approver ID to filter by
            current_user: Current authenticated user with organisation context
            
        Returns:
            List of reimbursement request summary DTOs pending approval
        """
        pass

    @abstractmethod
    async def get_receipt_file_path(
        self,
        request_id: str,
        current_user: "CurrentUser"
    ) -> Optional[str]:
        """
        Get receipt file path for a reimbursement request.
        
        Args:
            request_id: Reimbursement request ID
            current_user: Current authenticated user with organisation context
            
        Returns:
            File path to the receipt if it exists, None otherwise
        """
        pass


class ReimbursementAnalyticsService(ABC):
    """
    Service interface for reimbursement analytics and reporting.
    
    Provides methods for generating reimbursement statistics, analytics,
    and insights for business intelligence purposes.
    """
    
    @abstractmethod
    async def get_reimbursement_statistics(
        self, 
        current_user: "CurrentUser"
    ) -> ReimbursementStatisticsDTO:
        """
        Get comprehensive reimbursement statistics.
        
        Args:
            current_user: Current authenticated user with organisation context
        
        Returns:
            Reimbursement statistics including counts, amounts, and distributions
        """
        pass
    
    @abstractmethod
    async def get_reimbursement_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        current_user: "CurrentUser" = None
    ) -> Dict[str, Any]:
        """
        Get detailed reimbursement analytics.
        
        Args:
            start_date: Start date for analytics period
            end_date: End date for analytics period
            current_user: Current authenticated user with organisation context
            
        Returns:
            Detailed analytics including trends and patterns
        """
        pass
    
    @abstractmethod
    async def get_employee_reimbursement_report(
        self,
        employee_id: str,
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """
        Get reimbursement report for a specific employee.
        
        Args:
            employee_id: Employee ID
            current_user: Current authenticated user with organisation context
            
        Returns:
            Employee-specific reimbursement report
        """
        pass
    
    @abstractmethod
    async def get_category_wise_report(
        self,
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """
        Get category-wise reimbursement report.
        
        Args:
            current_user: Current authenticated user with organisation context
            
        Returns:
            Category-wise breakdown report
        """
        pass


class ReimbursementService(
    ReimbursementTypeCommandService,
    ReimbursementRequestCommandService,
    ReimbursementQueryService,
    ReimbursementAnalyticsService
):
    """
    Combined reimbursement service interface.
    
    Aggregates all reimbursement service interfaces for convenience
    when a single implementation handles all operations.
    """
    pass 