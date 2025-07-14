"""
Base service class for AI providers
"""

from abc import ABC, abstractmethod
from typing import List

from .types import PromptMessage, AIResponse


class BaseAIService(ABC):
    """Base class for all AI provider services"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self):
        """Setup the API client for the specific provider"""
        pass
    
    @abstractmethod
    async def send_prompt(self, messages: List[PromptMessage], model: str) -> AIResponse:
        """Send prompt to the AI provider"""
        pass
    
    def is_available(self) -> bool:
        """Check if the service is available (has valid client)"""
        return self.client is not None 