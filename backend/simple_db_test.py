#!/usr/bin/env python3

import asyncio
import sys
import os
from pymongo import MongoClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import MONGO_URI, DATABASE_NAME

async def test_database():
    """Simple database connectivity test"""
    try:
        print("Starting simple database test...")
        print(f"MongoDB URI: {MONGO_URI}")
        print(f"Database Name: {DATABASE_NAME}")
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, tls=True)
        
        # Get the global database
        db = client[DATABASE_NAME]
        print(f"Connected to database: {db.name}")
        
        # List all collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Test users collection
        if "users" in collections:
            users_collection = db.users
            user_count = users_collection.count_documents({})
            print(f"Total users in collection: {user_count}")
            
            # Sample some users
            sample_users = list(users_collection.find({}).limit(3))
            print(f"Sample users found: {len(sample_users)}")
            
            for i, user in enumerate(sample_users):
                print(f"  User {i+1}:")
                print(f"    ID: {user.get('_id')}")
                print(f"    Name: {user.get('name', 'N/A')}")
                print(f"    Email: {user.get('email', 'N/A')}")
                print(f"    Hostname: {user.get('hostname', 'N/A')}")
                print(f"    Active: {user.get('is_active', 'N/A')}")
                print(f"    Department: {user.get('department', 'N/A')}")
                
            # Check different hostname values
            print("\n--- Hostname Analysis ---")
            hostname_counts = {}
            for user in users_collection.find({}, {"hostname": 1}):
                hostname = user.get("hostname", "null")
                hostname_counts[hostname] = hostname_counts.get(hostname, 0) + 1
            
            print("Hostname distribution:")
            for hostname, count in hostname_counts.items():
                print(f"  '{hostname}': {count} users")
                
        else:
            print("No 'users' collection found!")
            
        # Test with the MongoDB connection string from mongodb_config
        print("\n--- Testing with mongodb_config ---")
        from app.config.mongodb_config import get_mongodb_connection_string, mongodb_settings
        alt_connection_string = get_mongodb_connection_string()
        print(f"Alternative connection string: {alt_connection_string}")
        print(f"Database name from settings: {mongodb_settings.database_name}")
        
        # Try connecting with the alternative settings
        try:
            alt_client = MongoClient(alt_connection_string)
            alt_db = alt_client[mongodb_settings.database_name]
            alt_collections = alt_db.list_collection_names()
            print(f"Alternative DB collections: {alt_collections}")
            
            if "users" in alt_collections:
                alt_user_count = alt_db.users.count_documents({})
                print(f"Alternative DB user count: {alt_user_count}")
        except Exception as e:
            print(f"Error with alternative connection: {e}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database()) 