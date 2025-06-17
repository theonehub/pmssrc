#!/usr/bin/env python3

import asyncio
import sys
import os
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock current user class
class MockCurrentUser:
    def __init__(self, hostname: str = "localhost", employee_id: str = "test123"):
        self.hostname = hostname
        self.employee_id = employee_id

async def test_analytics():
    """Test analytics use case directly"""
    try:
        print("Starting analytics debug test...")
        
        # Direct database connection test
        from app.config.mongodb_config import get_mongodb_connection_string
        print(f"MongoDB connection string: {get_mongodb_connection_string()}")
        
        # Test database connection
        from app.database.database_connector import connect_to_database
        db = connect_to_database("global")  # Try with global database
        print(f"Database connected: {db.name}")
        
        # Test user repository
        from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
        user_repo = MongoDBUserRepository(db)
        
        # Test different hostnames
        hostnames_to_test = ["localhost", "local", "dev", "test"]
        
        for hostname in hostnames_to_test:
            print(f"\n--- Testing hostname: {hostname} ---")
            try:
                users, count = await user_repo.find_with_filters(None, hostname)
                print(f"Users found for '{hostname}': {count}")
                
                if users:
                    print("Sample user data:")
                    for i, user in enumerate(users[:2]):
                        print(f"  {i+1}. Name: {user.name}, Active: {user.is_active}, Dept: {user.department}")
                
            except Exception as e:
                print(f"Error with hostname '{hostname}': {e}")
        
        # Test with actual analytics use case
        print("\n--- Testing GetDashboardAnalyticsUseCase ---")
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from app.application.use_cases.reporting.get_dashboard_analytics_use_case import GetDashboardAnalyticsUseCase
        
        reimbursement_repo = MongoDBReimbursementRepository(db)
        use_case = GetDashboardAnalyticsUseCase(
            user_repository=user_repo,
            reimbursement_repository=reimbursement_repo,
            attendance_repository=None
        )
        
        # Test with localhost hostname first
        current_user = MockCurrentUser("localhost")
        analytics = await use_case.execute(current_user)
        
        print(f"\nAnalytics result:")
        print(f"  Total users: {analytics.total_users}")
        print(f"  Active users: {analytics.active_users}")
        print(f"  Departments: {analytics.total_departments}")
        print(f"  Generated at: {analytics.generated_at}")
        if hasattr(analytics, 'error_message') and analytics.error_message:
            print(f"  Error: {analytics.error_message}")
        
        # Try to list all collections to see what's in the database
        print("\n--- Database Collections ---")
        collections = await db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Check user collection specifically
        if "users" in collections:
            user_count = await db.users.count_documents({})
            print(f"Total documents in users collection: {user_count}")
            
            # Sample document
            sample_user = await db.users.find_one({})
            if sample_user:
                print(f"Sample user document keys: {list(sample_user.keys())}")
                if 'hostname' in sample_user:
                    print(f"Sample hostname value: '{sample_user['hostname']}'")
        else:
            print("No 'users' collection found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analytics()) 