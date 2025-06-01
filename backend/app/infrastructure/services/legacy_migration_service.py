"""
Legacy Migration Service
Provides backward-compatible methods while using new SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.application.interfaces.services.user_service import UserService
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UserLoginRequestDTO, UserResponseDTO
)
from app.domain.value_objects.user_credentials import UserRole, UserStatus, Gender

logger = logging.getLogger(__name__)


class LegacyMigrationService:
    """
    Service to provide legacy-compatible methods while using new architecture.
    
    This service acts as an adapter between legacy code and new SOLID architecture,
    allowing gradual migration without breaking existing functionality.
    """
    
    def __init__(self, user_service: UserService):
        """
        Initialize with new user service.
        
        Args:
            user_service: New SOLID-compliant user service
        """
        self.user_service = user_service
    
    async def create_default_user(self) -> str:
        """
        Create default superadmin user (legacy compatibility).
        
        Returns:
            Message indicating success or that user already exists
        """
        try:
            # Check if default user already exists
            existing_user = await self.user_service.get_user_by_id("superadmin")
            if existing_user:
                logger.info("Default user already exists.")
                return "Default user already exists"
            
            # Create default user using new service
            request = CreateUserRequestDTO(
                employee_id="superadmin",
                email="clickankit4u@gmail.com",
                name="superadmin",
                password="admin123",
                role=UserRole.SUPERADMIN,
                gender=Gender.MALE,
                date_of_birth="1990-01-01",
                date_of_joining="1990-01-01",
                mobile="1234567890",
                department="admin",
                designation="admin",
                location="admin",
                manager_id="admin",
                status=UserStatus.ACTIVE
            )
            
            user = await self.user_service.create_user(request)
            logger.info(f"Default user created successfully: {user.employee_id}")
            return f"User created successfully, ID: {user.employee_id}"
            
        except Exception as e:
            logger.error(f"Error creating default user: {e}")
            raise
    
    async def get_user_by_employee_id(self, employee_id: str, hostname: str = None) -> Optional[Dict[str, Any]]:
        """
        Get user by employee ID (legacy compatibility).
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname (for legacy compatibility)
            
        Returns:
            User data in legacy format or None
        """
        try:
            user = await self.user_service.get_user_by_id(employee_id)
            if not user:
                return None
            
            # Convert to legacy format
            return {
                "employee_id": user.employee_id,
                "name": user.name,
                "email": user.email,
                "mobile": user.mobile,
                "password": user.password_hash,
                "role": user.role,
                "department": user.department,
                "designation": user.designation,
                "location": user.location,
                "manager_id": user.manager_id,
                "is_active": user.status == "active",
                "gender": user.gender,
                "dob": user.date_of_birth,
                "doj": user.date_of_joining,
                "dol": user.date_of_leaving or "",
                "pan_number": user.pan_number,
                "aadhar_number": user.aadhar_number,
                "photo_path": user.photo_path,
                "pan_document_path": user.pan_document_path,
                "aadhar_document_path": user.aadhar_document_path,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting user by employee_id {employee_id}: {e}")
            return None
    
    async def get_all_users(self, hostname: str = None) -> List[Dict[str, Any]]:
        """
        Get all users (legacy compatibility).
        
        Args:
            hostname: Organization hostname (for legacy compatibility)
            
        Returns:
            List of users in legacy format
        """
        try:
            result = await self.user_service.get_all_users(
                skip=0,
                limit=1000,  # Large limit for legacy compatibility
                include_inactive=True
            )
            
            # Convert to legacy format
            legacy_users = []
            for user in result.users:
                legacy_user = {
                    "employee_id": user.employee_id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile,
                    "role": user.role,
                    "department": user.department,
                    "designation": user.designation,
                    "location": user.location,
                    "manager_id": user.manager_id,
                    "is_active": user.status == "active",
                    "gender": user.gender,
                    "dob": user.date_of_birth,
                    "doj": user.date_of_joining,
                    "dol": user.date_of_leaving or "",
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                legacy_users.append(legacy_user)
            
            return legacy_users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_users_stats(self, hostname: str = None) -> Dict[str, Any]:
        """
        Get user statistics (legacy compatibility).
        
        Args:
            hostname: Organization hostname (for legacy compatibility)
            
        Returns:
            User statistics in legacy format
        """
        try:
            stats = await self.user_service.get_user_statistics()
            
            # Convert to legacy format
            return {
                "total_users": stats.total_users,
                "active_users": stats.active_users,
                "inactive_users": stats.inactive_users,
                "total_admins": stats.users_by_role.get("admin", 0),
                "total_employees": stats.users_by_role.get("employee", 0),
                "total_managers": stats.users_by_role.get("manager", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "total_admins": 0,
                "total_employees": 0,
                "total_managers": 0
            }
    
    async def get_users_by_manager_id(self, manager_id: str, hostname: str = None) -> List[Dict[str, Any]]:
        """
        Get users by manager ID (legacy compatibility).
        
        Args:
            manager_id: Manager ID
            hostname: Organization hostname (for legacy compatibility)
            
        Returns:
            List of users under the manager in legacy format
        """
        try:
            users = await self.user_service.get_users_by_manager(manager_id)
            
            # Convert to legacy format
            legacy_users = []
            for user in users:
                legacy_user = {
                    "employee_id": user.employee_id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile,
                    "role": user.role,
                    "department": user.department,
                    "designation": user.designation,
                    "is_active": user.status == "active",
                    "manager_id": user.manager_id
                }
                legacy_users.append(legacy_user)
            
            return legacy_users
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            return []
    
    async def update_user_leave_balance(
        self, 
        employee_id: str, 
        leave_balance: Dict[str, Any], 
        hostname: str = None
    ) -> bool:
        """
        Update user leave balance (legacy compatibility).
        
        Args:
            employee_id: Employee ID
            leave_balance: Leave balance data
            hostname: Organization hostname (for legacy compatibility)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would need to be implemented based on how leave balance
            # is handled in the new architecture
            logger.info(f"Updating leave balance for user {employee_id}")
            
            # For now, return True as placeholder
            # In real implementation, this would update the user's leave balance
            # through the appropriate service
            return True
            
        except Exception as e:
            logger.error(f"Error updating leave balance for user {employee_id}: {e}")
            return False


