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

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import UserRole, UserStatus, Gender
from app.application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository, UserAnalyticsRepository,
    UserProfileRepository, UserBulkOperationsRepository, UserRepository
)
from app.application.dto.user_dto import (
    UserSearchFiltersDTO, UserStatisticsDTO, UserAnalyticsDTO,
    UserProfileCompletionDTO
)
from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.events.user_events import UserCreated, UserUpdated, UserDeleted
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

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
        
        # Connection configuration (will be set by dependency container)
        self._connection_string = None
        self._client_options = None
        
    def set_connection_config(self, connection_string: str, client_options: Dict[str, Any]):
        """
        Set MongoDB connection configuration.
        
        Args:
            connection_string: MongoDB connection string
            client_options: MongoDB client options
        """
        self._connection_string = connection_string
        self._client_options = client_options
        
    async def _get_collection(self, organisation_id: Optional[str] = None):
        """
        Get users collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        """
        db_name = organisation_id if organisation_id else "pms_global_database"
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.info("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    logger.info("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    logger.info("Loading connection parameters from mongodb_config")
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            db = self.db_connector.get_database('pms_'+db_name)
            collection = db[self._collection_name]
            logger.info(f"Successfully retrieved collection: {self._collection_name} from database: {'pms_'+db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    def _user_to_document(self, user: User) -> Dict[str, Any]:
        """Convert domain entity to database document."""
        
        # Safe value extraction for enums - handle both enum objects and strings
        def safe_enum_value(field_value):
            if hasattr(field_value, 'value'):
                return field_value.value
            return str(field_value) if field_value is not None else None
        
        # Safe extraction for complex nested objects
        def safe_get_attr(obj, attr_path, default=None):
            """Safely get nested attributes like 'permissions.role.value'"""
            try:
                attrs = attr_path.split('.')
                value = obj
                for attr in attrs:
                    value = getattr(value, attr, None)
                    if value is None:
                        return default
                return value
            except (AttributeError, TypeError):
                return default
        
        # Convert date objects to datetime for MongoDB compatibility
        def safe_date_conversion(date_value):
            """Convert date objects to datetime objects for MongoDB"""
            if date_value is None:
                return None
            if isinstance(date_value, datetime):
                return date_value
            elif hasattr(date_value, 'date') and callable(date_value.date):
                # It's a datetime, return as is
                return date_value
            elif hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
                # It's a date object, convert to datetime
                from datetime import datetime as dt
                return dt.combine(date_value, dt.min.time())
            else:
                return date_value
        
        # Safe boolean extraction - call method if it's callable
        def safe_boolean_value(obj, attr_name, default=True):
            """Safely get boolean value, calling method if needed"""
            try:
                value = getattr(obj, attr_name, default)
                if callable(value):
                    return value()
                return bool(value) if value is not None else default
            except (AttributeError, TypeError):
                return default
        
        return {
            "employee_id": str(user.employee_id),
            "username": getattr(user, 'username', str(user.employee_id)),
            "email": safe_get_attr(user, 'email', ''),
            "name": getattr(user, 'name', ''),
            "gender": safe_enum_value(safe_get_attr(user, 'personal_details.gender')),
            "date_of_birth": safe_date_conversion(safe_get_attr(user, 'personal_details.date_of_birth')),
            "date_of_joining": safe_date_conversion(safe_get_attr(user, 'personal_details.date_of_joining') or getattr(user, 'date_of_joining', None)),
            "date_of_leaving": safe_date_conversion(getattr(user, 'date_of_leaving', None)),
            "mobile": safe_get_attr(user, 'personal_details.mobile'),
            "password_hash": safe_get_attr(user, 'password.hashed_value', ''),
            "role": safe_enum_value(safe_get_attr(user, 'permissions.role')),
            "status": safe_enum_value(getattr(user, 'status', None)),
            "department": getattr(user, 'department', None),
            "designation": getattr(user, 'designation', None),
            "location": getattr(user, 'location', None),
            "manager_id": str(user.manager_id) if user.manager_id else None,
            "salary": safe_get_attr(user, 'personal_details.salary'),
            "pan_number": safe_get_attr(user, 'personal_details.pan_number'),
            "aadhar_number": safe_get_attr(user, 'personal_details.aadhar_number'),
            "bank_account_number": safe_get_attr(user, 'personal_details.bank_account_number'),
            "ifsc_code": safe_get_attr(user, 'personal_details.ifsc_code'),
            "photo_path": safe_get_attr(user, 'documents.photo_path'),
            "pan_document_path": safe_get_attr(user, 'documents.pan_document_path'),
            "aadhar_document_path": safe_get_attr(user, 'documents.aadhar_document_path'),
            "leave_balance": getattr(user, 'leave_balance', {}),
            "is_active": safe_boolean_value(user, 'is_active', True),
            "created_at": safe_date_conversion(getattr(user, 'created_at', None)),
            "updated_at": safe_date_conversion(getattr(user, 'updated_at', None)),
            "created_by": getattr(user, 'created_by', None),
            "updated_by": getattr(user, 'updated_by', None),
            "last_login": safe_date_conversion(getattr(user, 'last_login_at', None)),
            "login_count": getattr(user, 'login_count', 0),
            "failed_login_attempts": getattr(user, 'login_attempts', 0),
            "locked_until": safe_date_conversion(getattr(user, 'locked_until', None)),
            "password_changed_at": safe_date_conversion(safe_get_attr(user, 'password.changed_at')),
            "custom_permissions": safe_get_attr(user, 'permissions.custom_permissions', []),
            "profile_completion_percentage": getattr(user, 'profile_completion_percentage', 0.0),
            "version": getattr(user, 'version', 1)
        }
    
    def _document_to_user(self, document: Dict[str, Any]) -> User:
        """Convert database document to domain entity."""
        
        try:
            # For now, create a simple User object that can work with the existing system
            # This is a temporary solution until we properly understand the User entity structure
            
            # Create a minimal User-like object
            class SimpleUser:
                def __init__(self, **kwargs):
                    # Core identity
                    self.employee_id = EmployeeId(kwargs.get("employee_id"))
                    self.username = kwargs.get("username", str(self.employee_id))
                    self.email = kwargs.get("email", "")
                    self.name = kwargs.get("name", "")
                    
                    # Status and credentials
                    self.gender = Gender(kwargs.get("gender", "male")) if kwargs.get("gender") else Gender.MALE
                    self.role = UserRole(kwargs.get("role", "user"))
                    self.status = UserStatus(kwargs.get("status", "active"))
                    
                    # Personal info
                    self.date_of_birth = kwargs.get("date_of_birth")
                    self.date_of_joining = kwargs.get("date_of_joining")
                    self.date_of_leaving = kwargs.get("date_of_leaving")
                    self.mobile = kwargs.get("mobile")
                    self.department = kwargs.get("department")
                    self.designation = kwargs.get("designation")
                    self.location = kwargs.get("location")
                    self.manager_id = EmployeeId(kwargs.get("manager_id")) if kwargs.get("manager_id") else None
                    
                    # Financial info
                    self.salary = kwargs.get("salary")
                    self.pan_number = kwargs.get("pan_number")
                    self.aadhar_number = kwargs.get("aadhar_number")
                    self.bank_account_number = kwargs.get("bank_account_number")
                    self.ifsc_code = kwargs.get("ifsc_code")
                    
                    # Documents
                    self.photo_path = kwargs.get("photo_path")
                    self.pan_document_path = kwargs.get("pan_document_path")
                    self.aadhar_document_path = kwargs.get("aadhar_document_path")
                    
                    # System fields
                    self.leave_balance = kwargs.get("leave_balance", {})
                    self.is_active = kwargs.get("is_active", True)
                    self.created_at = kwargs.get("created_at")
                    self.updated_at = kwargs.get("updated_at")
                    self.created_by = kwargs.get("created_by")
                    self.updated_by = kwargs.get("updated_by")
                    self.last_login = kwargs.get("last_login")
                    self.login_count = kwargs.get("login_count", 0)
                    self.failed_login_attempts = kwargs.get("failed_login_attempts", 0)
                    self.locked_until = kwargs.get("locked_until")
                    self.password_changed_at = kwargs.get("password_changed_at")
                    self.custom_permissions = kwargs.get("custom_permissions", [])
                    self.profile_completion_percentage = kwargs.get("profile_completion_percentage", 0.0)
                    self.version = kwargs.get("version", 1)
                    
                    # Store is_active flag internally to avoid conflict with method
                    self._is_active = kwargs.get("is_active", True)
                    
                    # Password hash for authentication
                    self.password_hash = kwargs.get("password_hash", "")
                    
                    # Make this work with the User interface
                    self.credentials = type('obj', (object,), {
                        'password_hash': self.password_hash,
                        'role': self.role,
                        'status': self.status
                    })()
                    
                def get_domain_events(self):
                    return []
                    
                def clear_domain_events(self):
                    pass
                
                def is_active(self) -> bool:
                    """Check if user is active - method to match Employee entity interface"""
                    # Check both the is_active flag and status
                    active_flag = getattr(self, '_is_active', True)  # Use internal property
                    status_active = True
                    if hasattr(self, 'status') and hasattr(self.status, 'value'):
                        status_active = self.status.value == "active"
                    elif hasattr(self, 'status') and isinstance(self.status, str):
                        status_active = self.status == "active"
                    return active_flag and status_active
            
            # Create the simple user object
            user = SimpleUser(
                employee_id=document["employee_id"],
                username=document.get("username", document.get("employee_id")),
                email=document.get("email", ""),
                name=document.get("name", ""),
                gender=document.get("gender"),
                role=document.get("role", "user"),
                status=document.get("status", "active"),
                date_of_birth=document.get("date_of_birth"),
                date_of_joining=document.get("date_of_joining"),
                date_of_leaving=document.get("date_of_leaving"),
                mobile=document.get("mobile"),
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
                version=document.get("version", 1),
                password_hash=document.get("password_hash", "")
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating User entity from document: {e}")
            raise ValueError(f"Failed to reconstruct User entity: {e}")
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        # Implementation would depend on event publisher
        for event in events:
            logger.info(f"Publishing event: {type(event).__name__}")
    
    # Command Repository Implementation
    async def save(self, user: User, hostname: str) -> User:
        """Save a user (create or update)."""
        try:
            collection = await self._get_collection(hostname)
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
            # Group users by organisation
            users_by_org = {}
            for user in users:
                org_id = user.organisation_id or "pms_global_database"
                if org_id not in users_by_org:
                    users_by_org[org_id] = []
                users_by_org[org_id].append(user)
            
            saved_users = []
            for org_id, org_users in users_by_org.items():
                collection = await self._get_collection(org_id)
                
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
    
    async def delete(self, employee_id: EmployeeId, soft_delete: bool = True, hostname: Optional[str] = None) -> bool:
        """Delete a user by ID."""
        try:
            # For soft delete, we need to find the user first to get organisation
            user = await self.get_by_id(employee_id, hostname)
            if not user:
                return False
            
            collection = await self._get_collection(hostname)
            
            if soft_delete:
                # Soft delete - mark as deleted
                result = await collection.update_one(
                    {"employee_id": str(employee_id)},
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
                result = await collection.delete_one({"employee_id": str(employee_id)})
            
            if result.modified_count > 0 or result.deleted_count > 0:
                # Publish delete event
                delete_event = UserDeleted(
                    employee_id=employee_id,
                    organisation_id=hostname,
                    soft_delete=soft_delete,
                    deleted_at=datetime.utcnow()
                )
                await self._publish_events([delete_event])
                
                logger.info(f"User deleted: {employee_id} (soft: {soft_delete})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user {employee_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, employee_id: EmployeeId, organisation_id: Optional[str] = None) -> Optional[User]:
        """Get user by ID."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "employee_id": str(employee_id),
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_user(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {employee_id}: {e}")
            raise
    
    async def get_by_email(self, email: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """Get user by email."""
        try:
            collection = await self._get_collection(organisation_id)
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
    
    async def get_by_username(self, username: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """Get user by username."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "username": username,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_user(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise
    
    async def get_by_mobile(self, mobile: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """Get user by mobile number."""
        try:
            collection = await self._get_collection(organisation_id)
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
    
    async def get_by_pan_number(self, pan_number: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """Get user by PAN number."""
        try:
            collection = await self._get_collection(organisation_id)
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
        organisation_id: Optional[str] = None
    ) -> List[User]:
        """Get all users with pagination."""
        try:
            collection = await self._get_collection(organisation_id)
            
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
    
    async def search(self, filters: UserSearchFiltersDTO, organisation_id: Optional[str] = None) -> List[User]:
        """Search users with filters."""
        try:
            collection = await self._get_collection(organisation_id)
            
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
    
    async def get_by_role(self, role: UserRole, organisation_id: Optional[str] = None) -> List[User]:
        """Get users by role."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "role": role.value,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            raise
    
    async def get_by_status(self, status: UserStatus, organisation_id: Optional[str] = None) -> List[User]:
        """Get users by status."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by status {status}: {e}")
            raise
    
    async def get_by_department(self, department: str, organisation_id: Optional[str] = None) -> List[User]:
        """Get users by department."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "department": department,
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by department {department}: {e}")
            raise
    
    async def get_by_manager(self, manager_id: EmployeeId, organisation_id: Optional[str] = None) -> List[User]:
        """Get users by manager."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "manager_id": str(manager_id),
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            raise
    
    async def get_active_users(self, organisation_id: Optional[str] = None) -> List[User]:
        """Get all active users."""
        try:
            collection = await self._get_collection(organisation_id)
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
    
    async def get_locked_users(self, organisation_id: Optional[str] = None) -> List[User]:
        """Get all locked users."""
        try:
            collection = await self._get_collection(organisation_id)
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
    async def count_total(self, include_deleted: bool = False, organisation_id: Optional[str] = None) -> int:
        """Count total users."""
        try:
            collection = await self._get_collection(organisation_id)
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            return await collection.count_documents(filter_query)
            
        except Exception as e:
            logger.error(f"Error counting total users: {e}")
            raise
    
    async def count_by_status(self, status: UserStatus, organisation_id: Optional[str] = None) -> int:
        """Count users by status."""
        try:
            collection = await self._get_collection(organisation_id)
            return await collection.count_documents({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting users by status {status}: {e}")
            raise
    
    async def count_by_role(self, role: UserRole, organisation_id: Optional[str] = None) -> int:
        """Count users by role."""
        try:
            collection = await self._get_collection(organisation_id)
            return await collection.count_documents({
                "role": role.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting users by role {role}: {e}")
            raise
    
    # Existence checks
    async def exists_by_email(self, email: str, exclude_id: Optional[EmployeeId] = None, organisation_id: Optional[str] = None) -> bool:
        """Check if user exists by email."""
        try:
            collection = await self._get_collection(organisation_id)
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
    
    async def exists_by_mobile(self, mobile: str, exclude_id: Optional[EmployeeId] = None, organisation_id: Optional[str] = None) -> bool:
        """Check if user exists by mobile."""
        try:
            collection = await self._get_collection(organisation_id)
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
    
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[EmployeeId] = None, organisation_id: Optional[str] = None) -> bool:
        """Check if user exists by PAN number."""
        try:
            collection = await self._get_collection(organisation_id)
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
    async def get_statistics(self, organisation_id: Optional[str] = None) -> UserStatisticsDTO:
        """Get comprehensive user statistics."""
        try:
            collection = await self._get_collection(organisation_id)
            
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
    
    async def get_analytics(self, organisation_id: Optional[str] = None) -> UserAnalyticsDTO:
        """Get detailed user analytics."""
        try:
            # Implementation would include complex analytics queries
            # For now, return basic analytics
            stats = await self.get_statistics(organisation_id)
            
            return UserAnalyticsDTO(
                user_statistics=stats,
                growth_trends={},
                activity_patterns={},
                security_metrics={}
            )
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            raise

    # Analytics Repository Methods
    async def get_users_by_role_count(self, organisation_id: Optional[str] = None) -> Dict[str, int]:
        """Get user count by role."""
        try:
            collection = await self._get_collection(organisation_id)
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            return {doc["_id"]: doc["count"] for doc in result}
            
        except Exception as e:
            logger.error(f"Error getting users by role count: {e}")
            return {}

    async def get_users_by_status_count(self, organisation_id: Optional[str] = None) -> Dict[str, int]:
        """Get user count by status."""
        try:
            collection = await self._get_collection(organisation_id)
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            return {doc["_id"]: doc["count"] for doc in result}
            
        except Exception as e:
            logger.error(f"Error getting users by status count: {e}")
            return {}

    async def get_users_by_department_count(self, organisation_id: Optional[str] = None) -> Dict[str, int]:
        """Get user count by department."""
        try:
            collection = await self._get_collection(organisation_id)
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$department", "count": {"$sum": 1}}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            return {doc["_id"]: doc["count"] for doc in result}
            
        except Exception as e:
            logger.error(f"Error getting users by department count: {e}")
            return {}

    async def get_login_activity_stats(self, days: int = 30, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get login activity statistics."""
        try:
            # Basic implementation - would be more complex in real scenario
            collection = await self._get_collection(organisation_id)
            cutoff_date = datetime.now() - timedelta(days=days)
            
            active_users = await collection.count_documents({
                "last_login": {"$gte": cutoff_date},
                "is_deleted": {"$ne": True}
            })
            
            return {
                "active_users_last_n_days": active_users,
                "period_days": days,
                "total_logins": active_users  # Simplified
            }
            
        except Exception as e:
            logger.error(f"Error getting login activity stats: {e}")
            return {}

    async def get_profile_completion_stats(self, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get profile completion statistics."""
        try:
            collection = await self._get_collection(organisation_id)
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {
                    "$group": {
                        "_id": None,
                        "avg_completion": {"$avg": "$profile_completion_percentage"},
                        "complete_profiles": {
                            "$sum": {"$cond": [{"$gte": ["$profile_completion_percentage", 100]}, 1, 0]}
                        },
                        "incomplete_profiles": {
                            "$sum": {"$cond": [{"$lt": ["$profile_completion_percentage", 100]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            stats = result[0] if result else {}
            
            return {
                "average_completion": stats.get("avg_completion", 0),
                "complete_profiles": stats.get("complete_profiles", 0),
                "incomplete_profiles": stats.get("incomplete_profiles", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting profile completion stats: {e}")
            return {}

    async def get_most_active_users(self, limit: int = 10, organisation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get most active users."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find(
                {"is_deleted": {"$ne": True}},
                {"employee_id": 1, "name": 1, "login_count": 1, "last_login": 1}
            ).sort("login_count", DESCENDING).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Error getting most active users: {e}")
            return []

    async def get_users_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime,
        organisation_id: Optional[str] = None
    ) -> List[User]:
        """Get users created in a specific period."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "created_at": {"$gte": start_date, "$lte": end_date},
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_user(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting users created in period: {e}")
            return []

    async def get_password_security_metrics(self, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get password security metrics."""
        try:
            collection = await self._get_collection(organisation_id)
            now = datetime.now()
            
            # Users with old passwords (older than 90 days)
            old_password_cutoff = now - timedelta(days=90)
            old_passwords = await collection.count_documents({
                "password_changed_at": {"$lt": old_password_cutoff},
                "is_deleted": {"$ne": True}
            })
            
            # Locked accounts
            locked_accounts = await collection.count_documents({
                "status": UserStatus.LOCKED.value,
                "is_deleted": {"$ne": True}
            })
            
            return {
                "users_with_old_passwords": old_passwords,
                "locked_accounts": locked_accounts,
                "password_age_threshold_days": 90
            }
            
        except Exception as e:
            logger.error(f"Error getting password security metrics: {e}")
            return {}

    # Profile Repository Methods
    async def get_profile_completion(self, employee_id: EmployeeId, organisation_id: Optional[str] = None) -> UserProfileCompletionDTO:
        """Get profile completion for a user."""
        try:
            user = await self.get_by_id(employee_id)
            if not user:
                return UserProfileCompletionDTO(
                    employee_id=employee_id,
                    completion_percentage=0.0,
                    missing_fields=[],
                    completed_fields=[]
                )
            
            # Calculate completion based on required fields
            required_fields = ['name', 'email', 'mobile', 'department', 'designation']
            completed_fields = []
            missing_fields = []
            
            for field in required_fields:
                if hasattr(user, field) and getattr(user, field):
                    completed_fields.append(field)
                else:
                    missing_fields.append(field)
            
            completion_percentage = (len(completed_fields) / len(required_fields)) * 100
            
            return UserProfileCompletionDTO(
                employee_id=employee_id,
                completion_percentage=completion_percentage,
                missing_fields=missing_fields,
                completed_fields=completed_fields
            )
            
        except Exception as e:
            logger.error(f"Error getting profile completion for {employee_id}: {e}")
            return UserProfileCompletionDTO(
                employee_id=employee_id,
                completion_percentage=0.0,
                missing_fields=[],
                completed_fields=[]
            )

    async def get_incomplete_profiles(self, threshold: float = 80.0, organisation_id: Optional[str] = None) -> List[UserProfileCompletionDTO]:
        """Get users with incomplete profiles."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "profile_completion_percentage": {"$lt": threshold},
                "is_deleted": {"$ne": True}
            })
            
            documents = await cursor.to_list(length=None)
            result = []
            
            for doc in documents:
                user = self._document_to_user(doc)
                completion = await self.get_profile_completion(user.employee_id, organisation_id)
                result.append(completion)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting incomplete profiles: {e}")
            return []

    async def get_users_missing_documents(self, organisation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get users missing required documents."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "$or": [
                    {"pan_document_path": {"$in": [None, ""]}},
                    {"aadhar_document_path": {"$in": [None, ""]}},
                    {"photo_path": {"$in": [None, ""]}}
                ],
                "is_deleted": {"$ne": True}
            }, {"employee_id": 1, "name": 1, "pan_document_path": 1, "aadhar_document_path": 1, "photo_path": 1})
            
            documents = await cursor.to_list(length=None)
            result = []
            
            for doc in documents:
                missing_docs = []
                if not doc.get("pan_document_path"):
                    missing_docs.append("PAN")
                if not doc.get("aadhar_document_path"):
                    missing_docs.append("Aadhar")
                if not doc.get("photo_path"):
                    missing_docs.append("Photo")
                
                result.append({
                    "employee_id": doc["employee_id"],
                    "name": doc["name"],
                    "missing_documents": missing_docs
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting users missing documents: {e}")
            return []

    async def track_profile_update(self, employee_id: EmployeeId, section: str, organisation_id: Optional[str] = None) -> None:
        """Track profile section update."""
        try:
            collection = await self._get_collection(organisation_id)
            await collection.update_one(
                {"employee_id": str(employee_id)},
                {"$set": {"updated_at": datetime.now()}}
            )
            logger.info(f"Tracked profile update for {employee_id}, section: {section}")
            
        except Exception as e:
            logger.error(f"Error tracking profile update: {e}")

    # Bulk Operations Repository Methods
    async def bulk_update_status(
        self, 
        employee_ids: List[EmployeeId], 
        status: UserStatus,
        updated_by: str,
        reason: Optional[str] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update user status."""
        try:
            collection = await self._get_collection(organisation_id)
            filter_query = {"employee_id": {"$in": [str(uid) for uid in employee_ids]}}
            update_data = {
                "$set": {
                    "status": status.value,
                    "updated_at": datetime.now(),
                    "updated_by": updated_by
                }
            }
            
            if reason:
                update_data["$set"]["status_change_reason"] = reason
            
            result = await collection.update_many(filter_query, update_data)
            
            return {
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "status": "success" if result.modified_count > 0 else "no_changes"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk status update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_update_role(
        self, 
        employee_ids: List[EmployeeId], 
        role: UserRole,
        updated_by: str,
        reason: str,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update user role."""
        try:
            collection = await self._get_collection(organisation_id)
            filter_query = {"employee_id": {"$in": [str(uid) for uid in employee_ids]}}
            update_data = {
                "$set": {
                    "role": role.value,
                    "updated_at": datetime.now(),
                    "updated_by": updated_by,
                    "role_change_reason": reason
                }
            }
            
            result = await collection.update_many(filter_query, update_data)
            
            return {
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "status": "success" if result.modified_count > 0 else "no_changes"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk role update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_update_department(
        self, 
        employee_ids: List[EmployeeId], 
        department: str,
        updated_by: str,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update user department."""
        try:
            collection = await self._get_collection(organisation_id)
            filter_query = {"employee_id": {"$in": [str(uid) for uid in employee_ids]}}
            update_data = {
                "$set": {
                    "department": department,
                    "updated_at": datetime.now(),
                    "updated_by": updated_by
                }
            }
            
            result = await collection.update_many(filter_query, update_data)
            
            return {
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "status": "success" if result.modified_count > 0 else "no_changes"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk department update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_export(
        self, 
        employee_ids: Optional[List[EmployeeId]] = None,
        format: str = "csv",
        include_sensitive: bool = False,
        organisation_id: Optional[str] = None
    ) -> bytes:
        """Bulk export user data."""
        try:
            import csv
            import io
            
            collection = await self._get_collection(organisation_id)
            
            # Build query
            query = {"is_deleted": {"$ne": True}}
            if employee_ids:
                query["employee_id"] = {"$in": [str(uid) for uid in employee_ids]}
            
            # Select fields based on sensitivity
            projection = {
                "employee_id": 1, "name": 1, "email": 1, "department": 1, 
                "designation": 1, "role": 1, "status": 1, "date_of_joining": 1
            }
            
            if include_sensitive:
                projection.update({
                    "mobile": 1, "salary": 1, "pan_number": 1, "aadhar_number": 1
                })
            
            cursor = collection.find(query, projection)
            documents = await cursor.to_list(length=None)
            
            # Convert to CSV
            output = io.StringIO()
            if documents:
                fieldnames = list(documents[0].keys())
                if '_id' in fieldnames:
                    fieldnames.remove('_id')
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for doc in documents:
                    doc.pop('_id', None)  # Remove MongoDB _id
                    writer.writerow(doc)
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error in bulk export: {e}")
            return b""

    async def bulk_import(
        self, 
        data: bytes, 
        format: str = "csv",
        created_by: str = "system",
        validate_only: bool = False,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk import user data."""
        try:
            import csv
            import io
            
            # Parse CSV data
            content = data.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
            
            users_data = list(reader)
            valid_users = []
            errors = []
            
            for i, user_data in enumerate(users_data):
                try:
                    # Basic validation
                    if not user_data.get('employee_id'):
                        errors.append(f"Row {i+1}: Missing employee_id")
                        continue
                    
                    if not user_data.get('email'):
                        errors.append(f"Row {i+1}: Missing email")
                        continue
                    
                    valid_users.append(user_data)
                    
                except Exception as e:
                    errors.append(f"Row {i+1}: {str(e)}")
            
            result = {
                "total_rows": len(users_data),
                "valid_rows": len(valid_users),
                "errors": errors,
                "status": "validation_complete" if validate_only else "import_complete"
            }
            
            if not validate_only and valid_users:
                # Perform actual import
                collection = await self._get_collection(organisation_id)
                operations = []
                
                for user_data in valid_users:
                    # Set defaults
                    user_data['created_by'] = created_by
                    user_data['created_at'] = datetime.now()
                    user_data['is_active'] = True
                    user_data['role'] = user_data.get('role', 'user')
                    user_data['status'] = user_data.get('status', 'active')
                    
                    operations.append({
                        "replaceOne": {
                            "filter": {"employee_id": user_data['employee_id']},
                            "replacement": user_data,
                            "upsert": True
                        }
                    })
                
                if operations:
                    bulk_result = await collection.bulk_write(operations)
                    result["inserted_count"] = bulk_result.upserted_count
                    result["modified_count"] = bulk_result.modified_count
            
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_password_reset(
        self, 
        employee_ids: List[EmployeeId],
        reset_by: str,
        send_email: bool = True,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk password reset for users."""
        try:
            import secrets
            import string
            
            collection = await self._get_collection(organisation_id)
            reset_results = []
            
            for employee_id in employee_ids:
                try:
                    # Generate temporary password
                    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                    
                    # Hash password (simplified - would use proper hashing)
                    password_hash = f"hashed_{temp_password}"
                    
                    # Update user
                    result = await collection.update_one(
                        {"employee_id": str(employee_id)},
                        {
                            "$set": {
                                "password_hash": password_hash,
                                "password_changed_at": datetime.now(),
                                "updated_by": reset_by,
                                "force_password_change": True
                            }
                        }
                    )
                    
                    if result.modified_count > 0:
                        reset_results.append({
                            "employee_id": str(employee_id),
                            "status": "success",
                            "temp_password": temp_password if not send_email else "sent_via_email"
                        })
                    else:
                        reset_results.append({
                            "employee_id": str(employee_id),
                            "status": "failed",
                            "error": "User not found"
                        })
                        
                except Exception as e:
                    reset_results.append({
                        "employee_id": str(employee_id),
                        "status": "failed",
                        "error": str(e)
                    })
            
            successful_resets = len([r for r in reset_results if r["status"] == "success"])
            
            return {
                "total_requested": len(employee_ids),
                "successful_resets": successful_resets,
                "failed_resets": len(employee_ids) - successful_resets,
                "results": reset_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk password reset: {e}")
            return {"error": str(e), "status": "failed"}

    # ==================== FACTORY METHODS IMPLEMENTATION ====================
    # These methods are required by the repository interfaces but are not used
    # in the current dependency injection architecture. They return self since
    # this repository implements all user repository interfaces.
    
    def create_command_repository(self) -> UserCommandRepository:
        """Create command repository instance."""
        return self
    
    def create_query_repository(self) -> UserQueryRepository:
        """Create query repository instance."""
        return self
    
    def create_analytics_repository(self) -> UserAnalyticsRepository:
        """Create analytics repository instance."""
        return self
    
    def create_profile_repository(self) -> UserProfileRepository:
        """Create profile repository instance."""
        return self
    
    def create_bulk_operations_repository(self) -> UserBulkOperationsRepository:
        """Create bulk operations repository instance."""
        return self 