#!/usr/bin/env python3
"""
Database Manager for AI Prompt Sender
Provides easy access to database operations and querying
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from database.service import get_db_service
from database.connection import close_database
from services import Provider

load_dotenv()


class DatabaseManager:
    """Database management interface for AI Prompt Sender"""
    
    def __init__(self):
        self.db_service = get_db_service()
    
    async def show_statistics(self):
        """Display database statistics"""
        print("📊 Database Statistics")
        print("=" * 40)
        
        stats = await self.db_service.get_statistics()
        print(f"Total Conversations: {stats['total_conversations']}")
        print(f"Total Responses: {stats['total_responses']}")
        print("\nProvider Statistics:")
        for provider, count in stats['provider_stats'].items():
            print(f"  {provider}: {count} responses")
    
    async def list_conversations(self, limit: int = 10, provider: Optional[str] = None):
        """List recent conversations"""
        print(f"📚 Recent Conversations (limit: {limit})")
        print("=" * 50)
        
        if provider:
            conversations = await self.db_service.get_conversations_by_provider(provider, limit)
            print(f"Filtered by provider: {provider}")
        else:
            conversations = await self.db_service.get_all_conversations(limit=limit)
        
        if not conversations:
            print("No conversations found.")
            return
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{i}. Conversation ID: {conv.conversation_id}")
            print(f"   Created: {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Messages: {len(conv.messages)}")
            print(f"   Responses: {len(conv.responses)}")
            
            if conv.system_prompt:
                print(f"   System Prompt: {conv.system_prompt[:50]}...")
            
            # Show first user message
            user_messages = [msg for msg in conv.messages if msg.role == "user"]
            if user_messages:
                print(f"   First User Message: {user_messages[0].content[:80]}...")
            
            # Show providers used
            providers = [resp.provider for resp in conv.responses]
            print(f"   Providers: {', '.join(providers)}")
    
    async def show_conversation(self, conversation_id: str):
        """Show detailed information about a specific conversation"""
        print(f"🔍 Conversation Details: {conversation_id}")
        print("=" * 60)
        
        conversation = await self.db_service.get_conversation(conversation_id)
        if not conversation:
            print("Conversation not found.")
            return
        
        print(f"ID: {conversation.conversation_id}")
        print(f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if conversation.system_prompt:
            print(f"\nSystem Prompt:")
            print(f"  {conversation.system_prompt}")
        
        print(f"\nMessages ({len(conversation.messages)}):")
        for i, msg in enumerate(conversation.messages, 1):
            print(f"  {i}. [{msg.role.upper()}] {msg.content}")
        
        print(f"\nResponses ({len(conversation.responses)}):")
        for i, resp in enumerate(conversation.responses, 1):
            print(f"  {i}. [{resp.provider.upper()}] {resp.model}")
            print(f"     Content: {resp.content}")
            if resp.tokens_used:
                print(f"     Tokens: {resp.tokens_used}")
            if resp.response_time_ms:
                print(f"     Response Time: {resp.response_time_ms:.2f}ms")
            if resp.error:
                print(f"     Error: {resp.error}")
            print()
        
        if conversation.metadata:
            print(f"Metadata: {json.dumps(conversation.metadata, indent=2)}")
    
    async def search_conversations(self, query: str, limit: int = 20):
        """Search conversations by content"""
        print(f"🔍 Search Results for: '{query}'")
        print("=" * 50)
        
        conversations = await self.db_service.search_conversations(query, limit=limit)
        
        if not conversations:
            print("No conversations found matching your query.")
            return
        
        print(f"Found {len(conversations)} conversations:")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{i}. {conv.conversation_id}")
            print(f"   Date: {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show matching content
            user_messages = [msg for msg in conv.messages if msg.role == "user"]
            if user_messages:
                print(f"   User: {user_messages[0].content[:100]}...")
            
            providers = [resp.provider for resp in conv.responses]
            print(f"   Providers: {', '.join(providers)}")
    
    async def export_conversation(self, conversation_id: str, format: str = "json"):
        """Export a conversation to JSON"""
        conversation = await self.db_service.get_conversation(conversation_id)
        if not conversation:
            print("Conversation not found.")
            return
        
        filename = f"conversation_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to dict for JSON serialization
        conv_dict = conversation.model_dump(by_alias=True)
        conv_dict['_id'] = str(conv_dict['_id'])  # Convert ObjectId to string
        
        with open(filename, 'w') as f:
            json.dump(conv_dict, f, indent=2, default=str)
        
        print(f"✅ Exported conversation to {filename}")
    
    async def delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        success = await self.db_service.delete_conversation(conversation_id)
        if success:
            print(f"✅ Deleted conversation: {conversation_id}")
        else:
            print(f"❌ Failed to delete conversation: {conversation_id}")
    
    async def close(self):
        """Close database connections"""
        await close_database()


async def interactive_mode():
    """Interactive database management mode"""
    manager = DatabaseManager()
    
    print("🗄️ AI Prompt Sender Database Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Show statistics")
        print("2. List recent conversations")
        print("3. Show conversation details")
        print("4. Search conversations")
        print("5. Export conversation")
        print("6. Delete conversation")
        print("7. List conversations by provider")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        try:
            if choice == "0":
                break
            elif choice == "1":
                await manager.show_statistics()
            elif choice == "2":
                limit = int(input("Enter limit (default 10): ") or "10")
                await manager.list_conversations(limit=limit)
            elif choice == "3":
                conv_id = input("Enter conversation ID: ").strip()
                await manager.show_conversation(conv_id)
            elif choice == "4":
                query = input("Enter search query: ").strip()
                limit = int(input("Enter limit (default 20): ") or "20")
                await manager.search_conversations(query, limit=limit)
            elif choice == "5":
                conv_id = input("Enter conversation ID: ").strip()
                await manager.export_conversation(conv_id)
            elif choice == "6":
                conv_id = input("Enter conversation ID: ").strip()
                confirm = input(f"Are you sure you want to delete {conv_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    await manager.delete_conversation(conv_id)
            elif choice == "7":
                provider = input("Enter provider name: ").strip()
                limit = int(input("Enter limit (default 10): ") or "10")
                await manager.list_conversations(limit=limit, provider=provider)
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    await manager.close()


async def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        await interactive_mode()
        return
    
    manager = DatabaseManager()
    command = sys.argv[1]
    
    try:
        if command == "stats":
            await manager.show_statistics()
        elif command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            await manager.list_conversations(limit=limit)
        elif command == "show":
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py show <conversation_id>")
                return
            await manager.show_conversation(sys.argv[2])
        elif command == "search":
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py search <query>")
                return
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            await manager.search_conversations(sys.argv[2], limit=limit)
        elif command == "export":
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py export <conversation_id>")
                return
            await manager.export_conversation(sys.argv[2])
        elif command == "delete":
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py delete <conversation_id>")
                return
            await manager.delete_conversation(sys.argv[2])
        else:
            print("Unknown command. Use: stats, list, show, search, export, delete")
    
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main()) 