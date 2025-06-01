"""
SOLID Activity Tracker Repository Implementation

This module implements the activity tracker repository following SOLID principles:
- Single Responsibility: Handles only activity tracking data operations
- Open/Closed: Extensible through interfaces without modification
- Liskov Substitution: Implements consistent interfaces
- Interface Segregation: Focused interfaces for specific operations
- Dependency Inversion: Depends on abstractions, not concretions

Author: System Architecture Team
Date: 2024
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.infrastructure.database.database_connector import DatabaseConnector
from app.infrastructure.repositories.base_repository import BaseRepository
from app.application.interfaces.repositories.activity_tracker_repository_interface import (
    ActivityTrackerCommandRepository,
    ActivityTrackerQueryRepository,
    ActivityTrackerAnalyticsRepository
)
from app.domain.entities.activity_tracker import ActivityTracker
from app.application.dto.activity_tracker_dto import (
    ActivityTrackerCreateDTO,
    ActivityTrackerUpdateDTO,
    ActivityTrackerResponseDTO
)

logger = logging.getLogger(__name__)

class SolidActivityTrackerRepository(
    BaseRepository,
    ActivityTrackerCommandRepository,
    ActivityTrackerQueryRepository,
    ActivityTrackerAnalyticsRepository
):
    """
    SOLID-compliant activity tracker repository implementation.
    
    Provides comprehensive activity tracking with:
    - CRUD operations
    - Date-based queries
    - Employee activity analytics
    - Performance optimization
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Initialize the repository with database connector.
        
        Args:
            db_connector: Database connector following DIP
        """
        super().__init__(db_connector, "activity_tracker")
        self.logger = logging.getLogger(__name__)
    
    # Command Repository Implementation
    
    async def create_activity_tracker(
        self, 
        activity_data: ActivityTrackerCreateDTO, 
        company_id: str
    ) -> str:
        """
        Create a new activity tracker entry.
        
        Args:
            activity_data: Activity tracker creation data
            company_id: Company identifier
            
        Returns:
            str: Created activity tracker ID
            
        Raises:
            ValueError: If data validation fails
            RuntimeError: If creation fails
        """
        try:
            self.logger.info(f"Creating activity tracker for employee {activity_data.employee_id}")
            
            # Validate required fields
            if not activity_data.employee_id:
                raise ValueError("Employee ID is required")
            if not activity_data.date:
                raise ValueError("Date is required")
            
            # Check for duplicate entry
            existing = await self.get_activity_tracker_by_employee_id_and_date(
                activity_data.employee_id, 
                activity_data.date, 
                company_id
            )
            if existing:
                raise ValueError(f"Activity tracker already exists for employee {activity_data.employee_id} on {activity_data.date}")
            
            # Prepare document
            doc = activity_data.model_dump()
            doc.update({
                "activity_tracker_id": str(ObjectId()),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            # Insert document
            collection = await self._get_collection(company_id)
            result = await collection.insert_one(doc)
            
            self.logger.info(f"Created activity tracker {doc['activity_tracker_id']}")
            return doc["activity_tracker_id"]
            
        except Exception as e:
            self.logger.error(f"Error creating activity tracker: {str(e)}")
            raise RuntimeError(f"Failed to create activity tracker: {str(e)}")
    
    async def update_activity_tracker(
        self, 
        activity_tracker_id: str, 
        update_data: ActivityTrackerUpdateDTO, 
        company_id: str
    ) -> bool:
        """
        Update an existing activity tracker entry.
        
        Args:
            activity_tracker_id: Activity tracker identifier
            update_data: Update data
            company_id: Company identifier
            
        Returns:
            bool: True if update successful
            
        Raises:
            ValueError: If activity tracker not found
            RuntimeError: If update fails
        """
        try:
            self.logger.info(f"Updating activity tracker {activity_tracker_id}")
            
            # Check if activity tracker exists
            existing = await self.get_activity_tracker_by_id(activity_tracker_id, company_id)
            if not existing:
                raise ValueError(f"Activity tracker {activity_tracker_id} not found")
            
            # Prepare update document
            update_doc = update_data.model_dump(exclude_unset=True)
            update_doc["updated_at"] = datetime.now()
            
            # Update document
            collection = await self._get_collection(company_id)
            result = await collection.update_one(
                {"activity_tracker_id": activity_tracker_id},
                {"$set": update_doc}
            )
            
            if result.modified_count == 0:
                raise RuntimeError("No documents were updated")
            
            self.logger.info(f"Updated activity tracker {activity_tracker_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating activity tracker: {str(e)}")
            raise RuntimeError(f"Failed to update activity tracker: {str(e)}")
    
    async def delete_activity_tracker(self, activity_tracker_id: str, company_id: str) -> bool:
        """
        Delete an activity tracker entry.
        
        Args:
            activity_tracker_id: Activity tracker identifier
            company_id: Company identifier
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            ValueError: If activity tracker not found
            RuntimeError: If deletion fails
        """
        try:
            self.logger.info(f"Deleting activity tracker {activity_tracker_id}")
            
            # Check if activity tracker exists
            existing = await self.get_activity_tracker_by_id(activity_tracker_id, company_id)
            if not existing:
                raise ValueError(f"Activity tracker {activity_tracker_id} not found")
            
            # Delete document
            collection = await self._get_collection(company_id)
            result = await collection.delete_one({"activity_tracker_id": activity_tracker_id})
            
            if result.deleted_count == 0:
                raise RuntimeError("No documents were deleted")
            
            self.logger.info(f"Deleted activity tracker {activity_tracker_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting activity tracker: {str(e)}")
            raise RuntimeError(f"Failed to delete activity tracker: {str(e)}")
    
    # Query Repository Implementation
    
    async def get_activity_tracker_by_id(
        self, 
        activity_tracker_id: str, 
        company_id: str
    ) -> Optional[ActivityTrackerResponseDTO]:
        """
        Get activity tracker by ID.
        
        Args:
            activity_tracker_id: Activity tracker identifier
            company_id: Company identifier
            
        Returns:
            Optional[ActivityTrackerResponseDTO]: Activity tracker if found
        """
        try:
            collection = await self._get_collection(company_id)
            doc = await collection.find_one({"activity_tracker_id": activity_tracker_id})
            
            if doc:
                return ActivityTrackerResponseDTO(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting activity tracker by ID: {str(e)}")
            raise RuntimeError(f"Failed to get activity tracker: {str(e)}")
    
    async def get_activity_tracker_by_employee_id(
        self, 
        employee_id: str, 
        company_id: str
    ) -> List[ActivityTrackerResponseDTO]:
        """
        Get all activity trackers for an employee.
        
        Args:
            employee_id: Employee identifier
            company_id: Company identifier
            
        Returns:
            List[ActivityTrackerResponseDTO]: List of activity trackers
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({"employee_id": employee_id}).sort("date", -1)
            
            trackers = []
            async for doc in cursor:
                trackers.append(ActivityTrackerResponseDTO(**doc))
            
            return trackers
            
        except Exception as e:
            self.logger.error(f"Error getting activity trackers by employee ID: {str(e)}")
            raise RuntimeError(f"Failed to get activity trackers: {str(e)}")
    
    async def get_activity_tracker_by_date(
        self, 
        target_date: date, 
        company_id: str
    ) -> List[ActivityTrackerResponseDTO]:
        """
        Get all activity trackers for a specific date.
        
        Args:
            target_date: Target date
            company_id: Company identifier
            
        Returns:
            List[ActivityTrackerResponseDTO]: List of activity trackers
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({"date": target_date}).sort("employee_id", 1)
            
            trackers = []
            async for doc in cursor:
                trackers.append(ActivityTrackerResponseDTO(**doc))
            
            return trackers
            
        except Exception as e:
            self.logger.error(f"Error getting activity trackers by date: {str(e)}")
            raise RuntimeError(f"Failed to get activity trackers: {str(e)}")
    
    async def get_activity_tracker_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        company_id: str
    ) -> List[ActivityTrackerResponseDTO]:
        """
        Get activity trackers within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            company_id: Company identifier
            
        Returns:
            List[ActivityTrackerResponseDTO]: List of activity trackers
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({
                "date": {"$gte": start_date, "$lte": end_date}
            }).sort([("date", -1), ("employee_id", 1)])
            
            trackers = []
            async for doc in cursor:
                trackers.append(ActivityTrackerResponseDTO(**doc))
            
            return trackers
            
        except Exception as e:
            self.logger.error(f"Error getting activity trackers by date range: {str(e)}")
            raise RuntimeError(f"Failed to get activity trackers: {str(e)}")
    
    async def get_activity_tracker_by_employee_id_and_date(
        self, 
        employee_id: str, 
        target_date: date, 
        company_id: str
    ) -> Optional[ActivityTrackerResponseDTO]:
        """
        Get activity tracker for specific employee and date.
        
        Args:
            employee_id: Employee identifier
            target_date: Target date
            company_id: Company identifier
            
        Returns:
            Optional[ActivityTrackerResponseDTO]: Activity tracker if found
        """
        try:
            collection = await self._get_collection(company_id)
            doc = await collection.find_one({
                "employee_id": employee_id,
                "date": target_date
            })
            
            if doc:
                return ActivityTrackerResponseDTO(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting activity tracker by employee and date: {str(e)}")
            raise RuntimeError(f"Failed to get activity tracker: {str(e)}")
    
    async def get_activity_tracker_by_employee_id_and_date_range(
        self, 
        employee_id: str, 
        start_date: date, 
        end_date: date, 
        company_id: str
    ) -> List[ActivityTrackerResponseDTO]:
        """
        Get activity trackers for employee within date range.
        
        Args:
            employee_id: Employee identifier
            start_date: Start date
            end_date: End date
            company_id: Company identifier
            
        Returns:
            List[ActivityTrackerResponseDTO]: List of activity trackers
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({
                "employee_id": employee_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }).sort("date", -1)
            
            trackers = []
            async for doc in cursor:
                trackers.append(ActivityTrackerResponseDTO(**doc))
            
            return trackers
            
        except Exception as e:
            self.logger.error(f"Error getting activity trackers by employee and date range: {str(e)}")
            raise RuntimeError(f"Failed to get activity trackers: {str(e)}")
    
    async def get_activity_tracker_by_activity_type(
        self, 
        activity_type: str, 
        company_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ActivityTrackerResponseDTO]:
        """
        Get activity trackers by activity type.
        
        Args:
            activity_type: Activity type
            company_id: Company identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List[ActivityTrackerResponseDTO]: List of activity trackers
        """
        try:
            collection = await self._get_collection(company_id)
            
            query = {"activity": activity_type}
            if start_date and end_date:
                query["date"] = {"$gte": start_date, "$lte": end_date}
            
            cursor = collection.find(query).sort([("date", -1), ("employee_id", 1)])
            
            trackers = []
            async for doc in cursor:
                trackers.append(ActivityTrackerResponseDTO(**doc))
            
            return trackers
            
        except Exception as e:
            self.logger.error(f"Error getting activity trackers by activity type: {str(e)}")
            raise RuntimeError(f"Failed to get activity trackers: {str(e)}")
    
    # Analytics Repository Implementation
    
    async def get_activity_statistics(
        self, 
        company_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get activity statistics.
        
        Args:
            company_id: Company identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict[str, Any]: Activity statistics
        """
        try:
            collection = await self._get_collection(company_id)
            
            match_stage = {}
            if start_date and end_date:
                match_stage["date"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_activities": {"$sum": 1},
                        "unique_employees": {"$addToSet": "$employee_id"},
                        "activity_types": {"$addToSet": "$activity"},
                        "avg_duration": {"$avg": "$duration"},
                        "total_duration": {"$sum": "$duration"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_activities": 1,
                        "unique_employees_count": {"$size": "$unique_employees"},
                        "activity_types_count": {"$size": "$activity_types"},
                        "avg_duration": {"$round": ["$avg_duration", 2]},
                        "total_duration": 1
                    }
                }
            ])
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if result:
                return result[0]
            
            return {
                "total_activities": 0,
                "unique_employees_count": 0,
                "activity_types_count": 0,
                "avg_duration": 0,
                "total_duration": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting activity statistics: {str(e)}")
            raise RuntimeError(f"Failed to get activity statistics: {str(e)}")
    
    async def get_employee_activity_summary(
        self, 
        employee_id: str, 
        company_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get activity summary for a specific employee.
        
        Args:
            employee_id: Employee identifier
            company_id: Company identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict[str, Any]: Employee activity summary
        """
        try:
            collection = await self._get_collection(company_id)
            
            match_stage = {"employee_id": employee_id}
            if start_date and end_date:
                match_stage["date"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": "$activity",
                        "count": {"$sum": 1},
                        "total_duration": {"$sum": "$duration"},
                        "avg_duration": {"$avg": "$duration"},
                        "dates": {"$addToSet": "$date"}
                    }
                },
                {
                    "$project": {
                        "activity_type": "$_id",
                        "count": 1,
                        "total_duration": 1,
                        "avg_duration": {"$round": ["$avg_duration", 2]},
                        "unique_dates": {"$size": "$dates"},
                        "_id": 0
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            # Get overall summary
            total_pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": None,
                        "total_activities": {"$sum": 1},
                        "total_duration": {"$sum": "$duration"},
                        "unique_dates": {"$addToSet": "$date"}
                    }
                }
            ]
            
            total_result = await collection.aggregate(total_pipeline).to_list(1)
            
            summary = {
                "employee_id": employee_id,
                "activity_breakdown": result,
                "total_activities": total_result[0]["total_activities"] if total_result else 0,
                "total_duration": total_result[0]["total_duration"] if total_result else 0,
                "active_days": len(total_result[0]["unique_dates"]) if total_result else 0
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting employee activity summary: {str(e)}")
            raise RuntimeError(f"Failed to get employee activity summary: {str(e)}")
    
    async def get_daily_activity_trends(
        self, 
        company_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Get daily activity trends.
        
        Args:
            company_id: Company identifier
            start_date: Start date
            end_date: End date
            
        Returns:
            Dict[str, Any]: Daily activity trends
        """
        try:
            collection = await self._get_collection(company_id)
            
            pipeline = [
                {
                    "$match": {
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$date",
                        "total_activities": {"$sum": 1},
                        "unique_employees": {"$addToSet": "$employee_id"},
                        "total_duration": {"$sum": "$duration"},
                        "activity_types": {"$addToSet": "$activity"}
                    }
                },
                {
                    "$project": {
                        "date": "$_id",
                        "total_activities": 1,
                        "unique_employees_count": {"$size": "$unique_employees"},
                        "total_duration": 1,
                        "activity_types_count": {"$size": "$activity_types"},
                        "_id": 0
                    }
                },
                {"$sort": {"date": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            return {
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "daily_trends": result
            }
            
        except Exception as e:
            self.logger.error(f"Error getting daily activity trends: {str(e)}")
            raise RuntimeError(f"Failed to get daily activity trends: {str(e)}")
    
    # Health Check Methods
    
    async def health_check(self, company_id: str) -> Dict[str, Any]:
        """
        Perform health check on the activity tracker repository.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            collection = await self._get_collection(company_id)
            
            # Test basic operations
            count = await collection.count_documents({})
            
            # Test index performance
            explain_result = await collection.find({"employee_id": "test"}).explain()
            
            return {
                "status": "healthy",
                "total_documents": count,
                "collection_name": self.collection_name,
                "indexes_used": len(explain_result.get("executionStats", {}).get("allPlansExecution", [])),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 