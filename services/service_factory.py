"""
Service factory for managing all AI provider services
"""

import os
import time
from typing import Dict, List, Optional
import asyncio
from logging_config import get_logger

from .types import Provider, PromptMessage, AIResponse
from .openai_service import OpenAIService
from .anthropic_service import AnthropicService
from .gemini_service import GeminiService
from .perplexity_service import PerplexityService

logger = get_logger("services.factory")


class AIServiceFactory:
    """Factory class for managing AI provider services"""
    
    def __init__(self):
        """Initialize the service factory with all available providers"""
        self.services: Dict[Provider, any] = {}
        self._setup_services()
    
    def _setup_services(self):
        """Setup all available AI services based on environment variables"""
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.services[Provider.OPENAI] = OpenAIService(openai_key)
            logger.info("OpenAI service initialized")
        else:
            logger.warning("OPENAI_API_KEY not found in environment")
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.services[Provider.ANTHROPIC] = AnthropicService(anthropic_key)
            logger.info("Anthropic service initialized")
        else:
            logger.warning("ANTHROPIC_API_KEY not found in environment")
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.services[Provider.GEMINI] = GeminiService(gemini_key)
            logger.info("Gemini service initialized")
        else:
            logger.warning("GEMINI_API_KEY not found in environment")
        
        logger.info(f"Service factory initialized with {len(self.services)} services")
    
    def get_service(self, provider: Provider):
        """Get a specific service by provider"""
        service = self.services.get(provider)
        if service:
            logger.debug(f"Retrieved service for provider: {provider.value}")
        else:
            logger.warning(f"No service available for provider: {provider.value}")
        return service
    
    def get_available_services(self) -> List[Provider]:
        """Get list of available services"""
        services = list(self.services.keys())
        logger.debug(f"Available services: {[s.value for s in services]}")
        return services
    
    async def send_to_provider(self, provider: Provider, messages: List[PromptMessage], model: Optional[str] = None, action: Optional[str] = None) -> AIResponse:
        """Send prompt to a specific provider"""
        logger.debug(f"Sending to provider: {provider.value}, model: {model}, action: {action}")
        
        service = self.get_service(provider)
        if not service:
            logger.error(f"Service not available for provider: {provider.value}")
            return AIResponse(
                provider=provider.value,
                content="",
                model=model or "",
                error=f"Service not available for provider: {provider.value}"
            )
        
        default_models = {
            Provider.OPENAI: "gpt-4.1",
            Provider.ANTHROPIC: "claude-sonnet-4-20250514",
            Provider.GEMINI: "gemini-2.5-pro"
        }
        
        return await service.send_prompt(messages, model or default_models[provider], action)
    
    async def send_to_all(self, messages: List[PromptMessage], models: Optional[Dict[Provider, str]] = None) -> List[AIResponse]:
        """Send prompt to all available providers"""
        if not self.services:
            logger.error("No services are available. Please set up API keys.")
            return [AIResponse(
                provider="None",
                content="",
                model="",
                error="No services are available. Please set up API keys."
            )]
        
        logger.info(f"Sending to all {len(self.services)} available providers")
        tasks = []
        for provider, service in self.services.items():
            model = models.get(provider) if models else None
            tasks.append(self.send_to_provider(provider, messages, model))
        
        return await asyncio.gather(*tasks) 