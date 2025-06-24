"""
Organisation Service Interfaces
Following Interface Segregation Principle for organisation business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import OrganisationType
from app.application.dto.organisation_dto import (
    CreateOrganisationRequestDTO, UpdateOrganisationRequestDTO,
    OrganisationSearchFiltersDTO, OrganisationResponseDTO, OrganisationSummaryDTO, 
    OrganisationListResponseDTO, OrganisationStatisticsDTO, OrganisationAnalyticsDTO, 
    OrganisationHealthCheckDTO, BulkOrganisationUpdateResultDTO
)


class OrganisationCommandService(ABC):
    """
    Service interface for organisation command operations.
    
    Follows SOLID principles:
    - SRP: Only handles command operations
    - OCP: Can be extended with new command operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def create_organisation(self, request: CreateOrganisationRequestDTO) -> OrganisationResponseDTO:
        """
        Create a new organisation.
        
        Args:
            request: Organisation creation request DTO
            
        Returns:
            Created organisation response DTO
            
        Raises:
            OrganisationValidationError: If request data is invalid
            OrganisationConflictError: If organisation already exists
            OrganisationBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_organisation(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO
    ) -> OrganisationResponseDTO:
        """
        Update an existing organisation.
        
        Args:
            organisation_id: ID of organisation to update
            request: Organisation update request DTO
            
        Returns:
            Updated organisation response DTO
            
        Raises:
            OrganisationNotFoundError: If organisation not found
            OrganisationValidationError: If request data is invalid
            OrganisationBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def increment_employee_usage(self, organisation_id: str) -> OrganisationResponseDTO:
        """
        Increment employee usage for an organisation.
        
        Args:
            organisation_id: ID of organisation
            
        Returns:
            Updated organisation response DTO
            
        Raises:
            OrganisationNotFoundError: If organisation not found
            OrganisationBusinessRuleError: If capacity limit reached
        """
        pass
    
    @abstractmethod
    async def decrement_employee_usage(self, organisation_id: str) -> OrganisationResponseDTO:
        """
        Decrement employee usage for an organisation.
        
        Args:
            organisation_id: ID of organisation
            
        Returns:
            Updated organisation response DTO
            
        Raises:
            OrganisationNotFoundError: If organisation not found
            OrganisationBusinessRuleError: If usage cannot be decremented
        """
        pass


class OrganisationQueryService(ABC):
    """
    Service interface for organisation query operations.
    
    Follows SOLID principles:
    - SRP: Only handles query operations
    - OCP: Can be extended with new query operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_organisation_by_id(self, organisation_id: str) -> Optional[OrganisationResponseDTO]:
        """
        Get organisation by ID.
        
        Args:
            organisation_id: Organisation ID to search for
            
        Returns:
            Organisation response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_organisation_by_name(self, name: str) -> Optional[OrganisationResponseDTO]:
        """
        Get organisation by name.
        
        Args:
            name: Organisation name to search for
            
        Returns:
            Organisation response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_organisation_by_hostname(self, hostname: str) -> Optional[OrganisationResponseDTO]:
        """
        Get organisation by hostname.
        
        Args:
            hostname: Hostname to search for
            
        Returns:
            Organisation response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_organisation_by_pan(self, pan_number: str) -> Optional[OrganisationResponseDTO]:
        """
        Get organisation by PAN number.
        
        Args:
            pan_number: PAN number to search for
            
        Returns:
            Organisation response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all_organisations(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> OrganisationListResponseDTO:
        """
        Get all organisations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive organisations
            
        Returns:
            Paginated list of organisation summaries
        """
        pass
    
    @abstractmethod
    async def search_organisations(self, filters: OrganisationSearchFiltersDTO) -> OrganisationListResponseDTO:
        """
        Search organisations with filters.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            Paginated list of organisation summaries matching filters
        """
        pass
    
    @abstractmethod
    async def get_organisations_by_status(self, status: str) -> List[OrganisationSummaryDTO]:
        """
        Get organisations by status.
        
        Args:
            status: Organisation status to filter by
            
        Returns:
            List of organisation summaries with specified status
        """
        pass
    
    @abstractmethod
    async def get_organisations_by_type(self, organisation_type: str) -> List[OrganisationSummaryDTO]:
        """
        Get organisations by type.
        
        Args:
            organisation_type: Organisation type to filter by
            
        Returns:
            List of organisation summaries with specified type
        """
        pass
    
    @abstractmethod
    async def get_organisations_by_location(
        self, 
        city: Optional[str] = None, 
        state: Optional[str] = None, 
        country: Optional[str] = None
    ) -> List[OrganisationSummaryDTO]:
        """
        Get organisations by location.
        
        Args:
            city: City to filter by
            state: State to filter by
            country: Country to filter by
            
        Returns:
            List of organisation summaries in specified location
        """
        pass
    
    @abstractmethod
    async def check_organisation_exists(
        self, 
        name: Optional[str] = None,
        hostname: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Check if organisation exists by various criteria.
        
        Args:
            name: Organisation name to check
            hostname: Hostname to check
            pan_number: PAN number to check
            exclude_id: Organisation ID to exclude from check
            
        Returns:
            Dictionary with existence status for each checked field
        """
        pass


