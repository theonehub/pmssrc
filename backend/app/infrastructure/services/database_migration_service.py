"""
Database Migration Service
Helps transition from procedural database functions to SOLID architecture
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..database.database_connector import DatabaseConnector
from ..database.mongodb_connector import MongoDBConnector
from ..database.connection_factory import (
    ConnectionFactory, DatabaseType, DatabaseConnectionManager
)
from ..repositories.solid_user_repository import SolidUserRepository
from ..repositories.solid_payout_repository import SolidPayoutRepository
from ..repositories.solid_attendance_repository import SolidAttendanceRepository
from ..repositories.solid_employee_leave_repository import SolidEmployeeLeaveRepository
from ..repositories.solid_reimbursement_repository import SolidReimbursementRepository

logger = logging.getLogger(__name__)


class DatabaseMigrationService:
    """
    Service to help migrate from procedural database functions to SOLID architecture.
    
    Provides:
    - Legacy function compatibility
    - Gradual migration support
    - Connection management
    - Repository factory methods
    
    Follows SOLID principles:
    - SRP: Only handles database migration concerns
    - OCP: Can be extended with new migration strategies
    - LSP: Provides consistent interface for database operations
    - ISP: Focused interface for migration operations
    - DIP: Depends on database abstractions
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize migration service.
        
        Args:
            connection_string: MongoDB connection string
        """
        self.connection_string = connection_string
        self.connection_manager = DatabaseConnectionManager()
        self._repositories: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Initialize database connections and repositories."""
        try:
            # Create main database connection
            await self.connection_manager.create_connection(
                name="main",
                db_type=DatabaseType.MONGODB,
                connection_string=self.connection_string,
                tls=True
            )
            
            # Initialize repositories
            main_connector = self.connection_manager.get_connection("main")
            self._repositories["user"] = SolidUserRepository(main_connector)
            self._repositories["payout"] = SolidPayoutRepository(main_connector)
            self._repositories["attendance"] = SolidAttendanceRepository(main_connector)
            self._repositories["employee_leave"] = SolidEmployeeLeaveRepository(main_connector)
            self._repositories["reimbursement"] = SolidReimbursementRepository(main_connector)
            
            logger.info("Database migration service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database migration service: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up database connections."""
        try:
            await self.connection_manager.close_all()
            logger.info("Database migration service cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up database migration service: {e}")
    
    def get_user_repository(self) -> SolidUserRepository:
        """
        Get user repository instance.
        
        Returns:
            SOLID-compliant user repository
        """
        return self._repositories["user"]
    
    def get_payout_repository(self) -> SolidPayoutRepository:
        """
        Get payout repository instance.
        
        Returns:
            SOLID-compliant payout repository
        """
        return self._repositories["payout"]
    
    def get_attendance_repository(self) -> SolidAttendanceRepository:
        """
        Get attendance repository instance.
        
        Returns:
            SOLID-compliant attendance repository
        """
        return self._repositories["attendance"]
    
    def get_employee_leave_repository(self) -> SolidEmployeeLeaveRepository:
        """
        Get employee leave repository instance.
        
        Returns:
            SOLID-compliant employee leave repository
        """
        return self._repositories["employee_leave"]
    
    def get_reimbursement_repository(self) -> SolidReimbursementRepository:
        """
        Get reimbursement repository instance.
        
        Returns:
            SOLID-compliant reimbursement repository
        """
        return self._repositories["reimbursement"]
    
    # Legacy compatibility methods
    async def create_user_legacy(self, user_data: Dict[str, Any], hostname: str) -> Dict[str, Any]:
        """
        Legacy compatibility for create_user() function.
        
        Args:
            user_data: User data dictionary
            hostname: Organization hostname
            
        Returns:
            Creation result dictionary
        """
        try:
            user_repo = self.get_user_repository()
            result = await user_repo.create_user_legacy(user_data, hostname)
            
            logger.info(f"Created user (legacy): {user_data.get('employee_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating user (legacy): {e}")
            raise
    
    async def get_all_users_legacy(self, hostname: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_all_users() function.
        
        Args:
            hostname: Organization hostname
            
        Returns:
            List of user documents
        """
        try:
            user_repo = self.get_user_repository()
            users = await user_repo.get_all_users_legacy(hostname)
            
            logger.info(f"Retrieved {len(users)} users (legacy)")
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users (legacy): {e}")
            raise
    
    async def get_users_stats_legacy(self, hostname: str) -> Dict[str, int]:
        """
        Legacy compatibility for get_users_stats() function.
        
        Args:
            hostname: Organization hostname
            
        Returns:
            User statistics dictionary
        """
        try:
            user_repo = self.get_user_repository()
            stats = await user_repo.get_users_stats_legacy(hostname)
            
            logger.info(f"Retrieved user stats (legacy): {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats (legacy): {e}")
            raise
    
    async def get_user_by_employee_id_legacy(self, employee_id: str, hostname: str) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility for get_user_by_employee_id() function.
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname
            
        Returns:
            User document or None
        """
        try:
            user_repo = self.get_user_repository()
            
            # Use the new SOLID method but return raw document for compatibility
            try:
                from app.domain.value_objects.employee_id import EmployeeId
            except ImportError:
                # Create a simple EmployeeId class if not available
                class EmployeeId:
                    def __init__(self, value: str):
                        self.value = value
                    def __str__(self):
                        return self.value
            
            user = await user_repo.get_by_id(EmployeeId(employee_id))
            
            if user:
                # Convert back to document format for legacy compatibility
                return {
                    "employee_id": getattr(user, 'employee_id', getattr(user, 'employee_id', employee_id)),
                    "email": getattr(user, 'email', ''),
                    "name": getattr(user, 'name', ''),
                    "gender": getattr(user, 'gender', ''),
                    "date_of_birth": getattr(user, 'date_of_birth', None),
                    "date_of_joining": getattr(user, 'date_of_joining', None),
                    "date_of_leaving": getattr(user, 'date_of_leaving', None),
                    "mobile": getattr(user, 'mobile', ''),
                    "password": getattr(user, 'password', ''),
                    "role": getattr(user, 'role', ''),
                    "status": getattr(user, 'status', ''),
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
                    "created_at": getattr(user, 'created_at', None),
                    "updated_at": getattr(user, 'updated_at', None)
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by employee_id (legacy): {e}")
            raise
    
    async def update_user_leave_balance_legacy(
        self, 
        employee_id: str, 
        leave_name: str, 
        leave_count: int, 
        hostname: str
    ) -> Dict[str, Any]:
        """
        Legacy compatibility for update_user_leave_balance() function.
        
        Args:
            employee_id: Employee ID
            leave_name: Name of leave type
            leave_count: Leave count to add/subtract
            hostname: Organization hostname
            
        Returns:
            Update result dictionary
        """
        try:
            user_repo = self.get_user_repository()
            
            try:
                from app.domain.value_objects.employee_id import EmployeeId
            except ImportError:
                # Create a simple EmployeeId class if not available
                class EmployeeId:
                    def __init__(self, value: str):
                        self.value = value
                    def __str__(self):
                        return self.value
            
            result = await user_repo.update_leave_balance(
                EmployeeId(employee_id), leave_name, leave_count, hostname
            )
            
            if result:
                logger.info(f"Updated leave balance (legacy): {employee_id}")
                return {"msg": "Leave balance updated successfully"}
            else:
                return {"msg": "User not found or no changes made"}
                
        except Exception as e:
            logger.error(f"Error updating leave balance (legacy): {e}")
            raise
    
    # Health check and monitoring
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of database migration service.
        
        Returns:
            Health status information
        """
        try:
            status = self.connection_manager.get_connection_status()
            
            # Check repository health
            repo_health = {}
            for name, repo in self._repositories.items():
                repo_health[name] = await repo.health_check()
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "connections": status,
                "repositories": repo_health
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    # Migration utilities
    async def migrate_collection_indexes(self, organization_id: str) -> Dict[str, Any]:
        """
        Migrate collection indexes for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Migration result
        """
        try:
            connector = self.connection_manager.get_connection("main")
            
            # Define indexes for users collection
            user_indexes = [
                {
                    "keys": [("employee_id", 1)],
                    "unique": True,
                    "name": "employee_id_unique"
                },
                {
                    "keys": [("email", 1)],
                    "unique": True,
                    "sparse": True,
                    "name": "email_unique"
                },
                {
                    "keys": [("mobile", 1)],
                    "unique": True,
                    "sparse": True,
                    "name": "mobile_unique"
                },
                {
                    "keys": [("role", 1)],
                    "name": "role_index"
                },
                {
                    "keys": [("department", 1)],
                    "name": "department_index"
                },
                {
                    "keys": [("manager_id", 1)],
                    "name": "manager_id_index"
                },
                {
                    "keys": [("is_active", 1)],
                    "name": "is_active_index"
                },
                {
                    "keys": [("created_at", -1)],
                    "name": "created_at_desc"
                }
            ]
            
            await connector.create_indexes(
                f"pms_{organization_id}",
                "users_info",
                user_indexes
            )
            
            logger.info(f"Migrated indexes for organization: {organization_id}")
            return {
                "status": "success",
                "organization_id": organization_id,
                "indexes_created": len(user_indexes)
            }
            
        except Exception as e:
            logger.error(f"Error migrating indexes for {organization_id}: {e}")
            return {
                "status": "error",
                "organization_id": organization_id,
                "error": str(e)
            }


# Global migration service instance
_migration_service: Optional[DatabaseMigrationService] = None


async def get_migration_service(connection_string: str) -> DatabaseMigrationService:
    """
    Get or create global migration service instance.
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        Database migration service instance
    """
    global _migration_service
    
    if _migration_service is None:
        _migration_service = DatabaseMigrationService(connection_string)
        await _migration_service.initialize()
    
    return _migration_service


async def cleanup_migration_service() -> None:
    """Clean up global migration service instance."""
    global _migration_service
    
    if _migration_service is not None:
        await _migration_service.cleanup()
        _migration_service = None


# Legacy function wrappers for backward compatibility
async def create_user_solid(user_data: Dict[str, Any], hostname: str) -> Dict[str, Any]:
    """
    SOLID-compliant wrapper for create_user() function.
    
    This function provides backward compatibility while using the new SOLID architecture.
    """
    try:
        from config import MONGO_URI
    except ImportError:
        # Fallback to environment variable or default
        import os
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    migration_service = await get_migration_service(MONGO_URI)
    return await migration_service.create_user_legacy(user_data, hostname)


async def get_all_users_solid(hostname: str) -> List[Dict[str, Any]]:
    """
    SOLID-compliant wrapper for get_all_users() function.
    
    This function provides backward compatibility while using the new SOLID architecture.
    """
    try:
        from config import MONGO_URI
    except ImportError:
        import os
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    migration_service = await get_migration_service(MONGO_URI)
    return await migration_service.get_all_users_legacy(hostname)


async def get_users_stats_solid(hostname: str) -> Dict[str, int]:
    """
    SOLID-compliant wrapper for get_users_stats() function.
    
    This function provides backward compatibility while using the new SOLID architecture.
    """
    try:
        from config import MONGO_URI
    except ImportError:
        import os
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    migration_service = await get_migration_service(MONGO_URI)
    return await migration_service.get_users_stats_legacy(hostname)


async def get_user_by_employee_id_solid(employee_id: str, hostname: str) -> Optional[Dict[str, Any]]:
    """
    SOLID-compliant wrapper for get_user_by_employee_id() function.
    
    This function provides backward compatibility while using the new SOLID architecture.
    """
    try:
        from config import MONGO_URI
    except ImportError:
        import os
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    migration_service = await get_migration_service(MONGO_URI)
    return await migration_service.get_user_by_employee_id_legacy(employee_id, hostname)


async def update_user_leave_balance_solid(
    employee_id: str, 
    leave_name: str, 
    leave_count: int, 
    hostname: str
) -> Dict[str, Any]:
    """
    SOLID-compliant wrapper for update_user_leave_balance() function.
    
    This function provides backward compatibility while using the new SOLID architecture.
    """
    try:
        from config import MONGO_URI
    except ImportError:
        import os
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    migration_service = await get_migration_service(MONGO_URI)
    return await migration_service.update_user_leave_balance_legacy(
        employee_id, leave_name, leave_count, hostname
    ) 