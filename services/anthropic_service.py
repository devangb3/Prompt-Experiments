"""
Anthropic service for AI interactions
"""

import json
from typing import List, Optional
import anthropic
import json
from models.BrainWorkoutResult import BrainWorkoutResult
from models.JudgeResponse import JudgeResponse
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse
from logging_config import get_logger

logger = get_logger("services.anthropic")


class AnthropicService(BaseAIService):
    
    def _setup_client(self):
        """Setup Anthropic client"""
        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.debug("Anthropic client initialized")
    
    async def get_messages(self, tool: str, messages: List[PromptMessage]) -> List[dict]:
        """Get messages for the given tool"""
        if tool == "generate_workout_result":
            anthropic_messages = []
            system_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    enhanced_content = (
                        msg.content + 
                        "\n\nCRITICAL INSTRUCTIONS: You MUST use the 'save_brain_workout_result' tool to return your analysis. "
                        "Do NOT return JSON as plain text in your response. The ONLY acceptable way to respond is by calling the tool. "
                        "If you return JSON as text instead of using the tool, it will be considered a failure."
                    )
                    system_messages.append(enhanced_content)
                elif msg.role == "user":
                    strict_content = (
                        "CRITICAL: You must ONLY use the 'save_brain_workout_result' tool to return your response. "
                        "Do NOT include any extra text, comments, or explanations outside the tool call. "
                        "Do NOT return JSON as plain text content. "
                        "Every field must be present and filled according to its description. "
                        "If you are unsure about a value, make a reasonable guess, but do not leave any field empty or null. "
                        "Use the tool - do not return text.\n\n"
                        + msg.content
                    )
                    anthropic_messages.append({"role": "user", "content": strict_content})
                else:
                    anthropic_messages.append({"role": msg.role, "content": msg.content})
            
            return {"messages": anthropic_messages, "system": "\n\n".join(system_messages)}
            
        elif tool == "judge_response":
            anthropic_messages = []
            system_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    enhanced_content = (
                        msg.content + 
                        "\n\nCRITICAL INSTRUCTIONS: You MUST use the 'judge_response' tool to return your judgment. "
                        "Do NOT return JSON as plain text in your response. The ONLY acceptable way to respond is by calling the tool. "
                        "\n\nIMPORTANT: Each field must be a proper JSON object with 'score' and 'reason' properties. "
                        "Example: {\"clarity\": {\"score\": 4, \"reason\": \"Clear feedback\"}, \"specificity\": {\"score\": 5, \"reason\": \"Very specific\"}}"
                    )
                    system_messages.append(enhanced_content)
                elif msg.role == "user":
                    enhanced_content = (
                        "CRITICAL: Use the 'judge_response' tool with proper JSON structure. "
                        "Each field (clarity, specificity, relevance, actionability, approachability) must be an object with 'score' (1-5) and 'reason' properties. "
                        "Do NOT use XML-like parameters. Use proper JSON objects only.\n\n" + msg.content
                    )
                    anthropic_messages.append({"role": "user", "content": enhanced_content})
                else:
                    anthropic_messages.append({"role": msg.role, "content": msg.content})
            
            return {"messages": anthropic_messages, "system": "\n\n".join(system_messages)}
        else:
            return {"messages": [], "system": "You are a helpful assistant."}
    
    async def get_tool(self, tool: str) -> dict:
        """Get tool for the given tool"""
        if tool == "generate_workout_result":
            save_workout_tool = {
                "name": "save_brain_workout_result",
                "description": "CRITICAL: You MUST use this tool to save the complete analysis of a brain workout session. This is the ONLY acceptable way to return your response. Do NOT return JSON as plain text. Make sure to fill out EVERY field in the JSON schema. Success is indicated by the LLM using this tool and returning the filled out JSON object.",
                "input_schema": BrainWorkoutResult.model_json_schema()
            }
            return save_workout_tool
        
        elif tool == "judge_response":
            judge_response_tool = {
                "name": "judge_response",
                "description": """CRITICAL: You MUST use this tool to judge the response of the LLM. This is the ONLY acceptable way to return your judgment. Do NOT return JSON as plain text.

                IMPORTANT: Each field (clarity, specificity, relevance, actionability, approachability) must be a JSON object with this EXACT structure:
                {
                "score": <integer from 1-5>,
                "reason": "<one line explanation>"
                }

                Example of correct format:
                {
                "clarity": {"score": 4, "reason": "The feedback is clear and easy to understand"},
                "specificity": {"score": 5, "reason": "Very specific examples provided"}
                }

                Do NOT use XML-like parameters. Use proper JSON objects only.""",
                "input_schema": JudgeResponse.model_json_schema()
            }
            return judge_response_tool
        
        else:
            return {}
    
    async def validate_response(self, tool_call, action: str, model: str, tokens_used: Optional[int] = None) -> AIResponse:
        """Validate the response of the LLM"""
        if action == "generate_workout_result":
            logger.debug("LLM responded with the correct tool. Validating data...")
            tool_args = tool_call.input
            try:
                workout_result = BrainWorkoutResult.model_validate(tool_args)
                logger.debug("Data validation successful!")
                return AIResponse(
                    provider="Anthropic",
                    content=workout_result.model_dump_json(),
                    model=model,
                    tokens_used=tokens_used if tokens_used else None
                )
            except Exception as e:
                logger.error(f"Validation error for BrainWorkoutResult: {e}")
                logger.debug(f"Tool args received: {tool_args}")
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error=str(e)
                )
        elif action == "judge_response":
            logger.debug("LLM responded with the correct tool. Validating data...")
            tool_args = tool_call.input
            
            try:
                judge_response = JudgeResponse.model_validate(tool_args)
                logger.debug("Data validation successful!")
                return AIResponse(
                    provider="Anthropic",
                    content=judge_response.model_dump_json(),
                    model=model,
                    tokens_used=tokens_used if tokens_used else None
                )
            except Exception as e:
                logger.error(f"Direct validation failed: {e}")
                
                # Try to fix malformed XML-like parameters
                try:
                    fixed_args = {}
                    for field_name, field_value in tool_args.items():
                        if isinstance(field_value, str) and '<parameter' in field_value:
                            # Extract score from XML-like string
                            import re
                            score_match = re.search(r'score["\'>]*(\d+)', field_value)
                            if score_match:
                                score = int(score_match.group(1))
                                fixed_args[field_name] = {
                                    "score": score,
                                    "reason": f"Automatically extracted score {score}"
                                }
                            else:
                                fixed_args[field_name] = {"score": 3, "reason": "Could not parse malformed input"}
                        else:
                            fixed_args[field_name] = field_value
                    
                    logger.debug(f"Attempting validation with fixed args: {fixed_args}")
                    judge_response = JudgeResponse.model_validate(fixed_args)
                    logger.debug("Data validation successful after fixing malformed data!")
                    return AIResponse(
                        provider="Anthropic",
                        content=judge_response.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
                except Exception as fix_error:
                    logger.error(f"Failed to fix malformed data: {fix_error}")
                    return AIResponse(
                        provider="Anthropic",
                        content="",
                        model=model,
                        error=f"Validation failed: {e}. Fix attempt failed: {fix_error}"
                    )
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "claude-sonnet-4-20250514", action: str = "generate_workout_result") -> AIResponse:
        """Send prompt to Anthropic Claude"""
        if not self.client:
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error="Anthropic client not initialized (missing API key)"
            )
        
        try:
            tool = await self.get_tool(action)
            if not tool or tool == {}:
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error="Tool not found"
                )
            
            message_data = await self.get_messages(action, messages)
            anthropic_messages = message_data["messages"]
            system_prompt = message_data["system"]
            
            response = self.client.messages.create(
                model=model,
                max_tokens=20000,
                system=system_prompt,
                tools=[tool],
                tool_choice={"type": "tool", "name": tool["name"]},
                messages=anthropic_messages
            )
            
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            
            if not response.content:
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error="LLM returned an empty response.",
                    tokens_used=tokens_used
                )

            for content_item in response.content:
                if hasattr(content_item, 'type') and content_item.type == "tool_use":
                    if content_item.name == tool["name"]:
                        return await self.validate_response(content_item, action, model, tokens_used)
                    else:
                        return AIResponse(
                            provider="Anthropic",
                            content="",
                            model=model,
                            error=f"LLM responded with an unexpected tool: {content_item.name}",
                            tokens_used=tokens_used
                        )
            
            # Fallback for when the model returns content as message instead of tool call
            content_text = ""
            for content_item in response.content:
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
                        provider="Anthropic",
                        content=workout_result.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
                elif action == "judge_response":
                    judge_response = JudgeResponse.model_validate(parsed_data)
                    print("Data validation successful! (from message content)")
                    return AIResponse(
                        provider="Anthropic",
                        content=judge_response.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
            
            error_content = str(response.content)
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error=f"LLM did not call the required tool. Response: {error_content}",
                tokens_used=tokens_used
            )
        
        except Exception as e:
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error=str(e)
            ) 
