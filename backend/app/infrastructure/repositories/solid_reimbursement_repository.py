"""
SOLID-Compliant Reimbursement Repository Implementation
Replaces the procedural reimbursement_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.reimbursement import Reimbursement
    from app.domain.value_objects.employee_id import EmployeeId
    from app.domain.value_objects.reimbursement_type import ReimbursementType
    from app.domain.value_objects.money import Money
    from models.reimbursements import ReimbursementRequestCreate
except ImportError:
    # Fallback classes for migration compatibility
    class Reimbursement:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class EmployeeId:
        def __init__(self, value: str):
            self.value = value
        def __str__(self):
            return self.value
    
    class ReimbursementType:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Money:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ReimbursementRequestCreate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# Import application interfaces
try:
    from app.application.interfaces.repositories.reimbursement_repository import (
        ReimbursementCommandRepository, ReimbursementQueryRepository,
        ReimbursementAnalyticsRepository, ReimbursementRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class ReimbursementCommandRepository(ABC):
        pass
    
    class ReimbursementQueryRepository(ABC):
        pass
    
    class ReimbursementAnalyticsRepository(ABC):
        pass
    
    class ReimbursementRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.reimbursement_dto import (
        ReimbursementSearchFiltersDTO, ReimbursementSummaryDTO,
        ReimbursementStatisticsDTO
    )
except ImportError:
    # Fallback DTOs
    class ReimbursementSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ReimbursementSummaryDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ReimbursementStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidReimbursementRepository(
    BaseRepository[Reimbursement],
    ReimbursementCommandRepository,
    ReimbursementQueryRepository,
    ReimbursementAnalyticsRepository,
    ReimbursementRepository
):
    """
    SOLID-compliant reimbursement repository implementation.
    
    Replaces the procedural reimbursement_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles reimbursement data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all reimbursement repository interfaces
    - Interface Segregation: Implements focused reimbursement repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize reimbursement repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "reimbursements")
        
    def _entity_to_document(self, reimbursement: Reimbursement) -> Dict[str, Any]:
        """
        Convert Reimbursement entity to database document.
        
        Args:
            reimbursement: Reimbursement entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(reimbursement, 'model_dump'):
            document = reimbursement.model_dump()
        elif hasattr(reimbursement, 'dict'):
            document = reimbursement.dict()
        else:
            document = {k: v for k, v in reimbursement.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Ensure proper field mapping for legacy compatibility
        if 'reimbursement_id' not in document and hasattr(reimbursement, 'reimbursement_id'):
            document['reimbursement_id'] = getattr(reimbursement, 'reimbursement_id')
        
        if 'employee_id' not in document and hasattr(reimbursement, 'employee_id'):
            employee_id = getattr(reimbursement, 'employee_id')
            if hasattr(employee_id, 'value'):
                document['employee_id'] = employee_id.value
            else:
                document['employee_id'] = str(employee_id)
        
        # Handle reimbursement type
        reimbursement_type = getattr(reimbursement, 'reimbursement_type', None)
        if reimbursement_type:
            if hasattr(reimbursement_type, 'type_id'):
                document['reimbursement_type_id'] = getattr(reimbursement_type, 'type_id')
            elif hasattr(reimbursement_type, 'id'):
                document['reimbursement_type_id'] = getattr(reimbursement_type, 'id')
        
        # Handle money/amount
        amount = getattr(reimbursement, 'amount', None)
        if amount:
            if hasattr(amount, 'value'):
                document['amount'] = float(getattr(amount, 'value'))
            elif isinstance(amount, (int, float, Decimal)):
                document['amount'] = float(amount)
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> Reimbursement:
        """
        Convert database document to Reimbursement entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            Reimbursement entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        # Map legacy fields to new structure
        if 'employee_id' in document and 'employee_id' not in document:
            document['employee_id'] = document['employee_id']
        
        if 'reimbursement_type_id' in document and 'reimbursement_type' not in document:
            document['reimbursement_type'] = document['reimbursement_type_id']
        
        return Reimbursement(**document)
    
    async def _ensure_indexes(self, organisation_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organisation_id)
            
            # Index for employee queries
            await collection.create_index([
                ("employee_id", 1),
                ("created_at", -1)
            ])
            
            # Index for status queries
            await collection.create_index([
                ("status", 1),
                ("created_at", -1)
            ])
            
            # Index for reimbursement type queries
            await collection.create_index([
                ("reimbursement_type_id", 1),
                ("created_at", -1)
            ])
            
            # Index for amount range queries
            await collection.create_index([
                ("amount", 1)
            ])
            
            # Compound index for manager queries
            await collection.create_index([
                ("status", 1),
                ("employee_id", 1),
                ("created_at", -1)
            ])
            
            logger.info(f"Reimbursement indexes ensured for organisation: {organisation_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring reimbursement indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, reimbursement: Reimbursement) -> Reimbursement:
        """
        Save reimbursement record.
        
        Replaces: create_reimbursement() function
        """
        try:
            # Get organisation from reimbursement or use default
            organisation_id = getattr(reimbursement, 'organisation_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organisation_id)
            
            # Prepare document
            document = self._entity_to_document(reimbursement)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            # Set default status if not present
            if not document.get('status'):
                document['status'] = 'PENDING'
            
            # Check for existing record by reimbursement_id
            existing = None
            if document.get('reimbursement_id'):
                existing = await self.get_by_id(document['reimbursement_id'], organisation_id)
            
            if existing:
                # Update existing record
                filters = {"reimbursement_id": document['reimbursement_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organisation_id=organisation_id
                )
                if success:
                    return await self.get_by_id(document['reimbursement_id'], organisation_id)
                else:
                    raise ValueError("Failed to update reimbursement record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organisation_id)
                # Return the saved document
                saved_doc = await self._get_collection(organisation_id).find_one({"_id": document_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving reimbursement: {e}")
            raise
    
    async def update(self, reimbursement_id: str, update_data: Dict[str, Any], 
                    organisation_id: str) -> bool:
        """
        Update reimbursement record.
        
        Replaces: update_reimbursement() function
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            # Use ObjectId for MongoDB compatibility
            if ObjectId.is_valid(reimbursement_id):
                filters = {"_id": ObjectId(reimbursement_id)}
            else:
                filters = {"reimbursement_id": reimbursement_id}
            
            success = await self._update_document(
                filters=filters,
                update_data=update_data,
                organisation_id=organisation_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating reimbursement {reimbursement_id}: {e}")
            return False
    
    async def delete(self, reimbursement_id: str, organisation_id: str) -> bool:
        """
        Delete reimbursement record.
        
        Replaces: delete_reimbursement() function
        """
        try:
            # Use ObjectId for MongoDB compatibility
            if ObjectId.is_valid(reimbursement_id):
                filters = {"_id": ObjectId(reimbursement_id)}
            else:
                filters = {"reimbursement_id": reimbursement_id}
            
            return await self._delete_document(
                filters=filters,
                organisation_id=organisation_id,
                soft_delete=True
            )
            
        except Exception as e:
            logger.error(f"Error deleting reimbursement {reimbursement_id}: {e}")
            return False
    
    async def update_status(self, reimbursement_id: str, status: str, 
                           comments: str, organisation_id: str) -> bool:
        """
        Update reimbursement status.
        
        Replaces: update_reimbursement_status() function
        """
        try:
            update_data = {
                "status": status,
                "comments": comments,
                "updated_at": datetime.now()
            }
            
            return await self.update(reimbursement_id, update_data, organisation_id)
            
        except Exception as e:
            logger.error(f"Error updating reimbursement status: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, reimbursement_id: str, organisation_id: str = "default") -> Optional[Reimbursement]:
        """Get reimbursement record by ID."""
        try:
            # Use ObjectId for MongoDB compatibility
            if ObjectId.is_valid(reimbursement_id):
                filters = {"_id": ObjectId(reimbursement_id)}
            else:
                filters = {"reimbursement_id": reimbursement_id}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organisation_id=organisation_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement {reimbursement_id}: {e}")
            return None
    
    async def get_by_employee_id(self, employee_id: str, organisation_id: str = "default") -> List[Dict[str, Any]]:
        """
        Get reimbursement requests for an employee with type information.
        
        Replaces: get_reimbursement_requests() function
        """
        try:
            collection = self._get_collection(organisation_id)
            
            # Use aggregation pipeline to join with reimbursement_types
            pipeline = [
                {"$match": {"employee_id": employee_id}},
                {"$lookup": {
                    "from": "reimbursement_types",
                    "localField": "reimbursement_type_id",
                    "foreignField": "reimbursement_type_id",
                    "as": "type_info"
                }},
                {"$unwind": {
                    "path": "$type_info",
                    "preserveNullAndEmptyArrays": True
                }},
                {"$project": {
                    "_id": 0,
                    "id": {"$toString": "$_id"},
                    "type_name": "$type_info.reimbursement_type_name",
                    "reimbursement_type_id": 1,
                    "amount": 1,
                    "note": 1,
                    "status": 1,
                    "file_url": 1,
                    "created_at": 1
                }},
                {"$sort": {"created_at": -1}}
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            logger.info(f"Found {len(results)} reimbursement requests for employee_id: {employee_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement requests for {employee_id}: {e}")
            return []
    
    async def get_pending_reimbursements(self, organisation_id: str = "default", 
                                        manager_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pending reimbursement requests with employee and type information.
        
        Replaces: get_pending_reimbursements() function
        """
        try:
            collection = self._get_collection(organisation_id)
            
            pipeline = [
                {"$match": {"status": "PENDING"}},
                {"$lookup": {
                    "from": "users",
                    "localField": "employee_id",
                    "foreignField": "employee_id",
                    "as": "employee_info"
                }},
                {"$unwind": {
                    "path": "$employee_info",
                    "preserveNullAndEmptyArrays": True
                }},
                {"$lookup": {
                    "from": "reimbursement_types",
                    "localField": "reimbursement_type_id",
                    "foreignField": "reimbursement_type_id",
                    "as": "type_info"
                }},
                {"$unwind": {
                    "path": "$type_info",
                    "preserveNullAndEmptyArrays": True
                }},
                {"$project": {
                    "_id": 0,
                    "id": {"$toString": "$_id"},
                    "employee_id": 1,
                    "employee_name": {"$concat": ["$employee_info.first_name", " ", "$employee_info.last_name"]},
                    "type_name": "$type_info.reimbursement_type_name",
                    "reimbursement_type_id": 1,
                    "amount": 1,
                    "note": 1,
                    "status": 1,
                    "comments": 1,
                    "file_url": 1,
                    "created_at": 1
                }},
                {"$sort": {"created_at": -1}}
            ]
            
            # If manager_id is provided, filter for employees under this manager
            if manager_id:
                pipeline.insert(1, {
                    "$match": {
                        "$or": [
                            {"employee_info.manager_id": manager_id},
                            {"employee_info.employee_id": manager_id}  # Include manager's own requests
                        ]
                    }
                })
            
            results = await self._aggregate(pipeline, organisation_id)
            logger.info(f"Found {len(results)} pending reimbursement requests")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving pending reimbursements: {e}")
            return []
    
    async def get_approved_reimbursements(self, organisation_id: str = "default", 
                                         manager_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get approved reimbursement requests with employee and type information.
        
        Replaces: get_approved_reimbursements() function
        """
        try:
            collection = self._get_collection(organisation_id)
            
            pipeline = [
                {"$match": {"status": "APPROVED"}},
                {"$lookup": {
                    "from": "users",
                    "localField": "employee_id",
                    "foreignField": "employee_id",
                    "as": "employee_info"
                }},
                {"$unwind": {
                    "path": "$employee_info",
                    "preserveNullAndEmptyArrays": True
                }},
                {"$lookup": {
                    "from": "reimbursement_types",
                    "localField": "reimbursement_type_id",
                    "foreignField": "reimbursement_type_id",
                    "as": "type_info"
                }},
                {"$unwind": {
                    "path": "$type_info",
                    "preserveNullAndEmptyArrays": True
                }},
                {"$project": {
                    "_id": 0,
                    "id": {"$toString": "$_id"},
                    "employee_id": 1,
                    "employee_name": {"$concat": ["$employee_info.first_name", " ", "$employee_info.last_name"]},
                    "type_name": "$type_info.reimbursement_type_name",
                    "reimbursement_type_id": 1,
                    "amount": 1,
                    "note": 1,
                    "status": 1,
                    "comments": 1,
                    "file_url": 1,
                    "created_at": 1
                }},
                {"$sort": {"created_at": -1}}
            ]
            
            # If manager_id is provided, filter for employees under this manager
            if manager_id:
                pipeline.insert(1, {
                    "$match": {
                        "$or": [
                            {"employee_info.manager_id": manager_id},
                            {"employee_info.employee_id": manager_id}  # Include manager's own requests
                        ]
                    }
                })
            
            results = await self._aggregate(pipeline, organisation_id)
            logger.info(f"Found {len(results)} approved reimbursement requests")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving approved reimbursements: {e}")
            return []
    
    async def get_by_status(self, status: str, organisation_id: str = "default",
                           limit: Optional[int] = None) -> List[Reimbursement]:
        """Get reimbursement requests by status."""
        try:
            filters = {"status": status}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=-1,
                limit=limit or 100,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursements by status {status}: {e}")
            return []
    
    async def get_by_date_range(self, start_date: date, end_date: date,
                               organisation_id: str = "default",
                               employee_ids: Optional[List[str]] = None) -> List[Reimbursement]:
        """Get reimbursement requests within a date range."""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            filters = {
                "created_at": {"$gte": start_datetime, "$lte": end_datetime}
            }
            
            if employee_ids:
                filters["employee_id"] = {"$in": employee_ids}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=-1,
                limit=500,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursements by date range: {e}")
            return []
    
    async def get_by_amount_range(self, min_amount: float, max_amount: float,
                                 organisation_id: str = "default") -> List[Reimbursement]:
        """Get reimbursement requests within an amount range."""
        try:
            filters = {
                "amount": {"$gte": min_amount, "$lte": max_amount}
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="amount",
                sort_order=-1,
                limit=200,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursements by amount range: {e}")
            return []
    
    async def search(self, filters: ReimbursementSearchFiltersDTO,
                    organisation_id: str = "default") -> List[Reimbursement]:
        """Search reimbursement requests with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'employee_ids') and filters.employee_ids:
                query_filters["employee_id"] = {"$in": filters.employee_ids}
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            if hasattr(filters, 'reimbursement_type_id') and filters.reimbursement_type_id:
                query_filters["reimbursement_type_id"] = filters.reimbursement_type_id
            
            if hasattr(filters, 'start_date') and filters.start_date:
                start_datetime = datetime.combine(filters.start_date, datetime.min.time())
                query_filters["created_at"] = {"$gte": start_datetime}
            
            if hasattr(filters, 'end_date') and filters.end_date:
                end_datetime = datetime.combine(filters.end_date, datetime.max.time())
                if "created_at" in query_filters:
                    query_filters["created_at"]["$lte"] = end_datetime
                else:
                    query_filters["created_at"] = {"$lte": end_datetime}
            
            if hasattr(filters, 'min_amount') and filters.min_amount is not None:
                query_filters["amount"] = {"$gte": filters.min_amount}
            
            if hasattr(filters, 'max_amount') and filters.max_amount is not None:
                if "amount" in query_filters:
                    query_filters["amount"]["$lte"] = filters.max_amount
                else:
                    query_filters["amount"] = {"$lte": filters.max_amount}
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            documents = await self._execute_query(
                filters=query_filters,
                skip=skip,
                limit=page_size,
                sort_by="created_at",
                sort_order=-1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching reimbursements: {e}")
            return []
    
    async def count_by_filters(self, filters: ReimbursementSearchFiltersDTO,
                              organisation_id: str = "default") -> int:
        """Count reimbursement requests matching filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            return await self._count_documents(query_filters, organisation_id)
            
        except Exception as e:
            logger.error(f"Error counting reimbursements: {e}")
            return 0
    
    # Analytics Repository Implementation
    async def get_reimbursement_statistics(self, organisation_id: str = "default",
                                          year: Optional[int] = None) -> Dict[str, Any]:
        """Get reimbursement statistics."""
        try:
            filters = {}
            
            if year:
                start_date = datetime(year, 1, 1)
                end_date = datetime(year + 1, 1, 1)
                filters = {
                    "created_at": {"$gte": start_date, "$lt": end_date}
                }
            
            # Use aggregation pipeline for statistics
            pipeline = [
                {"$match": filters},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "pending_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "PENDING"]}, 1, 0]}
                        },
                        "approved_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, 1, 0]}
                        },
                        "rejected_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "REJECTED"]}, 1, 0]}
                        },
                        "total_amount": {"$sum": "$amount"},
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, "$amount", 0]}
                        },
                        "average_amount": {"$avg": "$amount"}
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            if results:
                stats = results[0]
                return {
                    "total_requests": stats.get("total_requests", 0),
                    "pending_requests": stats.get("pending_requests", 0),
                    "approved_requests": stats.get("approved_requests", 0),
                    "rejected_requests": stats.get("rejected_requests", 0),
                    "total_amount": stats.get("total_amount", 0),
                    "approved_amount": stats.get("approved_amount", 0),
                    "average_amount": stats.get("average_amount", 0)
                }
            else:
                return {
                    "total_requests": 0,
                    "pending_requests": 0,
                    "approved_requests": 0,
                    "rejected_requests": 0,
                    "total_amount": 0,
                    "approved_amount": 0,
                    "average_amount": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting reimbursement statistics: {e}")
            return {}
    
    async def get_employee_reimbursement_summary(self, employee_id: str, year: int,
                                                organisation_id: str = "default") -> Dict[str, Any]:
        """Get reimbursement summary for an employee."""
        try:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            
            filters = {
                "employee_id": employee_id,
                "created_at": {"$gte": start_date, "$lt": end_date}
            }
            
            reimbursements = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            total_requests = len(reimbursements)
            approved_requests = sum(1 for r in reimbursements if r.get('status') == 'APPROVED')
            total_amount = sum(r.get('amount', 0) for r in reimbursements)
            approved_amount = sum(r.get('amount', 0) for r in reimbursements if r.get('status') == 'APPROVED')
            
            # Group by reimbursement type
            type_summary = {}
            for reimbursement in reimbursements:
                type_id = reimbursement.get('reimbursement_type_id', 'Unknown')
                if type_id not in type_summary:
                    type_summary[type_id] = {"count": 0, "amount": 0}
                type_summary[type_id]["count"] += 1
                type_summary[type_id]["amount"] += reimbursement.get('amount', 0)
            
            return {
                "employee_id": employee_id,
                "year": year,
                "total_requests": total_requests,
                "approved_requests": approved_requests,
                "total_amount": total_amount,
                "approved_amount": approved_amount,
                "type_summary": type_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting employee reimbursement summary: {e}")
            return {}
    
    # Legacy compatibility methods
    async def create_reimbursement_legacy(self, data: dict, hostname: str) -> Any:
        """
        Legacy compatibility for create_reimbursement() function.
        
        Args:
            data: Reimbursement data dictionary
            hostname: Organisation hostname
            
        Returns:
            Insert result
        """
        try:
            # Convert dict to Reimbursement entity
            reimbursement = Reimbursement(**data)
            
            # Save using new method
            saved_reimbursement = await self.save(reimbursement)
            
            # Return legacy-style result
            return type('InsertResult', (), {
                'inserted_id': getattr(saved_reimbursement, 'id', None)
            })()
            
        except Exception as e:
            logger.error(f"Error creating reimbursement (legacy): {e}")
            raise
    
    async def get_reimbursement_requests_legacy(self, employee_id: str, hostname: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_reimbursement_requests() function.
        """
        return await self.get_by_employee_id(employee_id, hostname)
    
    async def update_reimbursement_legacy(self, reimbursement_id: str, data: dict, hostname: str) -> bool:
        """
        Legacy compatibility for update_reimbursement() function.
        """
        return await self.update(reimbursement_id, data, hostname)
    
    async def delete_reimbursement_legacy(self, reimbursement_id: str, hostname: str) -> bool:
        """
        Legacy compatibility for delete_reimbursement() function.
        """
        return await self.delete(reimbursement_id, hostname)
    
    async def get_pending_reimbursements_legacy(self, hostname: str, manager_id: str = None) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_pending_reimbursements() function.
        """
        return await self.get_pending_reimbursements(hostname, manager_id)
    
    async def update_reimbursement_status_legacy(self, reimbursement_id: str, status: str, 
                                                comments: str, hostname: str) -> bool:
        """
        Legacy compatibility for update_reimbursement_status() function.
        """
        return await self.update_status(reimbursement_id, status, comments, hostname)
    
    async def get_approved_reimbursements_legacy(self, hostname: str, manager_id: str = None) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_approved_reimbursements() function.
        """
        return await self.get_approved_reimbursements(hostname, manager_id)

    # Missing Abstract Methods Implementation
    
    # ReimbursementCommandRepository Methods
    async def submit_request(self, request_id: str, submitted_by: str) -> bool:
        """Submit a reimbursement request."""
        try:
            collection = self._get_collection("default")
            result = await collection.update_one(
                {"reimbursement_id": request_id},
                {
                    "$set": {
                        "status": "submitted",
                        "submitted_by": submitted_by,
                        "submitted_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error submitting request {request_id}: {e}")
            return False

    async def approve_request(
        self,
        request_id: str,
        approved_by: str,
        approved_amount: Optional[Decimal] = None,
        approval_level: str = "manager",
        comments: Optional[str] = None
    ) -> bool:
        """Approve a reimbursement request."""
        try:
            collection = self._get_collection("default")
            update_data = {
                "status": "approved",
                "approved_by": approved_by,
                "approved_at": datetime.now(),
                "approval_level": approval_level,
                "updated_at": datetime.now()
            }
            
            if approved_amount is not None:
                update_data["approved_amount"] = float(approved_amount)
            
            if comments:
                update_data["approval_comments"] = comments
            
            result = await collection.update_one(
                {"reimbursement_id": request_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error approving request {request_id}: {e}")
            return False

    async def reject_request(
        self,
        request_id: str,
        rejected_by: str,
        rejection_reason: str
    ) -> bool:
        """Reject a reimbursement request."""
        try:
            collection = self._get_collection("default")
            result = await collection.update_one(
                {"reimbursement_id": request_id},
                {
                    "$set": {
                        "status": "rejected",
                        "rejected_by": rejected_by,
                        "rejected_at": datetime.now(),
                        "rejection_reason": rejection_reason,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error rejecting request {request_id}: {e}")
            return False

    async def cancel_request(
        self,
        request_id: str,
        cancelled_by: str,
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """Cancel a reimbursement request."""
        try:
            collection = self._get_collection("default")
            update_data = {
                "status": "cancelled",
                "cancelled_by": cancelled_by,
                "cancelled_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            if cancellation_reason:
                update_data["cancellation_reason"] = cancellation_reason
            
            result = await collection.update_one(
                {"reimbursement_id": request_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error cancelling request {request_id}: {e}")
            return False

    async def process_payment(
        self,
        request_id: str,
        paid_by: str,
        payment_method: str,
        payment_reference: Optional[str] = None,
        bank_details: Optional[str] = None
    ) -> bool:
        """Process payment for a reimbursement request."""
        try:
            collection = self._get_collection("default")
            update_data = {
                "status": "paid",
                "paid_by": paid_by,
                "paid_at": datetime.now(),
                "payment_method": payment_method,
                "updated_at": datetime.now()
            }
            
            if payment_reference:
                update_data["payment_reference"] = payment_reference
            if bank_details:
                update_data["bank_details"] = bank_details
            
            result = await collection.update_one(
                {"reimbursement_id": request_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error processing payment for {request_id}: {e}")
            return False

    async def upload_receipt(
        self,
        request_id: str,
        file_path: str,
        file_name: str,
        file_size: int,
        uploaded_by: str
    ) -> bool:
        """Upload receipt for a reimbursement request."""
        try:
            collection = self._get_collection("default")
            receipt_data = {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.now()
            }
            
            result = await collection.update_one(
                {"reimbursement_id": request_id},
                {
                    "$push": {"receipts": receipt_data},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error uploading receipt for {request_id}: {e}")
            return False

    async def bulk_approve(
        self,
        request_ids: List[str],
        approved_by: str,
        approval_criteria: str
    ) -> Dict[str, bool]:
        """Bulk approve reimbursement requests."""
        try:
            results = {}
            collection = self._get_collection("default")
            
            for request_id in request_ids:
                try:
                    result = await collection.update_one(
                        {"reimbursement_id": request_id, "status": {"$in": ["submitted", "pending"]}},
                        {
                            "$set": {
                                "status": "approved",
                                "approved_by": approved_by,
                                "approved_at": datetime.now(),
                                "approval_criteria": approval_criteria,
                                "updated_at": datetime.now()
                            }
                        }
                    )
                    results[request_id] = result.modified_count > 0
                except Exception as e:
                    logger.error(f"Error in bulk approve for {request_id}: {e}")
                    results[request_id] = False
            
            return results
        except Exception as e:
            logger.error(f"Error in bulk approve: {e}")
            return {req_id: False for req_id in request_ids}

    # ReimbursementQueryRepository Methods
    async def get_all(self) -> List[Reimbursement]:
        """Get all reimbursements."""
        try:
            collection = self._get_collection("default")
            cursor = collection.find({})
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting all reimbursements: {e}")
            return []

    async def get_pending_approval(self) -> List[Reimbursement]:
        """Get reimbursements pending approval."""
        try:
            collection = self._get_collection("default")
            cursor = collection.find({"status": {"$in": ["submitted", "pending"]}})
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting pending approval reimbursements: {e}")
            return []

    async def get_approved(self) -> List[Reimbursement]:
        """Get approved reimbursements."""
        try:
            collection = self._get_collection("default")
            cursor = collection.find({"status": "approved"})
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting approved reimbursements: {e}")
            return []

    async def get_paid(self) -> List[Reimbursement]:
        """Get paid reimbursements."""
        try:
            collection = self._get_collection("default")
            cursor = collection.find({"status": "paid"})
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting paid reimbursements: {e}")
            return []

    async def get_by_reimbursement_type(self, type_id: str) -> List[Reimbursement]:
        """Get reimbursements by type."""
        try:
            collection = self._get_collection("default")
            cursor = collection.find({"reimbursement_type_id": type_id})
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting reimbursements by type {type_id}: {e}")
            return []

    async def get_employee_reimbursements_by_period(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime,
        reimbursement_type_id: Optional[str] = None
    ) -> List[Reimbursement]:
        """Get employee reimbursements for a specific period."""
        try:
            collection = self._get_collection("default")
            query = {
                "employee_id": employee_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            if reimbursement_type_id:
                query["reimbursement_type_id"] = reimbursement_type_id
            
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting employee reimbursements by period: {e}")
            return []

    async def get_total_amount_by_employee_and_type(
        self,
        employee_id: str,
        reimbursement_type_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """Get total reimbursement amount for employee by type and period."""
        try:
            collection = self._get_collection("default")
            pipeline = [
                {
                    "$match": {
                        "employee_id": employee_id,
                        "reimbursement_type_id": reimbursement_type_id,
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "status": {"$in": ["approved", "paid"]}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_amount": {"$sum": "$amount"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                return Decimal(str(results[0].get("total_amount", 0)))
            return Decimal('0')
        except Exception as e:
            logger.error(f"Error getting total amount by employee and type: {e}")
            return Decimal('0')

    # ReimbursementAnalyticsRepository Methods
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get reimbursement statistics."""
        try:
            collection = self._get_collection("default")
            match_query = {}
            
            if start_date and end_date:
                match_query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                        "approved_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "paid_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "paid"]}, 1, 0]}
                        },
                        "pending_requests": {
                            "$sum": {"$cond": [{"$in": ["$status", ["submitted", "pending"]]}, 1, 0]}
                        },
                        "rejected_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                        },
                        "avg_amount": {"$avg": "$amount"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                return {
                    "total_requests": stats.get("total_requests", 0),
                    "total_amount": stats.get("total_amount", 0),
                    "approved_requests": stats.get("approved_requests", 0),
                    "paid_requests": stats.get("paid_requests", 0),
                    "pending_requests": stats.get("pending_requests", 0),
                    "rejected_requests": stats.get("rejected_requests", 0),
                    "average_amount": round(stats.get("avg_amount", 0), 2),
                    "approval_rate": round((stats.get("approved_requests", 0) / max(stats.get("total_requests", 1), 1)) * 100, 2)
                }
            
            return {"total_requests": 0, "total_amount": 0, "approved_requests": 0, "paid_requests": 0, "pending_requests": 0, "rejected_requests": 0, "average_amount": 0, "approval_rate": 0}
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    async def get_employee_statistics(
        self,
        employee_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for specific employee."""
        try:
            collection = self._get_collection("default")
            match_query = {"employee_id": employee_id}
            
            if start_date and end_date:
                match_query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount", 0]}
                        },
                        "paid_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "paid"]}, "$amount", 0]}
                        },
                        "pending_amount": {
                            "$sum": {"$cond": [{"$in": ["$status", ["submitted", "pending"]]}, "$amount", 0]}
                        },
                        "rejected_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, "$amount", 0]}
                        }
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                return results[0]
            return {"total_requests": 0, "total_amount": 0, "approved_amount": 0, "paid_amount": 0, "pending_amount": 0, "rejected_amount": 0}
        except Exception as e:
            logger.error(f"Error getting employee statistics: {e}")
            return {}

    async def get_category_wise_spending(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Decimal]:
        """Get spending breakdown by category."""
        try:
            collection = self._get_collection("default")
            match_query = {"status": {"$in": ["approved", "paid"]}}
            
            if start_date and end_date:
                match_query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$category",
                        "total_amount": {"$sum": "$amount"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {doc["_id"] or "uncategorized": Decimal(str(doc["total_amount"])) for doc in results}
        except Exception as e:
            logger.error(f"Error getting category wise spending: {e}")
            return {}

    async def get_monthly_trends(self, months: int = 12) -> Dict[str, Dict[str, Any]]:
        """Get monthly spending trends."""
        try:
            collection = self._get_collection("default")
            end_date = datetime.now()
            start_date = end_date.replace(month=end_date.month-months) if end_date.month > months else end_date.replace(year=end_date.year-1, month=12+end_date.month-months)
            
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"}
                        },
                        "total_amount": {"$sum": "$amount"},
                        "total_requests": {"$sum": 1},
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount", 0]}
                        }
                    }
                },
                {"$sort": {"_id.year": 1, "_id.month": 1}}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            trends = {}
            for doc in results:
                month_key = f"{doc['_id']['year']}-{doc['_id']['month']:02d}"
                trends[month_key] = {
                    "total_amount": doc["total_amount"],
                    "total_requests": doc["total_requests"],
                    "approved_amount": doc["approved_amount"]
                }
            
            return trends
        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return {}

    async def get_approval_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get approval metrics and turnaround times."""
        try:
            collection = self._get_collection("default")
            match_query = {}
            
            if start_date and end_date:
                match_query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_query},
                {
                    "$project": {
                        "status": 1,
                        "created_at": 1,
                        "approved_at": 1,
                        "rejected_at": 1,
                        "turnaround_time": {
                            "$cond": [
                                {"$ne": ["$approved_at", None]},
                                {"$subtract": ["$approved_at", "$created_at"]},
                                {"$cond": [
                                    {"$ne": ["$rejected_at", None]},
                                    {"$subtract": ["$rejected_at", "$created_at"]},
                                    None
                                ]}
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "approved_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "rejected_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                        },
                        "avg_turnaround_ms": {"$avg": "$turnaround_time"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                avg_turnaround_ms = stats.get("avg_turnaround_ms", 0)
                avg_turnaround_days = (avg_turnaround_ms / (1000 * 60 * 60 * 24)) if avg_turnaround_ms else 0
                
                return {
                    "total_requests": stats.get("total_requests", 0),
                    "approved_requests": stats.get("approved_requests", 0),
                    "rejected_requests": stats.get("rejected_requests", 0),
                    "approval_rate": round((stats.get("approved_requests", 0) / max(stats.get("total_requests", 1), 1)) * 100, 2),
                    "rejection_rate": round((stats.get("rejected_requests", 0) / max(stats.get("total_requests", 1), 1)) * 100, 2),
                    "average_turnaround_days": round(avg_turnaround_days, 2)
                }
            
            return {"total_requests": 0, "approved_requests": 0, "rejected_requests": 0, "approval_rate": 0, "rejection_rate": 0, "average_turnaround_days": 0}
        except Exception as e:
            logger.error(f"Error getting approval metrics: {e}")
            return {}

    async def get_top_spenders(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top spending employees."""
        try:
            collection = self._get_collection("default")
            match_query = {"status": {"$in": ["approved", "paid"]}}
            
            if start_date and end_date:
                match_query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$employee_id",
                        "total_amount": {"$sum": "$amount"},
                        "total_requests": {"$sum": 1}
                    }
                },
                {"$sort": {"total_amount": -1}},
                {"$limit": limit}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=limit)
            
            return [
                {
                    "employee_id": doc["_id"],
                    "total_amount": doc["total_amount"],
                    "total_requests": doc["total_requests"]
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error getting top spenders: {e}")
            return []

    async def get_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get compliance report with policy violations."""
        try:
            collection = self._get_collection("default")
            match_query = {}
            
            if start_date and end_date:
                match_query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            # This is a basic compliance report - would be enhanced based on specific policies
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "requests_without_receipts": {
                            "$sum": {"$cond": [{"$eq": [{"$size": {"$ifNull": ["$receipts", []]}}, 0]}, 1, 0]}
                        },
                        "high_value_requests": {
                            "$sum": {"$cond": [{"$gt": ["$amount", 10000]}, 1, 0]}  # Assuming 10k as high value
                        },
                        "requests_over_limit": {
                            "$sum": {"$cond": [{"$gt": ["$amount", 50000]}, 1, 0]}  # Assuming 50k as limit
                        }
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                total = stats.get("total_requests", 1)
                return {
                    "total_requests": total,
                    "requests_without_receipts": stats.get("requests_without_receipts", 0),
                    "high_value_requests": stats.get("high_value_requests", 0),
                    "requests_over_limit": stats.get("requests_over_limit", 0),
                    "compliance_rate": round(((total - stats.get("requests_without_receipts", 0) - stats.get("requests_over_limit", 0)) / total) * 100, 2)
                }
            
            return {"total_requests": 0, "requests_without_receipts": 0, "high_value_requests": 0, "requests_over_limit": 0, "compliance_rate": 100}
        except Exception as e:
            logger.error(f"Error getting compliance report: {e}")
            return {}

    async def get_payment_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get payment method analytics."""
        try:
            collection = self._get_collection("default")
            match_query = {"status": "paid"}
            
            if start_date and end_date:
                match_query["paid_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$payment_method",
                        "count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            payment_methods = {}
            for doc in results:
                method = doc["_id"] or "unknown"
                payment_methods[method] = {
                    "count": doc["count"],
                    "total_amount": doc["total_amount"]
                }
            
            return {
                "payment_methods": payment_methods,
                "total_paid_requests": sum(pm["count"] for pm in payment_methods.values()),
                "total_paid_amount": sum(pm["total_amount"] for pm in payment_methods.values())
            }
        except Exception as e:
            logger.error(f"Error getting payment analytics: {e}")
            return {}

    # ReimbursementReportRepository Methods
    async def generate_employee_report(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate detailed employee reimbursement report."""
        try:
            reimbursements = await self.get_employee_reimbursements_by_period(employee_id, start_date, end_date)
            stats = await self.get_employee_statistics(employee_id, start_date, end_date)
            
            return {
                "employee_id": employee_id,
                "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "statistics": stats,
                "reimbursements": [r.dict() if hasattr(r, 'dict') else r.__dict__ for r in reimbursements],
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating employee report: {e}")
            return {}

    async def generate_department_report(
        self,
        department: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate department-wise reimbursement report."""
        try:
            collection = self._get_collection("default")
            pipeline = [
                {
                    "$match": {
                        "department": department,
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$employee_id",
                        "total_amount": {"$sum": "$amount"},
                        "total_requests": {"$sum": 1},
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount", 0]}
                        }
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            employee_stats = await cursor.to_list(length=None)
            
            total_department_amount = sum(emp["total_amount"] for emp in employee_stats)
            total_department_requests = sum(emp["total_requests"] for emp in employee_stats)
            
            return {
                "department": department,
                "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "total_amount": total_department_amount,
                "total_requests": total_department_requests,
                "employee_breakdown": employee_stats,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating department report: {e}")
            return {}

    async def generate_tax_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate tax-related reimbursement report."""
        try:
            collection = self._get_collection("default")
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "status": {"$in": ["approved", "paid"]}
                    }
                },
                {
                    "$group": {
                        "_id": "$reimbursement_type_id",
                        "total_amount": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            type_breakdown = await cursor.to_list(length=None)
            
            return {
                "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "type_breakdown": type_breakdown,
                "total_taxable_amount": sum(item["total_amount"] for item in type_breakdown),
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            return {}

    async def generate_audit_trail(self, request_id: str) -> List[Dict[str, Any]]:
        """Generate audit trail for a reimbursement request."""
        try:
            collection = self._get_collection("default")
            reimbursement_doc = await collection.find_one({"reimbursement_id": request_id})
            
            if not reimbursement_doc:
                return []
            
            audit_trail = []
            
            # Creation event
            audit_trail.append({
                "timestamp": reimbursement_doc.get("created_at"),
                "event": "created",
                "user": reimbursement_doc.get("created_by", reimbursement_doc.get("employee_id")),
                "details": {"amount": reimbursement_doc.get("amount"), "type": reimbursement_doc.get("reimbursement_type_id")}
            })
            
            # Status changes
            if reimbursement_doc.get("submitted_at"):
                audit_trail.append({
                    "timestamp": reimbursement_doc.get("submitted_at"),
                    "event": "submitted",
                    "user": reimbursement_doc.get("submitted_by"),
                    "details": {}
                })
            
            if reimbursement_doc.get("approved_at"):
                audit_trail.append({
                    "timestamp": reimbursement_doc.get("approved_at"),
                    "event": "approved",
                    "user": reimbursement_doc.get("approved_by"),
                    "details": {
                        "approved_amount": reimbursement_doc.get("approved_amount"),
                        "comments": reimbursement_doc.get("approval_comments")
                    }
                })
            
            if reimbursement_doc.get("rejected_at"):
                audit_trail.append({
                    "timestamp": reimbursement_doc.get("rejected_at"),
                    "event": "rejected",
                    "user": reimbursement_doc.get("rejected_by"),
                    "details": {"reason": reimbursement_doc.get("rejection_reason")}
                })
            
            if reimbursement_doc.get("paid_at"):
                audit_trail.append({
                    "timestamp": reimbursement_doc.get("paid_at"),
                    "event": "paid",
                    "user": reimbursement_doc.get("paid_by"),
                    "details": {
                        "payment_method": reimbursement_doc.get("payment_method"),
                        "payment_reference": reimbursement_doc.get("payment_reference")
                    }
                })
            
            # Sort by timestamp
            audit_trail.sort(key=lambda x: x["timestamp"] or datetime.min)
            
            return audit_trail
        except Exception as e:
            logger.error(f"Error generating audit trail: {e}")
            return []

    async def export_to_excel(
        self,
        filters: ReimbursementSearchFiltersDTO,
        file_path: str
    ) -> str:
        """Export reimbursement data to Excel."""
        try:
            import pandas as pd
            
            # Get reimbursements based on filters
            reimbursements = await self.search(filters)
            
            if not reimbursements:
                return "No data to export"
            
            # Convert to DataFrame
            data = []
            for reimbursement in reimbursements:
                if hasattr(reimbursement, 'dict'):
                    data.append(reimbursement.dict())
                else:
                    data.append(reimbursement.__dict__)
            
            df = pd.DataFrame(data)
            
            # Clean up the dataframe
            if '_id' in df.columns:
                df.drop('_id', axis=1, inplace=True)
            
            # Save to Excel
            df.to_excel(file_path, index=False)
            
            return f"Data exported successfully to {file_path}"
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return f"Export failed: {str(e)}"

    # Composite Repository Properties
    @property
    def reimbursement_types(self):
        """Get reimbursement type query repository"""
        # This would typically return a separate repository instance
        # For now, returning self as a placeholder
        return self

    @property
    def reimbursement_type_commands(self):
        """Get reimbursement type command repository"""
        return self

    @property
    def reimbursements(self):
        """Get reimbursement query repository"""
        return self

    @property
    def reimbursement_commands(self):
        """Get reimbursement command repository"""
        return self

    @property
    def analytics(self):
        """Get analytics repository"""
        return self

    @property
    def reports(self):
        """Get reports repository"""
        return self

    # ReimbursementTypeCommandRepository methods (placeholder implementations)
    async def activate(self, type_id: str, updated_by: str) -> bool:
        """Activate a reimbursement type."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            result = await collection.update_one(
                {"type_id": type_id},
                {
                    "$set": {
                        "is_active": True,
                        "updated_by": updated_by,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error activating type {type_id}: {e}")
            return False

    async def deactivate(self, type_id: str, updated_by: str, reason: Optional[str] = None) -> bool:
        """Deactivate a reimbursement type."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            update_data = {
                "is_active": False,
                "updated_by": updated_by,
                "updated_at": datetime.now()
            }
            
            if reason:
                update_data["deactivation_reason"] = reason
            
            result = await collection.update_one(
                {"type_id": type_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deactivating type {type_id}: {e}")
            return False

    # ReimbursementTypeQueryRepository methods (placeholder implementations)
    async def get_by_code(self, code: str):
        """Get reimbursement type by code."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            return await collection.find_one({"code": code})
        except Exception as e:
            logger.error(f"Error getting type by code {code}: {e}")
            return None

    async def get_active(self):
        """Get active reimbursement types."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            cursor = collection.find({"is_active": True})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting active types: {e}")
            return []

    async def get_by_category(self, category: str):
        """Get reimbursement types by category."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            cursor = collection.find({"category": category})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting types by category {category}: {e}")
            return []

    async def exists_by_code(self, code: str, exclude_id: Optional[str] = None) -> bool:
        """Check if reimbursement type exists by code."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            query = {"code": code}
            
            if exclude_id:
                query["type_id"] = {"$ne": exclude_id}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking code existence {code}: {e}")
            return False

    # ReimbursementTypeAnalyticsRepository methods (placeholder implementations)
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get reimbursement type usage statistics."""
        try:
            collection = self._get_collection("default")
            pipeline = [
                {
                    "$group": {
                        "_id": "$reimbursement_type_id",
                        "count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                "type_usage": results,
                "total_types": len(results)
            }
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return {}

    async def get_category_breakdown(self) -> Dict[str, int]:
        """Get breakdown by category."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            pipeline = [
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {doc["_id"] or "uncategorized": doc["count"] for doc in results}
        except Exception as e:
            logger.error(f"Error getting category breakdown: {e}")
            return {}

    async def get_approval_level_distribution(self) -> Dict[str, int]:
        """Get approval level distribution."""
        try:
            collection = self._get_collection("default", "reimbursement_types")
            pipeline = [
                {
                    "$group": {
                        "_id": "$approval_level",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {doc["_id"] or "manager": doc["count"] for doc in results}
        except Exception as e:
            logger.error(f"Error getting approval level distribution: {e}")
            return {} 