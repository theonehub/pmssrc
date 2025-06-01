"""
Organization Service Interfaces
Following Interface Segregation Principle for organization business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.organization import Organization
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.organization_details import OrganizationType, OrganizationStatus
from app.application.dto.organization_dto import (
    CreateOrganizationRequestDTO, UpdateOrganizationRequestDTO,
    OrganizationStatusUpdateRequestDTO, OrganizationSearchFiltersDTO,
    OrganizationResponseDTO, OrganizationSummaryDTO, OrganizationListResponseDTO,
    OrganizationStatisticsDTO, OrganizationAnalyticsDTO, OrganizationHealthCheckDTO,
    BulkOrganizationUpdateDTO, BulkOrganizationUpdateResultDTO
)


class OrganizationCommandService(ABC):
    """
    Service interface for organization command operations.
    
    Follows SOLID principles:
    - SRP: Only handles command operations
    - OCP: Can be extended with new command operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def create_organization(self, request: CreateOrganizationRequestDTO) -> OrganizationResponseDTO:
        """
        Create a new organization.
        
        Args:
            request: Organization creation request DTO
            
        Returns:
            Created organization response DTO
            
        Raises:
            OrganizationValidationError: If request data is invalid
            OrganizationConflictError: If organization already exists
            OrganizationBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_organization(
        self, 
        organization_id: str, 
        request: UpdateOrganizationRequestDTO
    ) -> OrganizationResponseDTO:
        """
        Update an existing organization.
        
        Args:
            organization_id: ID of organization to update
            request: Organization update request DTO
            
        Returns:
            Updated organization response DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationValidationError: If request data is invalid
            OrganizationBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_organization_status(
        self, 
        organization_id: str, 
        request: OrganizationStatusUpdateRequestDTO
    ) -> OrganizationResponseDTO:
        """
        Update organization status (activate, deactivate, suspend).
        
        Args:
            organization_id: ID of organization to update
            request: Status update request DTO
            
        Returns:
            Updated organization response DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationValidationError: If request data is invalid
            OrganizationBusinessRuleError: If status change is not allowed
        """
        pass
    
    @abstractmethod
    async def delete_organization(
        self, 
        organization_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Delete an organization.
        
        Args:
            organization_id: ID of organization to delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationBusinessRuleError: If deletion is not allowed
        """
        pass
    
    @abstractmethod
    async def increment_employee_usage(self, organization_id: str) -> OrganizationResponseDTO:
        """
        Increment employee usage for an organization.
        
        Args:
            organization_id: ID of organization
            
        Returns:
            Updated organization response DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationBusinessRuleError: If capacity limit reached
        """
        pass
    
    @abstractmethod
    async def decrement_employee_usage(self, organization_id: str) -> OrganizationResponseDTO:
        """
        Decrement employee usage for an organization.
        
        Args:
            organization_id: ID of organization
            
        Returns:
            Updated organization response DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
            OrganizationBusinessRuleError: If usage cannot be decremented
        """
        pass


class OrganizationQueryService(ABC):
    """
    Service interface for organization query operations.
    
    Follows SOLID principles:
    - SRP: Only handles query operations
    - OCP: Can be extended with new query operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_organization_by_id(self, organization_id: str) -> Optional[OrganizationResponseDTO]:
        """
        Get organization by ID.
        
        Args:
            organization_id: Organization ID to search for
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_organization_by_name(self, name: str) -> Optional[OrganizationResponseDTO]:
        """
        Get organization by name.
        
        Args:
            name: Organization name to search for
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_organization_by_hostname(self, hostname: str) -> Optional[OrganizationResponseDTO]:
        """
        Get organization by hostname.
        
        Args:
            hostname: Hostname to search for
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_organization_by_pan(self, pan_number: str) -> Optional[OrganizationResponseDTO]:
        """
        Get organization by PAN number.
        
        Args:
            pan_number: PAN number to search for
            
        Returns:
            Organization response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all_organizations(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> OrganizationListResponseDTO:
        """
        Get all organizations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive organizations
            
        Returns:
            Paginated list of organization summaries
        """
        pass
    
    @abstractmethod
    async def search_organizations(self, filters: OrganizationSearchFiltersDTO) -> OrganizationListResponseDTO:
        """
        Search organizations with filters.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            Paginated list of organization summaries matching filters
        """
        pass
    
    @abstractmethod
    async def get_organizations_by_status(self, status: str) -> List[OrganizationSummaryDTO]:
        """
        Get organizations by status.
        
        Args:
            status: Organization status to filter by
            
        Returns:
            List of organization summaries with specified status
        """
        pass
    
    @abstractmethod
    async def get_organizations_by_type(self, organization_type: str) -> List[OrganizationSummaryDTO]:
        """
        Get organizations by type.
        
        Args:
            organization_type: Organization type to filter by
            
        Returns:
            List of organization summaries with specified type
        """
        pass
    
    @abstractmethod
    async def get_organizations_by_location(
        self, 
        city: Optional[str] = None, 
        state: Optional[str] = None, 
        country: Optional[str] = None
    ) -> List[OrganizationSummaryDTO]:
        """
        Get organizations by location.
        
        Args:
            city: City to filter by
            state: State to filter by
            country: Country to filter by
            
        Returns:
            List of organization summaries in specified location
        """
        pass
    
    @abstractmethod
    async def check_organization_exists(
        self, 
        name: Optional[str] = None,
        hostname: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Check if organization exists by various criteria.
        
        Args:
            name: Organization name to check
            hostname: Hostname to check
            pan_number: PAN number to check
            exclude_id: Organization ID to exclude from check
            
        Returns:
            Dictionary with existence status for each checked field
        """
        pass


class OrganizationAnalyticsService(ABC):
    """
    Service interface for organization analytics and reporting.
    
    Follows SOLID principles:
    - SRP: Only handles analytics operations
    - OCP: Can be extended with new analytics operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for analytics operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_organization_statistics(self) -> OrganizationStatisticsDTO:
        """
        Get comprehensive organization statistics.
        
        Returns:
            Organization statistics DTO
        """
        pass
    
    @abstractmethod
    async def get_organization_analytics(self) -> OrganizationAnalyticsDTO:
        """
        Get advanced organization analytics.
        
        Returns:
            Organization analytics DTO
        """
        pass
    
    @abstractmethod
    async def get_capacity_utilization_report(self) -> Dict[str, Any]:
        """
        Get employee capacity utilization report.
        
        Returns:
            Dictionary with capacity utilization data
        """
        pass
    
    @abstractmethod
    async def get_growth_trends_report(self, months: int = 12) -> Dict[str, Any]:
        """
        Get organization growth trends report.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with growth trend data
        """
        pass
    
    @abstractmethod
    async def get_geographic_distribution_report(self) -> Dict[str, Any]:
        """
        Get geographic distribution report.
        
        Returns:
            Dictionary with geographic distribution data
        """
        pass
    
    @abstractmethod
    async def get_type_distribution_report(self) -> Dict[str, Any]:
        """
        Get organization type distribution report.
        
        Returns:
            Dictionary with type distribution data
        """
        pass
    
    @abstractmethod
    async def get_top_organizations_report(
        self, 
        criteria: str = "capacity", 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top organizations report by various criteria.
        
        Args:
            criteria: Criteria for ranking (capacity, utilization, growth)
            limit: Number of top organizations to return
            
        Returns:
            List of top organization data
        """
        pass


class OrganizationHealthService(ABC):
    """
    Service interface for organization health monitoring.
    
    Follows SOLID principles:
    - SRP: Only handles health monitoring operations
    - OCP: Can be extended with new health checks
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for health operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def perform_health_check(self, organization_id: str) -> OrganizationHealthCheckDTO:
        """
        Perform comprehensive health check for an organization.
        
        Args:
            organization_id: Organization ID to check
            
        Returns:
            Organization health check DTO
            
        Raises:
            OrganizationNotFoundError: If organization not found
        """
        pass
    
    @abstractmethod
    async def get_unhealthy_organizations(self) -> List[OrganizationHealthCheckDTO]:
        """
        Get list of organizations with health issues.
        
        Returns:
            List of unhealthy organization health checks
        """
        pass
    
    @abstractmethod
    async def get_organizations_needing_attention(self) -> List[OrganizationHealthCheckDTO]:
        """
        Get organizations that need immediate attention.
        
        Returns:
            List of organizations needing attention
        """
        pass
    
    @abstractmethod
    async def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report for all organizations.
        
        Returns:
            Dictionary with health report data
        """
        pass
    
    @abstractmethod
    async def schedule_health_checks(self) -> Dict[str, Any]:
        """
        Schedule automated health checks for all organizations.
        
        Returns:
            Dictionary with scheduling results
        """
        pass


class OrganizationBulkOperationsService(ABC):
    """
    Service interface for organization bulk operations.
    
    Follows SOLID principles:
    - SRP: Only handles bulk operations
    - OCP: Can be extended with new bulk operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for bulk operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def bulk_update_organizations(
        self, 
        request: BulkOrganizationUpdateDTO
    ) -> BulkOrganizationUpdateResultDTO:
        """
        Perform bulk update on multiple organizations.
        
        Args:
            request: Bulk update request DTO
            
        Returns:
            Bulk update result DTO
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        organization_ids: List[str], 
        status: str,
        reason: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> BulkOrganizationUpdateResultDTO:
        """
        Bulk update organization status.
        
        Args:
            organization_ids: List of organization IDs to update
            status: New status to set
            reason: Reason for status change
            updated_by: User performing the update
            
        Returns:
            Bulk update result DTO
        """
        pass
    
    @abstractmethod
    async def bulk_update_employee_strength(
        self, 
        updates: Dict[str, int],
        updated_by: Optional[str] = None
    ) -> BulkOrganizationUpdateResultDTO:
        """
        Bulk update employee strength for multiple organizations.
        
        Args:
            updates: Dictionary mapping organization ID to new employee strength
            updated_by: User performing the update
            
        Returns:
            Bulk update result DTO
        """
        pass
    
    @abstractmethod
    async def bulk_export_organizations(
        self, 
        organization_ids: Optional[List[str]] = None,
        format: str = "csv",
        include_details: bool = True
    ) -> bytes:
        """
        Bulk export organization data.
        
        Args:
            organization_ids: List of organization IDs to export (None for all)
            format: Export format (csv, excel, json)
            include_details: Whether to include detailed information
            
        Returns:
            Exported data as bytes
        """
        pass
    
    @abstractmethod
    async def bulk_import_organizations(
        self, 
        data: bytes, 
        format: str = "csv",
        validate_only: bool = False,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk import organization data.
        
        Args:
            data: Import data as bytes
            format: Import format (csv, excel, json)
            validate_only: Whether to only validate without importing
            created_by: User performing the import
            
        Returns:
            Dictionary with import results
        """
        pass


class OrganizationValidationService(ABC):
    """
    Service interface for organization validation operations.
    
    Follows SOLID principles:
    - SRP: Only handles validation operations
    - OCP: Can be extended with new validation rules
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for validation operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def validate_organization_data(self, request: CreateOrganizationRequestDTO) -> List[str]:
        """
        Validate organization creation data.
        
        Args:
            request: Organization creation request DTO
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_organization_update(
        self, 
        organization_id: str, 
        request: UpdateOrganizationRequestDTO
    ) -> List[str]:
        """
        Validate organization update data.
        
        Args:
            organization_id: ID of organization being updated
            request: Organization update request DTO
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_business_rules(self, organization: Organization) -> List[str]:
        """
        Validate organization business rules.
        
        Args:
            organization: Organization entity to validate
            
        Returns:
            List of business rule violations (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_uniqueness_constraints(
        self, 
        name: Optional[str] = None,
        hostname: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> List[str]:
        """
        Validate uniqueness constraints.
        
        Args:
            name: Organization name to check
            hostname: Hostname to check
            pan_number: PAN number to check
            exclude_id: Organization ID to exclude from check
            
        Returns:
            List of uniqueness violations (empty if valid)
        """
        pass


class OrganizationNotificationService(ABC):
    """
    Service interface for organization notification operations.
    
    Follows SOLID principles:
    - SRP: Only handles notification operations
    - OCP: Can be extended with new notification types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for notification operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def send_organization_created_notification(self, organization: Organization) -> bool:
        """
        Send notification when organization is created.
        
        Args:
            organization: Created organization entity
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_organization_updated_notification(
        self, 
        organization: Organization, 
        updated_fields: List[str]
    ) -> bool:
        """
        Send notification when organization is updated.
        
        Args:
            organization: Updated organization entity
            updated_fields: List of fields that were updated
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_status_change_notification(
        self, 
        organization: Organization, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send notification when organization status changes.
        
        Args:
            organization: Organization entity
            old_status: Previous status
            new_status: New status
            reason: Reason for status change
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_capacity_alert_notification(
        self, 
        organization: Organization, 
        alert_type: str
    ) -> bool:
        """
        Send notification for capacity alerts.
        
        Args:
            organization: Organization entity
            alert_type: Type of alert (near_capacity, at_capacity, over_capacity)
            
        Returns:
            True if notification sent successfully
        """
        pass


class OrganizationServiceFactory(ABC):
    """
    Factory interface for creating organization service implementations.
    
    Follows SOLID principles:
    - SRP: Only creates service instances
    - OCP: Can be extended with new service types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for factory operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    def create_command_service(self) -> OrganizationCommandService:
        """Create command service instance"""
        pass
    
    @abstractmethod
    def create_query_service(self) -> OrganizationQueryService:
        """Create query service instance"""
        pass
    
    @abstractmethod
    def create_analytics_service(self) -> OrganizationAnalyticsService:
        """Create analytics service instance"""
        pass
    
    @abstractmethod
    def create_health_service(self) -> OrganizationHealthService:
        """Create health service instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_service(self) -> OrganizationBulkOperationsService:
        """Create bulk operations service instance"""
        pass
    
    @abstractmethod
    def create_validation_service(self) -> OrganizationValidationService:
        """Create validation service instance"""
        pass
    
    @abstractmethod
    def create_notification_service(self) -> OrganizationNotificationService:
        """Create notification service instance"""
        pass


class OrganizationService(
    OrganizationCommandService,
    OrganizationQueryService,
    OrganizationAnalyticsService,
    OrganizationHealthService,
    OrganizationBulkOperationsService,
    OrganizationValidationService,
    OrganizationNotificationService
):
    """
    Composite service interface combining all organization service interfaces.
    
    This interface can be used when you need access to all service operations
    in a single interface. Individual interfaces should be preferred when possible
    to follow the Interface Segregation Principle.
    
    Follows SOLID principles:
    - SRP: Combines related service operations
    - OCP: Can be extended through composition
    - LSP: All implementations must be substitutable
    - ISP: Composed of focused interfaces
    - DIP: Depends on abstractions
    """
    pass 