#!/usr/bin/env python3
"""
Test script for attendance check-in endpoint
"""

import requests
import json
from datetime import datetime, timedelta
from jose import jwt

# JWT Configuration
JWT_SECRET_KEY = 'your-jwt-secret-key-here'
JWT_ALGORITHM = 'HS256'

def create_test_token(employee_id: str = "superadmin", hostname: str = "localhost", role: str = "admin"):
    """Create a test JWT token"""
    # Token expires in 24 hours
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    payload = {
        "sub": employee_id,  # The auth.py looks for "sub" field
        "employee_id": employee_id,  # Include both formats for compatibility
        "hostname": hostname,
        "role": role,
        "exp": expiration.timestamp()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def test_checkin():
    """Test the check-in endpoint"""
    # Create a test token
    token = create_test_token()
    print(f"Generated token: {token}")
    
    # Test the check-in endpoint
    url = "http://localhost:8000/api/v2/attendance/checkin"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing URL: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Check-in successful!")
        else:
            print(f"❌ Check-in failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_checkin() 