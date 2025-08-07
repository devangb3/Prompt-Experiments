"""
Xano database service for conversation storage
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from .xano_models import XanoPromptMessageModel, XanoAIResponseModel
from .xano_client import XanoClient, get_xano_client
from .models import Conversation
from services.types import PromptMessage, AIResponse
from logging_config import get_logger

logger = get_logger("database.xano_service")


class XanoDatabaseService:
    """Service class for Xano database operations"""
    
    def __init__(self):
        self.client: Optional[XanoClient] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Xano client"""
        if not self._initialized:
            self.client = await get_xano_client()
            self._initialized = True
            logger.debug("Xano database service initialized")
    
    def _convert_prompt_messages(self, messages: List[PromptMessage]) -> List[XanoPromptMessageModel]:
        """Convert PromptMessage objects to XanoPromptMessageModel objects"""
        return [XanoPromptMessageModel(role=msg.role, content=msg.content) for msg in messages]
    
    def _convert_ai_responses(self, responses: List[AIResponse], response_times: Optional[Dict[str, float]] = None) -> List[XanoAIResponseModel]:
        """Convert AIResponse objects to XanoAIResponseModel objects"""
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
        """Convert Xano conversation data to MongoDB-compatible Conversation object"""
        def parse_timestamp(timestamp) -> datetime:
            if isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return datetime.fromtimestamp(timestamp)
        
        # Convert Xano response format to MongoDB format
        mongo_responses = []
        for xano_response in xano_data.get('responses', []):
            mongo_response = {
                'provider': xano_response.get('provider'),
                'content': xano_response.get('content'),
                'model': xano_response.get('model'),
                'tokens_used': xano_response.get('tokens_used'),
                'error': xano_response.get('error'),
                'response_time_ms': xano_response.get('response_time_ms'),
                'created_at': parse_timestamp(xano_response.get('created_at', datetime.now()))
            }
            mongo_responses.append(mongo_response)
        
        # Convert Xano message format to MongoDB format
        mongo_messages = []
        for xano_message in xano_data.get('messages', []):
            mongo_message = {
                'role': xano_message.get('role'),
                'content': xano_message.get('content'),
                'created_at': parse_timestamp(xano_message.get('created_at', datetime.now()))
            }
            mongo_messages.append(mongo_message)
        
        return Conversation(
            conversation_id=xano_data.get('conversation_id'),
            system_prompt=xano_data.get('system_prompt'),
            messages=mongo_messages,
            responses=mongo_responses,
            metadata=xano_data.get('metadata', {}),
            created_at=parse_timestamp(xano_data.get('created_at', datetime.now())),
            updated_at=parse_timestamp(xano_data.get('updated_at', datetime.now()))
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
        
        conversation_data = {
            "conversation_id": conversation_id,
            "system_prompt": system_prompt,
            "messages": self._convert_prompt_messages(messages),
            "responses": self._convert_ai_responses(responses, response_times),
            "metadata": metadata or {}
        }
        
        try:
            # Save to Xano
            saved_data = await self.client.create_conversation(conversation_data)
            logger.info(f"Saved conversation {conversation_id} to Xano")
            
            # Convert back to MongoDB-compatible format for return value
            return self._xano_to_mongo_conversation(saved_data)
            
        except Exception as e:
            logger.error(f"Failed to save conversation to Xano: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID from Xano"""
        await self.initialize()
        
        try:
            xano_data = await self.client.get_conversation(conversation_id)
            if xano_data:
                logger.debug(f"Retrieved conversation from Xano: {conversation_id}")
                return self._xano_to_mongo_conversation(xano_data)
            logger.warning(f"Conversation not found in Xano: {conversation_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get conversation from Xano: {e}")
            return None
    
    async def get_all_conversations(self, limit: int = 100, skip: int = 0) -> List[Conversation]:
        """Get all conversations with pagination from Xano"""
        await self.initialize()
        
        try:
            xano_conversations = await self.client.get_conversations(limit=limit, offset=skip)
            conversations = [self._xano_to_mongo_conversation(conv) for conv in xano_conversations]
            logger.debug(f"Retrieved {len(conversations)} conversations from Xano")
            return conversations
        except Exception as e:
            logger.error(f"Failed to get conversations from Xano: {e}")
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
            
            logger.debug(f"Found {len(filtered_conversations)} conversations for provider: {provider}")
            return filtered_conversations[:limit]
        except Exception as e:
            logger.error(f"Failed to get conversations by provider from Xano: {e}")
            return []
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from Xano"""
        await self.initialize()
        
        try:
            success = await self.client.delete_conversation(conversation_id)
            if success:
                logger.info(f"Deleted conversation from Xano: {conversation_id}")
            else:
                logger.warning(f"Failed to delete conversation from Xano: {conversation_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete conversation from Xano: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics - simplified implementation"""
        await self.initialize()
        
        try:
            conversations = await self.get_all_conversations(limit=1000)  # Sample size
            total_conversations = len(conversations)
            
            total_responses = 0
            provider_stats = {}
            
            for conv in conversations:
                total_responses += len(conv.responses)
                for response in conv.responses:
                    provider = response.provider
                    provider_stats[provider] = provider_stats.get(provider, 0) + 1
            
            stats = {
                "total_conversations": total_conversations,
                "total_responses": total_responses,
                "provider_stats": provider_stats
            }
            logger.debug(f"Retrieved statistics from Xano: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics from Xano: {e}")
            return {"total_conversations": 0, "total_responses": 0, "provider_stats": {}}
    
    async def search_conversations(self, query: str, limit: int = 50) -> List[Conversation]:
        """Search conversations by content - simplified implementation"""
        await self.initialize()
        
        try:
            all_conversations = await self.get_all_conversations(limit=limit * 2)  # Get more to filter
            matching_conversations = []
            
            for conv in all_conversations:
                # Search in messages
                for msg in conv.messages:
                    if query.lower() in msg.content.lower():
                        matching_conversations.append(conv)
                        break
                
                # Search in responses
                for response in conv.responses:
                    if query.lower() in response.content.lower():
                        if conv not in matching_conversations:
                            matching_conversations.append(conv)
                        break
                
                # Search in system prompt
                if conv.system_prompt and query.lower() in conv.system_prompt.lower():
                    if conv not in matching_conversations:
                        matching_conversations.append(conv)
            
            logger.debug(f"Found {len(matching_conversations)} conversations matching query: {query}")
            return matching_conversations[:limit]
        except Exception as e:
            logger.error(f"Failed to search conversations in Xano: {e}")
            return []


_xano_db_service = None

def get_xano_db_service() -> XanoDatabaseService:
    """Get the singleton Xano database service instance"""
    global _xano_db_service
    if _xano_db_service is None:
        _xano_db_service = XanoDatabaseService()
        logger.debug("Created new Xano database service instance")
    return _xano_db_service

async def close_xano_db_service():
    """Close the Xano database service"""
    global _xano_db_service
    if _xano_db_service and _xano_db_service.client:
        await _xano_db_service.client.close()
        logger.info("Xano database service closed") 