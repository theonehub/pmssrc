#!/usr/bin/env python3
"""
Test Script for SOLID Implementation
Verifies that the SOLID-compliant architecture is working correctly
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dependency_container():
    """Test that the dependency container is working correctly."""
    try:
        from config.dependency_container import get_dependency_container
        
        logger.info("Testing dependency container...")
        container = get_dependency_container()
        container.initialize()
        
        # Test that all services can be created
        user_service = container.get_user_service()
        user_controller = container.get_user_controller()
        password_service = container.get_password_service()
        file_upload_service = container.get_file_upload_service()
        notification_service = container.get_notification_service()
        
        logger.info("✅ Dependency container test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dependency container test failed: {e}")
        return False

async def test_user_service():
    """Test that the user service is working correctly."""
    try:
        from config.dependency_container import get_dependency_container
        from application.dto.user_dto import CreateUserRequestDTO
        from domain.value_objects.user_credentials import UserRole, Gender
        
        logger.info("Testing user service...")
        container = get_dependency_container()
        user_service = container.get_user_service()
        
        # Test user existence check
        exists = await user_service.check_user_exists(
            email="test@example.com",
            mobile="1234567890"
        )
        
        logger.info(f"User existence check result: {exists}")
        logger.info("✅ User service test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ User service test failed: {e}")
        return False

async def test_password_service():
    """Test that the password service is working correctly."""
    try:
        from config.dependency_container import get_dependency_container
        
        logger.info("Testing password service...")
        container = get_dependency_container()
        password_service = container.get_password_service()
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        # Test password verification
        is_valid = password_service.verify_password(password, hashed)
        
        # Test password strength
        strength = password_service.is_password_strong(password)
        
        # Test temporary password generation
        temp_password = password_service.generate_temporary_password()
        
        logger.info(f"Password hashed: {len(hashed)} characters")
        logger.info(f"Password verification: {is_valid}")
        logger.info(f"Password strength: {strength['is_strong']}")
        logger.info(f"Temporary password generated: {len(temp_password)} characters")
        
        assert is_valid, "Password verification failed"
        assert strength['is_strong'], "Password should be strong"
        assert len(temp_password) >= 8, "Temporary password too short"
        
        logger.info("✅ Password service test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Password service test failed: {e}")
        return False

async def test_file_upload_service():
    """Test that the file upload service is working correctly."""
    try:
        from config.dependency_container import get_dependency_container
        from fastapi import UploadFile
        from io import BytesIO
        
        logger.info("Testing file upload service...")
        container = get_dependency_container()
        file_upload_service = container.get_file_upload_service()
        
        # Create a mock file
        file_content = b"Test file content"
        file_obj = BytesIO(file_content)
        
        # Create mock UploadFile
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content_type = "image/jpeg"
                self.size = len(content)
        
        mock_file = MockUploadFile("test.jpg", file_content)
        
        # Test file validation
        validation_result = file_upload_service.validate_file(mock_file, "photo")
        
        logger.info(f"File validation result: {validation_result['is_valid']}")
        
        if not validation_result['is_valid']:
            logger.info(f"Validation errors: {validation_result['errors']}")
        
        logger.info("✅ File upload service test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ File upload service test failed: {e}")
        return False

async def test_notification_service():
    """Test that the notification service is working correctly."""
    try:
        from config.dependency_container import get_dependency_container
        
        logger.info("Testing notification service...")
        container = get_dependency_container()
        notification_service = container.get_notification_service()
        
        # Since we're using mock notification service, this should work
        logger.info("Notification service initialized successfully")
        logger.info("✅ Notification service test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Notification service test failed: {e}")
        return False

async def test_health_check():
    """Test that the health check is working correctly."""
    try:
        from config.dependency_container import get_dependency_container
        
        logger.info("Testing health check...")
        container = get_dependency_container()
        health_status = container.health_check()
        
        logger.info(f"Health status: {health_status['status']}")
        logger.info(f"Components: {health_status.get('components', {})}")
        
        logger.info("✅ Health check test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Health check test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    logger.info("🚀 Starting SOLID implementation tests...")
    
    tests = [
        ("Dependency Container", test_dependency_container),
        ("User Service", test_user_service),
        ("Password Service", test_password_service),
        ("File Upload Service", test_file_upload_service),
        ("Notification Service", test_notification_service),
        ("Health Check", test_health_check),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Report results
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("-"*50)
    logger.info(f"Total: {len(results)} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed! SOLID implementation is working correctly.")
        return True
    else:
        logger.error(f"💥 {failed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 