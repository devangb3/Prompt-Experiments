"""
Database connection management for MongoDB and Xano
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from logging_config import get_logger

logger = get_logger("database.connection")

# Global database client for MongoDB
_client: Optional[AsyncIOMotorClient] = None
_database = None


class DatabaseConnection:
    """Base class for database connections"""
    
    @staticmethod
    def get_provider_type() -> str:
        """Get the configured database provider from environment"""
        provider = os.getenv('DATABASE_PROVIDER', 'mongodb').lower()
        logger.info(f"Database provider configured as: {provider}")
        logger.debug(f"DATABASE_PROVIDER environment variable: {'is set' if 'DATABASE_PROVIDER' in os.environ else 'is NOT set'}")
        if 'DATABASE_PROVIDER' in os.environ:
            logger.debug(f"Actual DATABASE_PROVIDER value: {os.environ['DATABASE_PROVIDER']}")
        else:
            logger.debug("Using default provider: mongodb")
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
    
    provider_enabled = DatabaseConnection.is_mongodb_enabled()
    logger.info(f"Attempting database connection. MongoDB enabled: {provider_enabled}")
    
    if not provider_enabled:
        logger.error("MongoDB connection attempted but MongoDB is not the configured provider")
        raise RuntimeError("MongoDB is not the configured database provider. Check DATABASE_PROVIDER environment variable.")
    
    if _database is None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        database_name = os.getenv('MONGO_DATABASE', 'ai_prompt_sender')
        
        logger.info(f"Connecting to MongoDB database: {database_name}")
        logger.debug(f"Using MongoDB URI: {mongo_uri}")
        
        _client = AsyncIOMotorClient(mongo_uri)
        _database = _client[database_name]
        
        try:
            await _client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    return _database


async def close_database():
    """Close database connections (both MongoDB and Xano)"""
    global _client
    
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")
        _client = None
    
    from .xano_client import close_xano_client
    await close_xano_client()
    logger.info("Database connections closed")


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
    logger.debug(f"Getting connection info for provider: {provider}")
    
    if provider == "mongodb":
        info = {
            "provider": "MongoDB",
            "uri": os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
            "database": os.getenv('MONGO_DATABASE', 'ai_prompt_sender'),
            "connected": _database is not None
        }
    else:
        api_token = os.getenv('XANO_API_TOKEN')
        info = {
            "provider": "Xano",
            "base_url": os.getenv('XANO_BASE_URL', 'https://your-workspace.xano.com/api:version'),
            "has_token": bool(api_token),
            "endpoint_type": "Private" if api_token else "Public",
            "timeout": os.getenv('XANO_TIMEOUT', '30.0')
        }
    
    logger.debug(f"Connection info: {info}")
    return info 