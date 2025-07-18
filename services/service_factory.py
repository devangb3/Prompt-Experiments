"""
Service factory for managing all AI provider services
"""

import os
import time
from typing import Dict, List, Optional
import asyncio

from .types import Provider, PromptMessage, AIResponse
from .openai_service import OpenAIService
from .anthropic_service import AnthropicService
from .gemini_service import GeminiService
from .perplexity_service import PerplexityService


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
            print("OpenAI service initialized")
        else:
            print("OPENAI_API_KEY not found in environment")
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.services[Provider.ANTHROPIC] = AnthropicService(anthropic_key)
            print("Anthropic service initialized")
        else:
            print("ANTHROPIC_API_KEY not found in environment")
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.services[Provider.GEMINI] = GeminiService(gemini_key)
            print("Gemini service initialized")
        else:
            print("GEMINI_API_KEY not found in environment")
        
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        if perplexity_key:
            self.services[Provider.PERPLEXITY] = PerplexityService(perplexity_key)
            print("Perplexity service initialized")
        else:
            print("PERPLEXITY_API_KEY not found in environment")
    
    def get_service(self, provider: Provider):
        """Get a specific service by provider"""
        return self.services.get(provider)
    
    def get_available_services(self) -> List[Provider]:
        """Get list of available services"""
        return list(self.services.keys())
    
    async def send_to_provider(self, provider: Provider, messages: List[PromptMessage], model: Optional[str] = None) -> AIResponse:
        """Send prompt to a specific provider"""
        service = self.get_service(provider)
        if not service:
            return AIResponse(
                provider=provider.value,
                content="",
                model=model or "",
                error=f"Service not available for provider: {provider.value}"
            )
        
        default_models = {
            Provider.OPENAI: "o4-mini",
            Provider.ANTHROPIC: "claude-sonnet-4-20250514",
            Provider.GEMINI: "gemini-2.5-flash",
            Provider.PERPLEXITY: "sonar"
        }
        
        return await service.send_prompt(messages, model or default_models[provider])
    
    async def send_to_all(self, messages: List[PromptMessage], models: Optional[Dict[Provider, str]] = None) -> List[AIResponse]:
        """Send prompt to all available providers"""
        if not self.services:
            return [AIResponse(
                provider="None",
                content="",
                model="",
                error="No services are available. Please set up API keys."
            )]
        
        tasks = []
        for provider, service in self.services.items():
            model = models.get(provider) if models else None
            tasks.append(self.send_to_provider(provider, messages, model))
        
        return await asyncio.gather(*tasks) 