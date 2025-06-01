"""
Organization Repository Interfaces
Following Interface Segregation Principle for organization data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.organization import Organization
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.organization_details import OrganizationType, OrganizationStatus
from app.application.dto.organization_dto import (
    OrganizationSearchFiltersDTO, OrganizationStatisticsDTO, 
    OrganizationAnalyticsDTO, OrganizationHealthCheckDTO
)


class OrganizationCommandRepository(ABC):
    """
    Repository interface for organization write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def save(self, organization: Organization) -> Organization:
        """
        Save an organization (create or update).
        
        Args:
            organization: Organization entity to save
            
        Returns:
            Saved organization entity
            
        Raises:
            OrganizationConflictError: If organization conflicts with existing data
            OrganizationValidationError: If organization data is invalid
        """
        pass
    
    @abstractmethod
    async def save_batch(self, organizations: List[Organization]) -> List[Organization]:
        """
        Save multiple organizations in a batch operation.
        
        Args:
            organizations: List of organization entities to save
            
        Returns:
            List of saved organization entities
            
        Raises:
            OrganizationValidationError: If any organization data is invalid
        """
        pass
    
    @abstractmethod
    async def delete(self, organization_id: OrganizationId) -> bool:
        """
        Delete an organization by ID.
        
        Args:
            organization_id: ID of organization to delete
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            OrganizationBusinessRuleError: If deletion violates business rules
        """
        pass


class OrganizationQueryRepository(ABC):
    """
    Repository interface for organization read operations.
    
    Follows SOLID principles:
    - SRP: Only handles read operations
    - OCP: Can be extended with new query methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_by_id(self, organization_id: OrganizationId) -> Optional[Organization]:
        """
        Get organization by ID.
        
        Args:
            organization_id: Organization ID to search for
            
        Returns:
            Organization entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Organization]:
        """
        Get organization by name.
        
        Args:
            name: Organization name to search for
            
        Returns:
            Organization entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_hostname(self, hostname: str) -> Optional[Organization]:
        """
        Get organization by hostname.
        
        Args:
            hostname: Hostname to search for
            
        Returns:
            Organization entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_pan_number(self, pan_number: str) -> Optional[Organization]:
        """
        Get organization by PAN number.
        
        Args:
            pan_number: PAN number to search for
            
        Returns:
            Organization entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Organization]:
        """
        Get all organizations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive organizations
            
        Returns:
            List of organization entities
        """
        pass
    
    @abstractmethod
    async def search(self, filters: OrganizationSearchFiltersDTO) -> List[Organization]:
        """
        Search organizations with filters.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            List of organization entities matching filters
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: OrganizationStatus) -> List[Organization]:
        """
        Get organizations by status.
        
        Args:
            status: Organization status to filter by
            
        Returns:
            List of organizations with specified status
        """
        pass
    
    @abstractmethod
    async def get_by_type(self, organization_type: OrganizationType) -> List[Organization]:
        """
        Get organizations by type.
        
        Args:
            organization_type: Organization type to filter by
            
        Returns:
            List of organizations with specified type
        """
        pass
    
    @abstractmethod
    async def get_by_location(self, city: str = None, state: str = None, country: str = None) -> List[Organization]:
        """
        Get organizations by location.
        
        Args:
            city: City to filter by
            state: State to filter by
            country: Country to filter by
            
        Returns:
            List of organizations in specified location
        """
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """
        Get total count of organizations.
        
        Returns:
            Total number of organizations
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, status: OrganizationStatus) -> int:
        """
        Get count of organizations by status.
        
        Args:
            status: Organization status to count
            
        Returns:
            Number of organizations with specified status
        """
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str, exclude_id: Optional[OrganizationId] = None) -> bool:
        """
        Check if organization exists by name.
        
        Args:
            name: Organization name to check
            exclude_id: Organization ID to exclude from check (for updates)
            
        Returns:
            True if organization with name exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_hostname(self, hostname: str, exclude_id: Optional[OrganizationId] = None) -> bool:
        """
        Check if organization exists by hostname.
        
        Args:
            hostname: Hostname to check
            exclude_id: Organization ID to exclude from check (for updates)
            
        Returns:
            True if organization with hostname exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[OrganizationId] = None) -> bool:
        """
        Check if organization exists by PAN number.
        
        Args:
            pan_number: PAN number to check
            exclude_id: Organization ID to exclude from check (for updates)
            
        Returns:
            True if organization with PAN number exists, False otherwise
        """
        pass


class OrganizationAnalyticsRepository(ABC):
    """
    Repository interface for organization analytics and reporting.
    
    Follows SOLID principles:
    - SRP: Only handles analytics operations
    - OCP: Can be extended with new analytics methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for analytics operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_statistics(self) -> OrganizationStatisticsDTO:
        """
        Get organization statistics.
        
        Returns:
            Organization statistics DTO
        """
        pass
    
    @abstractmethod
    async def get_analytics(self) -> OrganizationAnalyticsDTO:
        """
        Get organization analytics.
        
        Returns:
            Organization analytics DTO
        """
        pass
    
    @abstractmethod
    async def get_organizations_by_type_count(self) -> Dict[str, int]:
        """
        Get count of organizations by type.
        
        Returns:
            Dictionary mapping organization type to count
        """
        pass
    
    @abstractmethod
    async def get_organizations_by_status_count(self) -> Dict[str, int]:
        """
        Get count of organizations by status.
        
        Returns:
            Dictionary mapping organization status to count
        """
        pass
    
    @abstractmethod
    async def get_organizations_by_location_count(self) -> Dict[str, Dict[str, int]]:
        """
        Get count of organizations by location.
        
        Returns:
            Dictionary with state and city counts
        """
        pass
    
    @abstractmethod
    async def get_capacity_utilization_stats(self) -> Dict[str, Any]:
        """
        Get employee capacity utilization statistics.
        
        Returns:
            Dictionary with capacity utilization metrics
        """
        pass
    
    @abstractmethod
    async def get_growth_trends(self, months: int = 12) -> Dict[str, Any]:
        """
        Get organization growth trends.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with growth trend data
        """
        pass
    
    @abstractmethod
    async def get_top_organizations_by_capacity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top organizations by employee capacity.
        
        Args:
            limit: Number of top organizations to return
            
        Returns:
            List of organization capacity data
        """
        pass
    
    @abstractmethod
    async def get_organizations_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Organization]:
        """
        Get organizations created in a specific period.
        
        Args:
            start_date: Start date of period
            end_date: End date of period
            
        Returns:
            List of organizations created in period
        """
        pass


class OrganizationHealthRepository(ABC):
    """
    Repository interface for organization health monitoring.
    
    Follows SOLID principles:
    - SRP: Only handles health monitoring operations
    - OCP: Can be extended with new health checks
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for health operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def perform_health_check(self, organization_id: OrganizationId) -> OrganizationHealthCheckDTO:
        """
        Perform health check for an organization.
        
        Args:
            organization_id: Organization ID to check
            
        Returns:
            Organization health check DTO
        """
        pass
    
    @abstractmethod
    async def get_unhealthy_organizations(self) -> List[OrganizationHealthCheckDTO]:
        """
        Get list of unhealthy organizations.
        
        Returns:
            List of unhealthy organization health checks
        """
        pass
    
    @abstractmethod
    async def get_organizations_needing_attention(self) -> List[OrganizationHealthCheckDTO]:
        """
        Get organizations that need attention.
        
        Returns:
            List of organizations needing attention
        """
        pass