# Global instance for legacy compatibility
_legacy_service: Optional[LegacyMigrationService] = None


def get_legacy_migration_service() -> LegacyMigrationService:
    """Get legacy migration service instance."""
    global _legacy_service
    if _legacy_service is None:
        from app.config.dependency_container import get_user_service
        user_service = get_user_service()
        _legacy_service = LegacyMigrationService(user_service)
    return _legacy_service


# Legacy function wrappers for backward compatibility
async def create_default_user() -> str:
    """Legacy function wrapper."""
    service = get_legacy_migration_service()
    return await service.create_default_user()


async def get_user_by_employee_id(employee_id: str, hostname: str = None) -> Optional[Dict[str, Any]]:
    """Legacy function wrapper."""
    service = get_legacy_migration_service()
    return await service.get_user_by_employee_id(employee_id, hostname)


async def get_all_users(hostname: str = None) -> List[Dict[str, Any]]:
    """Legacy function wrapper."""
    service = get_legacy_migration_service()
    return await service.get_all_users(hostname)


async def get_users_stats(hostname: str = None) -> Dict[str, Any]:
    """Legacy function wrapper."""
    service = get_legacy_migration_service()
    return await service.get_users_stats(hostname)


async def get_users_by_manager_id(manager_id: str, hostname: str = None) -> List[Dict[str, Any]]:
    """Legacy function wrapper."""
    service = get_legacy_migration_service()
    return await service.get_users_by_manager_id(manager_id, hostname)


async def update_user_leave_balance(
    employee_id: str, 
    leave_balance: Dict[str, Any], 
    hostname: str = None
) -> bool:
    """Legacy function wrapper."""
    service = get_legacy_migration_service()
    return await service.update_user_leave_balance(employee_id, leave_balance, hostname)


# Organisation service migration functions
async def user_creation_allowed(hostname: str) -> bool:
    """
    Check if user creation is allowed for the organization.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        True if user creation is allowed, False otherwise
    """
    try:
        from app.config.dependency_container import get_dependency_container
        
        container = get_dependency_container()
        organization_service = container.get_organization_service()
        
        # Get organization by hostname
        organization = await organization_service.get_organization_by_hostname(hostname)
        
        if not organization:
            logger.warning(f"Organization not found for hostname: {hostname}")
            return False
        
        # Check if used employee strength is less than total employee strength
        return organization.used_employee_strength < organization.employee_strength
        
    except Exception as e:
        logger.error(f"Error checking user creation allowance: {e}")
        return False


async def increment_used_employee_strength(hostname: str) -> bool:
    """
    Increment the used employee strength for an organization.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from app.config.dependency_container import get_dependency_container
        
        container = get_dependency_container()
        organization_service = container.get_organization_service()
        
        # Get organization by hostname
        organization = await organization_service.get_organization_by_hostname(hostname)
        
        if not organization:
            logger.warning(f"Organization not found for hostname: {hostname}")
            return False
        
        # Increment used employee strength
        await organization_service.increment_employee_usage(organization.organization_id)
        
        logger.info(f"Incremented employee strength for organization: {hostname}")
        return True
        
    except Exception as e:
        logger.error(f"Error incrementing employee strength: {e}")
        return False


async def decrement_used_employee_strength(hostname: str) -> bool:
    """
    Decrement the used employee strength for an organization.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from app.config.dependency_container import get_dependency_container
        
        container = get_dependency_container()
        organization_service = container.get_organization_service()
        
        # Get organization by hostname
        organization = await organization_service.get_organization_by_hostname(hostname)
        
        if not organization:
            logger.warning(f"Organization not found for hostname: {hostname}")
            return False
        
        # Decrement used employee strength
        await organization_service.decrement_employee_usage(organization.organization_id)
        
        logger.info(f"Decremented employee strength for organization: {hostname}")
        return True
        
    except Exception as e:
        logger.error(f"Error decrementing employee strength: {e}")
        return False