class OrganisationAnalyticsService(ABC):
    """
    Service interface for organisation analytics and reporting.
    
    Follows SOLID principles:
    - SRP: Only handles analytics operations
    - OCP: Can be extended with new analytics operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for analytics operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_organisation_statistics(self) -> OrganisationStatisticsDTO:
        """
        Get comprehensive organisation statistics.
        
        Returns:
            Organisation statistics DTO
        """
        pass
    
    @abstractmethod
    async def get_organisation_analytics(self) -> OrganisationAnalyticsDTO:
        """
        Get advanced organisation analytics.
        
        Returns:
            Organisation analytics DTO
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
        Get organisation growth trends report.
        
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
        Get organisation type distribution report.
        
        Returns:
            Dictionary with type distribution data
        """
        pass
    
    @abstractmethod
    async def get_top_organisations_report(
        self, 
        criteria: str = "capacity", 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top organisations report by various criteria.
        
        Args:
            criteria: Criteria for ranking (capacity, utilization, growth)
            limit: Number of top organisations to return
            
        Returns:
            List of top organisation data
        """
        pass


class OrganisationHealthService(ABC):
    """
    Service interface for organisation health monitoring.
    
    Follows SOLID principles:
    - SRP: Only handles health monitoring operations
    - OCP: Can be extended with new health checks
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for health operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def perform_health_check(self, organisation_id: str) -> OrganisationHealthCheckDTO:
        """
        Perform comprehensive health check for an organisation.
        
        Args:
            organisation_id: Organisation ID to check
            
        Returns:
            Organisation health check DTO
            
        Raises:
            OrganisationNotFoundError: If organisation not found
        """
        pass
    
    @abstractmethod
    async def get_unhealthy_organisations(self) -> List[OrganisationHealthCheckDTO]:
        """
        Get list of organisations with health issues.
        
        Returns:
            List of unhealthy organisation health checks
        """
        pass
    
    # @abstractmethod
    # async def get_organisations_needing_attention(self) -> List[OrganisationHealthCheckDTO]:
    #     """
    #     Get organisations that need immediate attention.
        
    #     Returns:
    #         List of organisations needing attention
    #     """
    #     pass
    
    # @abstractmethod
    # async def generate_health_report(self) -> Dict[str, Any]:
    #     """
    #     Generate comprehensive health report for all organisations.
        
    #     Returns:
    #         Dictionary with health report data
    #     """
    #     pass
    
    # @abstractmethod
    # async def schedule_health_checks(self) -> Dict[str, Any]:
    #     """
    #     Schedule automated health checks for all organisations.
        
    #     Returns:
    #         Dictionary with scheduling results
    #     """
    #     pass


class OrganisationBulkOperationsService(ABC):
    """
    Service interface for organisation bulk operations.
    
    Follows SOLID principles:
    - SRP: Only handles bulk operations
    - OCP: Can be extended with new bulk operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for bulk operations
    - DIP: Depends on abstractions
    """
    
    # @abstractmethod
    # async def bulk_update_organisations(
    #     self, 
    #     request: BulkOrganisationUpdateDTO
    # ) -> BulkOrganisationUpdateResultDTO:
    #     """
    #     Perform bulk update on multiple organisations.
        
    #     Args:
    #         request: Bulk update request DTO
            
    #     Returns:
    #         Bulk update result DTO
    #     """
    #     pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        organisation_ids: List[str], 
        status: str,
        reason: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> BulkOrganisationUpdateResultDTO:
        """
        Bulk update organisation status.
        
        Args:
            organisation_ids: List of organisation IDs to update
            status: New status to set
            reason: Reason for status change
            updated_by: User performing the update
            
        Returns:
            Bulk update result DTO
        """
        pass
    
    # @abstractmethod
    # async def bulk_update_employee_strength(
    #     self, 
    #     updates: Dict[str, int],
    #     updated_by: Optional[str] = None
    # ) -> BulkOrganisationUpdateResultDTO:
    #     """
    #     Bulk update employee strength for multiple organisations.
        
    #     Args:
    #         updates: Dictionary mapping organisation ID to new employee strength
    #         updated_by: User performing the update
            
    #     Returns:
    #         Bulk update result DTO
    #     """
    #     pass
    
    # @abstractmethod
    # async def bulk_export_organisations(
    #     self, 
    #     organisation_ids: Optional[List[str]] = None,
    #     format: str = "csv",
    #     include_details: bool = True
    # ) -> bytes:
    #     """
    #     Bulk export organisation data.
        
    #     Args:
    #         organisation_ids: List of organisation IDs to export (None for all)
    #         format: Export format (csv, excel, json)
    #         include_details: Whether to include detailed information
            
    #     Returns:
    #         Exported data as bytes
    #     """
    #     pass
    
    # @abstractmethod
    # async def bulk_import_organisations(
    #     self, 
    #     data: bytes, 
    #     format: str = "csv",
    #     validate_only: bool = False,
    #     created_by: Optional[str] = None
    # ) -> Dict[str, Any]:
    #     """
    #     Bulk import organisation data.
        
    #     Args:
    #         data: Import data as bytes
    #         format: Import format (csv, excel, json)
    #         validate_only: Whether to only validate without importing
    #         created_by: User performing the import
            
    #     Returns:
    #         Dictionary with import results
    #     """
    #     pass


