"""
Project Attributes Repository Interface
Abstract interface for project attributes data access following Dependency Inversion Principle
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.application.dto.project_attributes_dto import (
    ProjectAttributeCreateRequestDTO,
    ProjectAttributeUpdateRequestDTO,
    ProjectAttributeSearchFiltersDTO,
    ProjectAttributeResponseDTO
)


class ProjectAttributesRepository(ABC):
    """Abstract interface for project attributes repository."""
    
    @abstractmethod
    async def create(
        self, 
        request: ProjectAttributeCreateRequestDTO,
        hostname: str
    ) -> ProjectAttributeResponseDTO:
        """
        Create a new project attribute.
        
        Args:
            request: Project attribute creation request
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeResponseDTO with created attribute details
        """
        pass
    
    @abstractmethod
    async def get_by_key(
        self, 
        key: str,
        hostname: str
    ) -> Optional[ProjectAttributeResponseDTO]:
        """
        Get a project attribute by key.
        
        Args:
            key: Project attribute key
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeResponseDTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        filters: ProjectAttributeSearchFiltersDTO,
        hostname: str
    ) -> List[ProjectAttributeResponseDTO]:
        """
        Get all project attributes with filters.
        
        Args:
            filters: Search filters
            hostname: Organisation hostname
            
        Returns:
            List of ProjectAttributeResponseDTO
        """
        pass
    
    @abstractmethod
    async def update(
        self, 
        key: str,
        request: ProjectAttributeUpdateRequestDTO,
        hostname: str
    ) -> Optional[ProjectAttributeResponseDTO]:
        """
        Update a project attribute.
        
        Args:
            key: Project attribute key
            request: Update request
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeResponseDTO if updated, None if not found
        """
        pass
    
    @abstractmethod
    async def delete(
        self, 
        key: str,
        hostname: str
    ) -> bool:
        """
        Delete a project attribute.
        
        Args:
            key: Project attribute key
            hostname: Organisation hostname
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def get_by_category(
        self,
        category: str,
        hostname: str
    ) -> List[ProjectAttributeResponseDTO]:
        """
        Get all attributes in a category.
        
        Args:
            category: Category name
            hostname: Organisation hostname
            
        Returns:
            List of ProjectAttributeResponseDTO
        """
        pass
    
    @abstractmethod
    async def get_boolean_attribute(
        self,
        key: str,
        hostname: str,
        default: bool = False
    ) -> bool:
        """
        Get a boolean attribute value.
        
        Args:
            key: Attribute key
            hostname: Organisation hostname
            default: Default value if not found
            
        Returns:
            Boolean value
        """
        pass
    
    @abstractmethod
    async def get_numeric_attribute(
        self,
        key: str,
        hostname: str,
        default: float = 0.0
    ) -> float:
        """
        Get a numeric attribute value.
        
        Args:
            key: Attribute key
            hostname: Organisation hostname
            default: Default value if not found
            
        Returns:
            Numeric value
        """
        pass
    
    @abstractmethod
    async def get_string_attribute(
        self,
        key: str,
        hostname: str,
        default: str = ""
    ) -> str:
        """
        Get a string attribute value.
        
        Args:
            key: Attribute key
            hostname: Organisation hostname
            default: Default value if not found
            
        Returns:
            String value
        """
        pass 