"""
OpenAI service implementation
"""

from typing import List
from openai import OpenAI
from models.BrainWorkoutResult import BrainWorkoutResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse
import json

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
            
            save_workout_tool = {
                "type": "function",
                "name": "save_brain_workout_result",
                "description": "Saves the complete analysis of a brain workout session. Make sure to fill out EVERY field in the JSON schema. Success is indicated by the LLM returning the filled out JSON object.",
                "parameters": BrainWorkoutResult.model_json_schema()
            }

            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
            
            response = self.client.responses.create(
                model="gpt-4.1",
                input=openai_messages,
                tools=[save_workout_tool]
            )
            
            tool_call = response.output[0]
            tool_args = json.loads(tool_call.arguments)

            if tool_call.name == "save_brain_workout_result":
                print("LLM responded with the correct tool. Validating data...")
                workout_result = BrainWorkoutResult.model_validate(tool_args)
                print("Data validation successful!")
            
            return AIResponse(
                provider="OpenAI",
                content=workout_result.model_dump_json(),
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