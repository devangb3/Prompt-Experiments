"""
Perplexity service for AI interactions
"""

from typing import List
from openai import OpenAI
from models.BrainWorkoutResult import BrainWorkoutResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse
from logging_config import get_logger

logger = get_logger("services.perplexity")


class PerplexityService(BaseAIService):
    """Perplexity API service"""
    
    def _setup_client(self):
        """Setup Perplexity client"""
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        logger.debug("Perplexity client initialized")
    
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
                    "json_schema": {"schema": BrainWorkoutResult.model_json_schema()},
                },
            )
            
            response_content = response.choices[0].message.content
            logger.debug(f"Perplexity response: {response_content}")
            
            brain_workout_result = BrainWorkoutResult.model_validate_json(response_content)
            return AIResponse(
                provider="Perplexity",
                content=brain_workout_result.model_dump_json(),
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        
        except Exception as e:
            logger.error(f"Error in Perplexity service: {e}")
            return AIResponse(
                provider="Perplexity",
                content="",
                model=model,
                error=str(e)
            ) 