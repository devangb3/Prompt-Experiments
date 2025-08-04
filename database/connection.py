"""
Database connection management for MongoDB and Xano
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# Global database client for MongoDB
_client: Optional[AsyncIOMotorClient] = None
_database = None


class DatabaseConnection:
    """Base class for database connections"""
    
    @staticmethod
    def get_provider_type() -> str:
        """Get the configured database provider from environment"""
        provider = os.getenv('DATABASE_PROVIDER', 'mongodb').lower()
        return provider

    @staticmethod
    def is_mongodb_enabled() -> bool:
        """Check if MongoDB is the configured provider"""
        return DatabaseConnection.get_provider_type() == 'mongodb'

    @staticmethod
    def is_xano_enabled() -> bool:
        """Check if Xano is the configured provider"""
        return DatabaseConnection.get_provider_type() == 'xano'


async def get_database():
    """Get the MongoDB database instance (only used when MongoDB is configured)"""
    global _client, _database
    
    if not DatabaseConnection.is_mongodb_enabled():
        raise RuntimeError("MongoDB is not the configured database provider. Check DATABASE_PROVIDER environment variable.")
    
    if _database is None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        database_name = os.getenv('MONGO_DATABASE', 'ai_prompt_sender')
        
        _client = AsyncIOMotorClient(mongo_uri)
        _database = _client[database_name]
        
        try:
            await _client.admin.command('ping')
            print(f"Connected to MongoDB: {database_name}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    return _database


async def close_database():
    """Close database connections (both MongoDB and Xano)"""
    global _client
    
    if _client:
        _client.close()
        print("MongoDB connection closed")
        _client = None
    
    from .xano_client import close_xano_client
    await close_xano_client()
    print("Database connections closed")


def get_collection(collection_name: str):
    """Get a specific collection from the MongoDB database"""
    if not DatabaseConnection.is_mongodb_enabled():
        raise RuntimeError("MongoDB collections are not available when using Xano as the database provider")
    
    if _database is None:
        raise RuntimeError("Database not initialized. Call get_database() first.")
    return _database[collection_name]


def get_connection_info() -> dict:
    """Get information about the current database configuration"""
    provider = DatabaseConnection.get_provider_type()
    
    if provider == "mongodb":
        return {
            "provider": "MongoDB",
            "uri": os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
            "database": os.getenv('MONGO_DATABASE', 'ai_prompt_sender'),
            "connected": _database is not None
        }
    else:
        api_token = os.getenv('XANO_API_TOKEN')
        return {
            "provider": "Xano",
            "base_url": os.getenv('XANO_BASE_URL', 'https://your-workspace.xano.com/api:version'),
            "has_token": bool(api_token),
            "endpoint_type": "Private" if api_token else "Public",
            "timeout": os.getenv('XANO_TIMEOUT', '30.0')
        } 