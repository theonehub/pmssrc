#!/usr/bin/env python3
"""
Script to create a test user in the database for development/testing purposes.
This script bypasses the normal authentication flow to create a user directly in the database.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.auth.password_handler import hash_password


async def create_test_user():
    """Create a test user in the database."""
    
    # Test user credentials
    test_user = {
        "username": "admin",
        "employee_id": "EMP001",
        "name": "Admin User",
        "email": "admin@localhost.com",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "department": "IT",
        "designation": "System Administrator",
        "mobile": "1234567890",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "date_of_joining": "2024-01-01",
        "is_active": True,
        "status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": "system",
        "last_login": None,
        "login_count": 0,
        "failed_login_attempts": 0
    }
    
    try:
        # Connect to MongoDB
        connector = MongoDBConnector()
        connection_string = get_mongodb_connection_string()
        options = get_mongodb_client_options()
        
        print(f"Connecting to MongoDB: {connection_string}")
        await connector.connect(connection_string, **options)
        
        # Create user in global database
        db_name = "pms_global_database"
        users_collection = connector.get_collection(db_name, 'users_info')
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"username": test_user["username"]})
        
        if existing_user:
            print(f"User {test_user['username']} already exists in database")
            # Update the existing user
            await users_collection.update_one(
                {"username": test_user["username"]},
                {"$set": {
                    "password_hash": test_user["password_hash"],
                    "updated_at": datetime.now(),
                    "is_active": True
                }}
            )
            print(f"Updated existing user {test_user['username']} with new password")
        else:
            # Insert new user
            await users_collection.insert_one(test_user)
            print(f"Created new user {test_user['username']} in database")
        
        # Also create in localhost database
        db_name = "pms_localhost"
        users_collection = connector.get_collection(db_name, 'users_info')
        
        existing_user = await users_collection.find_one({"username": test_user["username"]})
        
        if existing_user:
            print(f"User {test_user['username']} already exists in localhost database")
            # Update the existing user
            await users_collection.update_one(
                {"username": test_user["username"]},
                {"$set": {
                    "password_hash": test_user["password_hash"],
                    "updated_at": datetime.now(),
                    "is_active": True
                }}
            )
            print(f"Updated existing user {test_user['username']} in localhost database")
        else:
            # Insert new user
            await users_collection.insert_one(test_user)
            print(f"Created new user {test_user['username']} in localhost database")
        
        await connector.disconnect()
        
        print("\n" + "="*50)
        print("TEST USER CREATED SUCCESSFULLY")
        print("="*50)
        print(f"Username: {test_user['username']}")
        print(f"Password: admin123")
        print(f"Employee ID: {test_user['employee_id']}")
        print(f"Role: {test_user['role']}")
        print(f"Email: {test_user['email']}")
        print("="*50)
        print("\nYou can now login with these credentials!")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(create_test_user()) 