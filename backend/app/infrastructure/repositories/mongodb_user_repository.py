"""
MongoDB User Repository Implementation
Following SOLID principles and DDD patterns for user data access
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import UserRole, UserStatus, Gender, Password
from app.domain.value_objects.user_permissions import UserPermissions
from app.domain.value_objects.personal_details import PersonalDetails
from app.domain.value_objects.user_documents import UserDocuments
from app.domain.value_objects.bank_details import BankDetails
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
        # Fix database name logic - if organisation_id is None or global, use global database directly
        if organisation_id and organisation_id not in ["global", "pms_global_database"]:
            # For specific organisation, use pms_organisationid format
            from app.utils.db_name_utils import sanitize_organisation_id
            safe_org_id = sanitize_organisation_id(organisation_id)
            db_name = f"pms_{safe_org_id}"
        else:
            # For global or None, use the global database name directly
            db_name = "pms_global_database"
        
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
            db = self.db_connector.get_database(db_name)
            collection = db[self._collection_name]
            logger.info(f"Successfully retrieved collection: {self._collection_name} from database: {db_name}")
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
            "personal_details": user.personal_details.to_dict() if user.personal_details else None,
            "password_hash": safe_get_attr(user, 'password.hashed_value', ''),
            "role": safe_enum_value(safe_get_attr(user, 'permissions.role')),
            "status": safe_enum_value(getattr(user, 'status', None)),
            "department": getattr(user, 'department', None),
            "designation": getattr(user, 'designation', None),
            "location": getattr(user, 'location', None),
            "manager_id": str(user.manager_id) if user.manager_id else None,
            
            # Bank details (new structure)
            "bank_details": safe_get_attr(user, 'bank_details').to_dict() if safe_get_attr(user, 'bank_details') else None,
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
            from app.domain.entities.user import User
            from app.domain.value_objects.employee_id import EmployeeId
            from app.domain.value_objects.user_credentials import Password, UserRole, UserStatus, Gender
            from app.domain.value_objects.user_permissions import UserPermissions
            from app.domain.value_objects.personal_details import PersonalDetails
            from app.domain.value_objects.user_documents import UserDocuments
            from app.domain.value_objects.bank_details import BankDetails

            # Parse value objects and handle missing fields
            employee_id = EmployeeId(document["employee_id"])
            name = document.get("name", "")
            email = document.get("email", "")
            username = document.get("username", str(employee_id))
            password_hash = document.get("password_hash", "")
            password = Password.from_hash(password_hash)
            role = UserRole(document.get("role", "user"))
            status = UserStatus(document.get("status", "active"))
            permissions = UserPermissions(role=role)
            
            # Create personal details from stored object
            if document.get("personal_details"):
                personal_details = PersonalDetails.from_dict(document["personal_details"])
            else:
                personal_details = PersonalDetails(
                    gender=Gender.MALE,
                    date_of_birth=date(1970, 1, 1),
                    date_of_joining=date(1970, 1, 1),
                    mobile="9999999999"
                )
            
            # Create documents (support both nested and top-level fields)
            if document.get("documents"):
                documents = UserDocuments.from_dict(document["documents"])
            else:
                documents = UserDocuments(
                    photo_path=document.get("photo_path"),
                    pan_document_path=document.get("pan_document_path"),
                    aadhar_document_path=document.get("aadhar_document_path")
                )
            
            # Create bank details if available
            bank_details = BankDetails.from_dict(document["bank_details"]) if document.get("bank_details") else None

            # Optional fields
            department = document.get("department")
            designation = document.get("designation")
            location = document.get("location")
            manager_id = EmployeeId(document.get("manager_id")) if document.get("manager_id") else None
            leave_balance = document.get("leave_balance", {})
            created_at = document.get("created_at")
            updated_at = document.get("updated_at")
            created_by = document.get("created_by")
            updated_by = document.get("updated_by")
            last_login_at = document.get("last_login_at")
            login_attempts = document.get("login_attempts", 0)
            locked_until = document.get("locked_until")
            is_deleted = document.get("is_deleted", False)
            deleted_at = document.get("deleted_at")
            deleted_by = document.get("deleted_by")

            # Construct the User entity
            user = User(
                employee_id=employee_id,
                name=name,
                email=email,
                username=username,
                password=password,
                permissions=permissions,
                personal_details=personal_details,
                status=status,
                department=department,
                designation=designation,
                location=location,
                manager_id=manager_id,
                documents=documents,
                bank_details=bank_details,
                leave_balance=leave_balance,
                created_at=created_at,
                updated_at=updated_at,
                created_by=created_by,
                updated_by=updated_by,
                last_login_at=last_login_at,
                login_attempts=login_attempts,
                locked_until=locked_until,
                is_deleted=is_deleted,
                deleted_at=deleted_at,
                deleted_by=deleted_by
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
            
            # Text search - check both name and email fields
            if filters.name:
                query["$or"] = [
                    {"name": {"$regex": filters.name, "$options": "i"}},
                    {"email": {"$regex": filters.name, "$options": "i"}},
                    {"employee_id": {"$regex": filters.name, "$options": "i"}}
                ]
            elif filters.email:
                query["email"] = {"$regex": filters.email, "$options": "i"}
            
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
            if filters.joined_after or filters.joined_before:
                date_filter = {}
                if filters.joined_after:
                    date_filter["$gte"] = filters.joined_after
                if filters.joined_before:
                    date_filter["$lte"] = filters.joined_before
                query["date_of_joining"] = date_filter

            # Active/deleted filters - use is_active field from DTO
            query["is_deleted"] = {"$ne": True}  # Always exclude deleted
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
            
            # Execute query with pagination
            cursor = collection.find(query)
            
                        # Apply sorting
            if filters.sort_by:
                sort_direction = DESCENDING if filters.sort_order == "desc" else ASCENDING
                cursor = cursor.sort(filters.sort_by, sort_direction)

            # Apply pagination - convert page/page_size to skip/limit
            skip = (filters.page - 1) * filters.page_size if filters.page > 0 else 0
            cursor = cursor.skip(skip).limit(filters.page_size)

            documents = await cursor.to_list(length=filters.page_size)
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

    async def count(self, hostname: str) -> int:
        """Count total users in organisation."""
        try:
            collection = await self._get_collection(hostname)
            return await collection.count_documents({
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting users for organisation {hostname}: {e}")
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
            
            # Select fields based on sensitivity - include all fields for comprehensive export
            projection = {
                "employee_id": 1, 
                "name": 1, 
                "email": 1, 
                "department": 1, 
                "designation": 1, 
                "role": 1, 
                "status": 1, 
                "date_of_joining": 1,
                "date_of_birth": 1,
                "gender": 1,
                "location": 1,
                "manager_id": 1,
                "personal_details": 1,
                "bank_details": 1,
                "is_active": 1,
                "created_at": 1,
                "last_login_at": 1
            }
            
            cursor = collection.find(query, projection)
            documents = await cursor.to_list(length=None)
            
            # Convert to CSV with proper field mapping
            output = io.StringIO()
            if documents:
                # Define the field order for CSV export
                fieldnames = [
                    # Basic Information
                    "employee_id",
                    "name", 
                    "email",
                    "mobile",
                    "gender",
                    "date_of_birth",
                    "date_of_joining",
                    "role",
                    "department",
                    "designation",
                    "location",
                    "manager_id",
                    "status",
                    
                    # Personal Details
                    "pan_number",
                    "aadhar_number",
                    "uan_number",
                    "esi_number",
                    
                    # Bank Details
                    "account_number",
                    "bank_name",
                    "ifsc_code",
                    "account_holder_name",
                    "branch_name",
                    "account_type",
                    
                    # System Fields
                    "is_active",
                    "created_at",
                    "last_login_at"
                ]
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for doc in documents:
                    # Map document fields to CSV fields
                    csv_row = {
                        # Basic Information
                        "employee_id": doc.get("employee_id", ""),
                        "name": doc.get("name", ""),
                        "email": doc.get("email", ""),
                        "mobile": doc.get("personal_details", {}).get("mobile", "") if doc.get("personal_details") else "",
                        "gender": doc.get("gender", ""),
                        "date_of_birth": doc.get("date_of_birth", ""),
                        "date_of_joining": doc.get("date_of_joining", ""),
                        "role": doc.get("role", ""),
                        "department": doc.get("department", ""),
                        "designation": doc.get("designation", ""),
                        "location": doc.get("location", ""),
                        "manager_id": doc.get("manager_id", ""),
                        "status": doc.get("status", ""),
                        
                        # Personal Details
                        "pan_number": doc.get("personal_details", {}).get("pan_number", "") if doc.get("personal_details") else "",
                        "aadhar_number": doc.get("personal_details", {}).get("aadhar_number", "") if doc.get("personal_details") else "",
                        "uan_number": doc.get("personal_details", {}).get("uan_number", "") if doc.get("personal_details") else "",
                        "esi_number": doc.get("personal_details", {}).get("esi_number", "") if doc.get("personal_details") else "",
                        
                        # Bank Details
                        "account_number": doc.get("bank_details", {}).get("account_number", "") if doc.get("bank_details") else "",
                        "bank_name": doc.get("bank_details", {}).get("bank_name", "") if doc.get("bank_details") else "",
                        "ifsc_code": doc.get("bank_details", {}).get("ifsc_code", "") if doc.get("bank_details") else "",
                        "account_holder_name": doc.get("bank_details", {}).get("account_holder_name", "") if doc.get("bank_details") else "",
                        "branch_name": doc.get("bank_details", {}).get("branch_name", "") if doc.get("bank_details") else "",
                        "account_type": doc.get("bank_details", {}).get("account_type", "") if doc.get("bank_details") else "",
                        
                        # System Fields
                        "is_active": doc.get("is_active", ""),
                        "created_at": doc.get("created_at", ""),
                        "last_login_at": doc.get("last_login_at", "")
                    }
                    writer.writerow(csv_row)
            
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
            from datetime import datetime
            from app.domain.value_objects.employee_id import EmployeeId
            from app.domain.value_objects.bank_details import BankDetails
            from app.domain.value_objects.personal_details import PersonalDetails
            from app.domain.entities.user import User
            from app.domain.value_objects.user_credentials import UserRole, UserStatus
            
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
                    
                    # Validate email format
                    if '@' not in user_data.get('email', ''):
                        errors.append(f"Row {i+1}: Invalid email format")
                        continue
                    
                    # Validate date formats if provided
                    try:
                        if user_data.get('date_of_birth'):
                            datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d')
                        if user_data.get('date_of_joining'):
                            datetime.strptime(user_data['date_of_joining'], '%Y-%m-%d')
                    except ValueError as e:
                        errors.append(f"Row {i+1}: Invalid date format - {str(e)}")
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
                    try:
                        # Create bank details if provided
                        bank_details = None
                        if user_data.get('account_number') and user_data.get('bank_name'):
                            bank_details = BankDetails(
                                account_number=user_data.get('account_number', ''),
                                bank_name=user_data.get('bank_name', ''),
                                ifsc_code=user_data.get('ifsc_code', ''),
                                account_holder_name=user_data.get('account_holder_name', ''),
                                branch_name=user_data.get('branch_name', ''),
                                account_type=user_data.get('account_type', 'savings')
                            )
                        
                        # Create personal details if provided
                        personal_details = None
                        if any([
                            user_data.get('mobile'),
                            user_data.get('pan_number'),
                            user_data.get('aadhar_number'),
                            user_data.get('uan_number'),
                            user_data.get('esi_number')
                        ]):
                            personal_details = PersonalDetails(
                                mobile=user_data.get('mobile', ''),
                                pan_number=user_data.get('pan_number', ''),
                                aadhar_number=user_data.get('aadhar_number', ''),
                                uan_number=user_data.get('uan_number', ''),
                                esi_number=user_data.get('esi_number', '')
                            )
                        
                        # Create user entity
                        user = User(
                            employee_id=EmployeeId(user_data['employee_id']),
                            name=user_data.get('name', ''),
                            email=user_data['email'],
                            role=UserRole(user_data.get('role', 'user')),
                            status=UserStatus(user_data.get('status', 'active')),
                            department=user_data.get('department', ''),
                            designation=user_data.get('designation', ''),
                            location=user_data.get('location', ''),
                            manager_id=EmployeeId(user_data['manager_id']) if user_data.get('manager_id') else None,
                            personal_details=personal_details,
                            bank_details=bank_details,
                            date_of_birth=datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d') if user_data.get('date_of_birth') else None,
                            date_of_joining=datetime.strptime(user_data['date_of_joining'], '%Y-%m-%d') if user_data.get('date_of_joining') else None,
                            gender=user_data.get('gender', ''),
                            created_by=created_by
                        )
                        
                        # Convert to document
                        user_document = self._user_to_document(user)
                        user_document['created_at'] = datetime.now()
                        user_document['is_active'] = True
                        
                        operations.append({
                            "replaceOne": {
                                "filter": {"employee_id": user_data['employee_id']},
                                "replacement": user_document,
                                "upsert": True
                            }
                        })
                        
                    except Exception as e:
                        errors.append(f"Row {i+1}: Error creating user - {str(e)}")
                        continue
                
                if operations:
                    try:
                        bulk_result = await collection.bulk_write(operations)
                        result["inserted_count"] = bulk_result.upserted_count
                        result["modified_count"] = bulk_result.modified_count
                    except Exception as e:
                        result["error"] = f"Bulk write failed: {str(e)}"
                        result["status"] = "failed"
            
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

    async def find_with_filters(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        hostname: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        Find users with filters for reporting purposes.
        
        Args:
            filters: Optional filters to apply
            hostname: Organisation hostname for database selection
            
        Returns:
            Tuple of (users list, total count)
        """
        try:
            collection = await self._get_collection(hostname)
            
            # Build query
            query = {"is_deleted": {"$ne": True}}
            
            if filters:
                # Apply any additional filters if provided
                for key, value in filters.items():
                    if value is not None:
                        query[key] = value
            
            # Get total count
            total_count = await collection.count_documents(query)
            
            # Get all users (for reporting, we typically need all data)
            cursor = collection.find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=None)
            
            users = [self._document_to_user(doc) for doc in documents if doc]
            users = [user for user in users if user is not None]
            
            logger.info(f"Found {len(users)} users with filters for organisation: {hostname}")
            return users, total_count
            
        except Exception as e:
            logger.error(f"Error finding users with filters for organisation {hostname}: {e}")
            return [], 0 
        
    async def _create_default_admin_user(self, organisation_id: str) -> User:
        """Create default admin user for the organisation."""
        try:
            collection = await self._get_collection(organisation_id)
            user = User(
                employee_id=EmployeeId(f"ADMIN0001"),
                username="ADMIN0001",
                personal_details=PersonalDetails(
                    mobile="9876543210",
                    gender=Gender.MALE,
                    date_of_birth=datetime.now(),
                    date_of_joining=datetime.now(),
                ),
                name="Admin",
                email=f"admin@admin.com",
                permissions=UserPermissions(role=UserRole.ADMIN),
                status=UserStatus.ACTIVE,
                created_by="system",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted=False,
                password=Password.from_plain_text("Admin@123"), #admin123
                last_login_at=datetime.now(),
            )

            user_document = self._user_to_document(user)
            user_document['created_at'] = datetime.now()
            user_document['is_active'] = True

            await collection.insert_one(user_document)

            return user
        
        except Exception as e:
            logger.error(f"Error creating default admin user for organisation {organisation_id}: {e}")
            return None