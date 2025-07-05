"""
Project Attributes Repository Implementation
MongoDB implementation for project attributes data access
"""

import logging
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.application.dto.project_attributes_dto import (
    ProjectAttributeCreateRequestDTO,
    ProjectAttributeUpdateRequestDTO,
    ProjectAttributeSearchFiltersDTO,
    ProjectAttributeResponseDTO,
    ValueType
)
from app.domain.entities.project_attribute import ProjectAttribute
from app.domain.value_objects.organisation_id import OrganisationId
from app.infrastructure.database.mongodb_connector import MongoDBConnector


class ProjectAttributesRepositoryImpl:
    """
    Project Attributes repository implementation using MongoDB.
    
    Provides data access for organization-specific configuration attributes.
    """
    
    def __init__(self, database_connector: MongoDBConnector = None):
        self._database_connector = database_connector
        self._logger = logging.getLogger(__name__)
        self._collection_name = "project_attributes"
    
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
        
        try:
            self._logger.info(f"Creating project attribute: {request.key}")
            
            # Get organization ID from hostname
            organisation_id = await self._get_organisation_id_from_hostname(hostname)
            
            # Create domain entity
            project_attribute = ProjectAttribute(
                key=request.key,
                value=request.value,
                value_type=request.value_type,
                organisation_id=organisation_id,
                description=request.description,
                is_active=request.is_active,
                default_value=request.default_value,
                validation_rules=request.validation_rules,
                category=request.category,
                is_system=request.is_system,
                created_by=request.created_by if hasattr(request, 'created_by') else None,
                created_at=datetime.utcnow()
            )
            
            # Convert to document
            document = project_attribute.to_dict()
            document['_id'] = ObjectId()
            document['organisation_hostname'] = hostname
            
            # Insert into database
            collection = await self._get_collection()
            result = await collection.insert_one(document)
            
            # Update entity with generated ID
            project_attribute._id = str(result.inserted_id)
            
            # Convert to response DTO
            return self._entity_to_response_dto(project_attribute)
            
        except Exception as e:
            self._logger.error(f"Error creating project attribute: {e}")
            raise
    
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
        
        try:
            self._logger.info(f"Getting project attribute: {key}")
            
            collection = await self._get_collection()
            document = await collection.find_one({
                'key': key,
                'organisation_hostname': hostname
            })
            
            if not document:
                return None
            
            # Convert to domain entity
            project_attribute = self._document_to_entity(document)
            
            # Convert to response DTO
            return self._entity_to_response_dto(project_attribute)
            
        except Exception as e:
            self._logger.error(f"Error getting project attribute: {e}")
            raise
    
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
        
        try:
            self._logger.info(f"Getting project attributes with filters")
            
            # Build query
            query = {'organisation_hostname': hostname}
            
            if filters.key:
                query['key'] = {'$regex': filters.key, '$options': 'i'}
            
            if filters.value_type:
                query['value_type'] = filters.value_type.value
            
            if filters.category:
                query['category'] = filters.category
            
            if filters.is_active is not None:
                query['is_active'] = filters.is_active
            
            if filters.is_system is not None:
                query['is_system'] = filters.is_system
            
            # Execute query
            collection = await self._get_collection()
            cursor = collection.find(query).skip(filters.skip).limit(filters.limit)
            
            # Convert to response DTOs
            attributes = []
            async for document in cursor:
                project_attribute = self._document_to_entity(document)
                attributes.append(self._entity_to_response_dto(project_attribute))
            
            return attributes
            
        except Exception as e:
            self._logger.error(f"Error getting project attributes: {e}")
            raise
    
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
        
        try:
            self._logger.info(f"Updating project attribute: {key}")
            
            # Get existing attribute
            existing_dto = await self.get_by_key(key, hostname)
            if not existing_dto:
                return None
            
            # Convert to domain entity
            project_attribute = self._response_dto_to_entity(existing_dto, hostname)
            
            # Apply updates
            if request.value is not None:
                project_attribute.update_value(request.value, request.updated_by if hasattr(request, 'updated_by') else None)
            
            if request.description is not None:
                project_attribute.update_description(request.description, request.updated_by if hasattr(request, 'updated_by') else None)
            
            if request.is_active is not None:
                project_attribute.set_active_status(request.is_active, request.updated_by if hasattr(request, 'updated_by') else None)
            
            if request.validation_rules is not None:
                project_attribute.update_validation_rules(request.validation_rules, request.updated_by if hasattr(request, 'updated_by') else None)
            
            # Update in database
            collection = await self._get_collection()
            update_data = project_attribute.to_dict()
            update_data['updated_at'] = datetime.utcnow()
            
            await collection.update_one(
                {'key': key, 'organisation_hostname': hostname},
                {'$set': update_data}
            )
            
            # Return updated DTO
            return self._entity_to_response_dto(project_attribute)
            
        except Exception as e:
            self._logger.error(f"Error updating project attribute: {e}")
            raise
    
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
        
        try:
            self._logger.info(f"Deleting project attribute: {key}")
            
            collection = await self._get_collection()
            result = await collection.delete_one({
                'key': key,
                'organisation_hostname': hostname
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            self._logger.error(f"Error deleting project attribute: {e}")
            raise
    
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
        
        filters = ProjectAttributeSearchFiltersDTO(category=category)
        return await self.get_all(filters, hostname)
    
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
        
        attribute = await self.get_by_key(key, hostname)
        if not attribute or not attribute.is_active:
            return default
        
        return attribute.get_boolean_value() if hasattr(attribute, 'get_boolean_value') else bool(attribute.value)
    
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
        
        attribute = await self.get_by_key(key, hostname)
        if not attribute or not attribute.is_active:
            return default
        
        return attribute.get_numeric_value() if hasattr(attribute, 'get_numeric_value') else float(attribute.value)
    
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
        
        attribute = await self.get_by_key(key, hostname)
        if not attribute or not attribute.is_active:
            return default
        
        return attribute.get_string_value() if hasattr(attribute, 'get_string_value') else str(attribute.value)
    
    async def _get_collection(self):
        """Get MongoDB collection."""
        if not self._database_connector:
            raise ValueError("Database connector not initialized")
        
        database = self._database_connector.get_database()
        return database[self._collection_name]
    
    async def _get_organisation_id_from_hostname(self, hostname: str) -> OrganisationId:
        """Get organization ID from hostname."""
        # This is a simplified implementation
        # In a real system, you'd query the organizations collection
        return OrganisationId(f"org_{hostname}")
    
    def _document_to_entity(self, document: dict) -> ProjectAttribute:
        """Convert MongoDB document to domain entity."""
        # Remove MongoDB-specific fields
        data = {k: v for k, v in document.items() if not k.startswith('_')}
        data['organisation_id'] = data.pop('organisation_hostname', 'unknown')
        
        return ProjectAttribute.from_dict(data)
    
    def _entity_to_response_dto(self, entity: ProjectAttribute) -> ProjectAttributeResponseDTO:
        """Convert domain entity to response DTO."""
        return ProjectAttributeResponseDTO(
            key=entity.key,
            value=entity.value,
            value_type=entity.value_type,
            description=entity.description,
            is_active=entity.is_active,
            default_value=entity.default_value,
            validation_rules=entity.validation_rules,
            category=entity.category,
            is_system=entity.is_system,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by
        )
    
    def _response_dto_to_entity(self, dto: ProjectAttributeResponseDTO, hostname: str) -> ProjectAttribute:
        """Convert response DTO to domain entity."""
        organisation_id = OrganisationId(f"org_{hostname}")
        
        return ProjectAttribute(
            key=dto.key,
            value=dto.value,
            value_type=dto.value_type,
            organisation_id=organisation_id,
            description=dto.description,
            is_active=dto.is_active,
            default_value=dto.default_value,
            validation_rules=dto.validation_rules,
            category=dto.category,
            is_system=dto.is_system,
            created_by=dto.created_by,
            updated_by=dto.updated_by,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        ) 