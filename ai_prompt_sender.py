#!/usr/bin/env python3
"""
AI Prompt Sender - Send prompts to multiple AI providers
Supports: OpenAI, Anthropic (Claude), Google Gemini, and Perplexity
With database integration (MongoDB or Xano) for conversation storage
"""

import asyncio
import time
from dotenv import load_dotenv
import json
import aiofiles
from prompt_creator import PromptCreator
from services import AIServiceFactory, Provider, PromptMessage, print_response, print_responses
from database.service_factory import get_database_service
from database.connection import close_database
from services.judge_service import JudgeService
from logging_config import get_logger
from services.types import AIResponse

load_dotenv()

logger = get_logger("ai_prompt_sender")


class AIPromptSender:
    """Main class for sending prompts to AI providers with database integration"""
    
    def __init__(self, enable_database: bool = True):
        """Initialize with the service factory"""
        self.factory = AIServiceFactory()
        self.enable_database = enable_database
        self.db_service = get_database_service() if enable_database else None
        logger.info(f"Initialized AIPromptSender with database enabled: {enable_database}")
    
    async def send_to_provider(self, provider: Provider, messages: list[PromptMessage], model: str = None, action: str = None):
        """Send prompt to a specific provider"""
        logger.info(f"Sending prompt to provider: {provider.value}")
        if model:
            logger.debug(f"Using model: {model}")
        if action:
            logger.debug(f"Action: {action}")
        
        start_time = time.time()
        response = await self.factory.send_to_provider(provider, messages, model, action)
        response_time = time.time() - start_time
        
        logger.info(f"Response received from {provider.value} in {response_time:.2f}s")
        
        return response
    
    async def save_to_database(self, provider: Provider, messages: list[PromptMessage], responses: list[AIResponse] | AIResponse, rating: AIResponse | None, response_time: float):
        """Save a conversation with ratings as a separate field."""
        if not (self.enable_database and self.db_service):
            return
        try:
            response_list: list[AIResponse] = responses if isinstance(responses, list) else [responses]
            
            rating_data = None
            if rating:
                try:
                    # Parse judge response JSON
                    parsed = json.loads(rating.content) if isinstance(rating.content, str) else rating.content
                    if isinstance(parsed, dict):
                        categories = ["clarity", "specificity", "relevance", "actionability", "approachability"]
                        rating_data = {
                            "provider_ratings": {
                                provider.value: {
                                    "score": 0.0,  # Will be calculated as average
                                    "categories": {},
                                    "overall_reason": ""
                                }
                            }
                        }
                        
                        total_score = 0
                        reasons = []
                        for key in categories:
                            tile = parsed.get(key)
                            if isinstance(tile, dict):
                                score = float(tile.get("score", 0))
                                reason = tile.get("reason", "").strip()
                                rating_data["provider_ratings"][provider.value]["categories"][key] = {
                                    "score": score,
                                    "reason": reason
                                }
                                total_score += score
                                if reason:
                                    reasons.append(f"{key}: {reason}")
                        
                        if categories:
                            rating_data["provider_ratings"][provider.value]["score"] = total_score / len(categories)
                        
                        if reasons:
                            rating_data["provider_ratings"][provider.value]["overall_reason"] = " | ".join(reasons)[:2000]
                except Exception as e:
                    logger.error(f"Failed to parse rating data: {e}")
                    rating_data = None
            
            await self.db_service.save_conversation(
                messages=messages,
                responses=response_list,
                response_times={provider.value: response_time},
                ratings=rating_data
            )
            logger.debug(f"Conversation saved to database for provider: {provider.value}")
        except Exception as e:
            logger.error(f"Failed to save conversation to database: {e}")

    async def send_to_all(self, messages: list[PromptMessage], models: dict = None):
        """Send prompt to all available providers"""
        logger.info("Sending prompt to all available providers")
        if models:
            logger.debug(f"Using custom models: {models}")
        
        start_time = time.time()
        responses = await self.factory.send_to_all(messages, models)
        total_time = time.time() - start_time
        
        logger.info(f"Received responses from {len(responses)} providers in {total_time:.2f}s")
                 
        return responses
    
    def get_available_services(self):
        """Get list of available services"""
        services = self.factory.get_available_services()
        logger.debug(f"Available services: {services}")
        return services
    
    async def get_conversation_history(self, limit: int = 10):
        """Get recent conversation history"""
        if self.db_service:
            conversations = await self.db_service.get_all_conversations(limit=limit)
            logger.debug(f"Retrieved {len(conversations)} conversations from history")
            return conversations
        logger.warning("Database service not available for conversation history")
        return []
    
    async def search_conversations(self, query: str, limit: int = 20):
        """Search conversations by content"""
        if self.db_service:
            conversations = await self.db_service.search_conversations(query, limit=limit)
            logger.debug(f"Found {len(conversations)} conversations matching query: {query}")
            return conversations
        logger.warning("Database service not available for conversation search")
        return []
    
    async def get_conversation_by_id(self, conversation_id: str):
        """Get a specific conversation by ID"""
        if self.db_service:
            conversation = await self.db_service.get_conversation(conversation_id)
            if conversation:
                logger.debug(f"Retrieved conversation: {conversation_id}")
            else:
                logger.warning(f"Conversation not found: {conversation_id}")
            return conversation
        logger.warning("Database service not available for conversation retrieval")
        return None
    
    async def get_statistics(self):
        """Get database statistics"""
        if self.db_service:
            stats = await self.db_service.get_statistics()
            logger.debug(f"Database statistics: {stats}")
            return stats
        logger.warning("Database service not available for statistics")
        return {"total_conversations": 0, "total_responses": 0, "provider_stats": {}}
    
    async def close(self):
        """Close database connections"""
        logger.info("Closing database connections")
        await close_database()


