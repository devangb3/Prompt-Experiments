"""
OpenAI service implementation
"""

from typing import List
from openai import OpenAI
from models.BrainScanResult import BrainScanResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse


class OpenAIService(BaseAIService):
    """OpenAI API service"""
    
    def _setup_client(self):
        """Setup OpenAI client"""
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "gpt-4o-mini") -> AIResponse:
        """Send prompt to OpenAI"""
        if not self.client:
            return AIResponse(
                provider="OpenAI",
                content="",
                model=model,
                error="OpenAI client not initialized (missing API key)"
            )
        
        try:
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
            
            response = self.client.chat.completions.parse(
                model=model,
                messages=openai_messages,
                response_format=BrainScanResult
            )
            
            return AIResponse(
                provider="OpenAI",
                content=response.choices[0].message.content,
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        
        except Exception as e:
            return AIResponse(
                provider="OpenAI",
                content="",
                model=model,
                error=str(e)
            ) 