#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
from jose import jwt, JWTError

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

print("JWT Debug Information")
print(f"JWT_SECRET: {'***' if JWT_SECRET else 'NOT SET'}")
print(f"JWT_ALGORITHM: {JWT_ALGORITHM}")

# Test token from our previous generation
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFTVAwMDEiLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZW1wbG95ZWVfaWQiOiJFTVAwMDEiLCJyb2xlIjoiYWRtaW4iLCJob3N0bmFtZSI6InRlc3QuY29tcGFueS5jb20iLCJwZXJtaXNzaW9ucyI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzUwNjg1Mjk1LjEyMjM4MiwiZXhwIjoxNzUwNjg4ODk1LjEyMjE5NSwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.rV94S8DQ30_1Pxu1Ts9nYrsNg2oruQURvNdLd_cWbto"

print("\nTesting token decoding without verification:")
try:
    unverified = jwt.decode(test_token, options={"verify_signature": False})
    print("SUCCESS - Token decoded:")
    for k, v in unverified.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"ERROR: {e}")

print("\nTesting token decoding with verification:")
try:
    verified = jwt.decode(test_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    print("SUCCESS - Token verified:")
    for k, v in verified.items():
        print(f"  {k}: {v}")
except JWTError as e:
    print(f"JWT ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")

print("\nDone!") 