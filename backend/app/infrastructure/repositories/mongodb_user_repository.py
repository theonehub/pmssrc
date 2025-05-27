"""
MongoDB User Repository Implementation
Following SOLID principles and DDD patterns for user data access
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from domain.entities.user import User
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.user_credentials import UserRole, UserStatus, Gender
from application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository, UserAnalyticsRepository,
    UserProfileRepository, UserBulkOperationsRepository, UserRepository
)
from application.dto.user_dto import (
    UserSearchFiltersDTO, UserStatisticsDTO, UserAnalyticsDTO,
    UserProfileCompletionDTO
)
from infrastructure.database.database_connector import DatabaseConnector
from domain.events.user_events import UserCreated, UserUpdated, UserDeleted

logger = logging.getLogger(__name__)


class MongoDBUserRepository(UserRepository):
    """
    MongoDB implementation of user repository following DDD patterns.
    
    Implements all user repository interfaces in a single class for simplicity
    while maintaining SOLID principles through interface segregation.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "users_info"
        
    def _get_collection(self, organization_id: Optional[str] = None) -> Collection:
        """Get users collection for specific organization or global."""
        db_name = organization_id if organization_id else "global_database"
        db = self.db_connector.get_database(db_name)
        return db[self._collection_name]
    
    def _user_to_document(self, user: User) -> Dict[str, Any]:
        """Convert domain entity to database document."""
        return {
            "employee_id": str(user.employee_id),
            "email": user.email.value,
            "name": user.name,
            "gender": user.gender.value,
            "date_of_birth": user.date_of_birth,
            "date_of_joining": user.date_of_joining,
            "date_of_leaving": user.date_of_leaving,
            "mobile": user.mobile,
            "password_hash": user.credentials.password_hash,
            "role": user.credentials.role.value,
            "status": user.credentials.status.value,
            "department": user.department,
            "designation": user.designation,
            "location": user.location,
            "manager_id": str(user.manager_id) if user.manager_id else None,
            "salary": user.salary,
            "pan_number": user.pan_number,
            "aadhar_number": user.aadhar_number,
            "bank_account_number": user.bank_account_number,
            "ifsc_code": user.ifsc_code,
            "photo_path": user.photo_path,
            "pan_document_path": user.pan_document_path,
            "aadhar_document_path": user.aadhar_document_path,
            "leave_balance": user.leave_balance,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "created_by": user.created_by,
            "updated_by": user.updated_by,
            "organization_id": user.organization_id,
            "last_login": user.last_login,
            "login_count": user.login_count,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "password_changed_at": user.password_changed_at,
            "custom_permissions": user.custom_permissions,
            "profile_completion_percentage": user.profile_completion_percentage,
            "version": user.version
        }
    
    def _document_to_user(self, document: Dict[str, Any]) -> User:
        """Convert database document to domain entity."""
        return User.reconstruct(
            employee_id=EmployeeId(document["employee_id"]),
            email=document["email"],
            name=document["name"],
            gender=Gender(document["gender"]),
            date_of_birth=document["date_of_birth"],
            date_of_joining=document["date_of_joining"],
            date_of_leaving=document.get("date_of_leaving"),
            mobile=document["mobile"],
            password_hash=document["password_hash"],
            role=UserRole(document["role"]),
            status=UserStatus(document["status"]),
            department=document["department"],
            designation=document["designation"],
            location=document["location"],
            manager_id=EmployeeId(document["manager_id"]) if document.get("manager_id") else None,
            salary=document.get("salary"),
            pan_number=document.get("pan_number"),
            aadhar_number=document.get("aadhar_number"),
            bank_account_number=document.get("bank_account_number"),
            ifsc_code=document.get("ifsc_code"),
            photo_path=document.get("photo_path"),
            pan_document_path=document.get("pan_document_path"),
            aadhar_document_path=document.get("aadhar_document_path"),
            leave_balance=document.get("leave_balance", {}),
            is_active=document.get("is_active", True),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at"),
            created_by=document.get("created_by"),
            updated_by=document.get("updated_by"),
            organization_id=document.get("organization_id"),
            last_login=document.get("last_login"),
            login_count=document.get("login_count", 0),
            failed_login_attempts=document.get("failed_login_attempts", 0),
            locked_until=document.get("locked_until"),
            password_changed_at=document.get("password_changed_at"),
            custom_permissions=document.get("custom_permissions", []),
            profile_completion_percentage=document.get("profile_completion_percentage", 0.0),
            version=document.get("version", 1)
        )
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        # Implementation would depend on event publisher
        for event in events:
            logger.info(f"Publishing event: {type(event).__name__}")
    
    # Command Repository Implementation
    async def save(self, user: User) -> User:
        """Save a user (create or update)."""
        try:
            collection = self._get_collection(user.organization_id)
            document = self._user_to_document(user)
            
            # Use upsert to handle both create and update
            result = await collection.replace_one(
                {"employee_id": str(user.employee_id)},
                document,
                upsert=True
            )
            
            # Publish domain events
            await self._publish_events(user.get_domain_events())
            user.clear_domain_events()
            
            logger.info(f"User saved: {user.employee_id}")
            return user
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error saving user {user.employee_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving user {user.employee_id}: {e}")
            raise
    
    async def save_batch(self, users: List[User]) -> List[User]:
        """Save multiple users in a batch operation."""
        try:
            # Group users by organization
            users_by_org = {}
            for user in users:
                org_id = user.organization_id or "global_database"
                if org_id not in users_by_org:
                    users_by_org[org_id] = []
                users_by_org[org_id].append(user)
            
            saved_users = []
            for org_id, org_users in users_by_org.items():
                collection = self._get_collection(org_id)
                
                # Prepare bulk operations
                operations = []
                for user in org_users:
                    document = self._user_to_document(user)
                    operations.append({
                        "replaceOne": {
                            "filter": {"employee_id": str(user.employee_id)},
                            "replacement": document,
                            "upsert": True
                        }
                    })
                
                # Execute bulk write
                if operations:
                    await collection.bulk_write(operations)
                    saved_users.extend(org_users)
                    
                    # Publish events for all users
                    for user in org_users:
                        await self._publish_events(user.get_domain_events())
                        user.clear_domain_events()
            
            logger.info(f"Batch saved {len(saved_users)} users")
            return saved_users
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise
    
    async def delete(self, user_id: EmployeeId, soft_delete: bool = True) -> bool:
        """Delete a user by ID."""
        try:
            # For soft delete, we need to find the user first to get organization
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            collection = self._get_collection(user.organization_id)
            
            if soft_delete:
                # Soft delete - mark as deleted
                result = await collection.update_one(
                    {"employee_id": str(user_id)},
                    {
                        "$set": {
                            "is_deleted": True,
                            "deleted_at": datetime.utcnow(),
                            "status": UserStatus.INACTIVE.value
                        }
                    }
                )
            else:
                # Hard delete
                result = await collection.delete_one({"employee_id": str(user_id)})
            
            if result.modified_count > 0 or result.deleted_count > 0:
                # Publish delete event
                delete_event = UserDeletedEvent(
                    user_id=user_id,
                    organization_id=user.organization_id,
                    soft_delete=soft_delete,
                    deleted_at=datetime.utcnow()
                )
                await self._publish_events([delete_event])
                
                logger.info(f"User deleted: {user_id} (soft: {soft_delete})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, user_id: EmployeeId) -> Optional[User]:
        """Get user by ID."""
        try:
            # Try global database first, then organization databases
            for org_id in [None, "global_database"]:  # Add more org IDs as needed
                collection = self._get_collection(org_id)
                document = await collection.find_one({
                    "employee_id": str(user_id),
                    "is_deleted": {"$ne": True}
                })
                
                if document:
                    return self._document_to_user(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            # Search across all organization databases
            for org_id in [None, "global_database"]:  # Add more org IDs as needed
                collection = self._get_collection(org_id)
                document = await collection.find_one({
                    "email": email,
                    "is_deleted": {"$ne": True}
                })
                
                if document:
                    return self._document_to_user(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    async def get_by_mobile(self, mobile: str) -> Optional[User]:
        """Get user by mobile number."""
        try:
            for org_id in [None, "global_database"]:
                collection = self._get_collection(org_id)
                document = await collection.find_one({
                    "mobile": mobile,
                    "is_deleted": {"$ne": True}
                })
                
                if document:
                    return self._document_to_user(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by mobile {mobile}: {e}")
            raise
    
    async def get_by_pan_number(self, pan_number: str) -> Optional[User]:
        """Get user by PAN number."""
        try:
            for org_id in [None, "global_database"]:
                collection = self._get_collection(org_id)
                document = await collection.find_one({
                    "pan_number": pan_number,
                    "is_deleted": {"$ne": True}
                })
                
                if document:
                    return self._document_to_user(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by PAN {pan_number}: {e}")
            raise
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        include_deleted: bool = False,
        organization_id: Optional[str] = None
    ) -> List[User]:
        """Get all users with pagination."""
        try:
            collection = self._get_collection(organization_id)
            
            # Build filter
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            if not include_inactive:
                filter_query["is_active"] = True
            
            # Execute query
            cursor = collection.find(filter_query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            users = [self._document_to_user(doc) for doc in documents]
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise
    
    async def search(self, filters: UserSearchFiltersDTO) -> List[User]:
        """Search users with filters."""
        try:
            collection = self._get_collection(filters.organization_id)
            
            # Build search query
            query = {}
            
            # Text search
            if filters.search_term:
                query["$or"] = [
                    {"name": {"$regex": filters.search_term, "$options": "i"}},
                    {"email": {"$regex": filters.search_term, "$options": "i"}},
                    {"employee_id": {"$regex": filters.search_term, "$options": "i"}}
                ]
            
            # Role filter
            if filters.role:
                query["role"] = filters.role
            
            # Status filter
            if filters.status:
                query["status"] = filters.status
            
            # Department filter
            if filters.department:
                query["department"] = filters.department
            
            # Manager filter
            if filters.manager_id:
                query["manager_id"] = filters.manager_id
            
            # Date range filters
            if filters.date_joined_from or filters.date_joined_to:
                date_filter = {}
                if filters.date_joined_from:
                    date_filter["$gte"] = filters.date_joined_from
                if filters.date_joined_to:
                    date_filter["$lte"] = filters.date_joined_to
                query["date_of_joining"] = date_filter
            
            # Active/deleted filters
            if not filters.include_deleted:
                query["is_deleted"] = {"$ne": True}
            if not filters.include_inactive:
                query["is_active"] = True
            
            # Execute query with pagination
            cursor = collection.find(query)
            
            # Apply sorting
            if filters.sort_by:
                sort_direction = DESCENDING if filters.sort_desc else ASCENDING
                cursor = cursor.sort(filters.sort_by, sort_direction)
            
            # Apply pagination
            cursor = cursor.skip(filters.skip).limit(filters.limit)
            
            documents = await cursor.to_list(length=filters.limit)
            users = [self._document_to_user(doc) for doc in documents]
            
            logger.info(f"Search returned {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise
    
    async def get_by_role(self, role: UserRole, organization_id: Optional[str] = None) -> List[User]:
        """Get users by role."""
        try:
            collection = self._get_collection(organization_id)
            cursor = collection.find({
                "role": role.value,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            raise
    
    async def get_by_status(self, status: UserStatus, organization_id: Optional[str] = None) -> List[User]:
        """Get users by status."""
        try:
            collection = self._get_collection(organization_id)
            cursor = collection.find({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by status {status}: {e}")
            raise
    
    async def get_by_department(self, department: str, organization_id: Optional[str] = None) -> List[User]:
        """Get users by department."""
        try:
            collection = self._get_collection(organization_id)
            cursor = collection.find({
                "department": department,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by department {department}: {e}")
            raise
    
    async def get_by_manager(self, manager_id: EmployeeId, organization_id: Optional[str] = None) -> List[User]:
        """Get users by manager."""
        try:
            collection = self._get_collection(organization_id)
            cursor = collection.find({
                "manager_id": str(manager_id),
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            raise
    
    async def get_active_users(self, organization_id: Optional[str] = None) -> List[User]:
        """Get all active users."""
        try:
            collection = self._get_collection(organization_id)
            cursor = collection.find({
                "is_active": True,
                "status": {"$ne": UserStatus.INACTIVE.value},
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            raise
    
    async def get_locked_users(self, organization_id: Optional[str] = None) -> List[User]:
        """Get all locked users."""
        try:
            collection = self._get_collection(organization_id)
            cursor = collection.find({
                "status": UserStatus.LOCKED.value,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting locked users: {e}")
            raise
    
    # Count methods
    async def count_total(self, include_deleted: bool = False, organization_id: Optional[str] = None) -> int:
        """Count total users."""
        try:
            collection = self._get_collection(organization_id)
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            return await collection.count_documents(filter_query)
            
        except Exception as e:
            logger.error(f"Error counting total users: {e}")
            raise
    
    async def count_by_status(self, status: UserStatus, organization_id: Optional[str] = None) -> int:
        """Count users by status."""
        try:
            collection = self._get_collection(organization_id)
            return await collection.count_documents({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting users by status {status}: {e}")
            raise
    
    async def count_by_role(self, role: UserRole, organization_id: Optional[str] = None) -> int:
        """Count users by role."""
        try:
            collection = self._get_collection(organization_id)
            return await collection.count_documents({
                "role": role.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting users by role {role}: {e}")
            raise
    
    # Existence checks
    async def exists_by_email(self, email: str, exclude_id: Optional[EmployeeId] = None, organization_id: Optional[str] = None) -> bool:
        """Check if user exists by email."""
        try:
            collection = self._get_collection(organization_id)
            query = {
                "email": email,
                "is_deleted": {"$ne": True}
            }
            
            if exclude_id:
                query["employee_id"] = {"$ne": str(exclude_id)}
            
            count = await collection.count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {e}")
            raise
    
    async def exists_by_mobile(self, mobile: str, exclude_id: Optional[EmployeeId] = None, organization_id: Optional[str] = None) -> bool:
        """Check if user exists by mobile."""
        try:
            collection = self._get_collection(organization_id)
            query = {
                "mobile": mobile,
                "is_deleted": {"$ne": True}
            }
            
            if exclude_id:
                query["employee_id"] = {"$ne": str(exclude_id)}
            
            count = await collection.count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking mobile existence {mobile}: {e}")
            raise
    
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[EmployeeId] = None, organization_id: Optional[str] = None) -> bool:
        """Check if user exists by PAN number."""
        try:
            collection = self._get_collection(organization_id)
            query = {
                "pan_number": pan_number,
                "is_deleted": {"$ne": True}
            }
            
            if exclude_id:
                query["employee_id"] = {"$ne": str(exclude_id)}
            
            count = await collection.count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking PAN existence {pan_number}: {e}")
            raise
    
    # Analytics Repository Implementation
    async def get_statistics(self, organization_id: Optional[str] = None) -> UserStatisticsDTO:
        """Get comprehensive user statistics."""
        try:
            collection = self._get_collection(organization_id)
            
            # Aggregate statistics
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {
                    "$group": {
                        "_id": None,
                        "total_users": {"$sum": 1},
                        "active_users": {
                            "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                        },
                        "inactive_users": {
                            "$sum": {"$cond": [{"$eq": ["$is_active", False]}, 1, 0]}
                        },
                        "roles": {"$addToSet": "$role"},
                        "departments": {"$addToSet": "$department"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            stats = result[0] if result else {}
            
            return UserStatisticsDTO(
                total_users=stats.get("total_users", 0),
                active_users=stats.get("active_users", 0),
                inactive_users=stats.get("inactive_users", 0),
                total_roles=len(stats.get("roles", [])),
                total_departments=len(stats.get("departments", []))
            )
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            raise
    
    async def get_analytics(self, organization_id: Optional[str] = None) -> UserAnalyticsDTO:
        """Get detailed user analytics."""
        try:
            # Implementation would include complex analytics queries
            # For now, return basic analytics
            stats = await self.get_statistics(organization_id)
            
            return UserAnalyticsDTO(
                user_statistics=stats,
                growth_trends={},
                activity_patterns={},
                security_metrics={}
            )
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            raise
    
    # Additional methods for other interfaces...
    # (Implementation continues with remaining methods) 