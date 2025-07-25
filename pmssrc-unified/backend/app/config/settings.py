"""
Application Settings Configuration
Contains basic configuration settings for the PMS application
"""

import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

# Database Configuration - Basic settings without circular imports
DATABASE_URL = os.getenv("MONGODB_URL", "mongodb+srv://admin:test123@mongodbtest.jhfj7s3.mongodb.net/?appName=mongodbTest")
MONGO_URI = DATABASE_URL
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "pms_global_database")

# Application Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# File Upload Configuration
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default 