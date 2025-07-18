#!/usr/bin/env python3
"""
AI Prompt Sender - Send prompts to multiple AI providers
Supports: OpenAI, Anthropic (Claude), Google Gemini, and Perplexity
With MongoDB integration for conversation storage
"""

import asyncio
import time
from dotenv import load_dotenv

from services import AIServiceFactory, Provider, PromptMessage, print_response, print_responses
from database.service import get_db_service
from database.connection import close_database

load_dotenv()


class AIPromptSender:
    """Main class for sending prompts to AI providers using the new service structure"""
    
    def __init__(self, enable_database: bool = True):
        """Initialize with the service factory"""
        self.factory = AIServiceFactory()
        self.enable_database = enable_database
        self.db_service = get_db_service() if enable_database else None
    
    async def send_to_provider(self, provider: Provider, messages: list[PromptMessage], model: str = None):
        """Send prompt to a specific provider"""
        start_time = time.time()
        response = await self.factory.send_to_provider(provider, messages, model)
        response_time = time.time() - start_time
        
        # Save to database if enabled
        if self.enable_database and self.db_service:
            try:
                await self.db_service.save_conversation(
                    messages=messages,
                    responses=[response],
                    response_times={provider.value: response_time}
                )
            except Exception as e:
                print(f"Failed to save conversation to database: {e}")
        
        return response
    
    async def send_to_all(self, messages: list[PromptMessage], models: dict = None):
        """Send prompt to all available providers"""
        start_time = time.time()
        responses = await self.factory.send_to_all(messages, models)
        total_time = time.time() - start_time
        
        if self.enable_database and self.db_service and len(responses) > 1:
            try:
                avg_time_per_provider = total_time / len(responses)
                response_times = {resp.provider: avg_time_per_provider for resp in responses}
                
                await self.db_service.save_conversation(
                    messages=messages,
                    responses=responses,
                    response_times=response_times
                )
            except Exception as e:
                print(f"Failed to save conversation to database: {e}")
        
        return responses
    
    def get_available_services(self):
        """Get list of available services"""
        return self.factory.get_available_services()
    
    async def get_conversation_history(self, limit: int = 10):
        """Get recent conversation history"""
        if self.db_service:
            return await self.db_service.get_all_conversations(limit=limit)
        return []
    
    async def search_conversations(self, query: str, limit: int = 20):
        """Search conversations by content"""
        if self.db_service:
            return await self.db_service.search_conversations(query, limit=limit)
        return []
    
    async def get_conversation_by_id(self, conversation_id: str):
        """Get a specific conversation by ID"""
        if self.db_service:
            return await self.db_service.get_conversation(conversation_id)
        return None
    
    async def get_statistics(self):
        """Get database statistics"""
        if self.db_service:
            return await self.db_service.get_statistics()
        return {"total_conversations": 0, "total_responses": 0, "provider_stats": {}}
    
    async def close(self):
        """Close database connections"""
        await close_database()


async def main():
    """Example usage of the refactored AI Prompt Sender with database integration"""
    sender = AIPromptSender()
    
    print("AI Prompt Sender with MongoDB Integration")
    print("=" * 50)
    
    messages = [
        PromptMessage(role="system", content="Fill this out with random placeholder data"),
        PromptMessage(role="user", content="Fill BrainScanResult out with random placeholder data")
    ]
    
    print("\nSending prompt to all providers...")
    responses = await sender.send_to_all(messages)
    print_responses(responses)
    
    print("\nDatabase Statistics:")
    stats = await sender.get_statistics()
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Total responses: {stats['total_responses']}")
    print("Provider stats:")
    for provider, count in stats['provider_stats'].items():
        print(f"  {provider}: {count}")
    
    print("\nRecent Conversations:")
    conversations = await sender.get_conversation_history(limit=3)
    for conv in conversations:
        print(f"  {conv.conversation_id}: {len(conv.messages)} messages, {len(conv.responses)} responses")
    
    await sender.close()


if __name__ == "__main__":
    print("AI Prompt Sender")
    print("=============================")
    print("\n" + "="*50)
    
    asyncio.run(main()) 