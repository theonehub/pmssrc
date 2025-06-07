"""
Company Leave Repository Interfaces
Defines contracts for company leave data persistence operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.company_leave import CompanyLeave
from app.application.dto.company_leave_dto import CompanyLeaveSearchFiltersDTO


class CompanyLeaveCommandRepository(ABC):
    """
    Command repository interface for company leave write operations.
    
    Follows SOLID principles:
    - SRP: Only handles company leave write operations
    - OCP: Can be implemented by different storage systems
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    async def save(self, company_leave: CompanyLeave, hostname: str) -> bool:
        """
        Save company leave record.
        
        Args:
            company_leave: CompanyLeave entity to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, company_leave: CompanyLeave, hostname: str) -> bool:
        """
        Update existing company leave record.
        
        Args:
            company_leave: CompanyLeave entity to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, company_leave_id: str, hostname: str) -> bool:
        """
        Delete company leave record.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class CompanyLeaveQueryRepository(ABC):
    """
    Query repository interface for company leave read operations.
    """
    
    @abstractmethod
    async def get_by_id(self, company_leave_id: str, hostname: str) -> Optional[CompanyLeave]:
        """
        Get company leave by ID.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            CompanyLeave entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all_active(self, hostname: str) -> List[CompanyLeave]:
        """
        Get all active company leaves.
        
        Returns:
            List of active CompanyLeave entities
        """
        pass
    
    @abstractmethod
    async def get_all(self, hostname: str, include_inactive: bool = False) -> List[CompanyLeave]:
        """
        Get all company leaves.
        
        Args:
            include_inactive: Whether to include inactive leaves
            
        Returns:
            List of CompanyLeave entities
        """
        pass
    
    @abstractmethod
    async def list_with_filters(self, filters: CompanyLeaveSearchFiltersDTO, hostname: str) -> List[CompanyLeave]:
        """
        Get company leaves with filters and pagination.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            List of CompanyLeave entities matching filters
        """
        pass
    
    @abstractmethod
    async def count_with_filters(self, filters: CompanyLeaveSearchFiltersDTO, hostname: str) -> int:
        """
        Count company leaves matching filters.
        
        Args:
            filters: Search filters
            
        Returns:
            Number of company leaves matching filters
        """
        pass
    
    @abstractmethod
    async def exists_by_id(self, company_leave_id: str, hostname: str) -> bool:
        """
        Check if company leave exists by ID.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def count_active(self, hostname: str) -> int:
        """
        Count active company leaves.
        
        Returns:
            Number of active company leaves
        """
        pass


class CompanyLeaveRepository(CompanyLeaveCommandRepository, CompanyLeaveQueryRepository):
    """
    Unified repository interface that combines both command and query operations.
    This is what some implementations prefer to use instead of separate interfaces.
    """
    pass
