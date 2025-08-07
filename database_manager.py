#!/usr/bin/env python3
"""
Database Manager for AI Prompt Sender
Provides command-line interface for managing conversations in the database
"""

import asyncio
import json
import os
from typing import Optional
from database.service_factory import get_database_service
from database.connection import close_database
from logging_config import get_logger

logger = get_logger("database_manager")


class DatabaseManager:
    """Database management interface for AI Prompt Sender"""
    
    def __init__(self):
        self.db_service = get_database_service()
        logger.debug("DatabaseManager initialized")
    
    async def show_statistics(self):
        """Display database statistics"""
        logger.info("Database Statistics")
        logger.info("=" * 40)
        
        stats = await self.db_service.get_statistics()
        logger.info(f"Total Conversations: {stats['total_conversations']}")
        logger.info(f"Total Responses: {stats['total_responses']}")
        logger.info("Provider Statistics:")
        for provider, count in stats['provider_stats'].items():
            logger.info(f"  {provider}: {count} responses")
    
    async def list_conversations(self, limit: int = 10, provider: Optional[str] = None):
        """List recent conversations"""
        logger.info(f"Recent Conversations (limit: {limit})")
        logger.info("=" * 50)
        
        if provider:
            conversations = await self.db_service.get_conversations_by_provider(provider, limit)
            logger.info(f"Filtered by provider: {provider}")
        else:
            conversations = await self.db_service.get_all_conversations(limit=limit)
        
        if not conversations:
            logger.info("No conversations found.")
            return
        
        for i, conv in enumerate(conversations, 1):
            logger.info(f"\n{i}. Conversation ID: {conv.conversation_id}")
            logger.info(f"   Created: {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"   Messages: {len(conv.messages)}")
            logger.info(f"   Responses: {len(conv.responses)}")
            
            if conv.system_prompt:
                logger.info(f"   System Prompt: {conv.system_prompt[:50]}...")
            
            # Show first user message
            user_messages = [msg for msg in conv.messages if msg.role == "user"]
            if user_messages:
                logger.info(f"   First User Message: {user_messages[0].content[:80]}...")
            
            # Show providers used
            providers = [resp.provider for resp in conv.responses]
            logger.info(f"   Providers: {', '.join(providers)}")
    
    async def show_conversation(self, conversation_id: str):
        """Show detailed information about a specific conversation"""
        logger.info(f"🔍 Conversation Details: {conversation_id}")
        logger.info("=" * 60)
        
        conversation = await self.db_service.get_conversation(conversation_id)
        if not conversation:
            logger.warning("Conversation not found.")
            return
        
        logger.info(f"ID: {conversation.conversation_id}")
        logger.info(f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if conversation.system_prompt:
            logger.info(f"\nSystem Prompt:")
            logger.info(f"  {conversation.system_prompt}")
        
        logger.info(f"\nMessages ({len(conversation.messages)}):")
        for i, msg in enumerate(conversation.messages, 1):
            logger.info(f"  {i}. [{msg.role.upper()}] {msg.content}")
        
        logger.info(f"\nResponses ({len(conversation.responses)}):")
        for i, resp in enumerate(conversation.responses, 1):
            logger.info(f"  {i}. [{resp.provider.upper()}] {resp.model}")
            logger.info(f"     Content: {resp.content}")
            if resp.tokens_used:
                logger.info(f"Tokens: {resp.tokens_used}")
            if resp.response_time_ms:
                logger.info(f"Response Time: {resp.response_time_ms:.2f}ms")
            if resp.error:
                logger.info(f"Error: {resp.error}")
            logger.info("")
        
        if conversation.metadata:
            logger.info(f"Metadata: {json.dumps(conversation.metadata, indent=2)}")
    
    async def search_conversations(self, query: str, limit: int = 20):
        """Search conversations by content"""
        logger.info(f"Search Results for: '{query}'")
        logger.info("=" * 50)
        
        conversations = await self.db_service.search_conversations(query, limit=limit)
        
        if not conversations:
            logger.info("No conversations found matching your query.")
            return
        
        logger.info(f"Found {len(conversations)} conversations:")
        
        for i, conv in enumerate(conversations, 1):
            logger.info(f"\n{i}. {conv.conversation_id}")
            logger.info(f"   Date: {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            user_messages = [msg for msg in conv.messages if msg.role == "user"]
            if user_messages:
                logger.info(f"   User: {user_messages[0].content[:100]}...")
            
            # Show providers used
            providers = [resp.provider for resp in conv.responses]
            logger.info(f"   Providers: {', '.join(providers)}")
    
    async def export_conversation(self, conversation_id: str, format: str = "json"):
        """Export a conversation to a file"""
        conversation = await self.db_service.get_conversation(conversation_id)
        if not conversation:
            logger.error("Conversation not found.")
            return
        
        filename = f"conversation_{conversation_id}.{format}"
        
        if format == "json":
            with open(filename, 'w') as f:
                json.dump(conversation.model_dump(), f, indent=2, default=str)
        
        logger.info(f"Exported conversation to {filename}")
    
    async def delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        success = await self.db_service.delete_conversation(conversation_id)
        if success:
            logger.info(f"Deleted conversation: {conversation_id}")
        else:
            logger.error(f"Failed to delete conversation: {conversation_id}")
    
    async def close(self):
        """Close database connections"""
        await close_database()


async def interactive_mode():
    """Run the database manager in interactive mode"""
    manager = DatabaseManager()
    
    logger.info("AI Prompt Sender Database Manager")
    logger.info("=" * 50)
    
    while True:
        logger.info("\nOptions:")
        logger.info("1. Show statistics")
        logger.info("2. List recent conversations")
        logger.info("3. Show conversation details")
        logger.info("4. Search conversations")
        logger.info("5. Export conversation")
        logger.info("6. Delete conversation")
        logger.info("7. List conversations by provider")
        logger.info("0. Exit")
        
        try:
            choice = input("\nEnter your choice (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await manager.show_statistics()
            elif choice == "2":
                limit = input("Enter limit (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                await manager.list_conversations(limit=limit)
            elif choice == "3":
                conv_id = input("Enter conversation ID: ").strip()
                await manager.show_conversation(conv_id)
            elif choice == "4":
                query = input("Enter search query: ").strip()
                limit = input("Enter limit (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                await manager.search_conversations(query, limit=limit)
            elif choice == "5":
                conv_id = input("Enter conversation ID: ").strip()
                format_choice = input("Enter format (json, default): ").strip() or "json"
                await manager.export_conversation(conv_id, format_choice)
            elif choice == "6":
                conv_id = input("Enter conversation ID: ").strip()
                confirm = input("Are you sure? (y/N): ").strip().lower()
                if confirm == 'y':
                    await manager.delete_conversation(conv_id)
                else:
                    logger.info("Deletion cancelled.")
            elif choice == "7":
                provider = input("Enter provider name: ").strip()
                limit = input("Enter limit (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                await manager.list_conversations(limit=limit, provider=provider)
            else:
                logger.warning("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    await manager.close()


async def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        await interactive_mode()
        return
    
    command = sys.argv[1].lower()
    manager = DatabaseManager()
    
    try:
        if command == "stats":
            await manager.show_statistics()
        elif command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            await manager.list_conversations(limit=limit)
        elif command == "show":
            if len(sys.argv) < 3:
                logger.error("Usage: python database_manager.py show <conversation_id>")
                return
            await manager.show_conversation(sys.argv[2])
        elif command == "search":
            if len(sys.argv) < 3:
                logger.error("Usage: python database_manager.py search <query>")
                return
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            await manager.search_conversations(sys.argv[2], limit=limit)
        elif command == "export":
            if len(sys.argv) < 3:
                logger.error("Usage: python database_manager.py export <conversation_id>")
                return
            format_choice = sys.argv[3] if len(sys.argv) > 3 else "json"
            await manager.export_conversation(sys.argv[2], format_choice)
        elif command == "delete":
            if len(sys.argv) < 3:
                logger.error("Usage: python database_manager.py delete <conversation_id>")
                return
            await manager.delete_conversation(sys.argv[2])
        else:
            logger.error("Unknown command. Use: stats, list, show, search, export, delete")
    
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main()) 