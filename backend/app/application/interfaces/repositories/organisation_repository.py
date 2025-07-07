"""
Organisation Repository Interfaces
Following Interface Segregation Principle for organisation data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import OrganisationType
from app.application.dto.organisation_dto import (
    OrganisationSearchFiltersDTO, OrganisationStatisticsDTO, 
    OrganisationAnalyticsDTO, OrganisationHealthCheckDTO
)


class OrganisationCommandRepository(ABC):
    """
    Repository interface for organisation write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def save(self, organisation: Organisation) -> Organisation:
        """
        Save an organisation (create or update).
        
        Args:
            organisation: Organisation entity to save
            
        Returns:
            Saved organisation entity
            
        Raises:
            OrganisationConflictError: If organisation conflicts with existing data
            OrganisationValidationError: If organisation data is invalid
        """
        pass
    
    @abstractmethod
    async def save_batch(self, organisations: List[Organisation]) -> List[Organisation]:
        """
        Save multiple organisations in a batch operation.
        
        Args:
            organisations: List of organisation entities to save
            
        Returns:
            List of saved organisation entities
            
        Raises:
            OrganisationValidationError: If any organisation data is invalid
        """
        pass
    
    @abstractmethod
    async def increment_used_employee_strength(self, organisation_id: OrganisationId) -> bool:
        """
        Increment the used employee strength for an organisation.
        
        Args:
            organisation_id: Organisation ID to update
            
        Returns:
            True if incremented successfully, False if organisation not found or at capacity
            
        Raises:
            OrganisationBusinessRuleError: If increment would exceed employee strength limit
        """
        pass
    
    @abstractmethod
    async def decrement_used_employee_strength(self, organisation_id: OrganisationId) -> bool:
        """
        Decrement the used employee strength for an organisation.
        
        Args:
            organisation_id: Organisation ID to update
            
        Returns:
            True if decremented successfully, False if organisation not found or already at zero
            
        Raises:
            OrganisationBusinessRuleError: If decrement would go below zero
        """
        pass
    
    # @abstractmethod
    # async def delete(self, organisation_id: OrganisationId) -> bool:
    #     """
    #     Delete an organisation by ID.
        
    #     Args:
    #         organisation_id: ID of organisation to delete
            
    #     Returns:
    #         True if deleted successfully, False if not found
            
    #     Raises:
    #         OrganisationBusinessRuleError: If deletion violates business rules
    #     """
    #     pass


