"""
Database service for integrating with AI services
"""

import uuid
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from .connection import get_database, get_collection
from .models import Conversation, PromptMessageModel, AIResponseModel, ConversationRepository
from services.types import PromptMessage, AIResponse


class DatabaseService:
    """Service for managing conversations in the database"""
    
    def __init__(self):
        self.repository = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the database connection and repository"""
        if not self._initialized:
            await get_database()
            collection = get_collection("conversations")
            self.repository = ConversationRepository(collection)
            self._initialized = True
    
    def _convert_prompt_messages(self, messages: List[PromptMessage]) -> List[PromptMessageModel]:
        """Convert service PromptMessage to database PromptMessageModel"""
        return [PromptMessageModel(role=msg.role, content=msg.content) for msg in messages]
    
    def _convert_ai_responses(self, responses: List[AIResponse], response_times: Optional[Dict[str, float]] = None) -> List[AIResponseModel]:
        """Convert service AIResponse to database AIResponseModel"""
        db_responses = []
        for response in responses:
            response_time = response_times.get(response.provider) if response_times else None
            db_response = AIResponseModel(
                provider=response.provider,
                content=response.content,
                model=response.model,
                tokens_used=response.tokens_used,
                error=response.error,
                response_time_ms=response_time * 1000 if response_time else None
            )
            db_responses.append(db_response)
        return db_responses
    
    async def save_conversation(
        self,
        messages: List[PromptMessage],
        responses: List[AIResponse],
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_times: Optional[Dict[str, float]] = None
    ) -> Conversation:
        """Save a complete conversation to the database"""
        await self.initialize()
        
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        system_prompt = None
        user_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                user_messages.append(msg)
        
        conversation = Conversation(
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            messages=self._convert_prompt_messages(messages),
            responses=self._convert_ai_responses(responses, response_times),
            metadata=metadata or {}
        )
        
        # Save to database
        saved_conversation = await self.repository.create(conversation)
        print(f"Saved conversation {conversation_id} to database")
        return saved_conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID"""
        await self.initialize()
        return await self.repository.find_by_id(conversation_id)
    
    async def get_all_conversations(self, limit: int = 100, skip: int = 0) -> List[Conversation]:
        """Get all conversations with pagination"""
        await self.initialize()
        return await self.repository.find_all(limit=limit, skip=skip)
    
    async def get_conversations_by_provider(self, provider: str, limit: int = 100) -> List[Conversation]:
        """Get conversations by AI provider"""
        await self.initialize()
        return await self.repository.find_by_provider(provider, limit=limit)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        await self.initialize()
        return await self.repository.delete(conversation_id)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        await self.initialize()
        return await self.repository.get_statistics()
    
    async def search_conversations(self, query: str, limit: int = 50) -> List[Conversation]:
        """Search conversations by content"""
        await self.initialize()
        
        search_query = {
            "$or": [
                {"messages.content": {"$regex": query, "$options": "i"}},
                {"responses.content": {"$regex": query, "$options": "i"}},
                {"system_prompt": {"$regex": query, "$options": "i"}}
            ]
        }
        
        cursor = self.repository.collection.find(search_query).limit(limit).sort("created_at", -1)
        conversations = []
        async for doc in cursor:
            conversations.append(Conversation(**doc))
        return conversations


_db_service = None

def get_db_service() -> DatabaseService:
    """Get the singleton database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service 