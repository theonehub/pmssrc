"""
SOLID-Compliant User Repository Implementation
Replaces procedural database functions with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Simplified domain objects for migration compatibility
class EmployeeId:
    def __init__(self, value: str):
        self.value = value
    
    def __str__(self):
        return self.value

class UserSearchFiltersDTO:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class UserStatisticsDTO:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Try to import from existing modules, fall back to simplified versions
try:
    from domain.entities.user import User
except ImportError:
    class User:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

try:
    from domain.value_objects.employee_id import EmployeeId as DomainEmployeeId
    EmployeeId = DomainEmployeeId
except ImportError:
    pass

try:
    from application.dto.user_dto import UserSearchFiltersDTO as AppUserSearchFiltersDTO
    UserSearchFiltersDTO = AppUserSearchFiltersDTO
except ImportError:
    pass

try:
    from application.dto.user_dto import UserStatisticsDTO as AppUserStatisticsDTO
    UserStatisticsDTO = AppUserStatisticsDTO
except ImportError:
    pass

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector
# from domain.events.user_events import UserCreated, UserUpdated, UserDeleted

logger = logging.getLogger(__name__)


class SolidUserRepository(BaseRepository[User]):
    """
    SOLID-compliant user repository implementation.
    
    Replaces the procedural database functions with proper SOLID architecture:
    - Single Responsibility: Only handles user data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements UserRepository interface
    - Interface Segregation: Implements focused user repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize user repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "users_info")
        
    def _entity_to_document(self, user: User) -> Dict[str, Any]:
        """
        Convert User entity to database document.
        
        Args:
            user: User entity to convert
            
        Returns:
            Database document representation
        """
        return {
            "emp_id": str(getattr(user, 'employee_id', getattr(user, 'emp_id', ''))),
            "email": getattr(user, 'email', ''),
            "name": getattr(user, 'name', ''),
            "gender": getattr(user, 'gender', ''),
            "date_of_birth": getattr(user, 'date_of_birth', None),
            "date_of_joining": getattr(user, 'date_of_joining', None),
            "date_of_leaving": getattr(user, 'date_of_leaving', None),
            "mobile": getattr(user, 'mobile', ''),
            "password": getattr(user, 'password', getattr(user, 'password_hash', '')),
            "role": getattr(user, 'role', ''),
            "status": getattr(user, 'status', 'active'),
            "department": getattr(user, 'department', ''),
            "designation": getattr(user, 'designation', ''),
            "location": getattr(user, 'location', ''),
            "manager_id": getattr(user, 'manager_id', None),
            "salary": getattr(user, 'salary', None),
            "pan_number": getattr(user, 'pan_number', ''),
            "aadhar_number": getattr(user, 'aadhar_number', ''),
            "bank_account_number": getattr(user, 'bank_account_number', ''),
            "ifsc_code": getattr(user, 'ifsc_code', ''),
            "photo_path": getattr(user, 'photo_path', ''),
            "pan_document_path": getattr(user, 'pan_document_path', ''),
            "aadhar_document_path": getattr(user, 'aadhar_document_path', ''),
            "leave_balance": getattr(user, 'leave_balance', {}),
            "is_active": getattr(user, 'is_active', True),
            "created_at": getattr(user, 'created_at', datetime.utcnow()),
            "updated_at": getattr(user, 'updated_at', datetime.utcnow()),
            "created_by": getattr(user, 'created_by', 'system'),
            "updated_by": getattr(user, 'updated_by', 'system'),
            "organization_id": getattr(user, 'organization_id', None),
            "last_login": getattr(user, 'last_login', None),
            "login_count": getattr(user, 'login_count', 0),
            "failed_login_attempts": getattr(user, 'failed_login_attempts', 0),
            "locked_until": getattr(user, 'locked_until', None),
            "password_changed_at": getattr(user, 'password_changed_at', None),
            "custom_permissions": getattr(user, 'custom_permissions', []),
            "profile_completion_percentage": getattr(user, 'profile_completion_percentage', 0.0),
            "version": getattr(user, 'version', 1)
        }
    
    def _document_to_entity(self, document: Dict[str, Any]) -> User:
        """
        Convert database document to User entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            User entity instance
        """
        # Create a simple User object that works with existing code
        class SimpleUser:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        return SimpleUser(
            employee_id=document.get("emp_id"),
            emp_id=document.get("emp_id"),  # For backward compatibility
            email=document.get("email"),
            name=document.get("name"),
            gender=document.get("gender"),
            date_of_birth=document.get("date_of_birth"),
            date_of_joining=document.get("date_of_joining"),
            date_of_leaving=document.get("date_of_leaving"),
            mobile=document.get("mobile"),
            password=document.get("password"),
            role=document.get("role"),
            status=document.get("status"),
            department=document.get("department"),
            designation=document.get("designation"),
            location=document.get("location"),
            manager_id=document.get("manager_id"),
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
    
    # Command Repository Implementation
    async def save(self, user: User) -> User:
        """
        Save a user (create or update).
        
        Replaces: create_user() and update_user() functions
        """
        try:
            document = self._entity_to_document(user)
            organization_id = getattr(user, 'organization_id', None)
            
            # Use upsert to handle both create and update
            emp_id = str(getattr(user, 'employee_id', getattr(user, 'emp_id', '')))
            filters = {"emp_id": emp_id}
            await self._update_document(
                filters=filters,
                update_data=document,
                organization_id=organization_id,
                upsert=True
            )
            
            logger.info(f"User saved: {emp_id}")
            return user
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error saving user {emp_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving user {emp_id}: {e}")
            raise
    
    async def save_batch(self, users: List[User]) -> List[User]:
        """
        Save multiple users in a batch operation.
        
        Provides bulk operations not available in original procedural code.
        """
        try:
            saved_users = []
            for user in users:
                saved_user = await self.save(user)
                saved_users.append(saved_user)
            
            logger.info(f"Batch saved {len(saved_users)} users")
            return saved_users
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise
    
    async def delete(self, user_id: Union[EmployeeId, str], soft_delete: bool = True) -> bool:
        """
        Delete a user by ID.
        
        Provides delete functionality not available in original procedural code.
        """
        try:
            emp_id = str(user_id) if isinstance(user_id, str) else str(user_id.value if hasattr(user_id, 'value') else user_id)
            filters = {"emp_id": emp_id}
            result = await self._delete_document(
                filters=filters,
                soft_delete=soft_delete
            )
            
            if result:
                logger.info(f"User deleted: {emp_id}")
            else:
                logger.warning(f"User not found for deletion: {emp_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, user_id: Union[EmployeeId, str]) -> Optional[User]:
        """
        Get user by ID.
        
        Replaces: get_user_by_emp_id() function
        """
        try:
            emp_id = str(user_id) if isinstance(user_id, str) else str(user_id.value if hasattr(user_id, 'value') else user_id)
            filters = {"emp_id": emp_id}
            documents = await self._execute_query(filters=filters, limit=1)
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Provides email lookup not available in original procedural code.
        """
        try:
            filters = {"email": email}
            documents = await self._execute_query(filters=filters, limit=1)
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    async def get_by_mobile(self, mobile: str) -> Optional[User]:
        """
        Get user by mobile number.
        
        Provides mobile lookup not available in original procedural code.
        """
        try:
            filters = {"mobile": mobile}
            documents = await self._execute_query(filters=filters, limit=1)
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by mobile {mobile}: {e}")
            raise
    
    async def get_by_pan_number(self, pan_number: str) -> Optional[User]:
        """
        Get user by PAN number.
        
        Provides PAN lookup not available in original procedural code.
        """
        try:
            filters = {"pan_number": pan_number}
            documents = await self._execute_query(filters=filters, limit=1)
            
            if documents:
                return self._document_to_entity(documents[0])
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
        """
        Get all users with pagination.
        
        Replaces: get_all_users() function with enhanced filtering
        """
        try:
            filters = {}
            
            if not include_inactive:
                filters["is_active"] = True
            
            if not include_deleted:
                filters["is_deleted"] = {"$ne": True}
            
            documents = await self._execute_query(
                filters=filters,
                skip=skip,
                limit=limit,
                organization_id=organization_id
            )
            
            users = [self._document_to_entity(doc) for doc in documents]
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise
    
    async def get_by_manager(self, manager_id: Union[EmployeeId, str], organization_id: Optional[str] = None) -> List[User]:
        """
        Get users by manager ID.
        
        Replaces: get_users_by_manager_id() and get_emp_ids_by_manager_id() functions
        """
        try:
            mgr_id = str(manager_id) if isinstance(manager_id, str) else str(manager_id.value if hasattr(manager_id, 'value') else manager_id)
            filters = {"manager_id": mgr_id}
            documents = await self._execute_query(
                filters=filters,
                organization_id=organization_id
            )
            
            users = [self._document_to_entity(doc) for doc in documents]
            logger.info(f"Retrieved {len(users)} users for manager {mgr_id}")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            raise
    
    async def update_leave_balance(
        self, 
        user_id: Union[EmployeeId, str], 
        leave_name: str, 
        leave_count: int, 
        organization_id: Optional[str] = None
    ) -> bool:
        """
        Update leave balance for a user.
        
        Replaces: update_user_leave_balance() function
        """
        try:
            emp_id = str(user_id) if isinstance(user_id, str) else str(user_id.value if hasattr(user_id, 'value') else user_id)
            collection = self._get_collection(organization_id)
            
            result = await collection.update_one(
                {"emp_id": emp_id},
                {
                    "$inc": {f"leave_balance.{leave_name}": leave_count},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated leave balance for {emp_id}: {leave_name} += {leave_count}")
                return True
            else:
                logger.warning(f"No user found to update leave balance: {emp_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating leave balance for {user_id}: {e}")
            raise
    
    # Analytics Repository Implementation
    async def get_statistics(self, organization_id: Optional[str] = None) -> UserStatisticsDTO:
        """
        Get user statistics.
        
        Replaces: get_users_stats() function with enhanced analytics
        """
        try:
            # Get role statistics
            role_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            role_stats = await self._aggregate(role_pipeline, organization_id)
            role_counts = {item["_id"]: item["count"] for item in role_stats}
            
            # Get status statistics
            status_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_stats = await self._aggregate(status_pipeline, organization_id)
            status_counts = {item["_id"]: item["count"] for item in status_stats}
            
            # Get total count
            total_count = await self._count_documents(
                {"is_deleted": {"$ne": True}},
                organization_id
            )
            
            return UserStatisticsDTO(
                total_users=total_count,
                users_by_role=role_counts,
                users_by_status=status_counts,
                active_users=role_counts.get("active", 0),
                inactive_users=role_counts.get("inactive", 0)
            )
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            raise
    
    # Additional methods for compatibility with existing code
    async def create_user_legacy(self, user_data: Dict[str, Any], organization_id: str) -> Dict[str, Any]:
        """
        Legacy compatibility method for create_user() function.
        
        This provides backward compatibility while migrating to SOLID architecture.
        """
        try:
            document = user_data.copy()
            document_id = await self._insert_document(document, organization_id)
            
            logger.info(f"User created (legacy): {user_data.get('emp_id')}")
            return {
                "msg": "User created successfully",
                "inserted_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error creating user (legacy): {e}")
            raise
    
    async def get_all_users_legacy(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility method for get_all_users() function.
        
        This provides backward compatibility while migrating to SOLID architecture.
        """
        try:
            documents = await self._execute_query(
                filters={},
                organization_id=organization_id,
                limit=1000  # Large limit for legacy compatibility
            )
            
            logger.info(f"Retrieved {len(documents)} users (legacy)")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all users (legacy): {e}")
            raise
    
    async def get_users_stats_legacy(self, organization_id: str) -> Dict[str, int]:
        """
        Legacy compatibility method for get_users_stats() function.
        
        This provides backward compatibility while migrating to SOLID architecture.
        """
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            results = await self._aggregate(pipeline, organization_id)
            stats = {item["_id"]: item["count"] for item in results}
            
            logger.info(f"User stats (legacy): {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats (legacy): {e}")
            raise 