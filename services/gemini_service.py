"""
Google Gemini service implementation
"""

from typing import List, Optional
from google import genai
from google.genai import types
from pydantic import ValidationError, BaseModel
from models.BrainWorkoutResult import BrainWorkoutResult
from models.JudgeResponse import JudgeResponse
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse
import json


def get_flattened_schema(cls: BaseModel):
    """
    Converts a Pydantic model to a flattened JSON schema dictionary
    by resolving all $ref references inline. This is required for 
    Google Gemini API function calling which doesn't support $ref.
    """
    schema = cls.model_json_schema()
    if "$defs" not in schema:
        return schema

    defs = schema.pop("$defs")
    resolved_refs = set()

    def _resolve(schema_part, current_path=""):
        if "$ref" in schema_part:
            ref = schema_part["$ref"]
            ref_name = ref.split("/")[-1]
            
            # Avoid infinite recursion by tracking resolved refs
            if ref in resolved_refs:
                # For circular refs, just remove the $ref and leave as generic object
                schema_part.pop("$ref")
                schema_part.update({"type": "object"})
                return
                
            if ref_name in defs:
                resolved_refs.add(ref)
                schema_part.pop("$ref")
                ref_schema = defs[ref_name].copy()
                schema_part.update(ref_schema)
                _resolve(schema_part, current_path + "/" + ref_name)
        
        # Handle anyOf structure for optional fields
        if "anyOf" in schema_part:
            # For optional fields, we want to take the non-null type
            # Find the schema that's not {"type": "null"}
            for option in schema_part["anyOf"]:
                if option.get("type") != "null":
                    # Replace the anyOf with the actual schema
                    schema_part.pop("anyOf")
                    schema_part.update(option)
                    _resolve(schema_part, current_path)
                    break
                
        if "properties" in schema_part:
            for prop_name, prop in schema_part["properties"].items():
                _resolve(prop, current_path + "/properties/" + prop_name)
        if "items" in schema_part:
            _resolve(schema_part["items"], current_path + "/items")
        schema_part.pop("title", None)

    _resolve(schema)
    return schema


