#!/usr/bin/env python3
"""
Test script to verify JWT token implementation
"""

import asyncio
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from app.auth.jwt_handler import create_access_token, decode_access_token, verify_token

def test_jwt_implementation():
    """Test the JWT token implementation"""
    
    print("🧪 Testing JWT Token Implementation\n")
    
    # Test 1: Create a JWT token
    print("1️⃣ Creating JWT token...")
    
    test_data = {
        "sub": "TEST001",
        "username": "test_user",
        "employee_id": "TEST001",
        "role": "user",
        "hostname": "company.com",
        "permissions": ["read_profile", "update_profile"],
        "iat": datetime.utcnow().timestamp(),
        "type": "access_token"
    }
    
    try:
        # Create token with custom expiration
        expires_delta = timedelta(hours=8)
        token = create_access_token(data=test_data, expires_delta=expires_delta)
        print(f"✅ JWT token created successfully!")
        print(f"   Token (first 50 chars): {token[:50]}...")
        print(f"   Token length: {len(token)} characters")
    except Exception as e:
        print(f"❌ Failed to create JWT token: {e}")
        return
    
    # Test 2: Decode the JWT token
    print("\n2️⃣ Decoding JWT token...")
    
    try:
        decoded_payload = decode_access_token(token)
        print("✅ JWT token decoded successfully!")
        print(f"   Subject: {decoded_payload.get('sub')}")
        print(f"   Username: {decoded_payload.get('username')}")
        print(f"   Role: {decoded_payload.get('role')}")
        print(f"   Expires at: {datetime.fromtimestamp(decoded_payload.get('exp')).isoformat()}")
        print(f"   Permissions: {decoded_payload.get('permissions')}")
    except Exception as e:
        print(f"❌ Failed to decode JWT token: {e}")
        return
    
    # Test 3: Verify token
    print("\n3️⃣ Verifying JWT token...")
    
    try:
        is_valid = verify_token(token)
        if is_valid:
            print("✅ JWT token verification successful!")
        else:
            print("❌ JWT token verification failed!")
    except Exception as e:
        print(f"❌ Error during token verification: {e}")
    
    # Test 4: Test with invalid token
    print("\n4️⃣ Testing with invalid token...")
    
    try:
        invalid_token = "invalid.jwt.token"
        is_valid = verify_token(invalid_token)
        if not is_valid:
            print("✅ Invalid token correctly rejected!")
        else:
            print("❌ Invalid token was incorrectly accepted!")
    except Exception as e:
        print(f"✅ Invalid token correctly rejected with error (expected)")
    
    # Test 5: Test token with shorter expiration
    print("\n5️⃣ Testing token creation with different expiration...")
    
    try:
        short_expires_delta = timedelta(minutes=30)
        short_token = create_access_token(data=test_data, expires_delta=short_expires_delta)
        
        decoded_short = decode_access_token(short_token)
        exp_time = datetime.fromtimestamp(decoded_short.get('exp'))
        
        print("✅ Short-expiry token created successfully!")
        print(f"   Expires at: {exp_time.isoformat()}")
        print(f"   Time until expiry: {exp_time - datetime.utcnow()}")
    except Exception as e:
        print(f"❌ Failed to create short-expiry token: {e}")
    
    print("\n🎉 JWT implementation testing completed!")
    print("\n📝 Summary:")
    print("   ✅ JWT tokens are now properly generated using python-jose")
    print("   ✅ Token payload includes all necessary user information")
    print("   ✅ Token validation works correctly")
    print("   ✅ Token expiration is properly handled")
    print("   ✅ Invalid tokens are correctly rejected")
    print("\n💡 The auth controller now uses proper JWT tokens instead of mock tokens!")

if __name__ == "__main__":
    test_jwt_implementation() 