class OrganizationBulkOperationsRepository(ABC):
    """
    Repository interface for organization bulk operations.
    
    Follows SOLID principles:
    - SRP: Only handles bulk operations
    - OCP: Can be extended with new bulk operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for bulk operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        organization_ids: List[OrganizationId], 
        status: OrganizationStatus,
        updated_by: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update organization status.
        
        Args:
            organization_ids: List of organization IDs to update
            status: New status to set
            updated_by: User performing the update
            reason: Reason for status change
            
        Returns:
            Dictionary with update results
        """
        pass
    
    @abstractmethod
    async def bulk_update_employee_strength(
        self, 
        updates: Dict[OrganizationId, int],
        updated_by: str
    ) -> Dict[str, Any]:
        """
        Bulk update employee strength for multiple organizations.
        
        Args:
            updates: Dictionary mapping organization ID to new employee strength
            updated_by: User performing the update
            
        Returns:
            Dictionary with update results
        """
        pass
    
    @abstractmethod
    async def bulk_export(
        self, 
        organization_ids: Optional[List[OrganizationId]] = None,
        format: str = "csv"
    ) -> bytes:
        """
        Bulk export organization data.
        
        Args:
            organization_ids: List of organization IDs to export (None for all)
            format: Export format (csv, excel, json)
            
        Returns:
            Exported data as bytes
        """
        pass
    
    @abstractmethod
    async def bulk_import(
        self, 
        data: bytes, 
        format: str = "csv",
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Bulk import organization data.
        
        Args:
            data: Import data as bytes
            format: Import format (csv, excel, json)
            created_by: User performing the import
            
        Returns:
            Dictionary with import results
        """
        pass


class OrganizationRepositoryFactory(ABC):
    """
    Factory interface for creating organization repository implementations.
    
    Follows SOLID principles:
    - SRP: Only creates repository instances
    - OCP: Can be extended with new repository types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for factory operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    def create_command_repository(self) -> OrganizationCommandRepository:
        """Create command repository instance"""
        pass
    
    @abstractmethod
    def create_query_repository(self) -> OrganizationQueryRepository:
        """Create query repository instance"""
        pass
    
    @abstractmethod
    def create_analytics_repository(self) -> OrganizationAnalyticsRepository:
        """Create analytics repository instance"""
        pass
    
    @abstractmethod
    def create_health_repository(self) -> OrganizationHealthRepository:
        """Create health repository instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_repository(self) -> OrganizationBulkOperationsRepository:
        """Create bulk operations repository instance"""
        pass


class OrganizationRepository(
    OrganizationCommandRepository,
    OrganizationQueryRepository,
    OrganizationAnalyticsRepository,
    OrganizationHealthRepository,
    OrganizationBulkOperationsRepository
):
    """
    Composite repository interface combining all organization repository interfaces.
    
    This interface can be used when you need access to all repository operations
    in a single interface. Individual interfaces should be preferred when possible
    to follow the Interface Segregation Principle.
    
    Follows SOLID principles:
    - SRP: Combines related repository operations
    - OCP: Can be extended through composition
    - LSP: All implementations must be substitutable
    - ISP: Composed of focused interfaces
    - DIP: Depends on abstractions
    """
    pass 