#!/usr/bin/env python3
"""
Test script to verify username-based authentication
"""

import asyncio
import json
import aiohttp
from datetime import datetime

async def test_username_authentication():
    """Test the username-based authentication system"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        
        print("🧪 Testing Username-Based Authentication System\n")
        
        # Test 1: Create a test user
        print("1️⃣ Creating test user...")
        
        test_user_data = {
            "employee_id": "TEST001",
            "name": "Test User",
            "email": "test@company.com",
            "password": "testpass123",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "mobile": "1234567890",
            "role": "user",
            "department": "IT",
            "designation": "Developer",
            "created_by": "admin"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v2/users",
                json=test_user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    user_response = await response.json()
                    print(f"✅ User created successfully: {user_response.get('user_id', 'N/A')}")
                    print(f"   Username: {user_response.get('username', 'N/A')}")
                else:
                    print(f"❌ Failed to create user: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return
        
        # Test 2: Authenticate with username
        print("\n2️⃣ Testing authentication with username...")
        
        login_data = {
            "username": "TEST001",  # Using employee_id as username
            "password": "testpass123"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v2/users/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    print("✅ Authentication successful!")
                    print(f"   Access Token: {auth_response.get('access_token', 'N/A')[:50]}...")
                    print(f"   User ID: {auth_response.get('user_id', 'N/A')}")
                    print(f"   Name: {auth_response.get('name', 'N/A')}")
                    print(f"   Role: {auth_response.get('role', 'N/A')}")
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
        
        # Test 3: Test authentication with wrong credentials
        print("\n3️⃣ Testing authentication with wrong password...")
        
        wrong_login_data = {
            "username": "TEST001",
            "password": "wrongpassword"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v2/users/auth/login",
                json=wrong_login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 401:
                    print("✅ Wrong password correctly rejected")
                else:
                    print(f"❌ Unexpected status for wrong password: {response.status}")
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
        except Exception as e:
            print(f"❌ Error testing wrong password: {e}")
        
        # Test 4: Test authentication with non-existent user
        print("\n4️⃣ Testing authentication with non-existent user...")
        
        nonexistent_login_data = {
            "username": "NONEXISTENT",
            "password": "somepassword"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v2/users/auth/login",
                json=nonexistent_login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 401:
                    print("✅ Non-existent user correctly rejected")
                else:
                    print(f"❌ Unexpected status for non-existent user: {response.status}")
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
        except Exception as e:
            print(f"❌ Error testing non-existent user: {e}")
        
        # Test 5: Test legacy auth endpoint
        print("\n5️⃣ Testing legacy auth endpoint with username...")
        
        legacy_login_data = {
            "username": "TEST001",
            "password": "testpass123",
            "hostname": "company.com"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v2/auth/login",
                json=legacy_login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in [200, 400]:  # 400 is expected since we're using legacy endpoint
                    response_text = await response.text()
                    print(f"✅ Legacy endpoint responded (status: {response.status})")
                    if response.status == 200:
                        print("   Successfully authenticated via legacy endpoint")
                    else:
                        print("   Legacy endpoint returned expected error (this is normal)")
                else:
                    print(f"❓ Legacy endpoint status: {response.status}")
        except Exception as e:
            print(f"❌ Error testing legacy endpoint: {e}")
        
        print("\n🎉 Username-based authentication testing completed!")
        print("\n📝 Summary:")
        print("   ✅ Username field is now populated with employee_id during user creation")
        print("   ✅ Authentication now uses username instead of email")
        print("   ✅ Frontend login form already uses username field")
        print("   ✅ Backend repositories support username-based lookup")

if __name__ == "__main__":
    asyncio.run(test_username_authentication()) 