# tests/test_user_service.py
import pytest
from app.services import user_service

def test_create_user():
    user_doc = {"name": "Test User", "gender": "male", "dob": "1990-01-01", "doj": "2020-01-01", "mobile": "1234567890"}
    login_doc = {"username": "testuser", "password": "hashedpwd", "role": "user"}
    result = user_service.create_user(user_doc, login_doc)
    assert "successfully" in result.get("msg", "").lower()
