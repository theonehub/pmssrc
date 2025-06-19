"""
Shared Database Utilities for Microservices
"""

import os
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)


class MongoDBConnector:
    """
    MongoDB connection manager for microservices.
    Each service gets its own database based on service name and hostname.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.connection_string: Optional[str] = None
        self._connected = False
    
    async def connect(self, connection_string: str) -> None:
        """Connect to MongoDB"""
        try:
            self.connection_string = connection_string
            self.client = AsyncIOMotorClient(connection_string)
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            
            logger.info(f"✅ Connected to MongoDB for {self.service_name}")
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info(f"🔴 Disconnected from MongoDB for {self.service_name}")
    
    def get_database(self, hostname: str) -> AsyncIOMotorDatabase:
        """
        Get database for specific organization hostname.
        Format: {service_name}_{hostname}
        """
        if not self._connected or not self.client:
            raise RuntimeError("Database not connected")
        
        db_name = f"{self.service_name}_{hostname}"
        return self.client[db_name]
    
    def get_default_database(self) -> AsyncIOMotorDatabase:
        """Get default database (for testing or single-tenant)"""
        if not self._connected or not self.client:
            raise RuntimeError("Database not connected")
        
        return self.client[self.service_name]
    
    def is_connected(self) -> bool:
        """Check if connected to database"""
        return self._connected
    
    async def create_indexes(self, hostname: str, indexes: dict) -> None:
        """
        Create indexes for service collections.
        
        Args:
            hostname: Organization hostname
            indexes: Dict of collection_name -> list of indexes
        """
        db = self.get_database(hostname)
        
        for collection_name, collection_indexes in indexes.items():
            collection = db[collection_name]
            
            for index in collection_indexes:
                try:
                    await collection.create_index(index)
                    logger.info(f"✅ Created index {index} on {collection_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create index {index}: {e}")


class BaseRepository:
    """
    Base repository class for all microservice repositories.
    Provides common CRUD operations with MongoDB.
    """
    
    def __init__(self, db_connector: MongoDBConnector, collection_name: str):
        self.db_connector = db_connector
        self.collection_name = collection_name
    
    def get_collection(self, hostname: str):
        """Get MongoDB collection for specific hostname"""
        db = self.db_connector.get_database(hostname)
        return db[self.collection_name]
    
    async def find_by_id(self, hostname: str, doc_id: str) -> Optional[dict]:
        """Find document by ID"""
        collection = self.get_collection(hostname)
        return await collection.find_one({"_id": doc_id})
    
    async def find_one(self, hostname: str, query: dict) -> Optional[dict]:
        """Find single document by query"""
        collection = self.get_collection(hostname)
        return await collection.find_one(query)
    
    async def find_many(self, hostname: str, query: dict, limit: int = None) -> list:
        """Find multiple documents"""
        collection = self.get_collection(hostname)
        cursor = collection.find(query)
        
        if limit:
            cursor = cursor.limit(limit)
            
        return await cursor.to_list(length=None)
    
    async def insert_one(self, hostname: str, document: dict) -> str:
        """Insert single document"""
        collection = self.get_collection(hostname)
        result = await collection.insert_one(document)
        return str(result.inserted_id)
    
    async def insert_many(self, hostname: str, documents: list) -> list:
        """Insert multiple documents"""
        collection = self.get_collection(hostname)
        result = await collection.insert_many(documents)
        return [str(doc_id) for doc_id in result.inserted_ids]
    
    async def update_one(self, hostname: str, query: dict, update: dict) -> bool:
        """Update single document"""
        collection = self.get_collection(hostname)
        result = await collection.update_one(query, {"$set": update})
        return result.modified_count > 0
    
    async def update_many(self, hostname: str, query: dict, update: dict) -> int:
        """Update multiple documents"""
        collection = self.get_collection(hostname)
        result = await collection.update_many(query, {"$set": update})
        return result.modified_count
    
    async def delete_one(self, hostname: str, query: dict) -> bool:
        """Delete single document"""
        collection = self.get_collection(hostname)
        result = await collection.delete_one(query)
        return result.deleted_count > 0
    
    async def delete_many(self, hostname: str, query: dict) -> int:
        """Delete multiple documents"""
        collection = self.get_collection(hostname)
        result = await collection.delete_many(query)
        return result.deleted_count
    
    async def count_documents(self, hostname: str, query: dict = None) -> int:
        """Count documents"""
        collection = self.get_collection(hostname)
        return await collection.count_documents(query or {})
    
    async def aggregate(self, hostname: str, pipeline: list) -> list:
        """Run aggregation pipeline"""
        collection = self.get_collection(hostname)
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)


def get_database_connector(service_name: str) -> MongoDBConnector:
    """Factory function to create database connector"""
    return MongoDBConnector(service_name) 