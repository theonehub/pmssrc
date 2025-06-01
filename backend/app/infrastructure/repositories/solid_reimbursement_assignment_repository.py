"""
SOLID-Compliant Reimbursement Assignment Repository Implementation
Replaces the procedural reimbursement_assignment_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.reimbursement_assignment import ReimbursementAssignment
    from app.domain.value_objects.employee_id import EmployeeId
    from models.reimbursement_assignment import ReimbursementAssignmentCreate
except ImportError:
    # Fallback classes for migration compatibility
    class ReimbursementAssignment:
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
    
    class ReimbursementAssignmentCreate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# Import application interfaces
try:
    from app.application.interfaces.repositories.reimbursement_assignment_repository import (
        ReimbursementAssignmentCommandRepository, ReimbursementAssignmentQueryRepository,
        ReimbursementAssignmentAnalyticsRepository, ReimbursementAssignmentRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class ReimbursementAssignmentCommandRepository(ABC):
        pass
    
    class ReimbursementAssignmentQueryRepository(ABC):
        pass
    
    class ReimbursementAssignmentAnalyticsRepository(ABC):
        pass
    
    class ReimbursementAssignmentRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.reimbursement_assignment_dto import (
        ReimbursementAssignmentSearchFiltersDTO, ReimbursementAssignmentStatisticsDTO
    )
except ImportError:
    # Fallback DTOs
    class ReimbursementAssignmentSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ReimbursementAssignmentStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidReimbursementAssignmentRepository(
    BaseRepository[ReimbursementAssignment],
    ReimbursementAssignmentCommandRepository,
    ReimbursementAssignmentQueryRepository,
    ReimbursementAssignmentAnalyticsRepository,
    ReimbursementAssignmentRepository
):
    """
    SOLID-compliant reimbursement assignment repository implementation.
    
    Replaces the procedural reimbursement_assignment_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles reimbursement assignment data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all reimbursement assignment repository interfaces
    - Interface Segregation: Implements focused reimbursement assignment repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize reimbursement assignment repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "reimbursement_assignments")
        
    def _entity_to_document(self, assignment: ReimbursementAssignment) -> Dict[str, Any]:
        """
        Convert ReimbursementAssignment entity to database document.
        
        Args:
            assignment: ReimbursementAssignment entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(assignment, 'model_dump'):
            document = assignment.model_dump()
        elif hasattr(assignment, 'dict'):
            document = assignment.dict()
        else:
            document = {k: v for k, v in assignment.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Ensure proper field mapping for legacy compatibility
        if 'employee_id' not in document and hasattr(assignment, 'employee_id'):
            employee_id = getattr(assignment, 'employee_id')
            if hasattr(employee_id, 'value'):
                document['employee_id'] = employee_id.value
            else:
                document['employee_id'] = str(employee_id)
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> ReimbursementAssignment:
        """
        Convert database document to ReimbursementAssignment entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            ReimbursementAssignment entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        return ReimbursementAssignment(**document)
    
    async def _ensure_indexes(self, organization_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organization_id)
            
            # Index for employee_id queries
            await collection.create_index([
                ("employee_id", 1)
            ], unique=True)
            
            # Index for reimbursement_type_ids queries
            await collection.create_index([
                ("reimbursement_type_ids", 1)
            ])
            
            # Index for created_at queries
            await collection.create_index([
                ("created_at", -1)
            ])
            
            logger.info(f"Reimbursement assignment indexes ensured for organization: {organization_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring reimbursement assignment indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, assignment: ReimbursementAssignment) -> ReimbursementAssignment:
        """
        Save reimbursement assignment record.
        
        Replaces: create_assignment() function
        """
        try:
            # Get organization from assignment or use default
            organization_id = getattr(assignment, 'organization_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organization_id)
            
            # Prepare document
            document = self._entity_to_document(assignment)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            # Check for existing record by employee_id
            existing = None
            if document.get('employee_id'):
                existing = await self.get_by_employee_id(document['employee_id'], organization_id)
            
            if existing:
                # Update existing record
                filters = {"employee_id": document['employee_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organization_id=organization_id
                )
                if success:
                    return await self.get_by_employee_id(document['employee_id'], organization_id)
                else:
                    raise ValueError("Failed to update reimbursement assignment record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organization_id)
                # Return the saved document
                saved_doc = await self._get_collection(organization_id).find_one({"_id": document_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving reimbursement assignment: {e}")
            raise
    
    async def update(self, employee_id: str, update_data: Dict[str, Any], 
                    organization_id: str) -> bool:
        """
        Update reimbursement assignment record.
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            filters = {"employee_id": employee_id}
            
            success = await self._update_document(
                filters=filters,
                update_data=update_data,
                organization_id=organization_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating reimbursement assignment {employee_id}: {e}")
            return False
    
    async def delete(self, employee_id: str, organization_id: str) -> bool:
        """
        Delete reimbursement assignment record.
        """
        try:
            filters = {"employee_id": employee_id}
            
            return await self._delete_document(
                filters=filters,
                organization_id=organization_id,
                soft_delete=False  # Hard delete for assignments
            )
            
        except Exception as e:
            logger.error(f"Error deleting reimbursement assignment {employee_id}: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_employee_id(self, employee_id: str, organization_id: str = "default") -> Optional[ReimbursementAssignment]:
        """
        Get reimbursement assignment by employee ID.
        
        Replaces: get_user_assignments() function
        """
        try:
            filters = {"employee_id": employee_id}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement assignment for {employee_id}: {e}")
            return None
    
    async def get_all_with_details(self, skip: int = 0, limit: int = 10, 
                                  search: str = None, organization_id: str = "default") -> Dict[str, Any]:
        """
        Get all assignments with user and reimbursement type details.
        
        Replaces: get_all_assignments() function
        """
        try:
            # Get collections
            assignments_collection = self._get_collection(organization_id)
            users_collection = self._db_connector.get_collection(f"pms_{organization_id}", "users")
            types_collection = self._db_connector.get_collection(f"pms_{organization_id}", "reimbursement_types")
            
            # Build search query for users
            user_query = {}
            if search:
                user_query = {
                    "$or": [
                        {"name": {"$regex": search, "$options": "i"}},
                        {"email": {"$regex": search, "$options": "i"}}
                    ]
                }
            
            # Get total count for pagination
            total_users = await users_collection.count_documents(user_query)
            
            # Get paginated users
            users_cursor = users_collection.find(user_query).skip(skip).limit(limit)
            users = await users_cursor.to_list(length=None)
            
            # Get all assignments and types
            assignments_cursor = assignments_collection.find({})
            assignments = await assignments_cursor.to_list(length=None)
            
            types_cursor = types_collection.find({})
            types = await types_cursor.to_list(length=None)
            
            # Create lookup dictionaries
            type_lookup = {str(rt["_id"]): rt for rt in types}
            assignment_lookup = {str(a["employee_id"]): a["reimbursement_type_ids"] for a in assignments}
            
            # Build response
            response = []
            for user in users:
                employee_id = str(user["employee_id"])
                assigned_ids = assignment_lookup.get(employee_id, [])
                assigned_types = []
                
                for tid in assigned_ids:
                    if tid in type_lookup:
                        type_info = type_lookup[tid]
                        assigned_types.append({
                            "reimbursement_type_id": tid,
                            "name": type_info["name"],
                            "description": type_info.get("description", ""),
                            "monthly_limit": type_info.get("max_limit"),
                            "required_docs": type_info.get("required_docs", False)
                        })
                
                response.append({
                    "employee_id": employee_id,
                    "name": user["name"],
                    "email": user.get("email", ""),
                    "assigned_reimbursements": assigned_types
                })
            
            return {
                "data": response,
                "total": total_users,
                "page": skip // limit + 1,
                "page_size": limit
            }
            
        except Exception as e:
            logger.error(f"Error getting all assignments with details: {e}")
            return {
                "data": [],
                "total": 0,
                "page": 1,
                "page_size": limit
            }
    
    async def get_by_reimbursement_type(self, reimbursement_type_id: str, 
                                       organization_id: str = "default") -> List[ReimbursementAssignment]:
        """Get assignments by reimbursement type ID."""
        try:
            filters = {"reimbursement_type_ids": reimbursement_type_id}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="created_at",
                sort_order=-1,
                limit=100,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving assignments by reimbursement type: {e}")
            return []
    
    async def get_all(self, organization_id: str = "default") -> List[ReimbursementAssignment]:
        """Get all reimbursement assignments."""
        try:
            documents = await self._execute_query(
                filters={},
                sort_by="created_at",
                sort_order=-1,
                limit=1000,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all assignments: {e}")
            return []
    
    async def search(self, filters: ReimbursementAssignmentSearchFiltersDTO,
                    organization_id: str = "default") -> List[ReimbursementAssignment]:
        """Search reimbursement assignments with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'reimbursement_type_id') and filters.reimbursement_type_id:
                query_filters["reimbursement_type_ids"] = filters.reimbursement_type_id
            
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
            logger.error(f"Error searching reimbursement assignments: {e}")
            return []
    
    async def count_by_filters(self, filters: ReimbursementAssignmentSearchFiltersDTO,
                              organization_id: str = "default") -> int:
        """Count reimbursement assignments matching filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'reimbursement_type_id') and filters.reimbursement_type_id:
                query_filters["reimbursement_type_ids"] = filters.reimbursement_type_id
            
            return await self._count_documents(query_filters, organization_id)
            
        except Exception as e:
            logger.error(f"Error counting reimbursement assignments: {e}")
            return 0
    
    # Analytics Repository Implementation
    async def get_assignment_statistics(self, organization_id: str = "default") -> Dict[str, Any]:
        """Get reimbursement assignment statistics."""
        try:
            # Use aggregation pipeline for statistics
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_assignments": {"$sum": 1},
                        "total_employees": {"$sum": 1},
                        "total_type_assignments": {"$sum": {"$size": "$reimbursement_type_ids"}},
                        "avg_types_per_employee": {"$avg": {"$size": "$reimbursement_type_ids"}}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_assignments": 1,
                        "total_employees": 1,
                        "total_type_assignments": 1,
                        "avg_types_per_employee": 1
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            if results:
                stats = results[0]
                return {
                    "total_assignments": stats.get("total_assignments", 0),
                    "total_employees": stats.get("total_employees", 0),
                    "total_type_assignments": stats.get("total_type_assignments", 0),
                    "avg_types_per_employee": stats.get("avg_types_per_employee", 0)
                }
            else:
                return {
                    "total_assignments": 0,
                    "total_employees": 0,
                    "total_type_assignments": 0,
                    "avg_types_per_employee": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting assignment statistics: {e}")
            return {}
    
    async def get_type_usage_statistics(self, organization_id: str = "default") -> Dict[str, Any]:
        """Get reimbursement type usage statistics."""
        try:
            pipeline = [
                {"$unwind": "$reimbursement_type_ids"},
                {
                    "$group": {
                        "_id": "$reimbursement_type_ids",
                        "employee_count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"employee_count": -1}
                },
                {
                    "$project": {
                        "reimbursement_type_id": "$_id",
                        "employee_count": 1,
                        "_id": 0
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            return {
                "type_usage": results
            }
            
        except Exception as e:
            logger.error(f"Error getting type usage statistics: {e}")
            return {}
    
    # Legacy compatibility methods
    async def create_assignment_legacy(self, data: dict, hostname: str) -> bool:
        """
        Legacy compatibility for create_assignment() function.
        
        Args:
            data: Assignment data dictionary
            hostname: Organization hostname
            
        Returns:
            True if successful
        """
        try:
            # Convert dict to ReimbursementAssignment entity
            assignment = ReimbursementAssignment(**data)
            
            # Save using new method
            await self.save(assignment)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating assignment (legacy): {e}")
            return False
    
    async def get_user_assignments_legacy(self, employee_id: str, hostname: str) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility for get_user_assignments() function.
        """
        try:
            assignment = await self.get_by_employee_id(employee_id, hostname)
            
            if assignment:
                return {
                    "employee_id": getattr(assignment, 'employee_id', ''),
                    "reimbursement_type_ids": getattr(assignment, 'reimbursement_type_ids', []),
                    "created_at": getattr(assignment, 'created_at', None),
                    "updated_at": getattr(assignment, 'updated_at', None)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user assignments (legacy): {e}")
            return None
    
    async def get_all_assignments_legacy(self, skip: int = 0, limit: int = 10, 
                                        search: str = None, hostname: str = None) -> Dict[str, Any]:
        """
        Legacy compatibility for get_all_assignments() function.
        """
        return await self.get_all_with_details(skip, limit, search, hostname) 