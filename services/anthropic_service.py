"""
Anthropic service implementation
"""

from typing import List
import anthropic
import json
from models.BrainScanResult import BrainScanResult
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
            
            schema_example = '''
            You MUST respond with ONLY a valid JSON object that follows the BrainScanResult schema exactly. Do not include any other text, explanations, or formatting - just the raw JSON:

            BrainScanResult:
                - scan_id: integer
                - accomplishments: List[Accomplishment]
                - categories: List[Category] 
                - reasoning_refinement: List[ReasoningRefinement]

            Where:
            Accomplishment: {title: str, detail: str}
            Category: {title: str, strength_spotlight: List[StrengthSpotlight], wisdom_whispers: List[WisdomWhispers]}
            StrengthSpotlight: {title: str, detail: str, importance: str, what_to_do_next_time: str, questions_to_ask_next_time: str}
            WisdomWhispers: {title: str, detail: str, importance: str, what_to_do_next_time: str, questions_to_ask_next_time: str}
            ReasoningRefinement: {blind_spots: List[str], unclear_assumptions: List[str], logic_issues: List[str], creativity_issues: List[str]}

            Example response:
            {
            "scan_id": 1,
            "accomplishments": [
                {"title": "Project Completion", "detail": "Successfully delivered the Q3 financial report ahead of schedule."},
                {"title": "Team Leadership", "detail": "Guided a cross-functional team to achieve a key milestone."}
            ],
            "categories": [
                {
                "title": "Strategic Planning",
                "strength_spotlight": [
                    {
                    "title": "Clear Vision",
                    "detail": "Demonstrated a strong ability to articulate long-term goals.",
                    "importance": "High: A clear vision provides direction and motivates the team.",
                    "what_to_do_next_time": "Ensure vision is communicated to all stakeholders.",
                    "questions_to_ask_next_time": "How can we better integrate this vision into daily tasks?"
                    }
                ],
                "wisdom_whispers": [
                    {
                    "title": "Over-Reliance on Past Data",
                    "detail": "Tendency to give undue weight to historical data, potentially overlooking new market trends.",
                    "importance": "Medium: Could lead to missed opportunities if not balanced with forward-looking analysis.",
                    "what_to_do_next_time": "Incorporate more predictive analytics and scenario planning.",
                    "questions_to_ask_next_time": "What external factors might invalidate our past assumptions?"
                    }
                ]
                }
            ],
            "reasoning_refinement": [
                {
                "blind_spots": ["Lack of consideration for international market regulations.", "Potential impact of emerging technologies not fully assessed."],
                "unclear_assumptions": ["Assuming user adoption rates will be linear.", "Underestimating competitor's response time."],
                "logic_issues": ["Correlation mistaken for causation in sales figures.", "Inconsistent application of risk assessment criteria."],
                "creativity_issues": ["Relying too heavily on conventional solutions.", "Limited exploration of disruptive business models."]
                }
            ]
            }
            '''
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt + "\n\n" + schema_example,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please analyze this data and provide advice in the exact BrainScanResult JSON format:\n\n{user_msg.content if user_msg else ''}"
                    }
                ]
            )
            
            response_text = response.content[0].text
            
            if not response_text or not response_text.strip():
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error="Empty response from Anthropic API"
                )
            
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            
            try:
                response_data = json.loads(response_text)
                brain_scan_result = BrainScanResult(**response_data)
                validated_content = brain_scan_result.model_dump_json()
            except json.JSONDecodeError as json_error:
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error=f"JSON parsing failed: {str(json_error)}. Raw response: {response_text[:200]}..."
                )
            except Exception as validation_error:
                return AIResponse(
                    provider="Anthropic",
                    content="",
                    model=model,
                    error=f"Model validation failed: {str(validation_error)}. Raw response: {response_text[:200]}..."
                )
            
            return AIResponse(
                provider="Anthropic",
                content=validated_content,
                model=model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )
        
        except Exception as e:
            return AIResponse(
                provider="Anthropic",
                content="",
                model=model,
                error=str(e)
            ) 
