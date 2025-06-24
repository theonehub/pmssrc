#!/usr/bin/env python3
"""
Script to create a test JWT token for authentication testing
"""

import os
from datetime import datetime, timedelta
from jose import jwt

# JWT Configuration (should match modules_all)
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_test_token():
    """Create a test JWT token with the required claims"""
    
    # Token expires in 24 hours instead of 1 hour
    expires_delta = timedelta(hours=24)
    expire = datetime.utcnow() + expires_delta
    
    # Create token payload with required claims
    token_data = {
        "sub": "EMP001",  # employee_id (subject)
        "username": "testuser",
        "employee_id": "EMP001",
        "role": "admin", 
        "hostname": "test.company.com",
        "permissions": ["read", "write"],
        "iat": datetime.utcnow().timestamp(),  # Issued at
        "exp": expire.timestamp(),  # Expiration
        "type": "access_token"
    }
    
    # Generate JWT token
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return token, token_data

if __name__ == "__main__":
    print("Creating test JWT token...")
    print(f"Using JWT_SECRET: {'***' if JWT_SECRET else 'NOT SET'}")
    print(f"Using JWT_ALGORITHM: {JWT_ALGORITHM}")
    print()
    
    try:
        token, payload = create_test_token()
        
        print("Token created successfully!")
        print(f"Token: {token}")
        print()
        print("Token payload:")
        for key, value in payload.items():
            if key == "exp" or key == "iat":
                # Convert timestamp to readable date
                readable_time = datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  {key}: {value} ({readable_time})")
            else:
                print(f"  {key}: {value}")
        print()
        
        # Test command for curl
        print("Test with curl:")
        print(f'curl -X GET "http://localhost:8001/api/debug/auth" \\')
        print(f'     -H "Authorization: Bearer {token}" \\')
        print(f'     -H "accept: application/json"')
        
    except Exception as e:
        print(f"Error creating token: {e}")
        import traceback
        traceback.print_exc() 