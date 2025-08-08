"""
MongoDB models for AI Prompt Sender using Pydantic for ORM-like functionality
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class PromptMessageModel(BaseModel):
    """Database model for prompt messages"""
    role: str = Field(..., description="Role of the message (system, user, assistant)")
    content: str = Field(..., description="Content of the message")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "What is the capital of France?"
            }
        }
    )


class AIResponseModel(BaseModel):
    """Database model for AI responses"""
    provider: str = Field(..., description="AI provider name")
    response: str = Field(..., description="Response content from the LLM")
    model: str = Field(..., description="Model used for the response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    error: Optional[str] = Field(None, description="Error message if any")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "provider": "openai",
                "response": "Paris is the capital of France.",
                "model": "gpt-4",
                "tokens_used": 15,
                "response_time_ms": 1250.5
            }
        }
    )


class Conversation(BaseModel):
    """Database model for complete conversations"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    system_prompt: Optional[str] = Field(None, description="System prompt if any")
    messages: List[PromptMessageModel] = Field(..., description="List of prompt messages")
    responses: List[AIResponseModel] = Field(..., description="List of AI responses")
    ratings: Optional[Dict[str, Any]] = Field(None, description="Rating data as JSON object")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "conversation_id": "conv_123456",
                "system_prompt": "You are a helpful assistant.",
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "responses": [
                    {
                        "provider": "openai",
                        "response": "Paris is the capital of France.",
                        "model": "gpt-4",
                        "tokens_used": 15
                    }
                ],
                "ratings": {
                    "provider_ratings": {
                        "openai": {
                            "score": 4.5,
                            "categories": {
                                "clarity": {"score": 4.5, "reason": "Clear and concise"},
                                "specificity": {"score": 4.0, "reason": "Specific answer"}
                            },
                            "overall_reason": "clarity: Clear and concise | specificity: Specific answer"
                        }
                    }
                },
                "metadata": {"session_id": "session_123"}
            }
        }
    )


class ConversationRepository:
    """Repository class for Conversation operations"""
    
    def __init__(self, collection):
        self.collection = collection
    
    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation"""
        conversation_dict = conversation.model_dump(by_alias=True)
        result = await self.collection.insert_one(conversation_dict)
        conversation.id = result.inserted_id
        return conversation
    
    async def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Find conversation by conversation_id"""
        doc = await self.collection.find_one({"conversation_id": conversation_id})
        if doc:
            return Conversation(**doc)
        return None
    
    async def find_all(self, limit: int = 100, skip: int = 0) -> List[Conversation]:
        """Find all conversations with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
        conversations = []
        async for doc in cursor:
            conversations.append(Conversation(**doc))
        return conversations
    
    async def update(self, conversation_id: str, conversation: Conversation) -> bool:
        """Update an existing conversation"""
        conversation.updated_at = datetime.utcnow()
        result = await self.collection.update_one(
            {"conversation_id": conversation_id},
            {"$set": conversation.model_dump(exclude={"id"}, by_alias=True)}
        )
        return result.modified_count > 0
    
    async def delete(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        result = await self.collection.delete_one({"conversation_id": conversation_id})
        return result.deleted_count > 0
    
    async def find_by_provider(self, provider: str, limit: int = 100) -> List[Conversation]:
        """Find conversations by AI provider"""
        cursor = self.collection.find(
            {"responses.provider": provider}
        ).limit(limit).sort("created_at", -1)
        conversations = []
        async for doc in cursor:
            conversations.append(Conversation(**doc))
        return conversations
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_conversations = await self.collection.count_documents({})
        total_responses = await self.collection.aggregate([
            {"$unwind": "$responses"},
            {"$count": "total"}
        ]).to_list(1)
        
        provider_stats = await self.collection.aggregate([
            {"$unwind": "$responses"},
            {"$group": {"_id": "$responses.provider", "count": {"$sum": 1}}}
        ]).to_list(None)
        
        return {
            "total_conversations": total_conversations,
            "total_responses": total_responses[0]["total"] if total_responses else 0,
            "provider_stats": {stat["_id"]: stat["count"] for stat in provider_stats}
        } 