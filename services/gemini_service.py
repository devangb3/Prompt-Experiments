"""
Google Gemini service implementation
"""

from typing import List
from google import genai
from google.genai import types

from .base_service import BaseAIService
from .types import PromptMessage, AIResponse


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
            
            response = self.client.models.generate_content(
                model=f"models/{model}",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            )
            
            return AIResponse(
                provider="Gemini",
                content=response.candidates[0].content.parts[0].text,
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