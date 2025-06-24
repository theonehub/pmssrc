"""
Salary Component Repository Interface
Abstract repository interface following SOLID principles
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.domain.entities.salary_component import SalaryComponent
from app.domain.value_objects.component_id import ComponentId
from app.application.dto.salary_component_dto import SalaryComponentSearchFiltersDTO


class SalaryComponentRepository(ABC):
    """
    Abstract repository interface for salary components.
    
    Follows SOLID principles:
    - Interface Segregation: Focused only on salary component operations
    - Dependency Inversion: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    async def save(self, component: SalaryComponent, hostname: str) -> SalaryComponent:
        """
        Save a salary component to the repository.
        
        Args:
            component: The salary component entity to save
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            The saved salary component with updated metadata
            
        Raises:
            SalaryComponentConflictError: If component code already exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, component_id: ComponentId, hostname: str) -> Optional[SalaryComponent]:
        """
        Get a salary component by its ID.
        
        Args:
            component_id: The component ID to search for
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            The salary component if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_code(self, code: str, hostname: str) -> Optional[SalaryComponent]:
        """
        Get a salary component by its code.
        
        Args:
            code: The component code to search for
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            The salary component if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_with_filters(
        self, 
        filters: SalaryComponentSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[SalaryComponent], int]:
        """
        Find salary components with filters and pagination.
        
        Args:
            filters: Search filters and pagination parameters
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Tuple of (components list, total count)
        """
        pass
    
    @abstractmethod
    async def get_all_active(self, hostname: str) -> List[SalaryComponent]:
        """
        Get all active salary components for an organization.
        
        Args:
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            List of all active salary components
        """
        pass
    
    @abstractmethod
    async def delete(self, component_id: ComponentId, hostname: str) -> bool:
        """
        Delete a salary component.
        
        Args:
            component_id: The component ID to delete
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            True if deleted successfully, False if not found
        """
        pass
    
    @abstractmethod
    async def check_code_exists(self, code: str, hostname: str, exclude_id: Optional[ComponentId] = None) -> bool:
        """
        Check if a component code already exists.
        
        Args:
            code: The component code to check
            hostname: Organization hostname for multi-tenancy
            exclude_id: Exclude this ID from the check (for updates)
            
        Returns:
            True if code exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_usage_count(self, component_id: ComponentId, hostname: str) -> int:
        """
        Get the number of employees using this component.
        
        Args:
            component_id: The component ID to check
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Number of active assignments using this component
        """
        pass
    
    @abstractmethod
    async def get_components_by_type(self, component_type: str, hostname: str) -> List[SalaryComponent]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The component type (EARNING, DEDUCTION, REIMBURSEMENT)
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            List of components of the specified type
        """
        pass 