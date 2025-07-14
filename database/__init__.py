"""
Database package for MongoDB integration
"""

from .models import Conversation, PromptMessageModel, AIResponseModel
from .connection import get_database, close_database

__all__ = ['Conversation', 'PromptMessageModel', 'AIResponseModel', 'get_database', 'close_database'] 