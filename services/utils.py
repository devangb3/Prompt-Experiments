"""
Utility functions for AI services
"""

from .types import AIResponse
from logging_config import get_logger

logger = get_logger("services.utils")


def print_response(response: AIResponse):
    """Pretty print an AI response"""
    logger.info("=" * 50)
    logger.info(f"Provider: {response.provider}")
    logger.info(f"Model: {response.model}")
    if response.tokens_used:
        logger.info(f"Tokens Used: {response.tokens_used}")
    if response.error:
        logger.error(f"Error: {response.error}")
    else:
        logger.info("Response:")
        logger.info(response.content)
    logger.info("=" * 50)


def print_responses(responses: list[AIResponse]):
    """Print multiple AI responses"""
    for response in responses:
        print_response(response) 