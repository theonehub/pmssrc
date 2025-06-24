#!/usr/bin/env python3
"""
Test script to verify the salary component assignment endpoint
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config.dependency_container import container
from app.api.controllers.salary_component_assignment_controller import SalaryComponentAssignmentController, CurrentUser

async def test_endpoint():
    """Test the global components endpoint"""
    try:
        print("Initializing container...")
        await container.initialize()
        print("Container initialized successfully")
        
        # Get the controller
        controller = container.get_salary_component_assignment_controller()
        print(f"Controller type: {type(controller)}")
        
        # Create a test user
        test_user = CurrentUser(
            employee_id="test_user",
            hostname="test.localhost",
            role="SUPERADMIN"
        )
        
        print("Testing get_global_components...")
        result = await controller.get_global_components(
            search_term="",
            component_type="",
            is_active=True,
            page=1,
            page_size=50,
            current_user=test_user
        )
        
        print(f"Result: {result}")
        
        if result["success"]:
            print("✅ Endpoint test successful!")
            print(f"Retrieved {result['total']} components")
        else:
            print("❌ Endpoint test failed!")
            print(f"Error: {result['message']}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await container.cleanup()

if __name__ == "__main__":
    asyncio.run(test_endpoint()) 