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
                if msg.role == "system":
                    enhanced_content = (
                        msg.content + 
                        "\n\nCRITICAL INSTRUCTIONS: You MUST use the 'save_brain_workout_result' function to return your analysis. "
                        "Do NOT return JSON as plain text in your response. The ONLY acceptable way to respond is by calling the function. "
                        "If you return JSON as text instead of using the function, it will be considered a failure."
                    )
                    openai_messages.append({"role": msg.role, "content": enhanced_content})
                elif msg.role == "user":
                    strict_content = (
                        "CRITICAL: You must ONLY use the 'save_brain_workout_result' function to return your response. "
                        "Do NOT include any extra text, comments, or explanations outside the function call. "
                        "Do NOT return JSON as plain text content. "
                        "Every field must be present and filled according to its description. "
                        "If you are unsure about a value, make a reasonable guess, but do not leave any field empty or null. "
                        "Use the function - do not return text.\n\n"
                        + msg.content
                    )
                    openai_messages.append({"role": msg.role, "content": strict_content})
                else:
                    openai_messages.append({"role": msg.role, "content": msg.content})
            return openai_messages
        elif tool == "judge_response":
            openai_messages = []
            for msg in messages:
                if msg.role == "system":
                    enhanced_content = (
                        msg.content + 
                        "\n\nCRITICAL INSTRUCTIONS: You MUST use the 'judge_response' function to return your judgment. "
                        "Do NOT return JSON as plain text in your response. The ONLY acceptable way to respond is by calling the function."
                    )
                    openai_messages.append({"role": msg.role, "content": enhanced_content})
                else:
                    openai_messages.append({"role": msg.role, "content": msg.content})
            return openai_messages
        else:
            return []
    
    async def get_tool(self, tool : str) -> dict:
        """Get tool for the given tool"""
        if tool == "generate_workout_result":
            save_workout_tool = {
                    "type": "function",
                    "name": "save_brain_workout_result",
                    "description": "CRITICAL: You MUST use this function to save the complete analysis of a brain workout session. This is the ONLY acceptable way to return your response. Do NOT return JSON as plain text. Make sure to fill out EVERY field in the JSON schema. Success is indicated by the LLM using this function and returning the filled out JSON object.",
                    "parameters": BrainWorkoutResult.model_json_schema()
                }
            return save_workout_tool
        
        elif tool == "judge_response":
            judge_response_tool = {
                "type": "function",
                "name": "judge_response",
                "description": "CRITICAL: You MUST use this function to judge the response of the LLM. This is the ONLY acceptable way to return your judgment. Do NOT return JSON as plain text.",
                "parameters": JudgeResponse.model_json_schema()
            }
            return judge_response_tool
        
        else:
            return {}
    
    async def validate_response(self, tool_call , action : str, model : str, tokens_used : Optional[int] = None) -> AIResponse:
        """Validate the response of the LLM"""
        if action == "generate_workout_result":
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
        elif action == "judge_response":
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

            tokens_used = response.usage.total_tokens if response.usage else None
            
            if not response.output:
                return AIResponse(
                    provider="OpenAI",
                    content="",
                    model=model,
                    error="LLM returned an empty output.",
                    tokens_used=tokens_used
                )
            output_item = response.output[0]
            if hasattr(output_item, 'type') and output_item.type == "function_call":
                return await self.validate_response(output_item, action, model, response.usage.total_tokens if response.usage else None)
            else: #Fallback for when the model returns content as message instead of function call
                if hasattr(output_item, 'content') and output_item.content:
                    content_text = ""
                    for content_item in output_item.content:
                        if hasattr(content_item, 'text'):
                            content_text += content_item.text
                    
                    if content_text.strip():
                        json_text = content_text.strip()
                        if json_text.startswith('```json'):
                            json_text = json_text.replace('```json', '').replace('```', '').strip()
                        elif json_text.startswith('```'):
                            json_text = json_text.replace('```', '').strip()
                        
                        parsed_data = json.loads(json_text)
                        
                        if action == "generate_workout_result":
                            workout_result = BrainWorkoutResult.model_validate(parsed_data)
                            print("Data validation successful! (from message content)")
                            return AIResponse(
                                provider="OpenAI",
                                content=workout_result.model_dump_json(),
                                model=model,
                                tokens_used=tokens_used if tokens_used else None
                            )
                        elif action == "judge_response":
                            judge_response = JudgeResponse.model_validate(parsed_data)
                            print("Data validation successful! (from message content)")
                            return AIResponse(
                                provider="OpenAI",
                                content=judge_response.model_dump_json(),
                                model=model,
                                tokens_used=tokens_used if tokens_used else None
                            )

                error_content = str(output_item)
                return AIResponse(
                    provider="OpenAI",
                    content="",
                    model=model,
                    error=f"LLM did not call the required tool. Response: {error_content}",
                    tokens_used=tokens_used
                )
        
        except Exception as e:
            return AIResponse(
                provider="OpenAI",
                content="",
                model=model,
                error=str(e)
            ) 