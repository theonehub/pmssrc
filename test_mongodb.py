import asyncio
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

async def test_mongodb_connection():
    try:
        connector = MongoDBConnector()
        connection_string = get_mongodb_connection_string()
        client_options = get_mongodb_client_options()
        
        print(f"Connecting to MongoDB...")
        print(f"Connection string: {connection_string}")
        print(f"Client options: {client_options}")
        
        await connector.connect(connection_string, **client_options)
        print("MongoDB connection successful!")
        
        # Test getting a database
        db = connector.get_database("pms_localhost")
        print(f"Database access successful: {db}")
        
        await connector.disconnect()
        print("MongoDB connection closed successfully!")
        
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection()) 