class GeminiService(BaseAIService):
    """Google Gemini API service"""
    
    def _setup_client(self):
        """Setup Gemini client"""
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
    
    async def get_messages(self, tool: str, messages: List[PromptMessage]) -> dict:
        """Get messages for the given tool"""
        contents = []
        system_prompt = ""
        
        if tool == "generate_workout_result":
            for msg in messages:
                if msg.role == "system":
                    enhanced_content = (
                        msg.content + 
                        "\n\nCRITICAL INSTRUCTIONS: You MUST use the 'save_brain_workout_result' function to return your analysis. "
                        "Do NOT return JSON as plain text in your response. The ONLY acceptable way to respond is by calling the function. "
                        "COMPLETENESS REQUIREMENT: Every single field in the schema must be filled with meaningful content. "
                        "NO null values, NO empty strings, NO missing fields are allowed. "
                        "If you're unsure about a value, make a reasonable guess based on the context provided. "
                        "The response will be strictly validated - incomplete responses will be rejected."
                    )
                    system_prompt = enhanced_content
                elif msg.role == "user":
                    strict_content = (
                        "CRITICAL: You must ONLY use the 'save_brain_workout_result' function to return your response. "
                        "Do NOT include any extra text, comments, or explanations outside the function call. "
                        "Do NOT return JSON as plain text content. "
                        "MANDATORY: Every field must be present and filled according to its description. "
                        "NO NULL VALUES ALLOWED - if you're unsure, make a reasonable guess. "
                        "ALL arrays must contain the required number of elements. "
                        "ALL objects must have ALL required properties filled. "
                        "Use the function - do not return text.\n\n"
                        + msg.content
                    )
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part(text=strict_content)]
                    ))
                else:
                    contents.append(types.Content(
                        role=msg.role,
                        parts=[types.Part(text=msg.content)]
                    ))
        
        elif tool == "judge_response":
            for msg in messages:
                if msg.role == "system":
                    enhanced_content = (
                        msg.content + 
                        "\n\nCRITICAL INSTRUCTIONS: You MUST use the 'save_brain_workout_result' function..."
                        "COMPLETENESS REQUIREMENT: Every single field in the schema must be filled. "
                        "**If a value is unknown or cannot be determined from the context, you MUST write the string 'Not applicable' or 'Unknown' instead of providing a null value.** "
                        "NO null values, NO empty strings, and NO missing fields are allowed."
                    )
                    system_prompt = enhanced_content
                elif msg.role == "user":
                    enhanced_content = (
                        "CRITICAL: Use the 'judge_response' function with proper JSON structure. "
                        "ALL FIVE FIELDS REQUIRED: clarity, specificity, relevance, actionability, approachability. "
                        "Each field must be an object with 'score' (1-5) and 'reason' properties. "
                        "NO null values allowed anywhere. Complete all fields or the response will fail validation.\n\n" + msg.content
                    )
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part(text=enhanced_content)]
                    ))
                else:
                    contents.append(types.Content(
                        role=msg.role,
                        parts=[types.Part(text=msg.content)]
                    ))
        
        return {"contents": contents, "system_prompt": system_prompt}
    
    async def get_tool(self, tool: str) -> types.FunctionDeclaration:
        """Get tool for the given tool"""
        if tool == "generate_workout_result":
            schema = get_flattened_schema(BrainWorkoutResult)
            return types.FunctionDeclaration(
                name="save_brain_workout_result",
                description="""CRITICAL: You MUST use this function to save the complete analysis of a brain workout session. This is the ONLY acceptable way to return your response. Do NOT return JSON as plain text. 

                                MANDATORY REQUIREMENTS:
                                - Fill out EVERY single field in the JSON schema - NO null values allowed
                                - Every object must have ALL required properties filled
                                - All arrays must contain the required number of elements
                                - All text fields must contain meaningful, specific content
                                - If you're unsure about a value, make a reasonable guess based on the context
                                - Success is indicated ONLY by returning a completely filled JSON object with NO missing or null fields

                                VALIDATION: The response will be strictly validated against the schema. Any missing, null, or incomplete fields will result in failure.""",
                parameters=schema
            )
        
        elif tool == "judge_response":
            schema = get_flattened_schema(JudgeResponse)
            return types.FunctionDeclaration(
                name="judge_response",
                description="""CRITICAL: You MUST use this function to judge the response of the LLM. This is the ONLY acceptable way to return your judgment. Do NOT return JSON as plain text.
                MANDATORY REQUIREMENTS:
                - ALL five fields (clarity, specificity, relevance, actionability, approachability) MUST be completed
                - Each field MUST be a JSON object with BOTH "score" and "reason" properties
                - NO null values are allowed anywhere
                - Scores must be integers from 1-5
                - Reasons must be meaningful explanations (not null or empty)

                EXACT REQUIRED STRUCTURE:
                {
                "clarity": {"score": <1-5>, "reason": "<detailed explanation>"},
                "specificity": {"score": <1-5>, "reason": "<detailed explanation>"},
                "relevance": {"score": <1-5>, "reason": "<detailed explanation>"},
                "actionability": {"score": <1-5>, "reason": "<detailed explanation>"},
                "approachability": {"score": <1-5>, "reason": "<detailed explanation>"}
                }

                VALIDATION: Any missing fields, null values, or incomplete objects will result in failure.""",
                parameters=schema
            )
        
        else:
            return None
    
    async def validate_response(self, function_call, action: str, model: str, tokens_used: Optional[int] = None) -> AIResponse:
        """Validate the response of the LLM"""
        if action == "generate_workout_result":
            print("LLM responded with the correct function. Validating data...")
            tool_args = function_call.args
            print(f"Tool args received: {tool_args}")
                       
            try:
                workout_result = BrainWorkoutResult.model_validate(tool_args)
                print("Data validation successful!")
                return AIResponse(
                    provider="Gemini",
                    content=workout_result.model_dump_json(),
                    model=model,
                    tokens_used=tokens_used if tokens_used else None
                )
            except Exception as e:
                print(f"Validation error for BrainWorkoutResult: {e}")
                return AIResponse(
                    provider="Gemini",
                    content="",
                    model=model,
                    error=f"Validation failed: {e}"
                )
        elif action == "judge_response":
            print("LLM responded with the correct function. Validating data...")
            tool_args = function_call.args
                        
            try:
                judge_response = JudgeResponse.model_validate(tool_args)
                print("Data validation successful!")
                return AIResponse(
                    provider="Gemini",
                    content=judge_response.model_dump_json(),
                    model=model,
                    tokens_used=tokens_used if tokens_used else None
                )
            except Exception as e:
                print(f"Direct validation failed: {e}")
                return AIResponse(
                    provider="Gemini",
                    content="",
                    model=model,
                    error=f"Validation failed: {e}"
                )
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "gemini-2.5-pro", action: str = "generate_workout_result") -> AIResponse:
        """Send prompt to Google Gemini"""
        if not self.client:
            return AIResponse(
                provider="Gemini",
                content="",
                model=model,
                error="Gemini client not initialized (missing API key)"
            )
        
        try:
            tool_declaration = await self.get_tool(action)
            if not tool_declaration:
                return AIResponse(
                    provider="Gemini",
                    content="",
                    model=model,
                    error="Tool not found"
                )
            
            message_data = await self.get_messages(action, messages)
            contents = message_data["contents"]
            system_prompt = message_data["system_prompt"]
            
            tools = types.Tool(function_declarations=[tool_declaration])
            
            config = types.GenerateContentConfig(
                system_instruction=system_prompt, 
                tools=[tools],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode='ANY')
                ),
                temperature=0.1,  # Lower temperature for more consistent, complete responses
                top_p=0.8,       # Slightly constrained sampling for better structure
                max_output_tokens=60000 
            )
           
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            
            tokens_used = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens_used = response.usage_metadata.total_token_count
            
            if not response.candidates or not response.candidates[0].content.parts:
                return AIResponse(
                    provider="Gemini",
                    content="",
                    model=model,
                    error="LLM returned an empty response.",
                    tokens_used=tokens_used
                )
            
            finish_reason = response.candidates[0].finish_reason
            print(f"Model finished with reason: {finish_reason}")

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    if function_call.name == tool_declaration.name:
                        return await self.validate_response(function_call, action, model, tokens_used)
                    else:
                        return AIResponse(
                            provider="Gemini",
                            content="",
                            model=model,
                            error=f"LLM responded with an unexpected function: {function_call.name}",
                            tokens_used=tokens_used
                        )
            
            content_text = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    content_text += part.text
            
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
                        provider="Gemini",
                        content=workout_result.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
                elif action == "judge_response":
                    judge_response = JudgeResponse.model_validate(parsed_data)
                    print("Data validation successful! (from message content)")
                    return AIResponse(
                        provider="Gemini",
                        content=judge_response.model_dump_json(),
                        model=model,
                        tokens_used=tokens_used if tokens_used else None
                    )
                
            
            error_content = str(response.candidates[0].content.parts)
            return AIResponse(
                provider="Gemini",
                content="",
                model=model,
                error=f"LLM did not call the required function. Response: {error_content}",
                tokens_used=tokens_used
            )
        
        except Exception as e:
            return AIResponse(
                provider="Gemini",
                content="",
                model=model,
                error=str(e)
            )
    
