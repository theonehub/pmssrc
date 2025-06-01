"""
SOLID Reimbursement Types Repository Implementation

This module implements the reimbursement types repository following SOLID principles:
- Single Responsibility: Handles only reimbursement type data operations
- Open/Closed: Extensible through interfaces without modification
- Liskov Substitution: Implements consistent interfaces
- Interface Segregation: Focused interfaces for specific operations
- Dependency Inversion: Depends on abstractions, not concretions

Author: System Architecture Team
Date: 2024
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.infrastructure.database.database_connector import DatabaseConnector
from app.infrastructure.repositories.base_repository import BaseRepository
from app.application.interfaces.repositories.reimbursement_types_repository_interface import (
    ReimbursementTypesCommandRepository,
    ReimbursementTypesQueryRepository,
    ReimbursementTypesAnalyticsRepository
)
from app.domain.entities.reimbursement_type import ReimbursementType
from app.application.dto.reimbursement_type_dto import (
    ReimbursementTypeCreateDTO,
    ReimbursementTypeUpdateDTO,
    ReimbursementTypeResponseDTO
)

logger = logging.getLogger(__name__)

class SolidReimbursementTypesRepository(
    BaseRepository,
    ReimbursementTypesCommandRepository,
    ReimbursementTypesQueryRepository,
    ReimbursementTypesAnalyticsRepository
):
    """
    SOLID-compliant reimbursement types repository implementation.
    
    Provides comprehensive reimbursement type management with:
    - CRUD operations
    - Analytics and reporting
    - Performance optimization
    - Error handling and logging
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Initialize the repository with database connector.
        
        Args:
            db_connector: Database connector following DIP
        """
        super().__init__(db_connector, "reimbursement_types")
        self.logger = logging.getLogger(__name__)
    
    # Command Repository Implementation
    
    async def create_reimbursement_type(
        self, 
        reimbursement_type_data: ReimbursementTypeCreateDTO, 
        company_id: str
    ) -> str:
        """
        Create a new reimbursement type.
        
        Args:
            reimbursement_type_data: Reimbursement type creation data
            company_id: Company identifier
            
        Returns:
            str: Created reimbursement type ID
            
        Raises:
            ValueError: If data validation fails
            RuntimeError: If creation fails
        """
        try:
            self.logger.info(f"Creating reimbursement type for company {company_id}")
            
            # Validate required fields
            if not reimbursement_type_data.name:
                raise ValueError("Reimbursement type name is required")
            
            # Check for duplicate names
            existing = await self.get_reimbursement_type_by_name(
                reimbursement_type_data.name, 
                company_id
            )
            if existing:
                raise ValueError(f"Reimbursement type '{reimbursement_type_data.name}' already exists")
            
            # Prepare document
            doc = reimbursement_type_data.model_dump()
            doc.update({
                "reimbursement_type_id": str(ObjectId()),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            })
            
            # Insert document
            collection = await self._get_collection(company_id)
            result = await collection.insert_one(doc)
            
            self.logger.info(f"Created reimbursement type {doc['reimbursement_type_id']}")
            return doc["reimbursement_type_id"]
            
        except Exception as e:
            self.logger.error(f"Error creating reimbursement type: {str(e)}")
            raise RuntimeError(f"Failed to create reimbursement type: {str(e)}")
    
    async def update_reimbursement_type(
        self, 
        reimbursement_type_id: str, 
        update_data: ReimbursementTypeUpdateDTO, 
        company_id: str
    ) -> bool:
        """
        Update an existing reimbursement type.
        
        Args:
            reimbursement_type_id: Reimbursement type identifier
            update_data: Update data
            company_id: Company identifier
            
        Returns:
            bool: True if update successful
            
        Raises:
            ValueError: If reimbursement type not found
            RuntimeError: If update fails
        """
        try:
            self.logger.info(f"Updating reimbursement type {reimbursement_type_id}")
            
            # Check if reimbursement type exists
            existing = await self.get_reimbursement_type_by_id(reimbursement_type_id, company_id)
            if not existing:
                raise ValueError(f"Reimbursement type {reimbursement_type_id} not found")
            
            # Check for duplicate names if name is being updated
            if update_data.name and update_data.name != existing.name:
                duplicate = await self.get_reimbursement_type_by_name(update_data.name, company_id)
                if duplicate and duplicate.reimbursement_type_id != reimbursement_type_id:
                    raise ValueError(f"Reimbursement type '{update_data.name}' already exists")
            
            # Prepare update document
            update_doc = update_data.model_dump(exclude_unset=True)
            update_doc["updated_at"] = datetime.now()
            
            # Update document
            collection = await self._get_collection(company_id)
            result = await collection.update_one(
                {"reimbursement_type_id": reimbursement_type_id},
                {"$set": update_doc}
            )
            
            if result.modified_count == 0:
                raise RuntimeError("No documents were updated")
            
            self.logger.info(f"Updated reimbursement type {reimbursement_type_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating reimbursement type: {str(e)}")
            raise RuntimeError(f"Failed to update reimbursement type: {str(e)}")
    
    async def delete_reimbursement_type(self, reimbursement_type_id: str, company_id: str) -> bool:
        """
        Delete a reimbursement type (soft delete).
        
        Args:
            reimbursement_type_id: Reimbursement type identifier
            company_id: Company identifier
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            ValueError: If reimbursement type not found
            RuntimeError: If deletion fails
        """
        try:
            self.logger.info(f"Deleting reimbursement type {reimbursement_type_id}")
            
            # Check if reimbursement type exists
            existing = await self.get_reimbursement_type_by_id(reimbursement_type_id, company_id)
            if not existing:
                raise ValueError(f"Reimbursement type {reimbursement_type_id} not found")
            
            # Soft delete
            collection = await self._get_collection(company_id)
            result = await collection.update_one(
                {"reimbursement_type_id": reimbursement_type_id},
                {
                    "$set": {
                        "is_active": False,
                        "deleted_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise RuntimeError("No documents were updated")
            
            self.logger.info(f"Deleted reimbursement type {reimbursement_type_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting reimbursement type: {str(e)}")
            raise RuntimeError(f"Failed to delete reimbursement type: {str(e)}")
    
    # Query Repository Implementation
    
    async def get_reimbursement_type_by_id(
        self, 
        reimbursement_type_id: str, 
        company_id: str
    ) -> Optional[ReimbursementTypeResponseDTO]:
        """
        Get reimbursement type by ID.
        
        Args:
            reimbursement_type_id: Reimbursement type identifier
            company_id: Company identifier
            
        Returns:
            Optional[ReimbursementTypeResponseDTO]: Reimbursement type if found
        """
        try:
            collection = await self._get_collection(company_id)
            doc = await collection.find_one({
                "reimbursement_type_id": reimbursement_type_id,
                "is_active": True
            })
            
            if doc:
                return ReimbursementTypeResponseDTO(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting reimbursement type by ID: {str(e)}")
            raise RuntimeError(f"Failed to get reimbursement type: {str(e)}")
    
    async def get_reimbursement_type_by_name(
        self, 
        name: str, 
        company_id: str
    ) -> Optional[ReimbursementTypeResponseDTO]:
        """
        Get reimbursement type by name.
        
        Args:
            name: Reimbursement type name
            company_id: Company identifier
            
        Returns:
            Optional[ReimbursementTypeResponseDTO]: Reimbursement type if found
        """
        try:
            collection = await self._get_collection(company_id)
            doc = await collection.find_one({
                "name": {"$regex": f"^{name}$", "$options": "i"},
                "is_active": True
            })
            
            if doc:
                return ReimbursementTypeResponseDTO(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting reimbursement type by name: {str(e)}")
            raise RuntimeError(f"Failed to get reimbursement type: {str(e)}")
    
    async def get_all_reimbursement_types(
        self, 
        company_id: str,
        include_inactive: bool = False
    ) -> List[ReimbursementTypeResponseDTO]:
        """
        Get all reimbursement types for a company.
        
        Args:
            company_id: Company identifier
            include_inactive: Whether to include inactive types
            
        Returns:
            List[ReimbursementTypeResponseDTO]: List of reimbursement types
        """
        try:
            collection = await self._get_collection(company_id)
            
            query = {}
            if not include_inactive:
                query["is_active"] = True
            
            cursor = collection.find(query).sort("name", 1)
            types = []
            
            async for doc in cursor:
                types.append(ReimbursementTypeResponseDTO(**doc))
            
            return types
            
        except Exception as e:
            self.logger.error(f"Error getting all reimbursement types: {str(e)}")
            raise RuntimeError(f"Failed to get reimbursement types: {str(e)}")
    
    async def search_reimbursement_types(
        self, 
        search_term: str, 
        company_id: str
    ) -> List[ReimbursementTypeResponseDTO]:
        """
        Search reimbursement types by name or description.
        
        Args:
            search_term: Search term
            company_id: Company identifier
            
        Returns:
            List[ReimbursementTypeResponseDTO]: Matching reimbursement types
        """
        try:
            collection = await self._get_collection(company_id)
            
            query = {
                "$and": [
                    {"is_active": True},
                    {
                        "$or": [
                            {"name": {"$regex": search_term, "$options": "i"}},
                            {"description": {"$regex": search_term, "$options": "i"}}
                        ]
                    }
                ]
            }
            
            cursor = collection.find(query).sort("name", 1)
            types = []
            
            async for doc in cursor:
                types.append(ReimbursementTypeResponseDTO(**doc))
            
            return types
            
        except Exception as e:
            self.logger.error(f"Error searching reimbursement types: {str(e)}")
            raise RuntimeError(f"Failed to search reimbursement types: {str(e)}")
    
    # Analytics Repository Implementation
    
    async def get_reimbursement_types_statistics(self, company_id: str) -> Dict[str, Any]:
        """
        Get reimbursement types statistics.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Dict[str, Any]: Statistics data
        """
        try:
            collection = await self._get_collection(company_id)
            
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_types": {"$sum": 1},
                        "active_types": {
                            "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                        },
                        "inactive_types": {
                            "$sum": {"$cond": [{"$eq": ["$is_active", False]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            
            return {
                "total_types": 0,
                "active_types": 0,
                "inactive_types": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting reimbursement types statistics: {str(e)}")
            raise RuntimeError(f"Failed to get statistics: {str(e)}")
    
    async def get_reimbursement_types_usage_analytics(self, company_id: str) -> Dict[str, Any]:
        """
        Get reimbursement types usage analytics.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Dict[str, Any]: Usage analytics data
        """
        try:
            # This would require joining with reimbursements collection
            # For now, return basic analytics
            collection = await self._get_collection(company_id)
            
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1},
                        "types": {"$push": "$name"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            return {
                "categories": result,
                "total_categories": len(result)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting usage analytics: {str(e)}")
            raise RuntimeError(f"Failed to get usage analytics: {str(e)}")
    
    # Health Check Methods
    
    async def health_check(self, company_id: str) -> Dict[str, Any]:
        """
        Perform health check on the reimbursement types repository.
        
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
            explain_result = await collection.find({"is_active": True}).explain()
            
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