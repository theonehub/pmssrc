# tests/test_user_service.py
import pytest
from app.services import user_service
from app.dependencies import get_dependency_container

def test_create_user():
    user_doc = {"name": "Test User", "gender": "male", "date_of_birth": "1990-01-01", "date_of_joining": "2020-01-01", "mobile": "1234567890"}
    login_doc = {"username": "testuser", "password": "hashedpwd", "role": "user"}
    result = user_service.create_user(user_doc, login_doc)
    assert "successfully" in result.get("msg", "").lower()

async def test_user_service():
    try:
        # Test data
        user_doc = {"name": "Test User", "gender": "male", "date_of_birth": "1990-01-01", "date_of_joining": "2020-01-01", "mobile": "1234567890"}
        
        # Get user service using dependency injection
        container = get_dependency_container()
        user_service = container.get_user_service()

        # ... existing code ...
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
