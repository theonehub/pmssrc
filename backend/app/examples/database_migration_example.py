"""
Database Migration Example
Demonstrates how to use the new SOLID-compliant database layer
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration handling
def get_mongo_uri():
    """Get MongoDB URI from config or environment."""
    try:
        from config import MONGO_URI
        return MONGO_URI
    except ImportError:
        return os.getenv('MONGO_URI', 'mongodb://localhost:27017')


async def example_legacy_compatibility():
    """
    Example showing how to use legacy compatibility functions.
    
    These functions work exactly like the old procedural functions
    but use the new SOLID architecture underneath.
    """
    print("\n=== Legacy Compatibility Example ===")
    
    try:
        from app.infrastructure.services.database_migration_service import (
            create_user_solid,
            get_all_users_solid,
            get_users_stats_solid,
            get_user_by_employee_id_solid,
            update_user_leave_balance_solid
        )
        
        hostname = "example_company"
        
        # Create a user (legacy style)
        user_data = {
            "employee_id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "mobile": "1234567890",
            "role": "Employee",
            "department": "Engineering",
            "designation": "Software Engineer",
            "date_of_joining": datetime.now(),
            "is_active": True
        }
        
        print("Creating user...")
        result = await create_user_solid(user_data, hostname)
        print(f"Create result: {result}")
        
        # Get all users (legacy style)
        print("\nGetting all users...")
        users = await get_all_users_solid(hostname)
        print(f"Found {len(users)} users")
        
        # Get user statistics (legacy style)
        print("\nGetting user statistics...")
        stats = await get_users_stats_solid(hostname)
        print(f"User stats: {stats}")
        
        # Get specific user (legacy style)
        print("\nGetting specific user...")
        user = await get_user_by_employee_id_solid("EMP001", hostname)
        if user:
            print(f"Found user: {user.get('name', 'Unknown')}")
        
        # Update leave balance (legacy style)
        print("\nUpdating leave balance...")
        leave_result = await update_user_leave_balance_solid(
            "EMP001", "annual", 5, hostname
        )
        print(f"Leave update result: {leave_result}")
        
    except Exception as e:
        logger.error(f"Error in legacy compatibility example: {e}")


async def example_solid_repository():
    """
    Example showing how to use the new SOLID repository directly.
    
    This is the recommended approach for new code.
    """
    print("\n=== SOLID Repository Example ===")
    
    try:
        from app.infrastructure.services.database_migration_service import get_migration_service
        
        # Initialize migration service
        print("Initializing migration service...")
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        
        # Get user repository
        user_repo = migration_service.get_user_repository()
        
        # Create a simple user object (in real code, use proper domain entities)
        class SimpleUser:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        user = SimpleUser(
            employee_id="EMP002",
            employee_id="EMP002",  # For backward compatibility
            name="Jane Smith",
            email="jane.smith@example.com",
            mobile="0987654321",
            role="Manager",
            department="Engineering",
            designation="Engineering Manager",
            date_of_joining=datetime.now(),
            is_active=True,
            organisation_id="example_company"
        )
        
        # Save user using repository
        print("Saving user with repository...")
        saved_user = await user_repo.save(user)
        print(f"Saved user: {getattr(saved_user, 'employee_id', getattr(saved_user, 'employee_id', 'Unknown'))}")
        
        # Get user by ID
        print("\nGetting user by ID...")
        retrieved_user = await user_repo.get_by_id("EMP002")
        if retrieved_user:
            print(f"Retrieved user: {getattr(retrieved_user, 'name', 'Unknown')}")
        
        # Get all users with pagination
        print("\nGetting users with pagination...")
        users = await user_repo.get_all(
            skip=0, 
            limit=10, 
            organisation_id="example_company"
        )
        print(f"Found {len(users)} users")
        
        # Get user statistics
        print("\nGetting user statistics...")
        stats = await user_repo.get_statistics(organisation_id="example_company")
        print(f"Total users: {getattr(stats, 'total_users', 0)}")
        print(f"Users by role: {getattr(stats, 'users_by_role', {})}")
        
        # Update leave balance
        print("\nUpdating leave balance...")
        balance_updated = await user_repo.update_leave_balance(
            "EMP002", "sick", 3, "example_company"
        )
        print(f"Leave balance updated: {balance_updated}")
        
        # Health check
        print("\nPerforming health check...")
        health = await user_repo.health_check("example_company")
        print(f"Repository health: {health.get('status', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Error in SOLID repository example: {e}")


async def example_advanced_features():
    """
    Example showing advanced features available in the new architecture.
    
    These features were not available in the old procedural code.
    """
    print("\n=== Advanced Features Example ===")
    
    try:
        from app.infrastructure.services.database_migration_service import get_migration_service
        
        # Get migration service and repository
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        user_repo = migration_service.get_user_repository()
        
        # Batch operations
        print("Demonstrating batch operations...")
        
        class SimpleUser:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        users = [
            SimpleUser(
                employee_id=f"EMP00{i}",
                employee_id=f"EMP00{i}",
                name=f"User {i}",
                email=f"user{i}@example.com",
                role="Employee",
                department="Engineering",
                organisation_id="example_company"
            )
            for i in range(3, 6)
        ]
        
        saved_users = await user_repo.save_batch(users)
        print(f"Batch saved {len(saved_users)} users")
        
        # Get users by manager
        print("\nGetting users by manager...")
        team_members = await user_repo.get_by_manager(
            "EMP002", "example_company"
        )
        print(f"Found {len(team_members)} team members")
        
        # Service health check
        print("\nPerforming service health check...")
        service_health = await migration_service.health_check()
        print(f"Service status: {service_health.get('status', 'Unknown')}")
        
        # Migrate indexes
        print("\nMigrating collection indexes...")
        index_result = await migration_service.migrate_collection_indexes("example_company")
        print(f"Index migration: {index_result.get('status', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Error in advanced features example: {e}")


async def example_error_handling():
    """
    Example showing proper error handling in the new architecture.
    """
    print("\n=== Error Handling Example ===")
    
    try:
        from app.infrastructure.services.database_migration_service import get_migration_service
        
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        user_repo = migration_service.get_user_repository()
        
        # Try to get a non-existent user
        print("Trying to get non-existent user...")
        user = await user_repo.get_by_id("NONEXISTENT")
        if user is None:
            print("User not found (handled gracefully)")
        
        # Try to create duplicate user (would raise error in real scenario)
        print("\nTrying operations with proper error handling...")
        
        class SimpleUser:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        try:
            user = SimpleUser(
                employee_id="EMP001",  # Might already exist
                employee_id="EMP001",
                name="Duplicate User",
                email="duplicate@example.com",
                organisation_id="example_company"
            )
            await user_repo.save(user)
            print("User saved successfully")
        except Exception as e:
            print(f"Handled error gracefully: {type(e).__name__}")
        
    except Exception as e:
        logger.error(f"Error in error handling example: {e}")


async def example_performance_monitoring():
    """
    Example showing performance monitoring capabilities.
    """
    print("\n=== Performance Monitoring Example ===")
    
    try:
        from app.infrastructure.services.database_migration_service import get_migration_service
        import time
        
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        user_repo = migration_service.get_user_repository()
        
        # Measure operation performance
        print("Measuring operation performance...")
        
        start_time = time.time()
        users = await user_repo.get_all(limit=100, organisation_id="example_company")
        end_time = time.time()
        
        print(f"Retrieved {len(users)} users in {end_time - start_time:.3f} seconds")
        
        # Connection status
        print("\nChecking connection status...")
        status = migration_service.connection_manager.get_connection_status()
        print(f"Connection status: {status}")
        
        # Repository health metrics
        print("\nGetting repository health metrics...")
        health = await user_repo.health_check("example_company")
        print(f"Document count: {health.get('document_count', 'N/A')}")
        print(f"Health status: {health.get('status', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Error in performance monitoring example: {e}")


async def main():
    """
    Main function to run all examples.
    """
    print("Database Migration Examples")
    print("=" * 50)
    
    try:
        # Run all examples
        await example_legacy_compatibility()
        await example_solid_repository()
        await example_advanced_features()
        await example_error_handling()
        await example_performance_monitoring()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
    
    finally:
        # Clean up
        try:
            from app.infrastructure.services.database_migration_service import cleanup_migration_service
            await cleanup_migration_service()
            print("\nCleaned up migration service")
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 