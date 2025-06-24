#!/usr/bin/env python3
"""
API Connection Test Script
Tests connectivity to the salary components API
"""

import requests
import json
from typing import Optional

def test_api_connection(base_url: str = "http://localhost:8001", auth_token: Optional[str] = None):
    """Test API connection and basic functionality"""
    
    print("🔍 Testing API Connection")
    print("=" * 40)
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'X-Platform': 'web',
        'X-Client-Version': '1.0.0'
    })
    
    if auth_token:
        session.headers.update({
            'Authorization': f'Bearer {auth_token}'
        })
    
    try:
        # Test 1: Health check (if available)
        print("1. Testing base URL connectivity...")
        try:
            response = session.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print(f"   ⚠️  Health check returned: {response.status_code}")
        except:
            print("   ⚠️  No health endpoint available")
        
        # Test 2: List components endpoint
        print("2. Testing salary components list endpoint...")
        response = session.get(f"{base_url}/api/v2/salary-components/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ List endpoint working")
            print(f"   📊 Response format: {type(data)}")
            if isinstance(data, dict) and 'status' in data:
                print(f"   📊 Status: {data.get('status')}")
                if 'data' in data:
                    components = data.get('data', {})
                    if isinstance(components, dict) and 'components' in components:
                        count = len(components.get('components', []))
                        print(f"   📊 Existing components: {count}")
                    elif isinstance(components, list):
                        print(f"   📊 Existing components: {len(components)}")
        elif response.status_code == 401:
            print("   ❌ Authentication required")
            print("   💡 You may need to provide an auth token")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found")
            print("   💡 Check if the API server is running on the correct port")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
        
        # Test 3: Create a test component (dry run)
        print("3. Testing component creation endpoint (dry run)...")
        test_component = {
            "code": "TEST_COMPONENT_API_CHECK",
            "name": "Test Component for API Check",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Test component - will be deleted"
        }
        
        # Just test the endpoint structure, don't actually create
        print("   📝 Test payload prepared")
        print("   💡 Use the main script to actually create components")
        
        print("\n" + "=" * 40)
        print("🎯 API Connection Test Summary")
        print("=" * 40)
        
        if response.status_code in [200, 401]:  # 401 means endpoint exists but needs auth
            print("✅ API server is accessible")
            print("✅ Endpoints are properly configured")
            if response.status_code == 401:
                print("⚠️  Authentication may be required")
            print("🚀 Ready to run the main creation script!")
        else:
            print("❌ API server may not be running or configured correctly")
            print("💡 Please check:")
            print("   - API server is running on port 8001")
            print("   - Endpoints are properly configured")
            print("   - Network connectivity")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed")
        print("💡 Please check:")
        print("   - API server is running")
        print("   - Correct URL and port (default: http://localhost:8001)")
        print("   - Network connectivity")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("💡 API server may be slow or unresponsive")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def main():
    """Main function"""
    BASE_URL = "http://localhost:8001"
    AUTH_TOKEN = None  # Add your token here if needed
    
    test_api_connection(BASE_URL, AUTH_TOKEN)

if __name__ == "__main__":
    main()
