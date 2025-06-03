"""
SOLID-Compliant Public Holiday Repository Implementation
Replaces the procedural public_holiday_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.public_holiday import PublicHoliday
    from app.domain.value_objects.holiday_id import HolidayId
    from models.public_holiday import PublicHoliday as PublicHolidayModel
except ImportError:
    # Fallback classes for migration compatibility
    class PublicHoliday:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class HolidayId:
        def __init__(self, value: str):
            self.value = value
        def __str__(self):
            return self.value
    
    class PublicHolidayModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self, exclude=None):
            result = {k: v for k, v in self.__dict__.items()}
            if exclude:
                for key in exclude:
                    result.pop(key, None)
            return result

# Import application interfaces
try:
    from app.application.interfaces.repositories.public_holiday_repository import (
        PublicHolidayCommandRepository, PublicHolidayQueryRepository,
        PublicHolidayAnalyticsRepository, PublicHolidayRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class PublicHolidayCommandRepository(ABC):
        pass
    
    class PublicHolidayQueryRepository(ABC):
        pass
    
    class PublicHolidayAnalyticsRepository(ABC):
        pass
    
    class PublicHolidayRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.public_holiday_dto import (
        PublicHolidaySearchFiltersDTO, PublicHolidayStatisticsDTO
    )
except ImportError:
    # Fallback DTOs
    class PublicHolidaySearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PublicHolidayStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidPublicHolidayRepository(
    BaseRepository[PublicHoliday],
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository,
    PublicHolidayAnalyticsRepository,
    PublicHolidayRepository
):
    """
    SOLID-compliant public holiday repository implementation.
    
    Replaces the procedural public_holiday_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles public holiday data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all public holiday repository interfaces
    - Interface Segregation: Implements focused public holiday repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize public holiday repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "public_holidays")
        
    def _entity_to_document(self, holiday: PublicHoliday) -> Dict[str, Any]:
        """
        Convert PublicHoliday entity to database document.
        
        Args:
            holiday: PublicHoliday entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(holiday, 'model_dump'):
            document = holiday.model_dump()
        elif hasattr(holiday, 'dict'):
            document = holiday.dict()
        else:
            document = {k: v for k, v in holiday.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Ensure proper field mapping for legacy compatibility
        if 'holiday_id' not in document and hasattr(holiday, 'holiday_id'):
            document['holiday_id'] = getattr(holiday, 'holiday_id')
        
        # Handle date field and extract day, month, year
        holiday_date = getattr(holiday, 'date', None)
        if holiday_date:
            if isinstance(holiday_date, str):
                try:
                    holiday_date = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        holiday_date = datetime.fromisoformat(holiday_date).date()
                    except ValueError:
                        logger.warning(f"Could not parse date: {holiday_date}")
                        holiday_date = None
            
            if holiday_date:
                document['date'] = holiday_date
                document['day'] = holiday_date.day
                document['month'] = holiday_date.month
                document['year'] = holiday_date.year
        
        # Set default values
        if 'is_active' not in document:
            document['is_active'] = True
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> PublicHoliday:
        """
        Convert database document to PublicHoliday entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            PublicHoliday entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        return PublicHoliday(**document)
    
    async def _ensure_indexes(self, organisation_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organisation_id)
            
            # Index for holiday_id queries
            await collection.create_index([
                ("holiday_id", 1)
            ], unique=True)
            
            # Index for date queries
            await collection.create_index([
                ("date", 1)
            ])
            
            # Index for month/year queries
            await collection.create_index([
                ("year", 1),
                ("month", 1)
            ])
            
            # Index for active holidays
            await collection.create_index([
                ("is_active", 1),
                ("date", 1)
            ])
            
            # Index for created_by queries
            await collection.create_index([
                ("created_by", 1),
                ("created_at", -1)
            ])
            
            logger.info(f"Public holiday indexes ensured for organisation: {organisation_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring public holiday indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, holiday: PublicHoliday) -> PublicHoliday:
        """
        Save public holiday record.
        
        Replaces: create_holiday() function
        """
        try:
            # Get organisation from holiday or use default
            organisation_id = getattr(holiday, 'organisation_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organisation_id)
            
            # Prepare document
            document = self._entity_to_document(holiday)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            # Generate holiday_id if not present
            if not document.get('holiday_id'):
                document['holiday_id'] = f"HOL-{datetime.now().timestamp()}"
            
            # Check for existing record by holiday_id
            existing = None
            if document.get('holiday_id'):
                existing = await self.get_by_id(document['holiday_id'], organisation_id)
            
            if existing:
                # Update existing record
                filters = {"holiday_id": document['holiday_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organisation_id=organisation_id
                )
                if success:
                    return await self.get_by_id(document['holiday_id'], organisation_id)
                else:
                    raise ValueError("Failed to update public holiday record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organisation_id)
                # Return the saved document
                saved_doc = await self._get_collection(organisation_id).find_one({"_id": document_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving public holiday: {e}")
            raise
    
    async def update(self, holiday_id: str, update_data: Dict[str, Any], 
                    organisation_id: str) -> bool:
        """
        Update public holiday record.
        
        Replaces: update_holiday() function
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            # Handle date updates
            if 'date' in update_data:
                holiday_date = update_data['date']
                if isinstance(holiday_date, str):
                    try:
                        holiday_date = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                    except ValueError:
                        holiday_date = datetime.fromisoformat(holiday_date).date()
                
                update_data['date'] = holiday_date
                update_data['day'] = holiday_date.day
                update_data['month'] = holiday_date.month
                update_data['year'] = holiday_date.year
            
            filters = {"holiday_id": holiday_id}
            
            success = await self._update_document(
                filters=filters,
                update_data=update_data,
                organisation_id=organisation_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating public holiday {holiday_id}: {e}")
            return False
    
    async def delete(self, holiday_id: str, organisation_id: str) -> bool:
        """
        Delete public holiday record (soft delete).
        
        Replaces: delete_holiday() function
        """
        try:
            # Soft delete by setting is_active to False
            update_data = {
                "is_active": False,
                "updated_at": datetime.now()
            }
            
            return await self.update(holiday_id, update_data, organisation_id)
            
        except Exception as e:
            logger.error(f"Error deleting public holiday {holiday_id}: {e}")
            return False
    
    async def bulk_import(self, holiday_data_list: List[Dict[str, Any]], 
                         employee_id: str, organisation_id: str) -> int:
        """
        Import multiple holidays from processed data.
        
        Replaces: import_holidays() function
        """
        try:
            # Ensure indexes
            await self._ensure_indexes(organisation_id)
            
            collection = self._get_collection(organisation_id)
            inserted_count = 0
            
            for holiday_data in holiday_data_list:
                try:
                    # Prepare document
                    document = {
                        "name": holiday_data['name'],
                        "description": holiday_data.get('description', ''),
                        "created_by": employee_id,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                        "is_active": True,
                        "holiday_id": holiday_data.get('holiday_id', f"HOL-{datetime.now().timestamp()}")
                    }
                    
                    # Handle date
                    holiday_date = holiday_data['date']
                    if isinstance(holiday_date, str):
                        holiday_date = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                    elif isinstance(holiday_date, datetime):
                        holiday_date = holiday_date.date()
                    
                    document['date'] = holiday_date
                    document['day'] = holiday_date.day
                    document['month'] = holiday_date.month
                    document['year'] = holiday_date.year
                    
                    # Insert document
                    await collection.insert_one(document)
                    inserted_count += 1
                    
                except Exception as e:
                    logger.error(f"Error importing holiday {holiday_data.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully imported {inserted_count} holidays")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error bulk importing holidays: {e}")
            return 0
    
    # Query Repository Implementation
    async def get_by_id(self, holiday_id: str, organisation_id: str = "default") -> Optional[PublicHoliday]:
        """Get public holiday record by ID."""
        try:
            filters = {"holiday_id": holiday_id}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organisation_id=organisation_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving public holiday {holiday_id}: {e}")
            return None
    
    async def get_all_active(self, organisation_id: str = "default") -> List[PublicHoliday]:
        """
        Get all active public holidays.
        
        Replaces: get_all_holidays() function
        """
        try:
            filters = {"is_active": True}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                limit=500,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all active holidays: {e}")
            return []
    
    async def get_by_month(self, month: int, year: int, 
                          organisation_id: str = "default") -> List[PublicHoliday]:
        """
        Get all active public holidays for a specific month and year.
        
        Replaces: get_holiday_by_month() function
        """
        try:
            filters = {
                "month": month,
                "year": year,
                "is_active": True
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="day",
                sort_order=1,
                limit=50,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving holidays for {month}/{year}: {e}")
            return []
    
    async def get_by_date(self, target_date: Union[date, str], 
                         organisation_id: str = "default") -> Optional[PublicHoliday]:
        """
        Get public holiday by specific date.
        
        Replaces: get_holiday_by_date_str() function
        """
        try:
            if isinstance(target_date, str):
                try:
                    target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
                except ValueError:
                    target_date = datetime.fromisoformat(target_date).date()
            
            filters = {
                "date": target_date,
                "is_active": True
            }
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organisation_id=organisation_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving holiday by date {target_date}: {e}")
            return None
    
    async def get_by_date_range(self, start_date: date, end_date: date,
                               organisation_id: str = "default") -> List[PublicHoliday]:
        """Get public holidays within a date range."""
        try:
            filters = {
                "date": {"$gte": start_date, "$lte": end_date},
                "is_active": True
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                limit=100,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving holidays by date range: {e}")
            return []
    
    async def get_by_year(self, year: int, organisation_id: str = "default") -> List[PublicHoliday]:
        """Get all active public holidays for a specific year."""
        try:
            filters = {
                "year": year,
                "is_active": True
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                limit=200,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving holidays for year {year}: {e}")
            return []
    
    async def search(self, filters: PublicHolidaySearchFiltersDTO,
                    organisation_id: str = "default") -> List[PublicHoliday]:
        """Search public holidays with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'name') and filters.name:
                query_filters["name"] = {"$regex": filters.name, "$options": "i"}
            
            if hasattr(filters, 'year') and filters.year:
                query_filters["year"] = filters.year
            
            if hasattr(filters, 'month') and filters.month:
                query_filters["month"] = filters.month
            
            if hasattr(filters, 'is_active') and filters.is_active is not None:
                query_filters["is_active"] = filters.is_active
            
            if hasattr(filters, 'created_by') and filters.created_by:
                query_filters["created_by"] = filters.created_by
            
            if hasattr(filters, 'start_date') and filters.start_date:
                query_filters["date"] = {"$gte": filters.start_date}
            
            if hasattr(filters, 'end_date') and filters.end_date:
                if "date" in query_filters:
                    query_filters["date"]["$lte"] = filters.end_date
                else:
                    query_filters["date"] = {"$lte": filters.end_date}
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            documents = await self._execute_query(
                filters=query_filters,
                skip=skip,
                limit=page_size,
                sort_by="date",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching public holidays: {e}")
            return []
    
    # Analytics Repository Implementation
    async def get_holiday_statistics(self, organisation_id: str = "default",
                                    year: Optional[int] = None) -> Dict[str, Any]:
        """Get public holiday statistics."""
        try:
            filters = {"is_active": True}
            
            if year:
                filters["year"] = year
            
            # Use aggregation pipeline for statistics
            pipeline = [
                {"$match": filters},
                {
                    "$group": {
                        "_id": None,
                        "total_holidays": {"$sum": 1},
                        "holidays_by_month": {
                            "$push": {
                                "month": "$month",
                                "name": "$name",
                                "date": "$date"
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_holidays": 1,
                        "holidays_by_month": 1
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            if results:
                stats = results[0]
                
                # Group holidays by month
                monthly_counts = {}
                for holiday in stats.get("holidays_by_month", []):
                    month = holiday["month"]
                    if month not in monthly_counts:
                        monthly_counts[month] = 0
                    monthly_counts[month] += 1
                
                return {
                    "total_holidays": stats.get("total_holidays", 0),
                    "year": year,
                    "monthly_distribution": monthly_counts,
                    "holidays_by_month": stats.get("holidays_by_month", [])
                }
            else:
                return {
                    "total_holidays": 0,
                    "year": year,
                    "monthly_distribution": {},
                    "holidays_by_month": []
                }
                
        except Exception as e:
            logger.error(f"Error getting holiday statistics: {e}")
            return {}
    
    async def get_upcoming_holidays(self, days_ahead: int = 30,
                                   organisation_id: str = "default") -> List[PublicHoliday]:
        """Get upcoming holidays within specified days."""
        try:
            from datetime import timedelta
            
            today = date.today()
            end_date = today + timedelta(days=days_ahead)
            
            return await self.get_by_date_range(today, end_date, organisation_id)
            
        except Exception as e:
            logger.error(f"Error getting upcoming holidays: {e}")
            return []
    
    # Legacy compatibility methods
    async def get_all_holidays_legacy(self, hostname: str) -> List[PublicHolidayModel]:
        """
        Legacy compatibility for get_all_holidays() function.
        
        Args:
            hostname: Organisation hostname
            
        Returns:
            List of PublicHoliday models
        """
        try:
            holidays = await self.get_all_active(hostname)
            
            # Convert to legacy model format
            legacy_holidays = []
            for holiday in holidays:
                legacy_data = {
                    "holiday_id": getattr(holiday, 'holiday_id', ''),
                    "name": getattr(holiday, 'name', ''),
                    "date": getattr(holiday, 'date', None),
                    "description": getattr(holiday, 'description', ''),
                    "is_active": getattr(holiday, 'is_active', True),
                    "created_by": getattr(holiday, 'created_by', ''),
                    "created_at": getattr(holiday, 'created_at', None),
                    "day": getattr(holiday, 'day', None),
                    "month": getattr(holiday, 'month', None),
                    "year": getattr(holiday, 'year', None)
                }
                legacy_holidays.append(PublicHolidayModel(**legacy_data))
            
            return legacy_holidays
            
        except Exception as e:
            logger.error(f"Error getting all holidays (legacy): {e}")
            return []
    
    async def create_holiday_legacy(self, holiday: PublicHolidayModel, employee_id: str, hostname: str) -> str:
        """
        Legacy compatibility for create_holiday() function.
        
        Args:
            holiday: PublicHoliday model
            employee_id: Employee ID creating the holiday
            hostname: Organisation hostname
            
        Returns:
            Holiday ID
        """
        try:
            # Convert model to entity
            holiday_data = holiday.dict(exclude={"id"})
            holiday_data["created_by"] = employee_id
            
            # Create entity
            holiday_entity = PublicHoliday(**holiday_data)
            
            # Save using new method
            saved_holiday = await self.save(holiday_entity)
            
            return getattr(saved_holiday, 'holiday_id', '')
            
        except Exception as e:
            logger.error(f"Error creating holiday (legacy): {e}")
            raise
    
    async def get_holiday_by_month_legacy(self, month: int, year: int, hostname: str) -> List[PublicHolidayModel]:
        """
        Legacy compatibility for get_holiday_by_month() function.
        """
        try:
            holidays = await self.get_by_month(month, year, hostname)
            
            # Convert to legacy model format
            legacy_holidays = []
            for holiday in holidays:
                legacy_data = {
                    "holiday_id": getattr(holiday, 'holiday_id', ''),
                    "name": getattr(holiday, 'name', ''),
                    "date": getattr(holiday, 'date', None),
                    "description": getattr(holiday, 'description', ''),
                    "is_active": getattr(holiday, 'is_active', True),
                    "created_by": getattr(holiday, 'created_by', ''),
                    "created_at": getattr(holiday, 'created_at', None),
                    "day": getattr(holiday, 'day', None),
                    "month": getattr(holiday, 'month', None),
                    "year": getattr(holiday, 'year', None)
                }
                legacy_holidays.append(PublicHolidayModel(**legacy_data))
            
            return legacy_holidays
            
        except Exception as e:
            logger.error(f"Error getting holidays by month (legacy): {e}")
            return []
    
    async def get_holiday_by_date_str_legacy(self, date_str: str, hostname: str) -> Optional[PublicHolidayModel]:
        """
        Legacy compatibility for get_holiday_by_date_str() function.
        """
        try:
            holiday = await self.get_by_date(date_str, hostname)
            
            if holiday:
                legacy_data = {
                    "holiday_id": getattr(holiday, 'holiday_id', ''),
                    "name": getattr(holiday, 'name', ''),
                    "date": getattr(holiday, 'date', None),
                    "description": getattr(holiday, 'description', ''),
                    "is_active": getattr(holiday, 'is_active', True),
                    "created_by": getattr(holiday, 'created_by', ''),
                    "created_at": getattr(holiday, 'created_at', None),
                    "day": getattr(holiday, 'day', None),
                    "month": getattr(holiday, 'month', None),
                    "year": getattr(holiday, 'year', None)
                }
                return PublicHolidayModel(**legacy_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting holiday by date (legacy): {e}")
            return None
    
    async def update_holiday_legacy(self, holiday_id: str, holiday: PublicHolidayModel, 
                                   employee_id: str, hostname: str) -> bool:
        """
        Legacy compatibility for update_holiday() function.
        """
        try:
            update_data = holiday.dict(exclude={"id"})
            update_data["created_by"] = employee_id
            
            return await self.update(holiday_id, update_data, hostname)
            
        except Exception as e:
            logger.error(f"Error updating holiday (legacy): {e}")
            return False
    
    async def import_holidays_legacy(self, holiday_data_list: List[Dict[str, Any]], 
                                    employee_id: str, hostname: str) -> int:
        """
        Legacy compatibility for import_holidays() function.
        """
        return await self.bulk_import(holiday_data_list, employee_id, hostname)
    
    async def delete_holiday_legacy(self, holiday_id: str, hostname: str) -> bool:
        """
        Legacy compatibility for delete_holiday() function.
        """
        return await self.delete(holiday_id, hostname)

    # Missing Abstract Methods Implementation
    
    # PublicHolidayCommandRepository Methods
    async def save_batch(self, holidays: List[PublicHoliday]) -> Dict[str, bool]:
        """Save multiple holidays in batch."""
        try:
            results = {}
            for holiday in holidays:
                try:
                    saved_holiday = await self.save(holiday)
                    holiday_id = getattr(holiday, 'holiday_id', str(getattr(saved_holiday, 'id', '')))
                    results[holiday_id] = True
                except Exception as e:
                    holiday_id = getattr(holiday, 'holiday_id', 'unknown')
                    logger.error(f"Error saving holiday {holiday_id}: {e}")
                    results[holiday_id] = False
            
            return results
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            return {}

    # PublicHolidayQueryRepository Methods
    async def get_all(self, include_inactive: bool = False) -> List[PublicHoliday]:
        """Get all public holidays."""
        try:
            organisation_id = "default"
            filters = {} if include_inactive else {"is_active": True}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting all holidays: {e}")
            return []

    async def get_by_category(self, category: str, include_inactive: bool = False) -> List[PublicHoliday]:
        """Get public holidays by category."""
        try:
            organisation_id = "default"
            filters = {"category": category}
            if not include_inactive:
                filters["is_active"] = True
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting holidays by category {category}: {e}")
            return []

    async def search_holidays(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        observance: Optional[str] = None,
        year: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[PublicHoliday]:
        """Search holidays with multiple filters."""
        try:
            organisation_id = "default"
            filters = {}
            
            if search_term:
                filters["$or"] = [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"description": {"$regex": search_term, "$options": "i"}}
                ]
            
            if category:
                filters["category"] = category
            
            if observance:
                filters["observance"] = observance
            
            if year:
                filters["year"] = year
            
            if is_active is not None:
                filters["is_active"] = is_active
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error searching holidays: {e}")
            return []

    async def exists_on_date(self, holiday_date: date) -> bool:
        """Check if any active holiday exists on a specific date."""
        try:
            organisation_id = "default"
            
            count = await self._count_documents(
                filters={"date": holiday_date, "is_active": True},
                organisation_id=organisation_id
            )
            
            return count > 0
        except Exception as e:
            logger.error(f"Error checking holiday existence on {holiday_date}: {e}")
            return False

    async def get_conflicts(self, holiday: PublicHoliday) -> List[PublicHoliday]:
        """Get holidays that conflict with the given holiday."""
        try:
            organisation_id = "default"
            holiday_date = getattr(holiday, 'date', None)
            holiday_id = getattr(holiday, 'holiday_id', None)
            
            if not holiday_date:
                return []
            
            filters = {"date": holiday_date, "is_active": True}
            if holiday_id:
                filters["holiday_id"] = {"$ne": holiday_id}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting conflicts: {e}")
            return []

    async def count_active(self) -> int:
        """Count active public holidays."""
        try:
            return await self._count_documents(
                filters={"is_active": True},
                organisation_id="default"
            )
        except Exception as e:
            logger.error(f"Error counting active holidays: {e}")
            return 0

    async def count_by_category(self, category: str) -> int:
        """Count holidays by category."""
        try:
            return await self._count_documents(
                filters={"category": category, "is_active": True},
                organisation_id="default"
            )
        except Exception as e:
            logger.error(f"Error counting holidays by category {category}: {e}")
            return 0

    # PublicHolidayAnalyticsRepository Methods
    async def get_category_distribution(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get distribution of holidays by category."""
        try:
            organisation_id = "default"
            collection = self._get_collection(organisation_id)
            
            match_filter = {"is_active": True}
            if year:
                match_filter["year"] = year
            
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1},
                        "holidays": {"$push": {"name": "$name", "date": "$date"}}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            return [
                {
                    "category": doc["_id"] or "uncategorized",
                    "count": doc["count"],
                    "holidays": doc["holidays"]
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error getting category distribution: {e}")
            return []

    async def get_monthly_distribution(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get distribution of holidays by month."""
        try:
            organisation_id = "default"
            match_filter = {"is_active": True}
            if year:
                match_filter["year"] = year
            
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": "$month",
                        "count": {"$sum": 1},
                        "holidays": {"$push": {"name": "$name", "date": "$date", "category": "$category"}}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            month_names = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            
            return [
                {
                    "month": doc["_id"],
                    "month_name": month_names.get(doc["_id"], "Unknown"),
                    "count": doc["count"],
                    "holidays": doc["holidays"]
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error getting monthly distribution: {e}")
            return []

    async def get_observance_analysis(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get analysis of holiday observance types."""
        try:
            organisation_id = "default"
            match_filter = {"is_active": True}
            if year:
                match_filter["year"] = year
            
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": "$observance",
                        "count": {"$sum": 1},
                        "holidays": {"$push": {"name": "$name", "date": "$date", "category": "$category"}}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            return [
                {
                    "observance": doc["_id"] or "standard",
                    "count": doc["count"],
                    "holidays": doc["holidays"]
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error getting observance analysis: {e}")
            return []

    async def get_holiday_trends(self, years: int = 5) -> List[Dict[str, Any]]:
        """Get holiday trends over multiple years."""
        try:
            organisation_id = "default"
            current_year = datetime.now().year
            start_year = current_year - years + 1
            
            pipeline = [
                {
                    "$match": {
                        "is_active": True,
                        "year": {"$gte": start_year, "$lte": current_year}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": "$year",
                            "category": "$category"
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id.year": 1, "_id.category": 1}}
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            # Group by year
            yearly_trends = {}
            for doc in results:
                year = doc["_id"]["year"]
                category = doc["_id"]["category"] or "uncategorized"
                count = doc["count"]
                
                if year not in yearly_trends:
                    yearly_trends[year] = {"year": year, "total": 0, "by_category": {}}
                
                yearly_trends[year]["by_category"][category] = count
                yearly_trends[year]["total"] += count
            
            return list(yearly_trends.values())
        except Exception as e:
            logger.error(f"Error getting holiday trends: {e}")
            return []

    async def get_weekend_analysis(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get weekend analysis of holidays."""
        try:
            organisation_id = "default"
            collection = self._get_collection(organisation_id)
            
            match_filter = {"is_active": True}
            if year:
                match_filter["year"] = year
            
            pipeline = [
                {"$match": match_filter},
                {
                    "$addFields": {
                        "day_of_week": {"$dayOfWeek": "$date"}  # 1=Sunday, 7=Saturday
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_holidays": {"$sum": 1},
                        "weekend_holidays": {
                            "$sum": {"$cond": [{"$in": ["$day_of_week", [1, 7]]}, 1, 0]}
                        },
                        "weekday_holidays": {
                            "$sum": {"$cond": [{"$not": {"$in": ["$day_of_week", [1, 7]]}}, 1, 0]}
                        }
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            if results:
                stats = results[0]
                total = stats.get("total_holidays", 0)
                weekend = stats.get("weekend_holidays", 0)
                weekday = stats.get("weekday_holidays", 0)
                
                return {
                    "total_holidays": total,
                    "weekend_holidays": weekend,
                    "weekday_holidays": weekday,
                    "weekend_percentage": round((weekend / total * 100) if total > 0 else 0, 2),
                    "weekday_percentage": round((weekday / total * 100) if total > 0 else 0, 2)
                }
            
            return {"total_holidays": 0, "weekend_holidays": 0, "weekday_holidays": 0, "weekend_percentage": 0, "weekday_percentage": 0}
        except Exception as e:
            logger.error(f"Error getting weekend analysis: {e}")
            return {}

    async def get_long_weekend_opportunities(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get long weekend opportunities."""
        try:
            year = year or datetime.now().year
            holidays = await self.get_by_year(year, "default")
            
            long_weekends = []
            
            for holiday in holidays:
                holiday_date = getattr(holiday, 'date', None)
                if not holiday_date:
                    continue
                
                # Check if holiday is on Friday or Monday
                day_of_week = holiday_date.weekday()  # 0=Monday, 6=Sunday
                
                if day_of_week == 4:  # Friday
                    long_weekends.append({
                        "type": "long_weekend",
                        "holiday_name": getattr(holiday, 'name', ''),
                        "holiday_date": holiday_date.isoformat(),
                        "pattern": "Friday holiday + weekend",
                        "total_days": 3,
                        "recommendation": "Take Thursday off for 4-day weekend"
                    })
                elif day_of_week == 0:  # Monday
                    long_weekends.append({
                        "type": "long_weekend",
                        "holiday_name": getattr(holiday, 'name', ''),
                        "holiday_date": holiday_date.isoformat(),
                        "pattern": "Weekend + Monday holiday",
                        "total_days": 3,
                        "recommendation": "Take Tuesday off for 4-day weekend"
                    })
            
            return long_weekends
        except Exception as e:
            logger.error(f"Error getting long weekend opportunities: {e}")
            return []

    async def get_holiday_calendar_summary(self, year: int, month: Optional[int] = None) -> Dict[str, Any]:
        """Get holiday calendar summary."""
        try:
            organisation_id = "default"
            filters = {"year": year, "is_active": True}
            
            if month:
                filters["month"] = month
            
            holidays = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            # Group by month if year-wide summary
            if not month:
                monthly_summary = {}
                for holiday in holidays:
                    h_month = holiday.get("month")
                    if h_month not in monthly_summary:
                        monthly_summary[h_month] = []
                    monthly_summary[h_month].append({
                        "name": holiday.get("name"),
                        "date": holiday.get("date"),
                        "category": holiday.get("category"),
                        "day_of_week": holiday.get("date").strftime("%A") if holiday.get("date") else None
                    })
                
                return {
                    "year": year,
                    "total_holidays": len(holidays),
                    "monthly_breakdown": monthly_summary,
                    "summary_type": "yearly"
                }
            else:
                return {
                    "year": year,
                    "month": month,
                    "total_holidays": len(holidays),
                    "holidays": [
                        {
                            "name": holiday.get("name"),
                            "date": holiday.get("date"),
                            "category": holiday.get("category"),
                            "day_of_week": holiday.get("date").strftime("%A") if holiday.get("date") else None
                        }
                        for holiday in holidays
                    ],
                    "summary_type": "monthly"
                }
        except Exception as e:
            logger.error(f"Error getting calendar summary: {e}")
            return {}

    async def get_compliance_report(self) -> Dict[str, Any]:
        """Get compliance report."""
        try:
            organisation_id = "default"
            
            # Get all holidays
            all_holidays = await self.get_all(include_inactive=True)
            active_holidays = [h for h in all_holidays if getattr(h, 'is_active', True)]
            
            # Check for potential issues
            issues = []
            warnings = []
            
            # Check for holidays without proper categories
            uncategorized = [h for h in active_holidays if not getattr(h, 'category', None)]
            if uncategorized:
                issues.append(f"{len(uncategorized)} holidays without category")
            
            # Check for duplicate dates
            date_counts = {}
            for holiday in active_holidays:
                h_date = getattr(holiday, 'date', None)
                if h_date:
                    date_key = h_date.isoformat()
                    date_counts[date_key] = date_counts.get(date_key, 0) + 1
            
            duplicates = {date: count for date, count in date_counts.items() if count > 1}
            if duplicates:
                warnings.append(f"Duplicate holidays on {len(duplicates)} dates")
            
            # Check for holidays without descriptions
            no_description = [h for h in active_holidays if not getattr(h, 'description', None)]
            if no_description:
                warnings.append(f"{len(no_description)} holidays without description")
            
            compliance_score = 100
            if issues:
                compliance_score -= len(issues) * 20
            if warnings:
                compliance_score -= len(warnings) * 10
            
            compliance_score = max(0, compliance_score)
            
            return {
                "total_holidays": len(all_holidays),
                "active_holidays": len(active_holidays),
                "inactive_holidays": len(all_holidays) - len(active_holidays),
                "compliance_score": compliance_score,
                "issues": issues,
                "warnings": warnings,
                "recommendations": [
                    "Add categories to uncategorized holidays",
                    "Resolve duplicate holiday dates",
                    "Add descriptions to holidays without them"
                ] if (issues or warnings) else ["All holidays are compliant"],
                "checked_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting compliance report: {e}")
            return {}

    async def get_usage_metrics(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get usage metrics."""
        try:
            # This is a basic implementation - in a real system, you'd track actual usage
            organisation_id = "default"
            
            if not from_date:
                from_date = datetime.now().replace(month=1, day=1)  # Start of year
            if not to_date:
                to_date = datetime.now()
            
            from_date_only = from_date.date()
            to_date_only = to_date.date()
            
            holidays_in_period = await self.get_by_date_range(from_date_only, to_date_only, "default")
            
            metrics = []
            for holiday in holidays_in_period:
                h_date = getattr(holiday, 'date', None)
                if h_date and from_date_only <= h_date <= to_date_only:
                    # Simulate usage metrics (in real system, this would come from actual usage data)
                    metrics.append({
                        "holiday_id": getattr(holiday, 'holiday_id', ''),
                        "holiday_name": getattr(holiday, 'name', ''),
                        "date": h_date.isoformat(),
                        "category": getattr(holiday, 'category', 'general'),
                        "views": 0,  # Would track actual views
                        "mentions": 0,  # Would track mentions in other systems
                        "calendar_exports": 0,  # Would track export usage
                        "last_accessed": None  # Would track last access
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting usage metrics: {e}")
            return []

    # PublicHolidayCalendarRepository Methods
    async def generate_yearly_calendar(
        self,
        year: int,
        include_weekends: bool = True,
        include_optional: bool = True
    ) -> Dict[str, Any]:
        """Generate yearly calendar."""
        try:
            holidays = await self.get_by_year(year, "default")
            
            # Filter optional holidays if requested
            if not include_optional:
                holidays = [h for h in holidays if getattr(h, 'is_optional', False) == False]
            
            monthly_calendar = {}
            
            for month in range(1, 13):
                month_holidays = [h for h in holidays if getattr(h, 'date', None) and getattr(h, 'date').month == month]
                
                monthly_calendar[month] = {
                    "month": month,
                    "month_name": ["", "January", "February", "March", "April", "May", "June",
                                  "July", "August", "September", "October", "November", "December"][month],
                    "holiday_count": len(month_holidays),
                    "holidays": [
                        {
                            "name": getattr(h, 'name', ''),
                            "date": getattr(h, 'date').isoformat() if getattr(h, 'date') else None,
                            "category": getattr(h, 'category', ''),
                            "is_optional": getattr(h, 'is_optional', False)
                        }
                        for h in month_holidays
                    ]
                }
            
            return {
                "year": year,
                "total_holidays": len(holidays),
                "include_weekends": include_weekends,
                "include_optional": include_optional,
                "monthly_calendar": monthly_calendar,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating yearly calendar: {e}")
            return {}

    async def generate_monthly_calendar(
        self,
        year: int,
        month: int,
        include_weekends: bool = True,
        include_optional: bool = True
    ) -> Dict[str, Any]:
        """Generate monthly calendar."""
        try:
            holidays = await self.get_by_month(month, year, "default")
            
            # Filter optional holidays if requested
            if not include_optional:
                holidays = [h for h in holidays if getattr(h, 'is_optional', False) == False]
            
            calendar_data = {
                "year": year,
                "month": month,
                "month_name": ["", "January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"][month],
                "holiday_count": len(holidays),
                "include_weekends": include_weekends,
                "include_optional": include_optional,
                "holidays": [
                    {
                        "name": getattr(h, 'name', ''),
                        "date": getattr(h, 'date').isoformat() if getattr(h, 'date') else None,
                        "day": getattr(h, 'date').day if getattr(h, 'date') else None,
                        "day_of_week": getattr(h, 'date').strftime("%A") if getattr(h, 'date') else None,
                        "category": getattr(h, 'category', ''),
                        "description": getattr(h, 'description', ''),
                        "is_optional": getattr(h, 'is_optional', False)
                    }
                    for h in holidays
                ],
                "generated_at": datetime.now().isoformat()
            }
            
            return calendar_data
        except Exception as e:
            logger.error(f"Error generating monthly calendar: {e}")
            return {}

    async def get_working_days_count(
        self,
        start_date: date,
        end_date: date,
        exclude_weekends: bool = True
    ) -> int:
        """Get working days count between dates."""
        try:
            from datetime import timedelta
            
            # Get holidays in the date range
            holidays = await self.get_by_date_range(start_date, end_date, "default")
            holiday_dates = {getattr(h, 'date') for h in holidays if getattr(h, 'date')}
            
            working_days = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends if requested
                if exclude_weekends and current_date.weekday() >= 5:  # Saturday=5, Sunday=6
                    current_date += timedelta(days=1)
                    continue
                
                # Skip holidays
                if current_date not in holiday_dates:
                    working_days += 1
                
                current_date += timedelta(days=1)
            
            return working_days
        except Exception as e:
            logger.error(f"Error counting working days: {e}")
            return 0

    async def get_next_working_day(
        self,
        from_date: date,
        exclude_weekends: bool = True
    ) -> date:
        """Get next working day from given date."""
        try:
            from datetime import timedelta
            
            current_date = from_date + timedelta(days=1)
            
            # Get holidays for the next month to check against
            end_check_date = current_date + timedelta(days=60)  # Check next 60 days
            holidays = await self.get_by_date_range(current_date, end_check_date, "default")
            holiday_dates = {getattr(h, 'date') for h in holidays if getattr(h, 'date')}
            
            while True:
                # Skip weekends if requested
                if exclude_weekends and current_date.weekday() >= 5:  # Saturday=5, Sunday=6
                    current_date += timedelta(days=1)
                    continue
                
                # Skip holidays
                if current_date not in holiday_dates:
                    return current_date
                
                current_date += timedelta(days=1)
                
                # Safety check to avoid infinite loop
                if current_date > from_date + timedelta(days=365):
                    break
            
            return current_date
        except Exception as e:
            logger.error(f"Error getting next working day: {e}")
            return from_date

    async def get_previous_working_day(
        self,
        from_date: date,
        exclude_weekends: bool = True
    ) -> date:
        """Get previous working day from given date."""
        try:
            from datetime import timedelta
            
            current_date = from_date - timedelta(days=1)
            
            # Get holidays for the previous month to check against
            start_check_date = current_date - timedelta(days=60)  # Check previous 60 days
            holidays = await self.get_by_date_range(start_check_date, current_date, "default")
            holiday_dates = {getattr(h, 'date') for h in holidays if getattr(h, 'date')}
            
            while True:
                # Skip weekends if requested
                if exclude_weekends and current_date.weekday() >= 5:  # Saturday=5, Sunday=6
                    current_date -= timedelta(days=1)
                    continue
                
                # Skip holidays
                if current_date not in holiday_dates:
                    return current_date
                
                current_date -= timedelta(days=1)
                
                # Safety check to avoid infinite loop
                if current_date < from_date - timedelta(days=365):
                    break
            
            return current_date
        except Exception as e:
            logger.error(f"Error getting previous working day: {e}")
            return from_date

    async def is_working_day(
        self,
        check_date: date,
        exclude_weekends: bool = True
    ) -> bool:
        """Check if given date is a working day."""
        try:
            # Check weekend
            if exclude_weekends and check_date.weekday() >= 5:  # Saturday=5, Sunday=6
                return False
            
            # Check if it's a holiday
            is_holiday = await self.exists_on_date(check_date)
            return not is_holiday
        except Exception as e:
            logger.error(f"Error checking if working day: {e}")
            return True  # Default to working day on error

    async def get_holiday_bridges(self, year: int) -> List[Dict[str, Any]]:
        """Get holiday bridges (opportunities for extended weekends)."""
        try:
            from datetime import timedelta
            
            holidays = await self.get_by_year(year, "default")
            bridges = []
            
            for holiday in holidays:
                h_date = getattr(holiday, 'date', None)
                if not h_date:
                    continue
                
                day_of_week = h_date.weekday()  # 0=Monday, 6=Sunday
                
                # Check for bridge opportunities
                if day_of_week == 1:  # Tuesday
                    # Monday is a bridge day
                    bridge_date = h_date - timedelta(days=1)
                    if not await self.exists_on_date(bridge_date):
                        bridges.append({
                            "holiday_name": getattr(holiday, 'name', ''),
                            "holiday_date": h_date.isoformat(),
                            "bridge_date": bridge_date.isoformat(),
                            "bridge_type": "Monday bridge",
                            "total_days_off": 4,  # Sat, Sun, Mon(bridge), Tue(holiday)
                            "recommendation": "Take Monday off for 4-day weekend"
                        })
                
                elif day_of_week == 3:  # Thursday
                    # Friday is a bridge day
                    bridge_date = h_date + timedelta(days=1)
                    if not await self.exists_on_date(bridge_date):
                        bridges.append({
                            "holiday_name": getattr(holiday, 'name', ''),
                            "holiday_date": h_date.isoformat(),
                            "bridge_date": bridge_date.isoformat(),
                            "bridge_type": "Friday bridge",
                            "total_days_off": 4,  # Thu(holiday), Fri(bridge), Sat, Sun
                            "recommendation": "Take Friday off for 4-day weekend"
                        })
            
            return bridges
        except Exception as e:
            logger.error(f"Error getting holiday bridges: {e}")
            return [] 