#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_repository_fix():
    """Test the fixed repository logic"""
    try:
        print("Testing repository fix...")
        
        # Import the MongoDB connector
        from app.infrastructure.database.mongodb_connector import MongoDBConnector
        from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
        
        # Create and connect database connector
        db_connector = MongoDBConnector()
        connection_string = get_mongodb_connection_string()
        client_options = get_mongodb_client_options()
        
        await db_connector.connect(connection_string, **client_options)
        print("✅ Database connector connected successfully")
        
        # Import and test user repository  
        from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
        
        user_repo = MongoDBUserRepository(db_connector)
        user_repo.set_connection_config(connection_string, client_options)
        
        # Test different hostname scenarios
        test_hostnames = [None, "localhost", "global", "pms_global_database"]
        
        for hostname in test_hostnames:
            print(f"\n--- Testing hostname: {hostname} ---")
            try:
                users, count = await user_repo.find_with_filters(None, hostname)
                print(f"✅ Found {count} users for hostname '{hostname}'")
                
                if users:
                    sample_user = users[0]
                    print(f"   Sample user: {sample_user.name} (ID: {sample_user.employee_id})")
                    
            except Exception as e:
                print(f"❌ Error with hostname '{hostname}': {e}")
        
        # Test the dashboard analytics use case
        print(f"\n--- Testing Dashboard Analytics Use Case ---")
        
        # Mock current user
        class MockCurrentUser:
            def __init__(self, hostname: str = "localhost"):
                self.hostname = hostname
                self.employee_id = "test123"
        
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository  
        from app.application.use_cases.reporting.get_dashboard_analytics_use_case import GetDashboardAnalyticsUseCase
        
        reimbursement_repo = MongoDBReimbursementRepository(db_connector)
        reimbursement_repo.set_connection_config(connection_string, client_options)
        
        analytics_use_case = GetDashboardAnalyticsUseCase(
            user_repository=user_repo,
            reimbursement_repository=reimbursement_repo,
            attendance_repository=None
        )
        
        # Test with None hostname (should use global database)
        current_user = MockCurrentUser(None)
        analytics = await analytics_use_case.execute(current_user)
        
        print(f"✅ Analytics result:")
        print(f"   Total users: {analytics.total_users}")
        print(f"   Active users: {analytics.active_users}")
        print(f"   Departments: {analytics.total_departments}")
        print(f"   Generated at: {analytics.generated_at}")
        
        if hasattr(analytics, 'error_message') and analytics.error_message:
            print(f"   ⚠️  Error: {analytics.error_message}")
        else:
            print(f"   ✅ No errors in analytics")
        
        await db_connector.disconnect()
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_repository_fix()) 