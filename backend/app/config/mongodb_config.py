"""
MongoDB Configuration for Taxation System
"""

import os
from typing import Dict, Any
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class MongoDBSettings(BaseSettings):
    """MongoDB configuration settings"""
    
    # MongoDB connection settings
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb+srv://admin:test123@mongodbtest.jhfj7s3.mongodb.net/?appName=mongodbTest")
    database_name: str = os.getenv("MONGODB_DATABASE", "")
    
    # Connection pool settings
    max_pool_size: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    min_pool_size: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    max_idle_time_ms: int = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000"))
    
    # Timeout settings
    connect_timeout_ms: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "10000"))
    server_selection_timeout_ms: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))
    
    # Authentication (if required)
    username: str = os.getenv("MONGODB_USERNAME", "")
    password: str = os.getenv("MONGODB_PASSWORD", "")
    auth_source: str = os.getenv("MONGODB_AUTH_SOURCE", "admin")
    
    # SSL settings
    use_ssl: bool = os.getenv("MONGODB_USE_SSL", "false").lower() == "true"
    ssl_cert_reqs: str = os.getenv("MONGODB_SSL_CERT_REQS", "CERT_REQUIRED")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
mongodb_settings = MongoDBSettings()

def get_mongodb_connection_string() -> str:
    """Get complete MongoDB connection string"""
    if mongodb_settings.username and mongodb_settings.password:
        # With authentication
        return (
            f"mongodb+srv://{mongodb_settings.username}:{mongodb_settings.password}@"
            f"{mongodb_settings.mongodb_url.replace('mongodb://', '')}"
            f"/{mongodb_settings.database_name}?authSource={mongodb_settings.auth_source}"
        )
    else:
        # Without authentication
        # return f"{mongodb_settings.mongodb_url}/{mongodb_settings.database_name}"
        return f"{mongodb_settings.mongodb_url}"

def get_mongodb_client_options() -> Dict[str, Any]:
    """Get MongoDB client options"""
    options = {
        "maxPoolSize": mongodb_settings.max_pool_size,
        "minPoolSize": mongodb_settings.min_pool_size,
        "maxIdleTimeMS": mongodb_settings.max_idle_time_ms,
        "connectTimeoutMS": mongodb_settings.connect_timeout_ms,
        "serverSelectionTimeoutMS": mongodb_settings.server_selection_timeout_ms,
    }
    
    if mongodb_settings.use_ssl:
        options.update({
            "ssl": True,
            "ssl_cert_reqs": mongodb_settings.ssl_cert_reqs
        })
    
    return options

# Tax calculation configuration
TAX_CALCULATION_CONFIG = {
    "default_regime": "new",
    "enable_event_processing": True,
    "enable_async_calculations": True,
    "max_event_retries": 3,
    "event_processing_batch_size": 100,
    "tax_year_start_month": 4,  # April
    "standard_deduction": {
        "old_regime": 50000,
        "new_regime": 75000
    },
    "rebate_87a": {
        "old_regime": {"limit": 500000, "amount": 12500},
        "new_regime": {"limit": 1200000, "amount": 60000}
    },
    "capital_gains_rates": {
        "stcg_111a": 0.20,  # Budget 2024 update
        "ltcg_112a": 0.125,  # Budget 2024 update
        "ltcg_other": 0.125,  # Budget 2024 update
        "ltcg_exemption_limit": 125000  # Budget 2024 update
    },
    "surcharge_slabs": [
        {"min_income": 5000000, "rate": 0.10},
        {"min_income": 10000000, "rate": 0.15},
        {"min_income": 20000000, "rate": 0.25},
        {"min_income": 50000000, "rate": 0.37}
    ],
    "cess_rate": 0.04  # Health and Education Cess
}

# Collection names
COLLECTION_NAMES = {
    "taxation": "taxation",
    "tax_events": "tax_events",
    "salary_change_records": "salary_change_records",
    "tax_calculation_results": "tax_calculation_results",
    "salary_projections": "salary_projections",
    "employee_lifecycle_events": "employee_lifecycle_events",
    "compliance_reports": "compliance_reports",
    "tax_analytics": "tax_analytics"
}

# Index definitions for MongoDB collections
INDEX_DEFINITIONS = {
    "taxation": [
        [("emp_id", 1)],
        [("hostname", 1)],
        [("tax_year", 1)],
        [("regime", 1)],
        [("emp_id", 1), ("hostname", 1)],  # Compound index
        [("tax_year", 1), ("regime", 1)]   # Compound index
    ],
    "tax_events": [
        [("employee_id", 1)],
        [("event_type", 1)],
        [("status", 1)],
        [("event_date", -1)],
        [("priority", 1)],
        [("employee_id", 1), ("event_type", 1)],  # Compound index
        [("status", 1), ("priority", 1)]          # Compound index
    ],
    "salary_change_records": [
        [("employee_id", 1)],
        [("effective_date", -1)],
        [("status", 1)],
        [("change_type", 1)],
        [("employee_id", 1), ("effective_date", -1)]  # Compound index
    ],
    "tax_calculation_results": [
        [("employee_id", 1)],
        [("tax_year", 1)],
        [("regime", 1)],
        [("calculation_date", -1)],
        [("employee_id", 1), ("tax_year", 1), ("regime", 1)]  # Compound index
    ],
    "salary_projections": [
        [("employee_id", 1)],
        [("tax_year", 1)],
        [("employee_id", 1), ("tax_year", 1)]  # Compound index
    ]
}

# Validation schemas for MongoDB collections
VALIDATION_SCHEMAS = {
    "taxation": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["emp_id", "hostname", "tax_year", "regime"],
            "properties": {
                "emp_id": {"bsonType": "string"},
                "hostname": {"bsonType": "string"},
                "tax_year": {"bsonType": "string"},
                "regime": {"bsonType": "string", "enum": ["old", "new"]},
                "emp_age": {"bsonType": "int", "minimum": 0, "maximum": 120},
                "total_tax": {"bsonType": "number", "minimum": 0},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"}
            }
        }
    },
    "tax_events": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id", "event_type", "employee_id", "event_date"],
            "properties": {
                "id": {"bsonType": "string"},
                "event_type": {"bsonType": "string"},
                "employee_id": {"bsonType": "string"},
                "event_date": {"bsonType": "date"},
                "status": {"bsonType": "string", "enum": ["pending", "processing", "completed", "failed", "retrying", "cancelled"]},
                "priority": {"bsonType": "string", "enum": ["low", "medium", "high", "critical"]},
                "retry_count": {"bsonType": "int", "minimum": 0},
                "max_retries": {"bsonType": "int", "minimum": 0}
            }
        }
    }
}

def get_database_config() -> Dict[str, Any]:
    """Get complete database configuration"""
    return {
        "connection_string": get_mongodb_connection_string(),
        "database_name": mongodb_settings.database_name,
        "client_options": get_mongodb_client_options(),
        "collection_names": COLLECTION_NAMES,
        "index_definitions": INDEX_DEFINITIONS,
        "validation_schemas": VALIDATION_SCHEMAS,
        "tax_calculation_config": TAX_CALCULATION_CONFIG
    } 