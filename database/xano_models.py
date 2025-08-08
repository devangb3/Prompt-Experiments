"""
Xano-compatible models for AI Prompt Sender
These models are designed to work with Xano's REST API structure
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class XanoPromptMessageModel(BaseModel):
    """Xano model for prompt messages"""
    role: str = Field(..., description="Role of the message (system, user, assistant)")
    content: str = Field(..., description="Content of the message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "What is the capital of France?"
            }
        }
    )


class XanoAIResponseModel(BaseModel):
    """Xano model for AI responses"""
    provider: str = Field(..., description="AI provider name")
    response: str = Field(..., description="Response content from the LLM")
    model: str = Field(..., description="Model used for the response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    error: Optional[str] = Field(None, description="Error message if any")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    
    model_config = ConfigDict(
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


class XanoConversation(BaseModel):
    """Xano model for complete conversations"""
    id: Optional[int] = Field(None, description="Xano auto-generated ID")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    system_prompt: Optional[str] = Field(None, description="System prompt if any")
    messages: List[XanoPromptMessageModel] = Field(..., description="List of prompt messages")
    responses: List[XanoAIResponseModel] = Field(..., description="List of AI responses")
    ratings: Optional[Dict[str, Any]] = Field(None, description="Rating data as JSON object")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp (managed by Xano)")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp (managed by Xano)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
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

    @classmethod
    def from_mongo_conversation(cls, mongo_conv):
        """Convert MongoDB Conversation to XanoConversation"""
        return cls(
            conversation_id=mongo_conv.conversation_id,
            system_prompt=mongo_conv.system_prompt,
            messages=[
                XanoPromptMessageModel(role=msg.role, content=msg.content)
                for msg in mongo_conv.messages
            ],
            responses=[
                XanoAIResponseModel(
                    provider=resp.provider,
                    response=getattr(resp, "response", None) or getattr(resp, "content", ""),
                    model=resp.model,
                    tokens_used=resp.tokens_used,
                    error=resp.error,
                    response_time_ms=resp.response_time_ms
                )
                for resp in mongo_conv.responses
            ],
            ratings=getattr(mongo_conv, 'ratings', None),
            metadata=mongo_conv.metadata
        )


class XanoSearchRequest(BaseModel):
    """Model for search requests to Xano"""
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(50, description="Maximum number of results")
    

class XanoStatistics(BaseModel):
    """Model for statistics response from Xano"""
    total_conversations: int = Field(0, description="Total number of conversations")
    total_responses: int = Field(0, description="Total number of responses")
    provider_stats: Dict[str, int] = Field(default_factory=dict, description="Provider usage statistics") 