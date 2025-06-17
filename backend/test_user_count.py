#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.database.database_connector import get_database

async def test_user_count():
    """Test retrieving users from database"""
    try:
        print("Testing user repository...")
        db = get_database()
        repo = MongoDBUserRepository(db)
        
        users, count = await repo.find_with_filters(None, 'localhost')
        print(f"Total users found: {count}")
        
        if users:
            print("Sample users:")
            for i, user in enumerate(users[:3]):  # Show first 3 users
                print(f"  {i+1}. Name: {user.name}, Active: {user.is_active}, Dept: {user.department}")
        else:
            print("No users found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_count()) 