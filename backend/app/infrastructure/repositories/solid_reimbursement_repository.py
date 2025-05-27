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
    from domain.entities.reimbursement import Reimbursement
    from domain.value_objects.employee_id import EmployeeId
    from domain.value_objects.reimbursement_type import ReimbursementType
    from domain.value_objects.money import Money
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
    from application.interfaces.repositories.reimbursement_repository import (
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
    from application.dto.reimbursement_dto import (
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
        
        if 'emp_id' not in document and hasattr(reimbursement, 'employee_id'):
            emp_id = getattr(reimbursement, 'employee_id')
            if hasattr(emp_id, 'value'):
                document['emp_id'] = emp_id.value
            else:
                document['emp_id'] = str(emp_id)
        
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
        if 'emp_id' in document and 'employee_id' not in document:
            document['employee_id'] = document['emp_id']
        
        if 'reimbursement_type_id' in document and 'reimbursement_type' not in document:
            document['reimbursement_type'] = document['reimbursement_type_id']
        
        return Reimbursement(**document)
    
    async def _ensure_indexes(self, organization_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organization_id)
            
            # Index for employee queries
            await collection.create_index([
                ("emp_id", 1),
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
                ("emp_id", 1),
                ("created_at", -1)
            ])
            
            logger.info(f"Reimbursement indexes ensured for organization: {organization_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring reimbursement indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, reimbursement: Reimbursement) -> Reimbursement:
        """
        Save reimbursement record.
        
        Replaces: create_reimbursement() function
        """
        try:
            # Get organization from reimbursement or use default
            organization_id = getattr(reimbursement, 'organization_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organization_id)
            
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
                existing = await self.get_by_id(document['reimbursement_id'], organization_id)
            
            if existing:
                # Update existing record
                filters = {"reimbursement_id": document['reimbursement_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organization_id=organization_id
                )
                if success:
                    return await self.get_by_id(document['reimbursement_id'], organization_id)
                else:
                    raise ValueError("Failed to update reimbursement record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organization_id)
                # Return the saved document
                saved_doc = await self._get_collection(organization_id).find_one({"_id": document_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving reimbursement: {e}")
            raise
    
    async def update(self, reimbursement_id: str, update_data: Dict[str, Any], 
                    organization_id: str) -> bool:
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
                organization_id=organization_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating reimbursement {reimbursement_id}: {e}")
            return False
    
    async def delete(self, reimbursement_id: str, organization_id: str) -> bool:
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
                organization_id=organization_id,
                soft_delete=True
            )
            
        except Exception as e:
            logger.error(f"Error deleting reimbursement {reimbursement_id}: {e}")
            return False
    
    async def update_status(self, reimbursement_id: str, status: str, 
                           comments: str, organization_id: str) -> bool:
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
            
            return await self.update(reimbursement_id, update_data, organization_id)
            
        except Exception as e:
            logger.error(f"Error updating reimbursement status: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, reimbursement_id: str, organization_id: str = "default") -> Optional[Reimbursement]:
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
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement {reimbursement_id}: {e}")
            return None
    
    async def get_by_employee_id(self, emp_id: str, organization_id: str = "default") -> List[Dict[str, Any]]:
        """
        Get reimbursement requests for an employee with type information.
        
        Replaces: get_reimbursement_requests() function
        """
        try:
            collection = self._get_collection(organization_id)
            
            # Use aggregation pipeline to join with reimbursement_types
            pipeline = [
                {"$match": {"emp_id": emp_id}},
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
            
            results = await self._aggregate(pipeline, organization_id)
            logger.info(f"Found {len(results)} reimbursement requests for emp_id: {emp_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement requests for {emp_id}: {e}")
            return []
    
    async def get_pending_reimbursements(self, organization_id: str = "default", 
                                        manager_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pending reimbursement requests with employee and type information.
        
        Replaces: get_pending_reimbursements() function
        """
        try:
            collection = self._get_collection(organization_id)
            
            pipeline = [
                {"$match": {"status": "PENDING"}},
                {"$lookup": {
                    "from": "users",
                    "localField": "emp_id",
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
                    "emp_id": 1,
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
            
            results = await self._aggregate(pipeline, organization_id)
            logger.info(f"Found {len(results)} pending reimbursement requests")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving pending reimbursements: {e}")
            return []
    
    async def get_approved_reimbursements(self, organization_id: str = "default", 
                                         manager_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get approved reimbursement requests with employee and type information.
        
        Replaces: get_approved_reimbursements() function
        """
        try:
            collection = self._get_collection(organization_id)
            
            pipeline = [
                {"$match": {"status": "APPROVED"}},
                {"$lookup": {
                    "from": "users",
                    "localField": "emp_id",
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
                    "emp_id": 1,
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
            
            results = await self._aggregate(pipeline, organization_id)
            logger.info(f"Found {len(results)} approved reimbursement requests")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving approved reimbursements: {e}")
            return []
    
    async def get_by_status(self, status: str, organization_id: str = "default",
                           limit: Optional[int] = None) -> List[Reimbursement]:
        """Get reimbursement requests by status."""
        try:
            filters = {"status": status}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=-1,
                limit=limit or 100,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursements by status {status}: {e}")
            return []
    
    async def get_by_date_range(self, start_date: date, end_date: date,
                               organization_id: str = "default",
                               emp_ids: Optional[List[str]] = None) -> List[Reimbursement]:
        """Get reimbursement requests within a date range."""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            filters = {
                "created_at": {"$gte": start_datetime, "$lte": end_datetime}
            }
            
            if emp_ids:
                filters["emp_id"] = {"$in": emp_ids}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=-1,
                limit=500,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursements by date range: {e}")
            return []
    
    async def get_by_amount_range(self, min_amount: float, max_amount: float,
                                 organization_id: str = "default") -> List[Reimbursement]:
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursements by amount range: {e}")
            return []
    
    async def search(self, filters: ReimbursementSearchFiltersDTO,
                    organization_id: str = "default") -> List[Reimbursement]:
        """Search reimbursement requests with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["emp_id"] = filters.employee_id
            
            if hasattr(filters, 'employee_ids') and filters.employee_ids:
                query_filters["emp_id"] = {"$in": filters.employee_ids}
            
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
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching reimbursements: {e}")
            return []
    
    async def count_by_filters(self, filters: ReimbursementSearchFiltersDTO,
                              organization_id: str = "default") -> int:
        """Count reimbursement requests matching filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["emp_id"] = filters.employee_id
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            return await self._count_documents(query_filters, organization_id)
            
        except Exception as e:
            logger.error(f"Error counting reimbursements: {e}")
            return 0
    
    # Analytics Repository Implementation
    async def get_reimbursement_statistics(self, organization_id: str = "default",
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
            
            results = await self._aggregate(pipeline, organization_id)
            
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
    
    async def get_employee_reimbursement_summary(self, emp_id: str, year: int,
                                                organization_id: str = "default") -> Dict[str, Any]:
        """Get reimbursement summary for an employee."""
        try:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            
            filters = {
                "emp_id": emp_id,
                "created_at": {"$gte": start_date, "$lt": end_date}
            }
            
            reimbursements = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=1,
                organization_id=organization_id
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
                "employee_id": emp_id,
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
            hostname: Organization hostname
            
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
    
    async def get_reimbursement_requests_legacy(self, emp_id: str, hostname: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_reimbursement_requests() function.
        """
        return await self.get_by_employee_id(emp_id, hostname)
    
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