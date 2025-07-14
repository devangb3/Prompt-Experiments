"""
Utility functions for AI services
"""

from .types import AIResponse


def print_response(response: AIResponse):
    """Pretty print an AI response"""
    print(f"\n{'='*50}")
    print(f"Provider: {response.provider}")
    print(f"Model: {response.model}")
    if response.tokens_used:
        print(f"Tokens Used: {response.tokens_used}")
    if response.error:
        print(f"Error: {response.error}")
    else:
        print(f"Response:")
        print(response.content)
    print(f"{'='*50}")


def print_responses(responses: list[AIResponse]):
    """Print multiple AI responses"""
    for response in responses:
        print_response(response) 