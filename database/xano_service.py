"""
Xano database service for integrating with AI services
Provides the same interface as DatabaseService but uses Xano REST API
"""

import uuid
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from .xano_client import get_xano_client, close_xano_client, XanoAPIError
from .xano_models import XanoConversation, XanoPromptMessageModel, XanoAIResponseModel
from .models import Conversation, PromptMessageModel, AIResponseModel
from services.types import PromptMessage, AIResponse


class XanoDatabaseService:
    """Service for managing conversations using Xano API"""
    
    def __init__(self):
        self.client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Xano client"""
        if not self._initialized:
            self.client = await get_xano_client()
            self._initialized = True
    
    def _convert_prompt_messages(self, messages: List[PromptMessage]) -> List[XanoPromptMessageModel]:
        """Convert service PromptMessage to Xano PromptMessageModel"""
        return [XanoPromptMessageModel(role=msg.role, content=msg.content) for msg in messages]
    
    def _convert_ai_responses(self, responses: List[AIResponse], response_times: Optional[Dict[str, float]] = None) -> List[XanoAIResponseModel]:
        """Convert service AIResponse to Xano AIResponseModel"""
        xano_responses = []
        for response in responses:
            response_time = response_times.get(response.provider) if response_times else None
            xano_response = XanoAIResponseModel(
                provider=response.provider,
                content=response.content,
                model=response.model,
                tokens_used=response.tokens_used,
                error=response.error,
                response_time_ms=response_time * 1000 if response_time else None
            )
            xano_responses.append(xano_response)
        return xano_responses
    
    def _xano_to_mongo_conversation(self, xano_data: Dict) -> Conversation:
        """Convert Xano API response to MongoDB-compatible Conversation model"""
        # Convert Xano response to MongoDB Conversation format for compatibility
        
        def parse_timestamp(timestamp) -> datetime:
            """Convert timestamp from Xano to datetime"""
            if timestamp is None:
                return datetime.utcnow()
            if isinstance(timestamp, int):
                return datetime.fromtimestamp(timestamp / 1000)
            if isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return datetime.utcnow()
        
        return Conversation(
            conversation_id=xano_data['conversation_id'],
            system_prompt=xano_data.get('system_prompt'),
            messages=[
                PromptMessageModel(role=msg['role'], content=msg['content'])
                for msg in xano_data.get('messages', [])
            ],
            responses=[
                AIResponseModel(
                    provider=resp['provider'],
                    content=resp['content'],
                    model=resp['model'],
                    tokens_used=resp.get('tokens_used'),
                    error=resp.get('error'),
                    response_time_ms=resp.get('response_time_ms')
                )
                for resp in xano_data.get('responses', [])
            ],
            created_at=parse_timestamp(xano_data.get('created_at')),
            updated_at=parse_timestamp(xano_data.get('updated_at')),
            metadata=xano_data.get('metadata', {})
        )
    
    async def save_conversation(
        self,
        messages: List[PromptMessage],
        responses: List[AIResponse],
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_times: Optional[Dict[str, float]] = None
    ) -> Conversation:
        """Save a complete conversation to Xano"""
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
        
        # Prepare data for Xano API
        conversation_data = {
            "conversation_id": conversation_id,
            "system_prompt": system_prompt,
            "messages": [msg.model_dump() for msg in self._convert_prompt_messages(messages)],
            "responses": [resp.model_dump() for resp in self._convert_ai_responses(responses, response_times)],
            "metadata": metadata or {}
        }
        
        try:
            # Save to Xano
            saved_data = await self.client.create_conversation(conversation_data)
            print(f"Saved conversation {conversation_id} to Xano")
            
            # Convert back to MongoDB-compatible format for return value
            return self._xano_to_mongo_conversation(saved_data)
            
        except XanoAPIError as e:
            print(f"Failed to save conversation to Xano: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID from Xano"""
        await self.initialize()
        
        try:
            xano_data = await self.client.get_conversation(conversation_id)
            if xano_data:
                return self._xano_to_mongo_conversation(xano_data)
            return None
        except XanoAPIError as e:
            print(f"Failed to get conversation from Xano: {e}")
            return None
    
    async def get_all_conversations(self, limit: int = 100, skip: int = 0) -> List[Conversation]:
        """Get all conversations with pagination from Xano"""
        await self.initialize()
        
        try:
            xano_conversations = await self.client.get_conversations(limit=limit, offset=skip)
            return [self._xano_to_mongo_conversation(conv) for conv in xano_conversations]
        except XanoAPIError as e:
            print(f"Failed to get conversations from Xano: {e}")
            return []
    
    async def get_conversations_by_provider(self, provider: str, limit: int = 100) -> List[Conversation]:
        await self.initialize()

        try:
            all_conversations = await self.get_all_conversations(limit=limit)
            filtered_conversations = []
            
            for conv in all_conversations:
                for response in conv.responses:
                    if response.provider == provider:
                        filtered_conversations.append(conv)
                        break
            
            return filtered_conversations[:limit]
        except Exception as e:
            print(f"Failed to get conversations by provider from Xano: {e}")
            return []
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from Xano"""
        await self.initialize()
        
        try:
            return await self.client.delete_conversation(conversation_id)
        except XanoAPIError as e:
            print(f"Failed to delete conversation from Xano: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics - simplified implementation"""
        await self.initialize()
        
        try:
            conversations = await self.get_all_conversations(limit=1000)  # Sample size
            total_conversations = len(conversations)
            
            # Count responses and providers
            total_responses = 0
            provider_stats = {}
            
            for conv in conversations:
                total_responses += len(conv.responses)
                for response in conv.responses:
                    provider = response.provider
                    provider_stats[provider] = provider_stats.get(provider, 0) + 1
            
            return {
                "total_conversations": total_conversations,
                "total_responses": total_responses,
                "provider_stats": provider_stats
            }
        except Exception as e:
            print(f"Failed to get statistics from Xano: {e}")
            return {"total_conversations": 0, "total_responses": 0, "provider_stats": {}}
    
    async def search_conversations(self, query: str, limit: int = 50) -> List[Conversation]:
        """Search conversations by content - simplified implementation"""
        await self.initialize()
        
        try:
            all_conversations = await self.get_all_conversations(limit=limit * 2)  # Get more to filter
            matching_conversations = []
            
            query_lower = query.lower()
            
            for conv in all_conversations:
                if conv.system_prompt and query_lower in conv.system_prompt.lower():
                    matching_conversations.append(conv)
                    continue
                
                for message in conv.messages:
                    if query_lower in message.content.lower():
                        matching_conversations.append(conv)
                        break
                else:
                    for response in conv.responses:
                        if query_lower in response.content.lower():
                            matching_conversations.append(conv)
                            break
            
            return matching_conversations[:limit]
        except Exception as e:
            print(f"Failed to search conversations in Xano: {e}")
            return []


_xano_db_service = None

def get_xano_db_service() -> XanoDatabaseService:
    """Get the singleton Xano database service instance"""
    global _xano_db_service
    if _xano_db_service is None:
        _xano_db_service = XanoDatabaseService()
    return _xano_db_service


async def close_xano_db_service():
    """Close the Xano database service"""
    await close_xano_client() 