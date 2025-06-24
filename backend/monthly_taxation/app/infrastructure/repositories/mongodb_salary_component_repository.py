"""
MongoDB Salary Component Repository Implementation
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime
from bson import ObjectId

from app.application.interfaces.repositories.salary_component_repository import SalaryComponentRepository
from app.application.dto.salary_component_dto import SalaryComponentSearchFiltersDTO
from app.domain.entities.salary_component import SalaryComponent
from app.domain.value_objects.component_id import ComponentId
from app.domain.value_objects.component_type import ComponentType, ValueType
from app.domain.entities.salary_component import ExemptionSection
from app.infrastructure.database.mongodb_connector import MongoDBConnector

logger = logging.getLogger(__name__)


class MongoDBSalaryComponentRepository(SalaryComponentRepository):
    """MongoDB implementation of salary component repository"""
    
    def __init__(self, database_connector: MongoDBConnector):
        self.db_connector = database_connector
        self.collection_name = "salary_components"
    
    async def save(self, component: SalaryComponent, hostname: str) -> SalaryComponent:
        """Save salary component to MongoDB"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            component_dict = self._entity_to_dict(component)
            
            # Check if component exists
            existing = await collection.find_one({"id": component.id.value})
            
            if existing is None:
                # Insert new component
                result = await collection.insert_one(component_dict)
                component_dict["_id"] = result.inserted_id
                logger.info(f"Created new salary component: {component.code}")
            else:
                # Update existing component
                await collection.replace_one(
                    {"id": component.id.value},
                    component_dict
                )
                logger.info(f"Updated salary component: {component.code}")
            
            return self._dict_to_entity(component_dict)
            
        except Exception as e:
            logger.error(f"Error saving salary component to database {hostname}: {e}")
            raise
    
    async def get_by_id(self, component_id: ComponentId, hostname: str) -> Optional[SalaryComponent]:
        """Get salary component by ID"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            component_dict = await collection.find_one({"id": component_id.value})
            
            if not component_dict:
                return None
            
            return self._dict_to_entity(component_dict)
            
        except Exception as e:
            logger.error(f"Error getting salary component {component_id.value}: {e}")
            raise
    
    async def get_by_code(self, code: str, hostname: str) -> Optional[SalaryComponent]:
        """Get salary component by code"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            component_dict = await collection.find_one({"code": code.upper()})
            
            if not component_dict:
                return None
            
            return self._dict_to_entity(component_dict)
            
        except Exception as e:
            logger.error(f"Error getting salary component by code {code}: {e}")
            raise
    
    async def find_with_filters(
        self, 
        filters: SalaryComponentSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[SalaryComponent], int]:
        """Find salary components with filters"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Build query
            query = {}
            if filters.component_type:
                query["component_type"] = filters.component_type.upper()
            if filters.value_type:
                query["value_type"] = filters.value_type.upper()
            if filters.is_taxable is not None:
                query["is_taxable"] = filters.is_taxable
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
            
            # Add search term filtering
            if filters.search_term:
                search_regex = {"$regex": filters.search_term, "$options": "i"}
                query["$or"] = [
                    {"code": search_regex},
                    {"name": search_regex},
                    {"description": search_regex}
                ]
            
            # Count total documents
            total_count = await collection.count_documents(query)
            
            # Calculate skip
            skip = (filters.page - 1) * filters.page_size
            
            # Build sort criteria
            sort_direction = 1 if filters.sort_order == "asc" else -1
            sort_criteria = [(filters.sort_by, sort_direction)]
            
            # Execute query with pagination and sorting
            cursor = collection.find(query).skip(skip).limit(filters.page_size).sort(sort_criteria)
            component_dicts = await cursor.to_list(length=filters.page_size)
            
            components = [self._dict_to_entity(doc) for doc in component_dicts]
            
            return components, total_count
            
        except Exception as e:
            logger.error(f"Error finding salary components: {e}")
            raise
    
    async def get_all_active(self, hostname: str) -> List[SalaryComponent]:
        """Get all active salary components"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            cursor = collection.find({"is_active": True})
            component_dicts = await cursor.to_list(length=None)
            
            components = [self._dict_to_entity(doc) for doc in component_dicts]
            
            return components
            
        except Exception as e:
            logger.error(f"Error getting active salary components: {e}")
            raise
    
    async def delete(self, component_id: ComponentId, hostname: str) -> bool:
        """Delete salary component"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Soft delete by marking as inactive
            result = await collection.update_one(
                {"id": component_id.value},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting salary component {component_id.value}: {e}")
            raise
    
    async def check_code_exists(self, code: str, hostname: str, exclude_id: Optional[ComponentId] = None) -> bool:
        """Check if component code exists"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            query = {"code": code.upper()}
            if exclude_id:
                query["id"] = {"$ne": exclude_id.value}
            
            existing = await collection.find_one(query)
            return existing is not None
            
        except Exception as e:
            logger.error(f"Error checking if code exists {code}: {e}")
            return False
    
    async def get_usage_count(self, component_id: ComponentId, hostname: str) -> int:
        """Get usage count for component"""
        try:
            db = await self.db_connector.get_database(hostname)
            
            # Check in employee_salaries collection for component usage
            employee_salaries_collection = db["employee_salaries"]
            
            # Count documents where this component is used in salary structure
            usage_count = await employee_salaries_collection.count_documents({
                "salary_structure.components.component_id": component_id.value
            })
            
            return usage_count
            
        except Exception as e:
            logger.error(f"Error getting usage count for component {component_id.value}: {e}")
            return 0
    
    async def get_components_by_type(self, component_type: str, hostname: str) -> List[SalaryComponent]:
        """Get components by type"""
        try:
            db = await self.db_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            cursor = collection.find({"component_type": component_type.upper()})
            component_dicts = await cursor.to_list(length=None)
            
            components = [self._dict_to_entity(doc) for doc in component_dicts]
            
            return components
            
        except Exception as e:
            logger.error(f"Error getting components by type {component_type}: {e}")
            raise
    
    def _entity_to_dict(self, component: SalaryComponent) -> dict:
        """Convert salary component entity to dictionary"""
        return {
            "id": component.id.value,
            "code": component.code,
            "name": component.name,
            "component_type": component.component_type.value,
            "value_type": component.value_type.value,
            "is_taxable": component.is_taxable,
            "exemption_section": component.exemption_section.value,
            "formula": component.formula,
            "default_value": float(component.default_value) if component.default_value else None,
            "description": component.description,
            "is_active": component.is_active,
            "created_at": component.created_at,
            "updated_at": component.updated_at,
            "created_by": component.created_by,
            "updated_by": component.updated_by,
            "metadata": component.metadata or {}
        }
    
    def _dict_to_entity(self, component_dict: dict) -> SalaryComponent:
        """Convert dictionary to salary component entity"""
        return SalaryComponent(
            id=ComponentId(component_dict["id"]),
            code=component_dict["code"],
            name=component_dict["name"],
            component_type=ComponentType(component_dict["component_type"]),
            value_type=ValueType(component_dict["value_type"]),
            is_taxable=component_dict["is_taxable"],
            exemption_section=ExemptionSection(component_dict["exemption_section"]),
            formula=component_dict.get("formula"),
            default_value=component_dict.get("default_value"),
            description=component_dict.get("description"),
            is_active=component_dict.get("is_active", True),
            created_at=component_dict.get("created_at"),
            updated_at=component_dict.get("updated_at"),
            created_by=component_dict.get("created_by"),
            updated_by=component_dict.get("updated_by"),
            metadata=component_dict.get("metadata", {})
        ) 