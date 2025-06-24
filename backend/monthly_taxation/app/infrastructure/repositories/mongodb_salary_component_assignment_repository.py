"""
MongoDB Salary Component Assignment Repository Implementation
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.application.interfaces.repositories.salary_component_assignment_repository import (
    SalaryComponentAssignmentRepository,
    GlobalSalaryComponentRepository
)
from app.domain.entities.salary_component_assignment import (
    SalaryComponentAssignment, 
    AssignmentStatus,
    BulkComponentAssignment
)
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.component_id import ComponentId
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

logger = logging.getLogger(__name__)


class MongoDBSalaryComponentAssignmentRepository(SalaryComponentAssignmentRepository):
    """MongoDB implementation of salary component assignment repository"""
    
    def __init__(self, db_connector: MongoDBConnector):
        self.db_connector = db_connector
        self.collection_name = "salary_component_assignments"
        self._connection_string = None
        self._client_options = None
    
    def set_connection_config(self, connection_string: str, **options):
        """Set connection configuration"""
        self._connection_string = connection_string
        self._client_options = options
    
    async def _get_collection(self):
        """Get MongoDB collection for assignments"""
        if not self.db_connector.is_connected:
            try:
                if self._connection_string and self._client_options:
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Use global database for assignments
        db = await self.db_connector.get_database("pms_global_database")
        collection = db[self.collection_name]
        
        # Ensure indexes
        await self._ensure_indexes(collection)
        
        return collection
    
    async def _ensure_indexes(self, collection):
        """Ensure database indexes exist"""
        try:
            # Compound index for organization and component
            await collection.create_index([
                ("organization_id", 1),
                ("component_id", 1)
            ], unique=True)
            
            # Index for organization
            await collection.create_index([("organization_id", 1)])
            
            # Index for component
            await collection.create_index([("component_id", 1)])
            
            # Index for status
            await collection.create_index([("status", 1)])
            
            # Index for assignment date
            await collection.create_index([("assigned_at", -1)])
            
            logger.info("Salary component assignment indexes ensured")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    async def save_assignment(self, assignment: SalaryComponentAssignment) -> SalaryComponentAssignment:
        """Save a component assignment"""
        try:
            collection = await self._get_collection()
            
            # Check if assignment already exists
            existing = await collection.find_one({
                "organization_id": str(assignment.organization_id),
                "component_id": str(assignment.component_id)
            })
            
            assignment_dict = self._entity_to_dict(assignment)
            
            if existing:
                # Update existing assignment
                await collection.replace_one(
                    {"_id": existing["_id"]},
                    assignment_dict
                )
                logger.info(f"Updated assignment for org {assignment.organization_id}, component {assignment.component_id}")
            else:
                # Insert new assignment
                result = await collection.insert_one(assignment_dict)
                assignment_dict["_id"] = result.inserted_id
                logger.info(f"Created assignment for org {assignment.organization_id}, component {assignment.component_id}")
            
            return self._dict_to_entity(assignment_dict)
            
        except Exception as e:
            logger.error(f"Error saving assignment: {e}")
            raise
    
    async def save_assignments(self, assignments: List[SalaryComponentAssignment]) -> List[SalaryComponentAssignment]:
        """Save multiple component assignments"""
        try:
            collection = await self._get_collection()
            
            # Prepare documents for bulk operation
            operations = []
            for assignment in assignments:
                assignment_dict = self._entity_to_dict(assignment)
                
                # Use upsert to handle both insert and update
                operations.append({
                    "replaceOne": {
                        "filter": {
                            "organization_id": str(assignment.organization_id),
                            "component_id": str(assignment.component_id)
                        },
                        "replacement": assignment_dict,
                        "upsert": True
                    }
                })
            
            if operations:
                result = await collection.bulk_write(operations)
                logger.info(f"Bulk saved {len(assignments)} assignments")
            
            return assignments
            
        except Exception as e:
            logger.error(f"Error saving assignments: {e}")
            raise
    
    async def get_assignment_by_id(self, assignment_id: str) -> Optional[SalaryComponentAssignment]:
        """Get assignment by ID"""
        try:
            collection = await self._get_collection()
            
            assignment_dict = await collection.find_one({"assignment_id": assignment_id})
            
            if not assignment_dict:
                return None
            
            return self._dict_to_entity(assignment_dict)
            
        except Exception as e:
            logger.error(f"Error getting assignment {assignment_id}: {e}")
            raise
    
    async def get_assignments_by_organization(
        self, 
        organization_id: OrganizationId,
        include_inactive: bool = False
    ) -> List[SalaryComponentAssignment]:
        """Get all assignments for an organization"""
        try:
            collection = await self._get_collection()
            
            query = {"organization_id": str(organization_id)}
            if not include_inactive:
                query["status"] = AssignmentStatus.ACTIVE.value
            
            cursor = collection.find(query).sort("assigned_at", -1)
            assignment_dicts = await cursor.to_list(length=None)
            
            assignments = [self._dict_to_entity(doc) for doc in assignment_dicts]
            
            return assignments
            
        except Exception as e:
            logger.error(f"Error getting assignments for organization {organization_id}: {e}")
            raise
    
    async def get_assignments_by_component(
        self, 
        component_id: ComponentId,
        include_inactive: bool = False
    ) -> List[SalaryComponentAssignment]:
        """Get all assignments for a component"""
        try:
            collection = await self._get_collection()
            
            query = {"component_id": str(component_id)}
            if not include_inactive:
                query["status"] = AssignmentStatus.ACTIVE.value
            
            cursor = collection.find(query).sort("assigned_at", -1)
            assignment_dicts = await cursor.to_list(length=None)
            
            assignments = [self._dict_to_entity(doc) for doc in assignment_dicts]
            
            return assignments
            
        except Exception as e:
            logger.error(f"Error getting assignments for component {component_id}: {e}")
            raise
    
    async def get_assignment_by_organization_and_component(
        self,
        organization_id: OrganizationId,
        component_id: ComponentId
    ) -> Optional[SalaryComponentAssignment]:
        """Get specific assignment by organization and component"""
        try:
            collection = await self._get_collection()
            
            assignment_dict = await collection.find_one({
                "organization_id": str(organization_id),
                "component_id": str(component_id)
            })
            
            if not assignment_dict:
                return None
            
            return self._dict_to_entity(assignment_dict)
            
        except Exception as e:
            logger.error(f"Error getting assignment for org {organization_id}, component {component_id}: {e}")
            raise
    
    async def update_assignment(self, assignment: SalaryComponentAssignment) -> SalaryComponentAssignment:
        """Update an existing assignment"""
        try:
            collection = await self._get_collection()
            
            assignment_dict = self._entity_to_dict(assignment)
            
            result = await collection.replace_one(
                {"assignment_id": assignment.assignment_id},
                assignment_dict
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Assignment {assignment.assignment_id} not found")
            
            logger.info(f"Updated assignment {assignment.assignment_id}")
            return assignment
            
        except Exception as e:
            logger.error(f"Error updating assignment {assignment.assignment_id}: {e}")
            raise
    
    async def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment"""
        try:
            collection = await self._get_collection()
            
            result = await collection.delete_one({"assignment_id": assignment_id})
            
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Deleted assignment {assignment_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting assignment {assignment_id}: {e}")
            raise
    
    async def delete_assignments_by_organization_and_components(
        self,
        organization_id: OrganizationId,
        component_ids: List[ComponentId]
    ) -> int:
        """Delete multiple assignments for an organization"""
        try:
            collection = await self._get_collection()
            
            result = await collection.delete_many({
                "organization_id": str(organization_id),
                "component_id": {"$in": [str(cid) for cid in component_ids]}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Deleted {deleted_count} assignments for organization {organization_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting assignments for organization {organization_id}: {e}")
            raise
    
    async def search_assignments(
        self,
        organization_id: Optional[OrganizationId] = None,
        component_id: Optional[ComponentId] = None,
        status: Optional[AssignmentStatus] = None,
        include_inactive: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[SalaryComponentAssignment], int]:
        """Search assignments with filters and pagination"""
        try:
            collection = await self._get_collection()
            
            # Build query
            query = {}
            if organization_id:
                query["organization_id"] = str(organization_id)
            if component_id:
                query["component_id"] = str(component_id)
            if status:
                query["status"] = status.value
            elif not include_inactive:
                query["status"] = AssignmentStatus.ACTIVE.value
            
            # Count total documents
            total_count = await collection.count_documents(query)
            
            # Calculate skip
            skip = (page - 1) * page_size
            
            # Execute query with pagination
            cursor = collection.find(query).skip(skip).limit(page_size).sort("assigned_at", -1)
            assignment_dicts = await cursor.to_list(length=page_size)
            
            assignments = [self._dict_to_entity(doc) for doc in assignment_dicts]
            
            return assignments, total_count
            
        except Exception as e:
            logger.error(f"Error searching assignments: {e}")
            raise
    
    async def get_assignment_summary(self, organization_id: OrganizationId) -> dict:
        """Get assignment summary for an organization"""
        try:
            collection = await self._get_collection()
            
            # Get total assignments
            total_count = await collection.count_documents({"organization_id": str(organization_id)})
            
            # Get active assignments
            active_count = await collection.count_documents({
                "organization_id": str(organization_id),
                "status": AssignmentStatus.ACTIVE.value
            })
            
            # Get inactive assignments
            inactive_count = await collection.count_documents({
                "organization_id": str(organization_id),
                "status": AssignmentStatus.INACTIVE.value
            })
            
            # Get last assignment date
            last_assignment = await collection.find_one(
                {"organization_id": str(organization_id)},
                sort=[("assigned_at", -1)]
            )
            
            last_assignment_date = last_assignment["assigned_at"] if last_assignment else None
            
            return {
                "total_assignments": total_count,
                "active_assignments": active_count,
                "inactive_assignments": inactive_count,
                "last_assignment_date": last_assignment_date
            }
            
        except Exception as e:
            logger.error(f"Error getting assignment summary for organization {organization_id}: {e}")
            raise
    
    async def check_component_assigned(
        self,
        organization_id: OrganizationId,
        component_id: ComponentId
    ) -> bool:
        """Check if a component is assigned to an organization"""
        try:
            collection = await self._get_collection()
            
            assignment = await collection.find_one({
                "organization_id": str(organization_id),
                "component_id": str(component_id),
                "status": AssignmentStatus.ACTIVE.value
            })
            
            return assignment is not None
            
        except Exception as e:
            logger.error(f"Error checking component assignment: {e}")
            raise
    
    async def get_effective_assignments(
        self,
        organization_id: OrganizationId,
        as_of_date: Optional[datetime] = None
    ) -> List[SalaryComponentAssignment]:
        """Get effective assignments for an organization as of a specific date"""
        try:
            assignments = await self.get_assignments_by_organization(organization_id, include_inactive=True)
            
            if as_of_date is None:
                as_of_date = datetime.utcnow()
            
            # Filter for effective assignments
            effective_assignments = [
                assignment for assignment in assignments
                if assignment.is_effective(as_of_date)
            ]
            
            return effective_assignments
            
        except Exception as e:
            logger.error(f"Error getting effective assignments: {e}")
            raise
    
    def _entity_to_dict(self, assignment: SalaryComponentAssignment) -> dict:
        """Convert assignment entity to dictionary"""
        return {
            "assignment_id": assignment.assignment_id,
            "organization_id": str(assignment.organization_id),
            "component_id": str(assignment.component_id),
            "status": assignment.status.value,
            "assigned_by": assignment.assigned_by,
            "assigned_at": assignment.assigned_at,
            "organization_specific_config": assignment.organization_specific_config,
            "notes": assignment.notes,
            "effective_from": assignment.effective_from,
            "effective_to": assignment.effective_to
        }
    
    def _dict_to_entity(self, assignment_dict: dict) -> SalaryComponentAssignment:
        """Convert dictionary to assignment entity"""
        return SalaryComponentAssignment(
            assignment_id=assignment_dict["assignment_id"],
            organization_id=OrganizationId(assignment_dict["organization_id"]),
            component_id=ComponentId(assignment_dict["component_id"]),
            status=AssignmentStatus(assignment_dict["status"]),
            assigned_by=assignment_dict["assigned_by"],
            assigned_at=assignment_dict["assigned_at"],
            organization_specific_config=assignment_dict.get("organization_specific_config", {}),
            notes=assignment_dict.get("notes"),
            effective_from=assignment_dict.get("effective_from"),
            effective_to=assignment_dict.get("effective_to")
        )


class MongoDBGlobalSalaryComponentRepository(GlobalSalaryComponentRepository):
    """MongoDB implementation of global salary component repository"""
    
    def __init__(self, db_connector: MongoDBConnector):
        self.db_connector = db_connector
        self.collection_name = "salary_components"
        self._connection_string = None
        self._client_options = None
    
    def set_connection_config(self, connection_string: str, **options):
        """Set connection configuration"""
        self._connection_string = connection_string
        self._client_options = options
    
    async def _get_collection(self):
        """Get MongoDB collection for global components"""
        if not self.db_connector.is_connected:
            try:
                if self._connection_string and self._client_options:
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Use global database for components
        db = await self.db_connector.get_database("global_database")
        collection = db[self.collection_name]
        
        return collection
    
    async def get_all_components(self) -> List[dict]:
        """Get all global salary components"""
        try:
            collection = await self._get_collection()
            
            cursor = collection.find({"is_active": True}).sort("name", 1)
            components = await cursor.to_list(length=None)
            
            return components
            
        except Exception as e:
            logger.error(f"Error getting all components: {e}")
            raise
    
    async def get_component_by_id(self, component_id: str) -> Optional[dict]:
        """Get global component by ID"""
        try:
            collection = await self._get_collection()
            
            component = await collection.find_one({"component_id": component_id})
            
            return component
            
        except Exception as e:
            logger.error(f"Error getting component {component_id}: {e}")
            raise
    
    async def get_components_by_type(self, component_type: str) -> List[dict]:
        """Get global components by type"""
        try:
            collection = await self._get_collection()
            
            cursor = collection.find({
                "component_type": component_type.upper(),
                "is_active": True
            }).sort("name", 1)
            
            components = await cursor.to_list(length=None)
            
            return components
            
        except Exception as e:
            logger.error(f"Error getting components by type {component_type}: {e}")
            raise
    
    async def get_active_components(self) -> List[dict]:
        """Get all active global components"""
        try:
            collection = await self._get_collection()
            
            cursor = collection.find({"is_active": True}).sort("name", 1)
            components = await cursor.to_list(length=None)
            
            return components
            
        except Exception as e:
            logger.error(f"Error getting active components: {e}")
            raise
    
    async def search_components(
        self,
        search_term: Optional[str] = None,
        component_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Search global components with filters and pagination"""
        try:
            collection = await self._get_collection()
            
            # Build query
            query = {}
            if component_type:
                query["component_type"] = component_type.upper()
            if is_active is not None:
                query["is_active"] = is_active
            
            # Add search term filtering
            if search_term:
                search_regex = {"$regex": search_term, "$options": "i"}
                query["$or"] = [
                    {"component_id": search_regex},
                    {"name": search_regex},
                    {"description": search_regex}
                ]
            
            # Count total documents
            total_count = await collection.count_documents(query)
            
            # Calculate skip
            skip = (page - 1) * page_size
            
            # Execute query with pagination
            cursor = collection.find(query).skip(skip).limit(page_size).sort("name", 1)
            components = await cursor.to_list(length=page_size)
            
            return components, total_count
            
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            raise 