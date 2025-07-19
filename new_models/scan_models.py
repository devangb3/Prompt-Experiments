from pydantic import BaseModel
from typing import List
from .score_models import ScoreNumbers, Theme, Feedback

class RoundScore(BaseModel):
    id: int  # construct id
    icon: str  # tabler svg code for icon
    title: str = "Neural Power"  # construct title, default: Neural Power
    num: ScoreNumbers
    theme: Theme
    explanation: str  # explanation for score

class RoundScores(BaseModel):
    c0: RoundScore  # central construct

class ScanRound(BaseModel):
    hasScore: bool  # some rounds may not show score
    hasFeedback: bool  # some rounds may not show feedback
    scores: RoundScores
    feedback: Feedback  # feedback across all constructs

class Scan(BaseModel):
    rounds: List[ScanRound]  # arbitrarily long (1 per round) 