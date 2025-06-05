"""
MongoDB Company Leave Repository Implementation
Concrete implementation of company leave repositories using MongoDB
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveRepository,
    CompanyLeaveCommandRepository,
    CompanyLeaveQueryRepository
)
from app.application.dto.company_leave_dto import CompanyLeaveSearchFiltersDTO
from app.domain.entities.company_leave import CompanyLeave
from app.infrastructure.database.database_connector import DatabaseConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

logger = logging.getLogger(__name__)


class MongoDBCompanyLeaveRepository(CompanyLeaveRepository):
    """
    MongoDB implementation of company leave repository.
    
    Follows SOLID principles:
    - SRP: Only handles company leave storage operations
    - OCP: Can be extended with new storage features
    - LSP: Can be substituted with other implementations
    - ISP: Implements both command and query operations
    - DIP: Depends on MongoDB abstractions
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "company_leaves"
        self._logger = logging.getLogger(__name__)
        
        # Connection configuration (will be set by dependency container)
        self._connection_string = None
        self._client_options = None
    
    def set_connection_config(self, connection_string: str, client_options: Dict[str, Any]):
        """
        Set MongoDB connection configuration.
        
        Args:
            connection_string: MongoDB connection string
            client_options: MongoDB client options
        """
        self._connection_string = connection_string
        self._client_options = client_options
        
    async def _get_collection(self, organisation_id: Optional[str] = None):
        """
        Get company leaves collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        Uses global database for company leave data.
        """
        db_name = "pms_"+organisation_id if organisation_id else "pms_"+self._collection_name
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.debug("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    logger.debug("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    logger.debug("Loading connection parameters from mongodb_config")
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            db = self.db_connector.get_database(db_name)
            collection = db[self._collection_name]
            logger.debug(f"Successfully retrieved collection: {self._collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def _ensure_indexes(self):
        """Ensure necessary indexes exist"""
        try:
            collection = await self._get_collection()
            await collection.create_index([("company_leave_id", ASCENDING)], unique=True)
            await collection.create_index([("accrual_type", ASCENDING)])
            await collection.create_index([("is_active", ASCENDING)])
            await collection.create_index([("created_at", DESCENDING)])
            self._logger.info("Company leave indexes ensured")
        except Exception as e:
            self._logger.warning(f"Error creating indexes: {e}")

    async def save(self, company_leave: CompanyLeave) -> bool:
        """Save company leave record"""
        try:
            collection = await self._get_collection()
            document = self._entity_to_document(company_leave)
            result = await collection.insert_one(document)
            
            if result.inserted_id:
                self._logger.info(f"Saved company leave: {company_leave.company_leave_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Error saving company leave: {e}")
            return False
    
    async def update(self, company_leave: CompanyLeave) -> bool:
        """Update existing company leave record"""
        try:
            collection = await self._get_collection()
            document = self._entity_to_document(company_leave)
            # Remove _id to avoid update conflicts
            document.pop('_id', None)
            
            result = await collection.replace_one(
                {"company_leave_id": company_leave.company_leave_id},
                document
            )
            
            if result.matched_count > 0:
                self._logger.info(f"Updated company leave: {company_leave.company_leave_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Error updating company leave: {e}")
            return False
    
    async def delete(self, company_leave_id: str) -> bool:
        """Delete company leave record (soft delete)"""
        try:
            collection = await self._get_collection()
            result = await collection.update_one(
                {"company_leave_id": company_leave_id},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                self._logger.info(f"Deleted company leave: {company_leave_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Error deleting company leave: {e}")
            return False
    
    async def get_by_id(self, company_leave_id: str) -> Optional[CompanyLeave]:
        """Get company leave by ID"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({"company_leave_id": company_leave_id})
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            self._logger.error(f"Error retrieving company leave by ID: {e}")
            return None
    
    async def get_all_active(self) -> List[CompanyLeave]:
        """Get all active company leaves"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"is_active": True}).sort("created_at", DESCENDING)
            documents = await cursor.to_list(None)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving active company leaves: {e}")
            return []
    
    async def get_all(self, include_inactive: bool = False) -> List[CompanyLeave]:
        """Get all company leaves"""
        try:
            logger.info(f"Retrieving all company leaves (include_inactive: {include_inactive})")
            collection = await self._get_collection()
            query = {} if include_inactive else {"is_active": True}
            
            logger.debug(f"Using query: {query}")
            cursor = collection.find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(None)
            
            logger.info(f"Retrieved {len(documents)} company leave documents from MongoDB")
            company_leaves = [self._document_to_entity(doc) for doc in documents]
            logger.info(f"Successfully converted {len(company_leaves)} documents to entities")
            
            return company_leaves
            
        except Exception as e:
            logger.error(f"Error retrieving company leaves: {e}")
            return []
    
    async def list_with_filters(self, filters: CompanyLeaveSearchFiltersDTO) -> List[CompanyLeave]:
        """Get company leaves with filters and pagination"""
        try:
            logger.info(f"Retrieving company leaves with filters: {filters.to_dict()}")
            collection = await self._get_collection()
            # Build query
            query = {}
            
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
            
            if filters.accrual_type:
                query["accrual_type"] = filters.accrual_type
            
            logger.debug(f"MongoDB query: {query}")
            
            # Calculate pagination
            skip = (filters.page - 1) * filters.page_size
            logger.debug(f"Pagination: skip={skip}, limit={filters.page_size}")
            
            # Build sort
            sort_direction = ASCENDING if filters.sort_order == "asc" else DESCENDING
            sort_field = filters.sort_by
            logger.debug(f"Sort: field={sort_field}, direction={sort_direction}")
            
            cursor = (
                collection
                .find(query)
                .sort(sort_field, sort_direction)
                .skip(skip)
                .limit(filters.page_size)
            )
            
            documents = await cursor.to_list(None)
            logger.info(f"Retrieved {len(documents)} company leave documents from MongoDB with filters")
            
            company_leaves = [self._document_to_entity(doc) for doc in documents]
            logger.info(f"Successfully converted {len(company_leaves)} filtered documents to entities")
            
            return company_leaves
            
        except Exception as e:
            logger.error(f"Error retrieving filtered company leaves: {e}")
            return []
    
    async def count_with_filters(self, filters: CompanyLeaveSearchFiltersDTO) -> int:
        """Count company leaves matching filters"""
        try:
            collection = await self._get_collection()
            # Build query
            query = {}
            
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
            
            if filters.accrual_type:
                query["accrual_type"] = filters.accrual_type
            
            return await collection.count_documents(query)
            
        except Exception as e:
            self._logger.error(f"Error counting filtered company leaves: {e}")
            return 0
    
    async def exists_by_id(self, company_leave_id: str) -> bool:
        """Check if company leave exists by ID"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({"company_leave_id": company_leave_id})
            return count > 0
            
        except Exception as e:
            self._logger.error(f"Error checking company leave existence: {e}")
            return False
    
    async def count_active(self) -> int:
        """Count active company leaves"""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({"is_active": True})
            
        except Exception as e:
            self._logger.error(f"Error counting active company leaves: {e}")
            return 0
    
    def _entity_to_document(self, company_leave: CompanyLeave) -> Dict[str, Any]:
        """Convert CompanyLeave entity to MongoDB document"""
        return {
            "company_leave_id": company_leave.company_leave_id,
            "leave_name": company_leave.leave_name,
            "accrual_type": company_leave.accrual_type,
            "annual_allocation": company_leave.annual_allocation,
            "computed_monthly_allocation": company_leave.computed_monthly_allocation,
            "is_active": company_leave.is_active,
            "description": company_leave.description,
            "encashable": company_leave.encashable,
            "is_allowed_on_probation": company_leave.is_allowed_on_probation,
            "created_at": company_leave.created_at,
            "updated_at": company_leave.updated_at,
            "created_by": company_leave.created_by,
            "updated_by": company_leave.updated_by
        }
    
    def _document_to_entity(self, document: Dict[str, Any]) -> CompanyLeave:
        """Convert MongoDB document to CompanyLeave entity"""
        return CompanyLeave(
            company_leave_id=document["company_leave_id"],
            leave_name=document.get("leave_name", ""),
            accrual_type=document["accrual_type"],
            annual_allocation=document["annual_allocation"],
            computed_monthly_allocation=document.get("computed_monthly_allocation", 0),
            is_active=document["is_active"],
            description=document.get("description"),
            encashable=document.get("encashable", False),
            is_allowed_on_probation=document.get("is_allowed_on_probation", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            created_by=document.get("created_by"),
            updated_by=document.get("updated_by")
        )