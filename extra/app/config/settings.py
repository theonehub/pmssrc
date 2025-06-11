"""
Application Settings Configuration
Pydantic-based settings for environment variables and configuration
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Application
    app_name: str = Field(default="Taxation Management System", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for application")
    
    # Database
    #mongodb_url: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URL")
    mongodb_url: str = Field(default="mongodb+srv://admin:test123@mongodbtest.jhfj7s3.mongodb.net/?appName=mongodbTest", description="MongoDB connection URL")
    database_prefix: str = Field(default="pms_", description="Database prefix for multi-tenancy")
    
    # Authentication
    jwt_secret_key: str = Field(default="dev-jwt-secret-key-change-in-production", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry in minutes")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # CORS
    allowed_origins: list = Field(default=["*"], description="Allowed CORS origins")
    
    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    api_v2_prefix: str = Field(default="/api/v2", description="API v2 prefix")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 