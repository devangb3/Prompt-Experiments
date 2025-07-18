"""
Perplexity service implementation
"""

from typing import List
from openai import OpenAI
from models.BrainScanResult import BrainScanResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse


class PerplexityService(BaseAIService):
    """Perplexity API service"""
    
    def _setup_client(self):
        """Setup Perplexity client"""
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "sonar") -> AIResponse:
        """Send prompt to Perplexity"""
        if not self.client:
            return AIResponse(
                provider="Perplexity",
                content="",
                model=model,
                error="Perplexity client not initialized (missing API key)"
            )
        
        try:
            perplexity_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=perplexity_messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {"schema": BrainScanResult.model_json_schema()},
                },
            )
            print("Response: ", response.choices[0].message.content)
            brain_scan_result = BrainScanResult.model_validate_json(response.choices[0].message.content)
            return AIResponse(
                provider="Perplexity",
                content=brain_scan_result,
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        
        except Exception as e:
            return AIResponse(
                provider="Perplexity",
                content="",
                model=model,
                error=str(e)
            ) 