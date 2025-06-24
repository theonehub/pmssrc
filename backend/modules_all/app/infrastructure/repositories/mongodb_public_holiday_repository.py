"""
MongoDB Public Holiday Repository Implementation
Following SOLID principles and DDD patterns for public holiday data access
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from app.domain.entities.public_holiday import PublicHoliday
from app.domain.value_objects.public_holiday_id import PublicHolidayId
from app.application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayRepository,
    PublicHolidayCommandRepository, 
    PublicHolidayQueryRepository, 
    PublicHolidayAnalyticsRepository,
    PublicHolidayCalendarRepository
)
from app.application.dto.public_holiday_dto import PublicHolidaySearchFiltersDTO
from app.infrastructure.database.database_connector import DatabaseConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

logger = logging.getLogger(__name__)


class MongoDBPublicHolidayRepository(PublicHolidayRepository):
    """
    MongoDB implementation of public holiday repository following User Module Architecture Guide.
    
    Handles organisation-based data segregation through database selection.
    Follows SOLID principles:
    - SRP: Only handles public holiday storage operations
    - OCP: Can be extended with new storage features
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused repository interface
    - DIP: Depends on MongoDB abstractions
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """Initialize repository with database connector."""
        self.db_connector = database_connector
        self._collection_name = "public_holidays"
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
        
    async def _get_collection(self, hostname: str):
        """
        Get public holidays collection for specific organisation.
        
        Ensures database connection is established in the correct event loop.
        Uses organisation-specific database for public holiday data.
        """
        db_name = f"pms_{hostname}"
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.info("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    logger.info("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    logger.info("Loading connection parameters from mongodb_config")
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
            logger.info(f"Successfully retrieved collection: {self._collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def _ensure_indexes(self, hostname: str):
        """Ensure necessary indexes exist"""
        try:
            collection = await self._get_collection(hostname)
            await collection.create_index([("id", ASCENDING)], unique=True)
            await collection.create_index([("date", ASCENDING)])
            await collection.create_index([("is_active", ASCENDING)])
            await collection.create_index([("created_at", DESCENDING)])
            self._logger.info("Public holiday indexes ensured")
        except Exception as e:
            self._logger.warning(f"Error creating indexes: {e}")

    async def save(self, holiday: PublicHoliday, hostname: str) -> PublicHoliday:
        """Save public holiday to organisation-specific database."""
        try:
            collection = await self._get_collection(hostname)
            holiday_dict = self._entity_to_dict(holiday)
            
            # if holiday.is_new():
            #     # Insert new holiday
            #     result = await collection.insert_one(holiday_dict)
            #     holiday_dict["_id"] = result.inserted_id
            #     self._logger.info(f"Saved new public holiday: {holiday.id}")
            # else:
            #     # Update existing holiday
            #     result = await collection.replace_one(
            #         {"id": str(holiday.id)},
            #         holiday_dict
            #     )
            #     if result.matched_count > 0:
            #         self._logger.info(f"Updated public holiday: {holiday.id}")
            
            result = await collection.insert_one(holiday_dict)
            holiday_dict["_id"] = result.inserted_id
            self._logger.info(f"Saved new public holiday: {holiday.id}")
            return self._dict_to_entity(holiday_dict)
            
        except Exception as e:
            logger.error(f"Error saving public holiday to database {hostname}: {e}")
            raise
    
    async def get_by_id(self, holiday_id: PublicHolidayId, hostname: str) -> Optional[PublicHoliday]:
        """Get public holiday by ID from organisation-specific database."""
        try:
            collection = await self._get_collection(hostname)
            holiday_dict = await collection.find_one({"id": str(holiday_id)})
            
            if not holiday_dict:
                return None
            
            return self._dict_to_entity(holiday_dict)
            
        except Exception as e:
            logger.error(f"Error getting public holiday {holiday_id} from database {hostname}: {e}")
            raise
    
    async def find_with_filters(
        self, 
        filters: PublicHolidaySearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[PublicHoliday], int]:
        """Find public holidays with filters from organisation-specific database."""
        try:
            collection = await self._get_collection(hostname)
            
            # Build query
            query = {}
            if filters.year:
                start_date = datetime(filters.year, 1, 1)
                end_date = datetime(filters.year, 12, 31, 23, 59, 59)
                query["date"] = {"$gte": start_date, "$lte": end_date}
            
            if filters.month and filters.year:
                start_date = datetime(filters.year, filters.month, 1)
                if filters.month == 12:
                    end_date = datetime(filters.year + 1, 1, 1) - timedelta(seconds=1)
                else:
                    end_date = datetime(filters.year, filters.month + 1, 1) - timedelta(seconds=1)
                query["date"] = {"$gte": start_date, "$lte": end_date}
            
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
            
            if filters.category:
                query["category"] = filters.category.value
            
            if filters.observance:
                query["observance"] = filters.observance.value
            
            # Count total documents
            total_count = await collection.count_documents(query)
            
            # Build sort criteria
            sort_criteria = []
            if filters.sort_by:
                sort_direction = 1 if filters.sort_order == "asc" else -1
                sort_criteria.append((filters.sort_by, sort_direction))
            
            # Calculate skip
            skip = (filters.page - 1) * filters.page_size
            
            # Execute query
            cursor = collection.find(query).sort(sort_criteria).skip(skip).limit(filters.page_size)
            holiday_dicts = await cursor.to_list(length=filters.page_size)
            
            holidays = [self._dict_to_entity(holiday_dict) for holiday_dict in holiday_dicts]
            
            return holidays, total_count
            
        except Exception as e:
            logger.error(f"Error finding public holidays with filters in database {hostname}: {e}")
            raise
    
    async def find_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        hostname: str
    ) -> List[PublicHoliday]:
        """Find public holidays within date range from organisation-specific database."""
        try:
            collection = await self._get_collection(hostname)
            
            # Convert dates to datetime for MongoDB query
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            query = {
                "date": {"$gte": start_datetime, "$lte": end_datetime},
                "is_active": True
            }
            
            cursor = collection.find(query).sort("date", 1)
            holiday_dicts = await cursor.to_list(length=None)
            
            holidays = [self._dict_to_entity(holiday_dict) for holiday_dict in holiday_dicts]
            
            return holidays
            
        except Exception as e:
            logger.error(f"Error finding public holidays by date range in database {hostname}: {e}")
            raise
    
    async def find_by_date(self, holiday_date: date, hostname: str) -> List[PublicHoliday]:
        """Find public holidays on specific date from organisation-specific database."""
        try:
            collection = await self._get_collection(hostname)
            
            # Convert date to datetime for MongoDB query
            start_datetime = datetime.combine(holiday_date, datetime.min.time())
            end_datetime = datetime.combine(holiday_date, datetime.max.time())
            
            query = {
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }
            
            cursor = collection.find(query)
            holiday_dicts = await cursor.to_list(length=None)
            
            holidays = [self._dict_to_entity(holiday_dict) for holiday_dict in holiday_dicts]
            
            return holidays
            
        except Exception as e:
            logger.error(f"Error finding public holidays by date in database {hostname}: {e}")
            raise
    
    async def delete(self, holiday_id: PublicHolidayId, hostname: str) -> bool:
        """Delete public holiday from organisation-specific database (soft delete)."""
        try:
            collection = await self._get_collection(hostname)
            
            result = await collection.update_one(
                {"id": str(holiday_id)},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.matched_count > 0
            if success:
                self._logger.info(f"Deleted public holiday: {holiday_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting public holiday {holiday_id} from database {hostname}: {e}")
            raise
    
    async def get_all_active(self, hostname: str) -> List[PublicHoliday]:
        """Get all active public holidays"""
        try:
            collection = await self._get_collection(hostname)
            cursor = collection.find({"is_active": True}).sort("date", ASCENDING)
            holiday_dicts = await cursor.to_list(length=None)
            
            return [self._dict_to_entity(holiday_dict) for holiday_dict in holiday_dicts]
            
        except Exception as e:
            logger.error(f"Error getting active holidays from database {hostname}: {e}")
            return []
    
    async def get_all(self, hostname: str, include_inactive: bool = False) -> List[PublicHoliday]:
        """Get all public holidays"""
        try:
            collection = await self._get_collection(hostname)
            
            query = {} if include_inactive else {"is_active": True}
            cursor = collection.find(query).sort("date", ASCENDING)
            holiday_dicts = await cursor.to_list(length=None)
            
            return [self._dict_to_entity(holiday_dict) for holiday_dict in holiday_dicts]
            
        except Exception as e:
            logger.error(f"Error getting all holidays from database {hostname}: {e}")
            return []
    
    async def exists_on_date(self, holiday_date: date, hostname: str) -> bool:
        """Check if any active holiday exists on a specific date."""
        try:
            collection = await self._get_collection(hostname)
            # Convert date to datetime for MongoDB compatibility
            start_datetime = datetime.combine(holiday_date, datetime.min.time())
            end_datetime = datetime.combine(holiday_date, datetime.max.time())
            
            count = await collection.count_documents({
                "date": {"$gte": start_datetime, "$lte": end_datetime},
                "is_active": True
            })
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking if holiday exists on date in database {hostname}: {e}")
            return False
    
    async def count_active(self, hostname: str) -> int:
        """Count active public holidays."""
        try:
            collection = await self._get_collection(hostname)
            return await collection.count_documents({"is_active": True})
            
        except Exception as e:
            logger.error(f"Error counting active holidays in database {hostname}: {e}")
            return 0
    
    def _entity_to_dict(self, holiday: PublicHoliday) -> dict:
        """Convert public holiday entity to dictionary."""
        return {
            "id": str(holiday.id),
            "name": holiday.name,
            "date": datetime.combine(holiday.date, datetime.min.time()),
            "description": holiday.description,
            "is_active": holiday.is_active,
            "created_at": holiday.created_at,
            "updated_at": holiday.updated_at,
            "created_by": holiday.created_by,
            "updated_by": holiday.updated_by,
            "location_specific": holiday.location_specific
        }
    
    def _dict_to_entity(self, holiday_dict: dict) -> PublicHoliday:
        """Convert dictionary to public holiday entity."""
        # Convert datetime back to date
        date_value = holiday_dict["date"]
        if isinstance(date_value, datetime):
            holiday_date = date_value.date()
        else:
            holiday_date = date_value
        
        return PublicHoliday(
            id=PublicHolidayId(holiday_dict["id"]),
            name=holiday_dict["name"],
            date=holiday_date,
            description=holiday_dict.get("description"),
            is_active=holiday_dict.get("is_active", True),
            created_at=holiday_dict.get("created_at"),
            updated_at=holiday_dict.get("updated_at"),
            created_by=holiday_dict.get("created_by"),
            updated_by=holiday_dict.get("updated_by"),
            location_specific=holiday_dict.get("location_specific")
        ) 