class OrganisationValidationService(ABC):
    """
    Service interface for organisation validation operations.
    
    Follows SOLID principles:
    - SRP: Only handles validation operations
    - OCP: Can be extended with new validation rules
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for validation operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def validate_organisation_data(self, request: CreateOrganisationRequestDTO) -> List[str]:
        """
        Validate organisation creation data.
        
        Args:
            request: Organisation creation request DTO
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_organisation_update(
        self, 
        organisation_id: str, 
        request: UpdateOrganisationRequestDTO
    ) -> List[str]:
        """
        Validate organisation update data.
        
        Args:
            organisation_id: ID of organisation being updated
            request: Organisation update request DTO
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_business_rules(self, organisation: Organisation) -> List[str]:
        """
        Validate organisation business rules.
        
        Args:
            organisation: Organisation entity to validate
            
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
            name: Organisation name to check
            hostname: Hostname to check
            pan_number: PAN number to check
            exclude_id: Organisation ID to exclude from check
            
        Returns:
            List of uniqueness violations (empty if valid)
        """
        pass


class OrganisationNotificationService(ABC):
    """
    Service interface for organisation notification operations.
    
    Follows SOLID principles:
    - SRP: Only handles notification operations
    - OCP: Can be extended with new notification types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for notification operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def send_organisation_created_notification(self, organisation: Organisation) -> bool:
        """
        Send notification when organisation is created.
        
        Args:
            organisation: Created organisation entity
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_organisation_updated_notification(
        self, 
        organisation: Organisation, 
        updated_fields: List[str]
    ) -> bool:
        """
        Send notification when organisation is updated.
        
        Args:
            organisation: Updated organisation entity
            updated_fields: List of fields that were updated
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_status_change_notification(
        self, 
        organisation: Organisation, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send notification when organisation status changes.
        
        Args:
            organisation: Organisation entity
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
        organisation: Organisation, 
        alert_type: str
    ) -> bool:
        """
        Send notification for capacity alerts.
        
        Args:
            organisation: Organisation entity
            alert_type: Type of alert (near_capacity, at_capacity, over_capacity)
            
        Returns:
            True if notification sent successfully
        """
        pass


class OrganisationServiceFactory(ABC):
    """
    Factory interface for creating organisation service implementations.
    
    Follows SOLID principles:
    - SRP: Only creates service instances
    - OCP: Can be extended with new service types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for factory operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    def create_command_service(self) -> OrganisationCommandService:
        """Create command service instance"""
        pass
    
    @abstractmethod
    def create_query_service(self) -> OrganisationQueryService:
        """Create query service instance"""
        pass
    
    @abstractmethod
    def create_analytics_service(self) -> OrganisationAnalyticsService:
        """Create analytics service instance"""
        pass
    
    @abstractmethod
    def create_health_service(self) -> OrganisationHealthService:
        """Create health service instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_service(self) -> OrganisationBulkOperationsService:
        """Create bulk operations service instance"""
        pass
    
    @abstractmethod
    def create_validation_service(self) -> OrganisationValidationService:
        """Create validation service instance"""
        pass
    
    @abstractmethod
    def create_notification_service(self) -> OrganisationNotificationService:
        """Create notification service instance"""
        pass


class OrganisationService(
    OrganisationCommandService,
    OrganisationQueryService,
    OrganisationAnalyticsService,
    OrganisationHealthService,
    OrganisationBulkOperationsService,
    OrganisationValidationService,
    OrganisationNotificationService
):
    """
    Composite service interface combining all organisation service interfaces.
    
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