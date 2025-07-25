"""
Get Project Attributes Use Case
Business workflow for retrieving project attributes with enhanced filtering and type support
"""

import logging
from typing import List, Optional

from app.application.dto.project_attributes_dto import (
    ProjectAttributeSearchFiltersDTO,
    ProjectAttributeResponseDTO,
    ProjectAttributeSummaryDTO,
    ProjectAttributeAnalyticsDTO,
    ValueType
)
from app.application.interfaces.repositories.project_attributes_repository import ProjectAttributesRepository


class GetProjectAttributesUseCase:
    """
    Use case for retrieving project attributes.
    
    Handles the business logic for querying organization-specific configuration attributes.
    """
    
    def __init__(self, repository: ProjectAttributesRepository):
        self._repository = repository
        self._logger = logging.getLogger(__name__)
    
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
            self._logger.info(f"Getting project attributes with filters")
            
            # Apply business logic filters
            enhanced_filters = await self._apply_business_filters(filters, hostname)
            
            # Get attributes from repository
            attributes = await self._repository.get_all(enhanced_filters, hostname)
            
            # Apply any additional business logic
            attributes = await self._apply_business_logic(attributes, hostname)
            
            self._logger.info(f"Retrieved {len(attributes)} project attributes")
            return attributes
            
        except Exception as e:
            self._logger.error(f"Failed to get project attributes: {str(e)}")
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
            
            # Get attribute from repository
            attribute = await self._repository.get_by_key(key, hostname)
            
            if not attribute:
                self._logger.warning(f"Project attribute not found: {key}")
                return None
            
            # Apply business logic
            attribute = await self._apply_attribute_business_logic(attribute, hostname)
            
            self._logger.info(f"Retrieved project attribute: {key}")
            return attribute
            
        except Exception as e:
            self._logger.error(f"Failed to get project attribute: {str(e)}")
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
            self._logger.info(f"Getting project attributes by category: {category}")
            
            attributes = await self._repository.get_by_category(category, hostname)
            
            # Apply business logic
            attributes = await self._apply_business_logic(attributes, hostname)
            
            self._logger.info(f"Retrieved {len(attributes)} attributes in category: {category}")
            return attributes
            
        except Exception as e:
            self._logger.error(f"Failed to get attributes by category: {str(e)}")
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
            
            value = await self._repository.get_boolean_attribute(key, hostname, default)
            
            self._logger.info(f"Boolean attribute {key} = {value}")
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get boolean attribute: {str(e)}")
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
            
            value = await self._repository.get_numeric_attribute(key, hostname, default)
            
            self._logger.info(f"Numeric attribute {key} = {value}")
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get numeric attribute: {str(e)}")
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
            
            value = await self._repository.get_string_attribute(key, hostname, default)
            
            self._logger.info(f"String attribute {key} = {value}")
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get string attribute: {str(e)}")
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
            
            # Get all attributes
            all_filters = ProjectAttributeSearchFiltersDTO(limit=1000)
            all_attributes = await self._repository.get_all(all_filters, hostname)
            
            # Calculate summary
            summary = ProjectAttributeSummaryDTO(
                total_attributes=len(all_attributes),
                active_attributes=len([a for a in all_attributes if a.is_active]),
                inactive_attributes=len([a for a in all_attributes if not a.is_active]),
                system_attributes=len([a for a in all_attributes if a.is_system]),
                custom_attributes=len([a for a in all_attributes if not a.is_system])
            )
            
            # Calculate type distribution
            type_distribution = {}
            for attribute in all_attributes:
                type_name = attribute.value_type.value
                type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
            
            summary.type_distribution = type_distribution
            
            # Calculate category distribution
            category_distribution = {}
            for attribute in all_attributes:
                if attribute.category:
                    category_distribution[attribute.category] = category_distribution.get(attribute.category, 0) + 1
            
            summary.category_distribution = category_distribution
            
            self._logger.info(f"Generated summary: {summary.total_attributes} total attributes")
            return summary
            
        except Exception as e:
            self._logger.error(f"Failed to get attributes summary: {str(e)}")
            raise
    
    async def _apply_business_filters(
        self, 
        filters: ProjectAttributeSearchFiltersDTO, 
        hostname: str
    ) -> ProjectAttributeSearchFiltersDTO:
        """
        Apply business logic to filters.
        
        Args:
            filters: Original filters
            hostname: Organisation hostname
            
        Returns:
            Enhanced filters
        """
        
        # For now, just return the original filters
        # In the future, this could include:
        # - Permission-based filtering
        # - Organization-specific defaults
        # - System attribute visibility rules
        return filters
    
    async def _apply_business_logic(
        self, 
        attributes: List[ProjectAttributeResponseDTO], 
        hostname: str
    ) -> List[ProjectAttributeResponseDTO]:
        """
        Apply business logic to attributes.
        
        Args:
            attributes: List of attributes
            hostname: Organisation hostname
            
        Returns:
            Processed attributes
        """
        
        # For now, just return the original attributes
        # In the future, this could include:
        # - Permission-based filtering
        # - Value transformation
        # - Audit logging
        return attributes
    
    async def _apply_attribute_business_logic(
        self, 
        attribute: ProjectAttributeResponseDTO, 
        hostname: str
    ) -> ProjectAttributeResponseDTO:
        """
        Apply business logic to a single attribute.
        
        Args:
            attribute: Attribute to process
            hostname: Organisation hostname
            
        Returns:
            Processed attribute
        """
        
        # For now, just return the original attribute
        # In the future, this could include:
        # - Permission checks
        # - Value transformation
        # - Audit logging
        return attribute 