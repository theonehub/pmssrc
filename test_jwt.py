import jwt
from datetime import datetime, timedelta

# JWT secret key (should match the one in your app)
SECRET_KEY = "your-secret-key-change-in-production"  # Default from settings
ALGORITHM = "HS256"

# Create payload
payload = {
    "sub": "EMP002",
    "employee_id": "EMP002", 
    "role": "admin",
    "hostname": "test_company",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

# Generate token
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(f"JWT Token: {token}") 