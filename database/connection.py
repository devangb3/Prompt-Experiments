"""
MongoDB connection management using motor for async operations
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_database = None


async def get_database():
    """Get the MongoDB database instance"""
    global _client, _database
    
    if _database is None:
        # Get MongoDB connection string from environment
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        database_name = os.getenv('MONGO_DATABASE', 'ai_prompt_sender')
        
        # Create async client
        _client = AsyncIOMotorClient(mongo_uri)
        _database = _client[database_name]
        
        # Test connection
        try:
            await _client.admin.command('ping')
            print(f"Connected to MongoDB: {database_name}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    return _database


async def close_database():
    """Close the MongoDB connection"""
    global _client
    
    if _client:
        _client.close()
        print("MongoDB connection closed")


def get_collection(collection_name: str):
    """Get a specific collection from the database"""
    if _database is None:
        raise RuntimeError("Database not initialized. Call get_database() first.")
    return _database[collection_name] 