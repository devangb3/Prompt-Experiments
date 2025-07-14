"""
Shared types and data structures for AI services
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Provider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"


@dataclass
class PromptMessage:
    role: str
    content: str


@dataclass
class AIResponse:
    provider: str
    content: str
    model: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None 