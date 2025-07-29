"""
Google Gemini service implementation
"""

from typing import List, Optional
from google import genai
from google.genai import types
from pydantic import ValidationError, BaseModel
from models.BrainWorkoutResult import BrainWorkoutResult
from .base_service import BaseAIService
from .types import PromptMessage, AIResponse


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
    
    async def send_prompt(self, messages: List[PromptMessage], model: str = "gemini-2.5-flash") -> AIResponse:
        """Send prompt to Google Gemini"""
        if not self.client:
            return AIResponse(
                provider="Gemini",
                content="",
                model=model,
                error="Gemini client not initialized (missing API key)"
            )
        
        try:
            
            contents = []
            system_prompt = ""
            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                elif msg.role == "user":
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part(text=msg.content)]
                    ))
            
           
            schema = get_flattened_schema(BrainWorkoutResult)
            
            save_workout_tool = types.FunctionDeclaration(
                name="save_brain_workout_result",
                description="Saves the complete analysis of a brain workout session.",
                parameters=schema
            )

            tools = types.Tool(function_declarations=[save_workout_tool])
            config = types.GenerateContentConfig(
                system_instruction=system_prompt, 
                tools=[tools],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode='ANY')
                ))
           
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=contents,
                config=config,
            )

            function_call = response.candidates[0].content.parts[0].function_call
            tool_args = function_call.args
            
            if function_call.name == "save_brain_workout_result":
                print("✅ LLM responded with the correct tool. Validating data...")
                workout_result = BrainWorkoutResult.model_validate(tool_args)
                print("✅ Data validation successful!")
            else:
                print(f"❌ Error: LLM responded with an unexpected tool: {function_call.name}")
                return AIResponse(
                    provider="Gemini",
                    content="",
                    model=model,
                    error=f"LLM responded with an unexpected tool: {function_call.name}"
                )
            
            return AIResponse(
                provider="Gemini",
                content=workout_result.model_dump_json(),
                model=model,
                tokens_used=None
            )
        
        except Exception as e:
            return AIResponse(
                provider="Gemini",
                content="",
                model=model,
                error=str(e)
            )
    
