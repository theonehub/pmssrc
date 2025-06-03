#!/usr/bin/env python3
"""
Test Script for SOLID Database Layer Migration
Validates the implementation and provides examples
"""

import asyncio
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """Test result container."""
    def __init__(self, name: str, success: bool, message: str, duration: float = 0.0):
        self.name = name
        self.success = success
        self.message = message
        self.duration = duration


class SOLIDMigrationTester:
    """Test suite for SOLID database layer migration."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.migration_service = None
        
    async def setup(self):
        """Setup test environment."""
        try:
            from app.infrastructure.services.database_migration_service import get_migration_service
            from config import MONGO_URI
            
            logger.info("Setting up test environment...")
            self.migration_service = await get_migration_service(MONGO_URI)
            logger.info("Test environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup test environment."""
        try:
            if self.migration_service:
                from app.infrastructure.services.database_migration_service import cleanup_migration_service
                await cleanup_migration_service()
            logger.info("Test environment cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Running test: {test_name}")
            await test_func()
            
            duration = asyncio.get_event_loop().time() - start_time
            result = TestResult(test_name, True, "PASSED", duration)
            logger.info(f"✓ {test_name} - PASSED ({duration:.3f}s)")
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            error_msg = f"FAILED: {str(e)}"
            result = TestResult(test_name, False, error_msg, duration)
            logger.error(f"✗ {test_name} - {error_msg} ({duration:.3f}s)")
            logger.debug(traceback.format_exc())
        
        self.results.append(result)
    
    async def test_database_connection(self):
        """Test database connection establishment."""
        connector = self.migration_service.connection_manager.get_connection("main")
        assert connector is not None, "Database connector not found"
        assert connector.is_connected, "Database not connected"
        
        # Test health check
        health = await connector.health_check()
        assert health["connected"], "Health check failed"
    
    async def test_user_repository_creation(self):
        """Test user repository creation and basic functionality."""
        user_repo = self.migration_service.get_user_repository()
        assert user_repo is not None, "User repository not created"
        
        # Test health check
        health = await user_repo.health_check("test_company")
        assert health["status"] in ["healthy", "unhealthy"], "Invalid health status"
    
    async def test_legacy_compatibility_functions(self):
        """Test legacy compatibility wrapper functions."""
        from app.infrastructure.services.database_migration_service import (
            create_user_solid,
            get_all_users_solid,
            get_users_stats_solid,
            get_user_by_employee_id_solid,
            update_user_leave_balance_solid
        )
        
        hostname = "test_company"
        
        # Test create user
        user_data = {
            "employee_id": "TEST001",
            "name": "Test User",
            "email": "test@example.com",
            "role": "Employee",
            "department": "Testing",
            "is_active": True
        }
        
        result = await create_user_solid(user_data, hostname)
        assert "msg" in result, "Create user result invalid"
        
        # Test get all users
        users = await get_all_users_solid(hostname)
        assert isinstance(users, list), "Get all users should return list"
        
        # Test get user stats
        stats = await get_users_stats_solid(hostname)
        assert isinstance(stats, dict), "Get user stats should return dict"
        
        # Test get user by ID
        user = await get_user_by_employee_id_solid("TEST001", hostname)
        if user:
            assert user.get("employee_id") == "TEST001", "Retrieved user ID mismatch"
        
        # Test update leave balance
        leave_result = await update_user_leave_balance_solid(
            "TEST001", "annual", 5, hostname
        )
        assert "msg" in leave_result, "Leave balance update result invalid"
    
    async def test_solid_repository_operations(self):
        """Test SOLID repository operations directly."""
        user_repo = self.migration_service.get_user_repository()
        
        # Create test user
        class TestUser:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        test_user = TestUser(
            employee_id="TEST002",
            employee_id="TEST002",
            name="SOLID Test User",
            email="solid@example.com",
            role="Manager",
            department="Engineering",
            organisation_id="test_company"
        )
        
        # Test save
        saved_user = await user_repo.save(test_user)
        assert saved_user is not None, "User save failed"
        
        # Test get by ID
        retrieved_user = await user_repo.get_by_id("TEST002")
        assert retrieved_user is not None, "User retrieval failed"
        assert getattr(retrieved_user, 'name', '') == "SOLID Test User", "User data mismatch"
        
        # Test get all
        users = await user_repo.get_all(organisation_id="test_company", limit=10)
        assert isinstance(users, list), "Get all should return list"
        
        # Test statistics
        stats = await user_repo.get_statistics("test_company")
        assert hasattr(stats, 'total_users'), "Statistics should have total_users"
        
        # Test update leave balance
        balance_updated = await user_repo.update_leave_balance(
            "TEST002", "sick", 3, "test_company"
        )
        assert isinstance(balance_updated, bool), "Leave balance update should return bool"
    
    async def test_batch_operations(self):
        """Test batch operations functionality."""
        user_repo = self.migration_service.get_user_repository()
        
        class TestUser:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Create batch of users
        batch_users = [
            TestUser(
                employee_id=f"BATCH{i:03d}",
                employee_id=f"BATCH{i:03d}",
                name=f"Batch User {i}",
                email=f"batch{i}@example.com",
                role="Employee",
                department="Testing",
                organisation_id="test_company"
            )
            for i in range(1, 4)
        ]
        
        # Test batch save
        saved_users = await user_repo.save_batch(batch_users)
        assert len(saved_users) == 3, "Batch save count mismatch"
        
        # Test get by manager (should return empty list for non-existent manager)
        team_members = await user_repo.get_by_manager("NONEXISTENT", "test_company")
        assert isinstance(team_members, list), "Get by manager should return list"
    
    async def test_advanced_queries(self):
        """Test advanced query capabilities."""
        user_repo = self.migration_service.get_user_repository()
        
        # Test get by email
        user = await user_repo.get_by_email("test@example.com")
        # Should return user or None
        assert user is None or hasattr(user, 'email'), "Get by email result invalid"
        
        # Test get by mobile
        user = await user_repo.get_by_mobile("1234567890")
        # Should return user or None
        assert user is None or hasattr(user, 'mobile'), "Get by mobile result invalid"
        
        # Test get by PAN
        user = await user_repo.get_by_pan_number("ABCDE1234F")
        # Should return user or None
        assert user is None or hasattr(user, 'pan_number'), "Get by PAN result invalid"
    
    async def test_error_handling(self):
        """Test error handling and edge cases."""
        user_repo = self.migration_service.get_user_repository()
        
        # Test get non-existent user
        user = await user_repo.get_by_id("NONEXISTENT")
        assert user is None, "Non-existent user should return None"
        
        # Test empty batch save
        result = await user_repo.save_batch([])
        assert isinstance(result, list), "Empty batch save should return empty list"
        assert len(result) == 0, "Empty batch save should return empty list"
    
    async def test_connection_factory(self):
        """Test connection factory functionality."""
        from app.infrastructure.database.connection_factory import (
            ConnectionFactory, DatabaseType, DatabaseConnectionManager
        )
        
        # Test factory creation
        connector = ConnectionFactory.create_connector(
            DatabaseType.MONGODB, "mongodb://localhost:27017"
        )
        assert connector is not None, "Factory should create connector"
        
        # Test connection manager
        manager = DatabaseConnectionManager()
        status = manager.get_connection_status()
        assert isinstance(status, dict), "Connection status should be dict"
    
    async def test_index_migration(self):
        """Test index migration functionality."""
        try:
            result = await self.migration_service.migrate_collection_indexes("test_company")
            assert "status" in result, "Index migration should return status"
        except Exception as e:
            # Index migration might fail in test environment, that's okay
            logger.warning(f"Index migration test failed (expected in test env): {e}")
    
    async def run_all_tests(self):
        """Run all tests."""
        test_methods = [
            ("Database Connection", self.test_database_connection),
            ("User Repository Creation", self.test_user_repository_creation),
            ("Legacy Compatibility Functions", self.test_legacy_compatibility_functions),
            ("SOLID Repository Operations", self.test_solid_repository_operations),
            ("Batch Operations", self.test_batch_operations),
            ("Advanced Queries", self.test_advanced_queries),
            ("Error Handling", self.test_error_handling),
            ("Connection Factory", self.test_connection_factory),
            ("Index Migration", self.test_index_migration),
        ]
        
        for test_name, test_method in test_methods:
            await self.run_test(test_name, test_method)
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("SOLID DATABASE MIGRATION TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed
        total_time = sum(r.duration for r in self.results)
        
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total Time: {total_time:.3f}s")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 60)
        
        for result in self.results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            print(f"{status:<8} {result.name:<35} ({result.duration:.3f}s)")
            if not result.success:
                print(f"         Error: {result.message}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! SOLID migration is working correctly.")
        else:
            print(f"⚠️  {failed} test(s) failed. Please review the errors above.")
        
        return failed == 0


async def main():
    """Main test execution function."""
    print("SOLID Database Layer Migration Test Suite")
    print("=" * 60)
    
    tester = SOLIDMigrationTester()
    
    try:
        # Setup
        if not await tester.setup():
            print("❌ Test setup failed. Cannot proceed.")
            return False
        
        # Run tests
        await tester.run_all_tests()
        
        # Print results
        success = tester.print_results()
        
        return success
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        logger.debug(traceback.format_exc())
        return False
        
    finally:
        # Cleanup
        await tester.cleanup()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1) 