async def main():
    """Example usage of the AI Prompt Sender with configurable database integration"""
    logger.info("Starting AI Prompt Sender with Database Integration")
    logger.info("=" * 50)
    
    sender = AIPromptSender()
    
    # Show database configuration
    from database.connection import get_connection_info
    db_info = get_connection_info()
    logger.info(f"Database Provider: {db_info['provider']}")
    if db_info['provider'] == 'MongoDB':
        logger.info(f"MongoDB URI: {db_info['uri']}")
        logger.info(f"Database: {db_info['database']}")
    else:
        logger.info(f"Xano Base URL: {db_info['base_url']}")
        logger.info(f"Has API Token: {db_info['has_token']}")
    
    prompt_template = """
                    {LLM_FRAMING_1}

                    {LLM_ANALYTICAL_TASK_1}:
                    {BRAIN_DATA_SAMPLE}

                    Based on the data and the following context, please perform the requested analysis.

                    User Context:
                    {USER_CONTEXT_1}

                    Exercise Context:
                    {EXERCISE_CONTEXT_1}

                    Analysis Task:
                    {LLM_ANALYTICAL_TASK_2}

                    Required output structure:
                    {OUTPUT_STRUCTURE_2}
                """
    
    prompt_creator = PromptCreator(
        prompt_template=prompt_template
    )
    system_prompt = prompt_creator.create_prompt()
    logger.debug("Prompt template created successfully")
    
    async with aiofiles.open("test_data/filledScanCollection.json", mode="r") as f:
        dummy_ui_request = json.loads(await f.read())
        logger.debug("Loaded test data from filledScanCollection.json")

    messages = [
        PromptMessage(role="system", content="""
        You are an expert assistant. Your ONLY task is to generate a valid BrainWorkoutResult JSON object.
        STRICT INSTRUCTIONS:
        - You MUST return a single, fully filled JSON object that strictly matches the provided schema.
        - Do NOT include any extra text, comments, or explanations.
        - Every field must be present and filled according to its description and required tone.
        - If you are unsure about a value, make a reasonable guess, but do not leave any field empty or null.
        - Your response will be parsed as JSON. Any deviation from the schema or extra output will be considered a failure.
        - Double-check your output for completeness and validity before submitting.
        """),
        PromptMessage(role="user", content="STRICT INSTRUCTIONS: Output ONLY a valid BrainWorkoutResult JSON object. Do NOT include any extra text or formatting. All fields must be present and filled. Your response will be parsed as JSON.\n" + json.dumps(dummy_ui_request))
    ]
    
    start_time = time.time()
    response = await sender.factory.send_to_provider(Provider.GEMINI, messages, None, "generate_workout_result")
    response_time = time.time() - start_time
    print_response(response)
    
    logger.info("Judging responses...")
    judge = JudgeService()
    judged_response = await judge.judge_response(Provider.GEMINI, response.content, dummy_ui_request)
    print_response(judged_response)

    await sender.save_to_database(Provider.GEMINI, messages, response, judged_response, response_time)
    
    await sender.close()
    logger.info("AI Prompt Sender completed successfully")


if __name__ == "__main__":
    logger.info("AI Prompt Sender")
    logger.info("=============================")
    logger.info("=" * 50)
    
    asyncio.run(main()) 