"""
Database service factory for switching between MongoDB and Xano
"""

from enum import Enum
from typing import Union
from .service import DatabaseService, get_db_service
from .xano_service import XanoDatabaseService, get_xano_db_service
from .connection import DatabaseConnection


class DatabaseServiceFactory:
    """Factory for creating appropriate database service based on configuration"""
    
    @staticmethod
    def create_service() -> Union[DatabaseService, XanoDatabaseService]:
        """Create the appropriate database service based on configuration"""
        if DatabaseConnection.is_xano_enabled():
            return get_xano_db_service()
        else:
            return get_db_service()


# Global service instance
_service_instance = None

def get_database_service() -> Union[DatabaseService, XanoDatabaseService]:
    """Get the configured database service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DatabaseServiceFactory.create_service()
    return _service_instance


def reset_service_instance():
    """Reset the service instance (useful for testing)"""
    global _service_instance
    _service_instance = None 