#!/usr/bin/env python3
"""
AI Prompt Sender - Send prompts to multiple AI providers
Supports: OpenAI, Anthropic (Claude), Google Gemini, and Perplexity

Refactored version using separate service files and proper folder structure
"""

import asyncio
from dotenv import load_dotenv

from services import AIServiceFactory, Provider, PromptMessage, print_response, print_responses

load_dotenv()


class AIPromptSender:
    """Main class for sending prompts to AI providers using the new service structure"""
    
    def __init__(self):
        """Initialize with the service factory"""
        self.factory = AIServiceFactory()
    
    async def send_to_provider(self, provider: Provider, messages: list[PromptMessage], model: str = None):
        """Send prompt to a specific provider"""
        return await self.factory.send_to_provider(provider, messages, model)
    
    async def send_to_all(self, messages: list[PromptMessage], models: dict = None):
        """Send prompt to all available providers"""
        return await self.factory.send_to_all(messages, models)
    
    def get_available_services(self):
        """Get list of available services"""
        return self.factory.get_available_services()


async def main():
    """Example usage of the refactored AI Prompt Sender"""
    sender = AIPromptSender()
    
    response = await sender.send_to_provider(
        Provider.GEMINI,
        [PromptMessage(role="user", content="Explain quantum computing in simple terms.")]
    )
    print_response(response)
    
    print("\n" + "="*50)
    print("Sending to all available providers...")
    print("="*50)
    
    responses = await sender.send_to_all([
        PromptMessage(role="user", content="What is the capital of France?")
    ])
    print_responses(responses)


if __name__ == "__main__":
    print("AI Prompt Sender (Refactored)")
    print("=============================")
    print("\n" + "="*50)
    
    # Run the examples
    asyncio.run(main()) 