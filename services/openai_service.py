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

            openai_messages = []
            for msg in messages:
                if msg.role == "user":
                    strict_content = (
                        "STRICT INSTRUCTIONS: You must ONLY return a valid BrainWorkoutResult JSON object. "
                        "Do NOT include any extra text, comments, or explanations. "
                        "Every field must be present and filled according to its description. "
                        "If you are unsure about a value, make a reasonable guess, but do not leave any field empty or null. "
                        "Your response will be parsed as JSON. Any deviation from the schema or extra output will be considered a failure. "
                        "Double-check your output for completeness and validity before submitting.\n\n"
                        + msg.content
                    )
                    openai_messages.append({"role": msg.role, "content": strict_content})
                else:
                    openai_messages.append({"role": msg.role, "content": msg.content})
            
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