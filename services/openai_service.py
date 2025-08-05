"""
OpenAI service implementation
"""

from typing import List, Optional
from openai import OpenAI
from models.BrainWorkoutResult import BrainWorkoutResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse
from models.JudgeResponse import JudgeResponse
import json

class OpenAIService(BaseAIService):
    """OpenAI API service"""
    
    def _setup_client(self):
        """Setup OpenAI client"""
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    async def get_messages(self, tool : str, messages : List[PromptMessage]) -> List[PromptMessage]:
        """Get messages for the given tool"""
        if tool == "generate_workout_result":
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
            return openai_messages
        elif tool == "judge_response":
            return [{"role": msg.role, "content": msg.content} for msg in messages]
        else:
            return []
    
    async def get_tool(self, tool : str) -> dict:
        """Get tool for the given tool"""
        if tool == "generate_workout_result":
            save_workout_tool = {
                    "type": "function",
                    "name": "save_brain_workout_result",
                    "description": "Saves the complete analysis of a brain workout session. Make sure to fill out EVERY field in the JSON schema. Success is indicated by the LLM returning the filled out JSON object.",
                    "parameters": BrainWorkoutResult.model_json_schema()
                }
            return save_workout_tool
        
        elif tool == "judge_response":
            judge_response_tool = {
                "type": "function",
                "name": "judge_response",
                "description": "Judges the response of the LLM",
                "parameters": JudgeResponse.model_json_schema()
            }
            return judge_response_tool
        
        else:
            return {}
    
    async def validate_response(self, tool_call , action : str, model : str, tokens_used : Optional[int] = None) -> AIResponse:
        """Validate the response of the LLM"""
        if action == "generate_workout_result":
            if tool_call.name == "save_brain_workout_result":
                print("LLM responded with the correct tool. Validating data...")
                tool_args = json.loads(tool_call.arguments)
                try:
                    workout_result = BrainWorkoutResult.model_validate(tool_args)
                    print("Data validation successful!")
                    return AIResponse(
                        provider="OpenAI",
                        content=workout_result.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
                except Exception as e:
                    return AIResponse(
                        provider="OpenAI",
                        content="",
                        model=model,
                        error=str(e)
                    )
            else:
                return AIResponse(
                    provider="OpenAI",
                    content="",
                    model=model,
                    error="Wrong tool call"
                )
        elif action == "judge_response":
            if tool_call.name == "judge_response":
                print("LLM responded with the correct tool. Validating data...")
                tool_args = json.loads(tool_call.arguments)
                try:
                    judge_response = JudgeResponse.model_validate(tool_args)
                    print("Data validation successful!")
                    return AIResponse(
                        provider="OpenAI",
                        content=judge_response.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
                except Exception as e:
                    return AIResponse(
                        provider="OpenAI",
                        content="",
                        model=model,
                        error=str(e)
                    )
            else:
                return AIResponse(
                    provider="OpenAI",
                    content="",
                    model=model,
                    error="Wrong tool call"
                )

    async def send_prompt(self, messages: List[PromptMessage], model: str = "gpt-4.1", action : str = "generate_workout_result") -> AIResponse:
        """Send prompt to OpenAI"""
        if not self.client:
            return AIResponse(
                provider="OpenAI",
                content="",
                model=model,
                error="OpenAI client not initialized (missing API key)"
            )
        
        try:
            tool = await self.get_tool(action)
            if not tool or tool == {}:
                return AIResponse(
                    provider="OpenAI",
                    content="",
                    model=model,
                    error="Tool not found"
                )
            openai_messages = await self.get_messages(action, messages)
            
            response = self.client.responses.create(
                model=model,
                input=openai_messages,
                tools=[tool]
            )
            
            return await self.validate_response(response.output[0], action, model, response.usage.total_tokens if response.usage else None)
        
        except Exception as e:
            return AIResponse(
                provider="OpenAI",
                content="",
                model=model,
                error=str(e)
            ) 