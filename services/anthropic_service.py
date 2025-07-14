"""
Anthropic service implementation
"""

from typing import List
import anthropic

from .base_service import BaseAIService
from .types import PromptMessage, AIResponse


class AnthropicService(BaseAIService):
    """Anthropic Claude API service"""
    
    def _setup_client(self):
        """Setup Anthropic client"""
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "claude-3-5-sonnet-20241022") -> AIResponse:
        """Send prompt to Anthropic Claude"""
        if not self.client:
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error="Anthropic client not initialized (missing API key)"
            )
        
        try:
            system_messages = [msg.content for msg in messages if msg.role == "system"]
            user_messages = [msg for msg in messages if msg.role != "system"]
            user_msg = user_messages[0] if user_messages else None
            system_prompt = "\n\n".join(system_messages) if system_messages else "You are a helpful assistant."
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please analyze this data and provide advice:\n\n{user_msg.content if user_msg else ''}"
                    }
                ]
            )
            
            return AIResponse(
                provider="Anthropic",
                content=response.content[0].text,
                model=model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )
        
        except Exception as e:
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error=str(e)
            ) 