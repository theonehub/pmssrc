"""
Employee Leave Repository Interfaces
Repository abstractions for employee leave data access following SOLID principles
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date

from app.domain.entities.employee_leave import EmployeeLeave
from app.domain.value_objects.employee_id import EmployeeId
from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO


class EmployeeLeaveCommandRepository(ABC):
    """
    Command repository interface for employee leave write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new write operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    async def save(self, employee_leave: EmployeeLeave, organisation_id: Optional[str] = None) -> EmployeeLeave:
        """
        Save employee leave application.
        
        Args:
            employee_leave: Employee leave entity to save
            organisation_id: Organisation identifier
            
        Returns:
            Saved EmployeeLeave entity
        """
        pass
    
    @abstractmethod
    async def save_batch(self, employee_leaves: List[EmployeeLeave], organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """
        Save multiple employee leave applications in batch.
        
        Args:
            employee_leaves: List of employee leave entities to save
            organisation_id: Organisation identifier
            
        Returns:
            List of saved EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    async def delete(self, leave_id: str, soft_delete: bool = True, organisation_id: Optional[str] = None) -> bool:
        """
        Delete employee leave application.
        
        Args:
            leave_id: Leave application identifier
            soft_delete: Whether to soft delete (mark as deleted) or hard delete
            organisation_id: Organisation identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass


class EmployeeLeaveQueryRepository(ABC):
    """
    Query repository interface for employee leave read operations.
    """
    
    @abstractmethod
    async def get_by_id(self, leave_id: str, organisation_id: Optional[str] = None) -> Optional[EmployeeLeave]:
        """
        Get employee leave by ID.
        
        Args:
            leave_id: Leave application identifier
            organisation_id: Organisation identifier
            
        Returns:
            EmployeeLeave entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_employee_id(self, employee_id: Union[str, EmployeeId], organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """
        Get employee leaves by employee ID.
        
        Args:
            employee_id: Employee identifier (string or EmployeeId)
            organisation_id: Organisation identifier
            
        Returns:
            List of EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str, organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """
        Get employee leaves by status.
        
        Args:
            status: Leave status (pending, approved, rejected, cancelled)
            organisation_id: Organisation identifier
            
        Returns:
            List of EmployeeLeave entities with the specified status
        """
        pass
    
    @abstractmethod
    async def get_by_leave_name(self, leave_name: str, organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """
        Get employee leaves by leave name.
        
        Args:
            leave_name: Leave name/type
            organisation_id: Organisation identifier
            
        Returns:
            List of EmployeeLeave entities with the specified leave name
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        organisation_id: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """
        Get employee leaves by date range.
        
        Args:
            start_date: Start date of range
            end_date: End date of range
            organisation_id: Organisation identifier
            employee_id: Optional employee ID to filter by
            
        Returns:
            List of EmployeeLeave entities within the date range
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False,
        organisation_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """
        Get all employee leaves with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records
            organisation_id: Organisation identifier
            
        Returns:
            List of EmployeeLeave entities
        """
        pass
    
    @abstractmethod
    async def search(self, filters: EmployeeLeaveSearchFiltersDTO, organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """
        Search employee leaves with filters.
        
        Args:
            filters: Search filters
            organisation_id: Organisation identifier
            
        Returns:
            List of EmployeeLeave entities matching the filters
        """
        pass
    
    @abstractmethod
    async def count_total(self, include_deleted: bool = False, organisation_id: Optional[str] = None) -> int:
        """
        Count total employee leaves.
        
        Args:
            include_deleted: Whether to include soft-deleted records
            organisation_id: Organisation identifier
            
        Returns:
            Total count of employee leaves
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, status: str, organisation_id: Optional[str] = None) -> int:
        """
        Count employee leaves by status.
        
        Args:
            status: Leave status
            organisation_id: Organisation identifier
            
        Returns:
            Count of employee leaves with the specified status
        """
        pass


class EmployeeLeaveAnalyticsRepository(ABC):
    """
    Analytics repository interface for employee leave analytics and reporting.
    """
    
    @abstractmethod
    async def get_leave_statistics(
        self,
        employee_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get leave statistics.
        
        Args:
            employee_id: Optional employee filter
            organisation_id: Organisation identifier
            year: Optional year filter
            
        Returns:
            Dictionary containing leave statistics
        """
        pass
    
    @abstractmethod
    async def get_leave_name_breakdown(
        self,
        employee_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get leave breakdown by leave name.
        
        Args:
            employee_id: Optional employee filter
            organisation_id: Organisation identifier
            year: Optional year filter
            
        Returns:
            Dictionary mapping leave names to counts
        """
        pass
    
    @abstractmethod
    async def get_monthly_leave_trends(
        self,
        employee_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get monthly leave trends.
        
        Args:
            employee_id: Optional employee filter
            organisation_id: Organisation identifier
            year: Optional year filter
            
        Returns:
            Dictionary mapping months to leave counts
        """
        pass


class EmployeeLeaveRepository(ABC):
    """
    Main repository interface that combines all employee leave repository interfaces.
    
    This interface provides factory methods to create specific repository instances
    while maintaining separation of concerns through interface segregation.
    """
    
    @abstractmethod
    def create_command_repository(self) -> EmployeeLeaveCommandRepository:
        """Create command repository instance."""
        pass
    
    @abstractmethod
    def create_query_repository(self) -> EmployeeLeaveQueryRepository:
        """Create query repository instance."""
        pass
    
    @abstractmethod
    def create_analytics_repository(self) -> EmployeeLeaveAnalyticsRepository:
        """Create analytics repository instance."""
        pass 