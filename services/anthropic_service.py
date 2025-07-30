"""
Anthropic service implementation
"""

from typing import List
import anthropic
import json
from models.BrainWorkoutResult import BrainWorkoutResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse


class AnthropicService(BaseAIService):
    """Anthropic Claude API service"""
    
    def _setup_client(self):
        """Setup Anthropic client"""
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "claude-sonnet-4-20250514") -> AIResponse:
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

            save_workout_tool = {
                "name": "save_brain_workout_result",
                "description": "Saves the complete analysis of a brain workout session. Make sure to fill out EVERY field in the JSON schema. Success is indicated by the LLM returning the filled out JSON object.",
                "input_schema": BrainWorkoutResult.model_json_schema()
            }
           
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                tools=[save_workout_tool],
                tool_choice={"type": "tool", "name": "save_brain_workout_result"},
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "STRICT INSTRUCTIONS: You must ONLY return a valid BrainWorkoutResult JSON object. "
                            "Do NOT include any extra text, comments, or explanations. "
                            "Every field must be present and filled according to its description. "
                            "If you are unsure about a value, make a reasonable guess, but do not leave any field empty or null. "
                            "Your response will be parsed as JSON. Any deviation from the schema or extra output will be considered a failure. "
                            "Double-check your output for completeness and validity before submitting.\n\n"
                            f"{user_msg.content if user_msg else ''}"
                        )
                    }
                ]
            )
            
            tool_call = response.content[0]
            tool_args = tool_call.input

            if tool_call.name == "save_brain_workout_result":
                print("LLM responded with the correct tool. Validating data...")
                workout_result = BrainWorkoutResult.model_validate(tool_args)
                print("Data validation successful!")

            else:
                print(f"Error: LLM responded with an unexpected tool: {tool_call.name}")
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error=f"LLM responded with an unexpected tool: {tool_call.name}"
                )
            return AIResponse(
                provider="Anthropic",
                content=workout_result.model_dump_json(),
                model=model,
                tokens_used=None
            )
        
        except Exception as e:
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error=str(e)
            ) 
