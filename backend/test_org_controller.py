#!/usr/bin/env python3
"""
Test script to verify organisation controller initialization
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

async def test_organisation_controller():
    """Test organisation controller initialization"""
    try:
        print("Testing organisation controller initialization...")
        
        # Import and initialize the main app (which should initialize the controller)
        from app.main import app, initialize_organisation_dependencies
        
        # Initialize organisation dependencies
        success = initialize_organisation_dependencies()
        if not success:
            print("❌ Failed to initialize organisation dependencies")
            return False
        
        print("✅ Organisation dependencies initialized successfully")
        
        # Test getting the controller
        from app.config.dependency_container import get_organisation_controller
        controller = get_organisation_controller()
        
        if controller:
            print(f"✅ Organisation controller retrieved successfully: {type(controller).__name__}")
            
            # Test some controller methods exist
            methods_to_check = [
                'create_organisation',
                'list_organisations', 
                'get_organisation_by_id',
                'update_organisation',
                'delete_organisation'
            ]
            
            for method_name in methods_to_check:
                if hasattr(controller, method_name):
                    print(f"✅ Method {method_name} exists")
                else:
                    print(f"❌ Method {method_name} missing")
                    return False
            
            return True
        else:
            print("❌ Controller is None")
            return False
            
    except Exception as e:
        print(f"❌ Error testing controller: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("=== Organisation Controller Test ===")
    
    success = await test_organisation_controller()
    
    if success:
        print("\n🎉 All tests passed! Organisation controller is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Organisation controller has issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 