async def get_organisation_by_hostname(hostname: str):
    """
    Get organization by hostname.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        Organization data or None if not found
    """
    try:
        from app.config.dependency_container import get_dependency_container
        
        container = get_dependency_container()
        organization_service = container.get_organization_service()
        
        # Get organization by hostname
        organization = await organization_service.get_organization_by_hostname(hostname)
        
        return organization
        
    except Exception as e:
        logger.error(f"Error getting organization by hostname: {e}")
        return None


async def is_govt_organisation(hostname: str) -> bool:
    """
    Check if organization is a government organization.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        True if government organization, False otherwise
    """
    try:
        organization = await get_organisation_by_hostname(hostname)
        
        if not organization:
            logger.warning(f"Organization not found for hostname: {hostname}")
            return False
        
        return organization.is_govt_organisation
        
    except Exception as e:
        logger.error(f"Error checking if government organization: {e}")
        return False


def is_govt_organisation_sync(hostname: str) -> bool:
    """
    Synchronous wrapper for is_govt_organisation.
    Used for legacy code that cannot be easily converted to async.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        True if government organization, False otherwise
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(is_govt_organisation(hostname))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(is_govt_organisation(hostname))
    except Exception as e:
        logger.error(f"Error in synchronous government organization check: {e}")
        return False


def get_organisation_by_hostname_sync(hostname: str):
    """
    Synchronous wrapper for get_organisation_by_hostname.
    Used for legacy code that cannot be easily converted to async.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        Organization data or None if not found
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_organisation_by_hostname(hostname))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(get_organisation_by_hostname(hostname))
    except Exception as e:
        logger.error(f"Error in synchronous organization retrieval: {e}")
        return None


# Public Holiday service migration functions
async def is_public_holiday(date_str: str, hostname: str) -> bool:
    """
    Check if a given date is a public holiday.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        hostname: Organization hostname
        
    Returns:
        True if the date is a public holiday, False otherwise
    """
    try:
        from app.config.dependency_container import get_dependency_container
        
        container = get_dependency_container()
        public_holiday_controller = container.get_public_holiday_controller()
        
        # Use the SOLID-compliant controller to check
        is_holiday = await public_holiday_controller.is_public_holiday(date_str, hostname)
        
        logger.info(f"Checked if {date_str} is public holiday: {is_holiday}")
        return is_holiday
        
    except Exception as e:
        logger.error(f"Error checking public holiday for {date_str}: {e}")
        return False


def is_public_holiday_sync(date_str: str, hostname: str) -> bool:
    """
    Synchronous wrapper for is_public_holiday.
    Used for legacy code that cannot be easily converted to async.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        hostname: Organization hostname
        
    Returns:
        True if the date is a public holiday, False otherwise
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(is_public_holiday(date_str, hostname))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(is_public_holiday(date_str, hostname))
    except Exception as e:
        logger.error(f"Error in synchronous public holiday check: {e}")
        return False


# Company Leave service migration functions
async def get_company_leave_by_type(leave_type: str, hostname: str):
    """
    Get company leave policy by type.
    
    Args:
        leave_type: Type of leave
        hostname: Organization hostname
        
    Returns:
        Company leave policy or None if not found
    """
    try:
        from app.config.dependency_container import get_dependency_container
        from app.application.dto.company_leave_dto import CompanyLeaveSearchFiltersDTO
        
        container = get_dependency_container()
        company_leave_controller = container.get_company_leave_controller()
        
        # Search for leave policy by type
        filters = CompanyLeaveSearchFiltersDTO(
            leave_type=leave_type,
            active_only=True,
            skip=0,
            limit=1
        )
        
        leaves = await company_leave_controller.get_company_leaves(filters, hostname)
        
        if leaves:
            logger.info(f"Found company leave policy for type: {leave_type}")
            return leaves[0]
        else:
            logger.warning(f"No company leave policy found for type: {leave_type}")
            return None
        
    except Exception as e:
        logger.error(f"Error getting company leave by type {leave_type}: {e}")
        return None


def get_company_leave_by_type_sync(leave_type: str, hostname: str):
    """
    Synchronous wrapper for get_company_leave_by_type.
    Used for legacy code that cannot be easily converted to async.
    
    Args:
        leave_type: Type of leave
        hostname: Organization hostname
        
    Returns:
        Company leave policy or None if not found
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_company_leave_by_type(leave_type, hostname))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(get_company_leave_by_type(leave_type, hostname))
    except Exception as e:
        logger.error(f"Error in synchronous company leave retrieval: {e}")
        return None 