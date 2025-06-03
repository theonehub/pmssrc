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
    from app.domain.entities.user import User
except ImportError:
    class User:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

try:
    from app.domain.value_objects.employee_id import EmployeeId as DomainEmployeeId
    EmployeeId = DomainEmployeeId
except ImportError:
    pass

try:
    from app.application.dto.user_dto import UserSearchFiltersDTO as AppUserSearchFiltersDTO
    UserSearchFiltersDTO = AppUserSearchFiltersDTO
except ImportError:
    pass

try:
    from app.application.dto.user_dto import UserStatisticsDTO as AppUserStatisticsDTO
    UserStatisticsDTO = AppUserStatisticsDTO
except ImportError:
    pass

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector
# from app.domain.events.user_events import UserCreated, UserUpdated, UserDeleted

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
        # Get the actual employee_id value
        employee_id = getattr(user, 'employee_id', None)
        if employee_id:
            employee_id = str(employee_id)
        else:
            employee_id = getattr(user, 'employee_id', getattr(user, 'employee_id', ''))
        
        # Handle password - convert Password object to string
        password_value = getattr(user, 'password', '')
        if hasattr(password_value, 'hashed_value'):
            password_value = password_value.hashed_value
        elif hasattr(password_value, 'value'):
            password_value = password_value.value
        
        # Handle role - convert enum to string value
        role_value = getattr(user, 'role', '')
        if hasattr(role_value, 'value'):
            role_value = role_value.value
        elif hasattr(user, 'permissions') and hasattr(user.permissions, 'role'):
            if hasattr(user.permissions.role, 'value'):
                role_value = user.permissions.role.value
        
        # Handle status - convert enum to string value  
        status_value = getattr(user, 'status', 'active')
        if hasattr(status_value, 'value'):
            status_value = status_value.value
        
        # Handle personal details
        personal_details = getattr(user, 'personal_details', None)
        gender_value = ''
        mobile_value = ''
        pan_number_value = ''
        aadhar_number_value = ''
        date_of_birth_value = None
        date_of_joining_value = None
        
        if personal_details:
            gender_value = getattr(personal_details, 'gender', '')
            if hasattr(gender_value, 'value'):
                gender_value = gender_value.value
            
            mobile_value = getattr(personal_details, 'mobile', '')
            pan_number_value = getattr(personal_details, 'pan_number', '')
            aadhar_number_value = getattr(personal_details, 'aadhar_number', '')
            date_of_birth_value = getattr(personal_details, 'date_of_birth', None)
            date_of_joining_value = getattr(personal_details, 'date_of_joining', None)
            
            # Convert date to datetime for MongoDB compatibility
            if date_of_birth_value and hasattr(date_of_birth_value, 'year'):
                from datetime import datetime as dt
                if isinstance(date_of_birth_value, dt):
                    date_of_birth_value = date_of_birth_value
                else:  # datetime.date
                    date_of_birth_value = dt.combine(date_of_birth_value, dt.min.time())

            if date_of_joining_value and hasattr(date_of_joining_value, 'year'):
                from datetime import datetime as dt
                if isinstance(date_of_joining_value, dt):
                    date_of_joining_value = date_of_joining_value
                else:  # datetime.date
                    date_of_joining_value = dt.combine(date_of_joining_value, dt.min.time())
        
        # Handle documents
        documents = getattr(user, 'documents', None)
        photo_path_value = ''
        pan_document_path_value = ''
        aadhar_document_path_value = ''
        
        if documents:
            photo_path_value = getattr(documents, 'photo_path', '')
            pan_document_path_value = getattr(documents, 'pan_document_path', '') 
            aadhar_document_path_value = getattr(documents, 'aadhar_document_path', '')
        
        return {
            "employee_id": employee_id,
            "username": getattr(user, 'username', employee_id),
            "email": getattr(user, 'email', ''),
            "name": getattr(user, 'name', ''),
            "gender": gender_value,
            "date_of_birth": date_of_birth_value,
            "date_of_joining": date_of_joining_value,
            "date_of_leaving": getattr(user, 'date_of_leaving', None),
            "mobile": mobile_value,
            "password": password_value,
            "role": role_value,
            "status": status_value,
            "department": getattr(user, 'department', ''),
            "designation": getattr(user, 'designation', ''),
            "location": getattr(user, 'location', ''),
            "manager_id": str(getattr(user, 'manager_id', '')) if getattr(user, 'manager_id') else None,
            "salary": getattr(user, 'salary', None),
            "pan_number": pan_number_value,
            "aadhar_number": aadhar_number_value,
            "bank_account_number": getattr(user, 'bank_account_number', ''),
            "ifsc_code": getattr(user, 'ifsc_code', ''),
            "photo_path": photo_path_value,
            "pan_document_path": pan_document_path_value,
            "aadhar_document_path": aadhar_document_path_value,
            "leave_balance": getattr(user, 'leave_balance', {}),
            "is_active": user.is_active() if hasattr(user, 'is_active') and callable(getattr(user, 'is_active')) else True,
            "created_at": getattr(user, 'created_at', datetime.utcnow()),
            "updated_at": getattr(user, 'updated_at', datetime.utcnow()),
            "created_by": getattr(user, 'created_by', 'system'),
            "updated_by": getattr(user, 'updated_by', 'system'),
            "last_login": getattr(user, 'last_login_at', None),
            "login_count": getattr(user, 'login_count', 0),
            "failed_login_attempts": getattr(user, 'login_attempts', 0),
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
            employee_id=document.get("employee_id"),
            username=document.get("username", document.get("employee_id")),  # Default to employee_id if username not present
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
    async def save(self, user: User, hostname: str) -> User:
        """
        Save a user (create or update).
        
        Replaces: create_user() and update_user() functions
        """
        try:
            document = self._entity_to_document(user)
            
            # Use upsert to handle both create and update
            employee_id = getattr(user, 'employee_id', None)
            if employee_id:
                employee_id = str(employee_id)
            else:
                employee_id = str(getattr(user, 'employee_id', getattr(user, 'employee_id', '')))
            
            filters = {"employee_id": employee_id}
            await self._update_document(
                filters=filters,
                update_data=document,
                organisation_id=hostname,
                upsert=True
            )
            
            logger.info(f"User saved: {employee_id}")
            return user
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error saving user {employee_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving user {employee_id}: {e}")
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
    
    async def delete(self, employee_id: Union[EmployeeId, str], soft_delete: bool = True) -> bool:
        """
        Delete a user by ID.
        
        Provides delete functionality not available in original procedural code.
        """
        try:
            employee_id = str(employee_id) if isinstance(employee_id, str) else str(employee_id.value if hasattr(employee_id, 'value') else employee_id)
            filters = {"employee_id": employee_id}
            result = await self._delete_document(
                filters=filters,
                soft_delete=soft_delete
            )
            
            if result:
                logger.info(f"User deleted: {employee_id}")
            else:
                logger.warning(f"User not found for deletion: {employee_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting user {employee_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, employee_id: Union[EmployeeId, str]) -> Optional[User]:
        """
        Get user by ID.
        
        Replaces: get_user_by_employee_id() function
        """
        try:
            employee_id = str(employee_id) if isinstance(employee_id, str) else str(employee_id.value if hasattr(employee_id, 'value') else employee_id)
            filters = {"employee_id": employee_id}
            documents = await self._execute_query(filters=filters, limit=1)
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {employee_id}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Replaces: get_user_by_email() function
        """
        try:
            filter_query = {"email": email}
            document = await self.find_one(filter_query)
            return self._document_to_entity(document) if document else None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        try:
            # First try by username field, then fall back to employee_id for backward compatibility
            filter_query = {"$or": [{"username": username}, {"employee_id": username}]}
            document = await self.find_one(filter_query)
            return self._document_to_entity(document) if document else None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
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
        organisation_id: Optional[str] = None
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
                organisation_id=organisation_id
            )
            
            users = [self._document_to_entity(doc) for doc in documents]
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise
    
    async def get_by_manager(self, manager_id: Union[EmployeeId, str], organisation_id: Optional[str] = None) -> List[User]:
        """
        Get users by manager ID.
        
        Replaces: get_users_by_manager_id() and get_employee_ids_by_manager_id() functions
        """
        try:
            mgr_id = str(manager_id) if isinstance(manager_id, str) else str(manager_id.value if hasattr(manager_id, 'value') else manager_id)
            filters = {"manager_id": mgr_id}
            documents = await self._execute_query(
                filters=filters,
                organisation_id=organisation_id
            )
            
            users = [self._document_to_entity(doc) for doc in documents]
            logger.info(f"Retrieved {len(users)} users for manager {mgr_id}")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            raise
    
    async def update_leave_balance(
        self, 
        employee_id: Union[EmployeeId, str], 
        leave_name: str, 
        leave_count: int, 
        organisation_id: Optional[str] = None
    ) -> bool:
        """
        Update leave balance for a user.
        
        Replaces: update_user_leave_balance() function
        """
        try:
            employee_id = str(employee_id) if isinstance(employee_id, str) else str(employee_id.value if hasattr(employee_id, 'value') else employee_id)
            collection = self._get_collection(organisation_id)
            
            result = await collection.update_one(
                {"employee_id": employee_id},
                {
                    "$inc": {f"leave_balance.{leave_name}": leave_count},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated leave balance for {employee_id}: {leave_name} += {leave_count}")
                return True
            else:
                logger.warning(f"No user found to update leave balance: {employee_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating leave balance for {employee_id}: {e}")
            raise
    
    # Analytics Repository Implementation
    async def get_statistics(self, organisation_id: Optional[str] = None) -> UserStatisticsDTO:
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
            role_stats = await self._aggregate(role_pipeline, organisation_id)
            role_counts = {item["_id"]: item["count"] for item in role_stats}
            
            # Get status statistics
            status_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_stats = await self._aggregate(status_pipeline, organisation_id)
            status_counts = {item["_id"]: item["count"] for item in status_stats}
            
            # Get total count
            total_count = await self._count_documents(
                {"is_deleted": {"$ne": True}},
                organisation_id
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
    async def create_user_legacy(self, user_data: Dict[str, Any], organisation_id: str) -> Dict[str, Any]:
        """
        Legacy compatibility method for create_user() function.
        
        This provides backward compatibility while migrating to SOLID architecture.
        """
        try:
            document = user_data.copy()
            document_id = await self._insert_document(document, organisation_id)
            
            logger.info(f"User created (legacy): {user_data.get('employee_id')}")
            return {
                "msg": "User created successfully",
                "inserted_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error creating user (legacy): {e}")
            raise
    
    async def get_all_users_legacy(self, organisation_id: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility method for get_all_users() function.
        
        This provides backward compatibility while migrating to SOLID architecture.
        """
        try:
            documents = await self._execute_query(
                filters={},
                organisation_id=organisation_id,
                limit=1000  # Large limit for legacy compatibility
            )
            
            logger.info(f"Retrieved {len(documents)} users (legacy)")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all users (legacy): {e}")
            raise
    
    async def get_users_stats_legacy(self, organisation_id: str) -> Dict[str, int]:
        """
        Legacy compatibility method for get_users_stats() function.
        
        This provides backward compatibility while migrating to SOLID architecture.
        """
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            results = await self._aggregate(pipeline, organisation_id)
            stats = {item["_id"]: item["count"] for item in results}
            
            logger.info(f"User stats (legacy): {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats (legacy): {e}")
            raise 