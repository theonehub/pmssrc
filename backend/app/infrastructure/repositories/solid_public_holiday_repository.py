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
    from domain.entities.public_holiday import PublicHoliday
    from domain.value_objects.holiday_id import HolidayId
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
    from application.interfaces.repositories.public_holiday_repository import (
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
    from application.dto.public_holiday_dto import (
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
    
    async def _ensure_indexes(self, organization_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organization_id)
            
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
            
            logger.info(f"Public holiday indexes ensured for organization: {organization_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring public holiday indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, holiday: PublicHoliday) -> PublicHoliday:
        """
        Save public holiday record.
        
        Replaces: create_holiday() function
        """
        try:
            # Get organization from holiday or use default
            organization_id = getattr(holiday, 'organization_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organization_id)
            
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
                existing = await self.get_by_id(document['holiday_id'], organization_id)
            
            if existing:
                # Update existing record
                filters = {"holiday_id": document['holiday_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organization_id=organization_id
                )
                if success:
                    return await self.get_by_id(document['holiday_id'], organization_id)
                else:
                    raise ValueError("Failed to update public holiday record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organization_id)
                # Return the saved document
                saved_doc = await self._get_collection(organization_id).find_one({"_id": document_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving public holiday: {e}")
            raise
    
    async def update(self, holiday_id: str, update_data: Dict[str, Any], 
                    organization_id: str) -> bool:
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
                organization_id=organization_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating public holiday {holiday_id}: {e}")
            return False
    
    async def delete(self, holiday_id: str, organization_id: str) -> bool:
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
            
            return await self.update(holiday_id, update_data, organization_id)
            
        except Exception as e:
            logger.error(f"Error deleting public holiday {holiday_id}: {e}")
            return False
    
    async def bulk_import(self, holiday_data_list: List[Dict[str, Any]], 
                         emp_id: str, organization_id: str) -> int:
        """
        Import multiple holidays from processed data.
        
        Replaces: import_holidays() function
        """
        try:
            # Ensure indexes
            await self._ensure_indexes(organization_id)
            
            collection = self._get_collection(organization_id)
            inserted_count = 0
            
            for holiday_data in holiday_data_list:
                try:
                    # Prepare document
                    document = {
                        "name": holiday_data['name'],
                        "description": holiday_data.get('description', ''),
                        "created_by": emp_id,
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
    async def get_by_id(self, holiday_id: str, organization_id: str = "default") -> Optional[PublicHoliday]:
        """Get public holiday record by ID."""
        try:
            filters = {"holiday_id": holiday_id}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving public holiday {holiday_id}: {e}")
            return None
    
    async def get_all_active(self, organization_id: str = "default") -> List[PublicHoliday]:
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all active holidays: {e}")
            return []
    
    async def get_by_month(self, month: int, year: int, 
                          organization_id: str = "default") -> List[PublicHoliday]:
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving holidays for {month}/{year}: {e}")
            return []
    
    async def get_by_date(self, target_date: Union[date, str], 
                         organization_id: str = "default") -> Optional[PublicHoliday]:
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
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving holiday by date {target_date}: {e}")
            return None
    
    async def get_by_date_range(self, start_date: date, end_date: date,
                               organization_id: str = "default") -> List[PublicHoliday]:
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving holidays by date range: {e}")
            return []
    
    async def get_by_year(self, year: int, organization_id: str = "default") -> List[PublicHoliday]:
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving holidays for year {year}: {e}")
            return []
    
    async def search(self, filters: PublicHolidaySearchFiltersDTO,
                    organization_id: str = "default") -> List[PublicHoliday]:
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching public holidays: {e}")
            return []
    
    # Analytics Repository Implementation
    async def get_holiday_statistics(self, organization_id: str = "default",
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
            
            results = await self._aggregate(pipeline, organization_id)
            
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
                                   organization_id: str = "default") -> List[PublicHoliday]:
        """Get upcoming holidays within specified days."""
        try:
            from datetime import timedelta
            
            today = date.today()
            end_date = today + timedelta(days=days_ahead)
            
            return await self.get_by_date_range(today, end_date, organization_id)
            
        except Exception as e:
            logger.error(f"Error getting upcoming holidays: {e}")
            return []
    
    # Legacy compatibility methods
    async def get_all_holidays_legacy(self, hostname: str) -> List[PublicHolidayModel]:
        """
        Legacy compatibility for get_all_holidays() function.
        
        Args:
            hostname: Organization hostname
            
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
    
    async def create_holiday_legacy(self, holiday: PublicHolidayModel, emp_id: str, hostname: str) -> str:
        """
        Legacy compatibility for create_holiday() function.
        
        Args:
            holiday: PublicHoliday model
            emp_id: Employee ID creating the holiday
            hostname: Organization hostname
            
        Returns:
            Holiday ID
        """
        try:
            # Convert model to entity
            holiday_data = holiday.dict(exclude={"id"})
            holiday_data["created_by"] = emp_id
            
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
                                   emp_id: str, hostname: str) -> bool:
        """
        Legacy compatibility for update_holiday() function.
        """
        try:
            update_data = holiday.dict(exclude={"id"})
            update_data["created_by"] = emp_id
            
            return await self.update(holiday_id, update_data, hostname)
            
        except Exception as e:
            logger.error(f"Error updating holiday (legacy): {e}")
            return False
    
    async def import_holidays_legacy(self, holiday_data_list: List[Dict[str, Any]], 
                                    emp_id: str, hostname: str) -> int:
        """
        Legacy compatibility for import_holidays() function.
        """
        return await self.bulk_import(holiday_data_list, emp_id, hostname)
    
    async def delete_holiday_legacy(self, holiday_id: str, hostname: str) -> bool:
        """
        Legacy compatibility for delete_holiday() function.
        """
        return await self.delete(holiday_id, hostname) 