class OrganisationQueryRepository(ABC):
    """
    Repository interface for organisation read operations.
    
    Follows SOLID principles:
    - SRP: Only handles read operations
    - OCP: Can be extended with new query methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_by_id(self, organisation_id: OrganisationId) -> Optional[Organisation]:
        """
        Get organisation by ID.
        
        Args:
            organisation_id: Organisation ID to search for
            
        Returns:
            Organisation entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_hostname(self, hostname: str) -> Optional[Organisation]:
        """
        Get organisation by hostname.
        
        Args:
            hostname: Organisation hostname to search for
            
        Returns:
            Organisation entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Organisation]:
        """
        Get all organisations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive organisations
            
        Returns:
            List of organisation entities
        """
        pass
    
    @abstractmethod
    async def search(self, filters: OrganisationSearchFiltersDTO) -> List[Organisation]:
        """
        Search organisations with filters.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            List of organisation entities matching filters
        """
        pass
    
    @abstractmethod
    async def get_by_type(self, organisation_type: OrganisationType) -> List[Organisation]:
        """
        Get organisations by type.
        
        Args:
            organisation_type: Organisation type to filter by
            
        Returns:
            List of organisations with specified type
        """
        pass
    
    @abstractmethod
    async def get_by_location(self, city: str = None, state: str = None, country: str = None) -> List[Organisation]:
        """
        Get organisations by location.
        
        Args:
            city: City to filter by
            state: State to filter by
            country: Country to filter by
            
        Returns:
            List of organisations in specified location
        """
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """
        Get total count of organisations.
        
        Returns:
            Total number of organisations
        """
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str, exclude_id: Optional[OrganisationId] = None) -> bool:
        """
        Check if organisation exists by name.
        
        Args:
            name: Organisation name to check
            exclude_id: Organisation ID to exclude from check (for updates)
            
        Returns:
            True if organisation with name exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_hostname(self, hostname: str, exclude_id: Optional[OrganisationId] = None) -> bool:
        """
        Check if organisation exists by hostname.
        
        Args:
            hostname: Hostname to check
            exclude_id: Organisation ID to exclude from check (for updates)
            
        Returns:
            True if organisation with hostname exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[OrganisationId] = None) -> bool:
        """
        Check if organisation exists by PAN number.
        
        Args:
            pan_number: PAN number to check
            exclude_id: Organisation ID to exclude from check (for updates)
            
        Returns:
            True if organisation with PAN number exists, False otherwise
        """
        pass


class OrganisationAnalyticsRepository(ABC):
    """
    Repository interface for organisation analytics and reporting.
    
    Follows SOLID principles:
    - SRP: Only handles analytics operations
    - OCP: Can be extended with new analytics methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for analytics operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_statistics(self) -> OrganisationStatisticsDTO:
        """
        Get organisation statistics.
        
        Returns:
            Organisation statistics DTO
        """
        pass
    
    @abstractmethod
    async def get_analytics(self) -> OrganisationAnalyticsDTO:
        """
        Get organisation analytics.
        
        Returns:
            Organisation analytics DTO
        """
        pass
    
    @abstractmethod
    async def get_organisations_by_type_count(self) -> Dict[str, int]:
        """
        Get count of organisations by type.
        
        Returns:
            Dictionary mapping organisation type to count
        """
        pass
    
    @abstractmethod
    async def get_organisations_by_status_count(self) -> Dict[str, int]:
        """
        Get count of organisations by status.
        
        Returns:
            Dictionary mapping organisation status to count
        """
        pass
    
    @abstractmethod
    async def get_organisations_by_location_count(self) -> Dict[str, Dict[str, int]]:
        """
        Get count of organisations by location.
        
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
        Get organisation growth trends.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with growth trend data
        """
        pass
    
    @abstractmethod
    async def get_top_organisations_by_capacity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top organisations by employee capacity.
        
        Args:
            limit: Number of top organisations to return
            
        Returns:
            List of organisation capacity data
        """
        pass
    
    @abstractmethod
    async def get_organisations_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Organisation]:
        """
        Get organisations created in a specific period.
        
        Args:
            start_date: Start date of period
            end_date: End date of period
            
        Returns:
            List of organisations created in period
        """
        pass


class OrganisationHealthRepository(ABC):
    """
    Repository interface for organisation health monitoring.
    
    Follows SOLID principles:
    - SRP: Only handles health monitoring operations
    - OCP: Can be extended with new health checks
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for health operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def perform_health_check(self, organisation_id: OrganisationId) -> OrganisationHealthCheckDTO:
        """
        Perform health check for an organisation.
        
        Args:
            organisation_id: Organisation ID to check
            
        Returns:
            Organisation health check DTO
        """
        pass
    
    @abstractmethod
    async def get_unhealthy_organisations(self) -> List[OrganisationHealthCheckDTO]:
        """
        Get list of unhealthy organisations.
        
        Returns:
            List of unhealthy organisation health checks
        """
        pass
    
    @abstractmethod
    async def get_organisations_needing_attention(self) -> List[OrganisationHealthCheckDTO]:
        """
        Get organisations that need attention.
        
        Returns:
            List of organisations needing attention
        """
        pass


class OrganisationBulkOperationsRepository(ABC):
    """
    Repository interface for organisation bulk operations.
    
    Follows SOLID principles:
    - SRP: Only handles bulk operations
    - OCP: Can be extended with new bulk operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for bulk operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def bulk_update_employee_strength(
        self, 
        updates: Dict[OrganisationId, int],
        updated_by: str
    ) -> Dict[str, Any]:
        """
        Bulk update employee strength for multiple organisations.
        
        Args:
            updates: Dictionary mapping organisation ID to new employee strength
            updated_by: User performing the update
            
        Returns:
            Dictionary with update results
        """
        pass
    
    @abstractmethod
    async def bulk_export(
        self, 
        organisation_ids: Optional[List[OrganisationId]] = None,
        format: str = "csv"
    ) -> bytes:
        """
        Bulk export organisation data.
        
        Args:
            organisation_ids: List of organisation IDs to export (None for all)
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
        Bulk import organisation data.
        
        Args:
            data: Import data as bytes
            format: Import format (csv, excel, json)
            created_by: User performing the import
            
        Returns:
            Dictionary with import results
        """
        pass


class OrganisationRepositoryFactory(ABC):
    """
    Factory interface for creating organisation repository implementations.
    
    Follows SOLID principles:
    - SRP: Only creates repository instances
    - OCP: Can be extended with new repository types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for factory operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    def create_command_repository(self) -> OrganisationCommandRepository:
        """Create command repository instance"""
        pass
    
    @abstractmethod
    def create_query_repository(self) -> OrganisationQueryRepository:
        """Create query repository instance"""
        pass
    
    @abstractmethod
    def create_analytics_repository(self) -> OrganisationAnalyticsRepository:
        """Create analytics repository instance"""
        pass
    
    @abstractmethod
    def create_health_repository(self) -> OrganisationHealthRepository:
        """Create health repository instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_repository(self) -> OrganisationBulkOperationsRepository:
        """Create bulk operations repository instance"""
        pass


class OrganisationRepository(
    OrganisationCommandRepository,
    OrganisationQueryRepository,
    OrganisationAnalyticsRepository,
    OrganisationHealthRepository,
    OrganisationBulkOperationsRepository
):
    """
    Composite repository interface combining all organisation repository interfaces.
    
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