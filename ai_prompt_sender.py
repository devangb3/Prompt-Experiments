#!/usr/bin/env python3
"""
AI Prompt Sender - Send prompts to multiple AI providers
Supports: OpenAI, Anthropic (Claude), Google Gemini, and Perplexity
"""

import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Import from the new service structure
from services import AIServiceFactory, Provider, PromptMessage, AIResponse, print_response

# Load environment variables from .env file
load_dotenv()


class AIPromptSender:
    def __init__(self):
        """Initialize with API keys from environment variables"""
        self.factory = AIServiceFactory()
    
    async def send_to_openai(self, messages: List[PromptMessage], model: str = "o4-mini-2025-04-16") -> AIResponse:
        """Send prompt to OpenAI"""
        return await self.factory.send_to_provider(Provider.OPENAI, messages, model)

    async def send_to_anthropic(self, messages: List[PromptMessage], model: str = "claude-3-5-sonnet-20241022") -> AIResponse:
        """Send prompt to Anthropic Claude"""
        return await self.factory.send_to_provider(Provider.ANTHROPIC, messages, model)

    async def send_to_gemini(self, messages: List[PromptMessage], model: str = "gemini-2.5-flash") -> AIResponse:
        """Send prompt to Google Gemini"""
        return await self.factory.send_to_provider(Provider.GEMINI, messages, model)

    async def send_to_perplexity(self, messages: List[PromptMessage], model: str = "llama-3.1-sonar-large-128k-online") -> AIResponse:
        """Send prompt to Perplexity"""
        return await self.factory.send_to_provider(Provider.PERPLEXITY, messages, model)

    async def send_to_all(self, messages: List[PromptMessage], models: Optional[Dict[str, str]] = None) -> List[AIResponse]:
        """Send prompt to all available providers"""
        # Convert string-based models dict to Provider-based dict if provided
        provider_models = None
        if models:
            provider_models = {}
            for provider_str, model in models.items():
                try:
                    provider = Provider(provider_str)
                    provider_models[provider] = model
                except ValueError:
                    # Skip invalid provider names
                    continue
        
        return await self.factory.send_to_all(messages, provider_models)

    async def send_to_provider(self, provider: Provider, messages: List[PromptMessage], model: Optional[str] = None) -> AIResponse:
        """Send prompt to a specific provider"""
        return await self.factory.send_to_provider(provider, messages, model)


async def main():
    sender = AIPromptSender()
    response = await sender.send_to_provider(
        Provider.GEMINI,
        [PromptMessage(role="user", content="Explain quantum computing in simple terms.")]
    )
    print_response(response)


if __name__ == "__main__":
    print("AI Prompt Sender")
    print("================")
    print("\n" + "="*50)
    
    # Run the examples
    asyncio.run(main()) 