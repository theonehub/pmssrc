"""
Project Attributes API Controller
FastAPI controller for project attributes management endpoints with enhanced type support
"""

import logging
from typing import List, Optional, Dict, Any

from app.application.dto.project_attributes_dto import (
    ProjectAttributeCreateRequestDTO,
    ProjectAttributeUpdateRequestDTO,
    ProjectAttributeSearchFiltersDTO,
    ProjectAttributeResponseDTO,
    ProjectAttributeSummaryDTO,
    ProjectAttributeAnalyticsDTO,
    ProjectAttributeValidationError,
    ProjectAttributeBusinessRuleError,
    ProjectAttributeNotFoundError,
    ValueType
)
from app.application.use_cases.project_attributes.create_project_attributes_use_case import CreateProjectAttributesUseCase
from app.application.use_cases.project_attributes.get_project_attributes_use_case import GetProjectAttributesUseCase


class ProjectAttributesController:
    """
    Project Attributes controller following SOLID principles.
    
    Handles HTTP requests for organization-specific configuration attributes.
    """
    
    def __init__(
        self, 
        create_use_case: CreateProjectAttributesUseCase = None, 
        query_use_case: GetProjectAttributesUseCase = None
    ):
        self._create_use_case = create_use_case
        self._query_use_case = query_use_case
        self._logger = logging.getLogger(__name__)
    
    async def health_check(self) -> Dict[str, str]:
        """
        Health check for project attributes service.
        
        Returns:
            Dict with service status
        """
        
        self._logger.info("Project attributes health check")
        
        return {
            "status": "healthy",
            "service": "project-attributes-v2",
            "version": "2.0.0",
            "implementation": "enhanced",
            "features": [
                "multiple_value_types",
                "organization_specific",
                "validation_rules",
                "categories",
                "system_attributes"
            ]
        }
    
    async def create_project_attribute(
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
        
        try:
            self._logger.info(f"Creating project attribute: {request.key}")
            
            if self._create_use_case:
                return await self._create_use_case.execute(request, hostname)
            
            raise ProjectAttributeBusinessRuleError(
                "Project attributes create use case not initialized"
            )
            
        except Exception as e:
            self._logger.error(f"Error creating project attribute: {e}")
            raise
    
    async def get_project_attributes(
        self, 
        filters: ProjectAttributeSearchFiltersDTO,
        hostname: str
    ) -> List[ProjectAttributeResponseDTO]:
        """
        Get project attributes with filters.
        
        Args:
            filters: Search filters
            hostname: Organisation hostname
            
        Returns:
            List of ProjectAttributeResponseDTO
        """
        
        try:
            self._logger.info(f"Getting project attributes")
            
            if self._query_use_case:
                return await self._query_use_case.get_project_attributes(filters, hostname)
            
            raise ProjectAttributeBusinessRuleError(
                "Project attributes query use case not initialized"
            )
            
        except Exception as e:
            self._logger.error(f"Error getting project attributes: {e}")
            raise
    
    async def get_project_attribute(
        self, 
        key: str,
        hostname: str
    ) -> Optional[ProjectAttributeResponseDTO]:
        """
        Get a specific project attribute by key.
        
        Args:
            key: Project attribute key
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeResponseDTO if found, None otherwise
        """
        
        try:
            self._logger.info(f"Getting project attribute: {key}")
            
            if self._query_use_case:
                return await self._query_use_case.get_project_attribute(key, hostname)
            
            raise ProjectAttributeBusinessRuleError(
                "Project attributes query use case not initialized"
            )
            
        except Exception as e:
            self._logger.error(f"Error getting project attribute: {e}")
            raise
    
    async def update_project_attribute(
        self, 
        key: str,
        request: ProjectAttributeUpdateRequestDTO,
        hostname: str
    ) -> ProjectAttributeResponseDTO:
        """
        Update an existing project attribute.
        
        Args:
            key: Project attribute key
            request: Update request
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeResponseDTO with updated details
        """
        
        try:
            self._logger.info(f"Updating project attribute: {key}")
            
            # For now, this is a stub implementation
            # In a full implementation, you would have an update use case
            raise ProjectAttributeNotFoundError(key)
            
        except Exception as e:
            self._logger.error(f"Error updating project attribute: {e}")
            raise
    
    async def delete_project_attribute(
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
        
        try:
            self._logger.info(f"Deleting project attribute: {key}")
            
            # For now, this is a stub implementation
            # In a full implementation, you would have a delete use case
            return False
            
        except Exception as e:
            self._logger.error(f"Error deleting project attribute: {e}")
            raise
    
    async def get_attributes_by_category(
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
        
        try:
            self._logger.info(f"Getting attributes by category: {category}")
            
            if self._query_use_case:
                return await self._query_use_case.get_attributes_by_category(category, hostname)
            
            raise ProjectAttributeBusinessRuleError(
                "Project attributes query use case not initialized"
            )
            
        except Exception as e:
            self._logger.error(f"Error getting attributes by category: {e}")
            raise
    
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
        
        try:
            self._logger.info(f"Getting boolean attribute: {key}")
            
            if self._query_use_case:
                return await self._query_use_case.get_boolean_attribute(key, hostname, default)
            
            return default
            
        except Exception as e:
            self._logger.error(f"Error getting boolean attribute: {e}")
            return default
    
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
        
        try:
            self._logger.info(f"Getting numeric attribute: {key}")
            
            if self._query_use_case:
                return await self._query_use_case.get_numeric_attribute(key, hostname, default)
            
            return default
            
        except Exception as e:
            self._logger.error(f"Error getting numeric attribute: {e}")
            return default
    
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
        
        try:
            self._logger.info(f"Getting string attribute: {key}")
            
            if self._query_use_case:
                return await self._query_use_case.get_string_attribute(key, hostname, default)
            
            return default
            
        except Exception as e:
            self._logger.error(f"Error getting string attribute: {e}")
            return default
    
    async def get_attributes_summary(
        self,
        hostname: str
    ) -> ProjectAttributeSummaryDTO:
        """
        Get summary statistics for project attributes.
        
        Args:
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeSummaryDTO with summary data
        """
        
        try:
            self._logger.info("Getting project attributes summary")
            
            if self._query_use_case:
                return await self._query_use_case.get_attributes_summary(hostname)
            
            # Return empty summary if use case not available
            return ProjectAttributeSummaryDTO()
            
        except Exception as e:
            self._logger.error(f"Error getting attributes summary: {e}")
            raise
    
    async def get_supported_value_types(self) -> List[Dict[str, Any]]:
        """
        Get list of supported value types.
        
        Returns:
            List of value type definitions
        """
        
        return [
            {
                "type": ValueType.BOOLEAN.value,
                "name": "Boolean",
                "description": "True/false values",
                "examples": ["true", "false"],
                "validation_rules": []
            },
            {
                "type": ValueType.STRING.value,
                "name": "String",
                "description": "Short text values",
                "examples": ["hello", "config_value"],
                "validation_rules": ["max_length"]
            },
            {
                "type": ValueType.NUMBER.value,
                "name": "Number",
                "description": "Numeric values",
                "examples": [42, 3.14, 100],
                "validation_rules": ["min", "max"]
            },
            {
                "type": ValueType.TEXT.value,
                "name": "Text",
                "description": "Longer text values",
                "examples": ["Description text"],
                "validation_rules": ["max_length"]
            },
            {
                "type": ValueType.MULTILINE_TEXT.value,
                "name": "Multiline Text",
                "description": "Multi-line text values",
                "examples": ["Address\nCity\nCountry"],
                "validation_rules": ["max_length"]
            },
            {
                "type": ValueType.DROPDOWN.value,
                "name": "Dropdown",
                "description": "Selection from predefined options",
                "examples": ["option1", "option2"],
                "validation_rules": ["options"]
            },
            {
                "type": ValueType.EMAIL.value,
                "name": "Email",
                "description": "Email addresses",
                "examples": ["user@example.com"],
                "validation_rules": []
            },
            {
                "type": ValueType.PHONE.value,
                "name": "Phone",
                "description": "Phone numbers",
                "examples": ["+1234567890"],
                "validation_rules": ["format"]
            },
            {
                "type": ValueType.URL.value,
                "name": "URL",
                "description": "Web URLs",
                "examples": ["https://example.com"],
                "validation_rules": []
            },
            {
                "type": ValueType.DATE.value,
                "name": "Date",
                "description": "Date values",
                "examples": ["2024-01-15"],
                "validation_rules": []
            },
            {
                "type": ValueType.JSON.value,
                "name": "JSON",
                "description": "JSON data structures",
                "examples": ['{"key": "value"}'],
                "validation_rules": []
            }
        ] 