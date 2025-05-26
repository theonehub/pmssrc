"""
MongoDB Initialization Script for Taxation System
Run this script to set up the database with proper indexes and validation
"""

import asyncio
import logging
from pymongo import MongoClient
from config.mongodb_config import (
    get_database_config, 
    INDEX_DEFINITIONS, 
    VALIDATION_SCHEMAS,
    COLLECTION_NAMES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBInitializer:
    """Initialize MongoDB database for taxation system"""
    
    def __init__(self):
        self.config = get_database_config()
        self.client = MongoClient(self.config["connection_string"])
        self.db = self.client[self.config["database_name"]]
    
    def create_collections(self):
        """Create collections with validation schemas"""
        logger.info("Creating collections with validation schemas...")
        
        for collection_name, schema in VALIDATION_SCHEMAS.items():
            try:
                # Check if collection exists
                if collection_name in self.db.list_collection_names():
                    logger.info(f"Collection '{collection_name}' already exists")
                    # Update validation schema
                    self.db.command({
                        "collMod": collection_name,
                        "validator": schema
                    })
                    logger.info(f"Updated validation schema for '{collection_name}'")
                else:
                    # Create collection with validation
                    self.db.create_collection(
                        collection_name,
                        validator=schema
                    )
                    logger.info(f"Created collection '{collection_name}' with validation")
            except Exception as e:
                logger.error(f"Error creating collection '{collection_name}': {str(e)}")
    
    def create_indexes(self):
        """Create indexes for all collections"""
        logger.info("Creating indexes for optimal performance...")
        
        for collection_name, indexes in INDEX_DEFINITIONS.items():
            try:
                collection = self.db[collection_name]
                
                for index_spec in indexes:
                    try:
                        # Create index
                        collection.create_index(index_spec)
                        logger.info(f"Created index {index_spec} on '{collection_name}'")
                    except Exception as e:
                        # Index might already exist
                        if "already exists" in str(e).lower():
                            logger.info(f"Index {index_spec} already exists on '{collection_name}'")
                        else:
                            logger.error(f"Error creating index {index_spec} on '{collection_name}': {str(e)}")
                            
            except Exception as e:
                logger.error(f"Error creating indexes for '{collection_name}': {str(e)}")
    
    def create_additional_collections(self):
        """Create additional collections that don't have validation schemas"""
        additional_collections = [
            "employee_lifecycle_events",
            "compliance_reports", 
            "tax_analytics",
            "audit_logs",
            "system_metrics"
        ]
        
        for collection_name in additional_collections:
            try:
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(collection_name)
                    logger.info(f"Created additional collection '{collection_name}'")
                else:
                    logger.info(f"Additional collection '{collection_name}' already exists")
            except Exception as e:
                logger.error(f"Error creating additional collection '{collection_name}': {str(e)}")
    
    def setup_database_settings(self):
        """Setup database-level settings"""
        try:
            # Enable profiling for slow operations (optional)
            self.db.set_profiling_level(1, slow_ms=1000)
            logger.info("Enabled database profiling for operations > 1000ms")
            
            # Set read/write concerns (optional)
            logger.info("Database settings configured")
            
        except Exception as e:
            logger.error(f"Error setting up database settings: {str(e)}")
    
    def verify_setup(self):
        """Verify that the database setup is correct"""
        logger.info("Verifying database setup...")
        
        # Check collections
        collections = self.db.list_collection_names()
        expected_collections = list(COLLECTION_NAMES.values()) + [
            "employee_lifecycle_events",
            "compliance_reports",
            "tax_analytics",
            "audit_logs",
            "system_metrics"
        ]
        
        missing_collections = [col for col in expected_collections if col not in collections]
        if missing_collections:
            logger.warning(f"Missing collections: {missing_collections}")
        else:
            logger.info("All expected collections are present")
        
        # Check indexes for main collections
        for collection_name in COLLECTION_NAMES.values():
            try:
                collection = self.db[collection_name]
                indexes = list(collection.list_indexes())
                logger.info(f"Collection '{collection_name}' has {len(indexes)} indexes")
            except Exception as e:
                logger.error(f"Error checking indexes for '{collection_name}': {str(e)}")
        
        # Test basic operations
        try:
            # Test write operation
            test_collection = self.db.test_collection
            test_doc = {"test": "data", "timestamp": "2024-01-01T00:00:00"}
            result = test_collection.insert_one(test_doc)
            
            # Test read operation
            retrieved_doc = test_collection.find_one({"_id": result.inserted_id})
            
            # Clean up
            test_collection.delete_one({"_id": result.inserted_id})
            
            logger.info("Database read/write operations working correctly")
            
        except Exception as e:
            logger.error(f"Error testing database operations: {str(e)}")
    
    def initialize(self):
        """Run complete database initialization"""
        logger.info(f"Initializing MongoDB database: {self.config['database_name']}")
        logger.info(f"Connection string: {self.config['connection_string']}")
        
        try:
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create collections
            self.create_collections()
            
            # Create additional collections
            self.create_additional_collections()
            
            # Create indexes
            self.create_indexes()
            
            # Setup database settings
            self.setup_database_settings()
            
            # Verify setup
            self.verify_setup()
            
            logger.info("MongoDB initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during MongoDB initialization: {str(e)}")
            raise
        finally:
            self.client.close()

def main():
    """Main function to run the initialization"""
    try:
        initializer = MongoDBInitializer()
        initializer.initialize()
        print("✅ MongoDB taxation system database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing MongoDB: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 