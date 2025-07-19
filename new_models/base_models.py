from pydantic import BaseModel
from typing import List

class Accomplishment(BaseModel):
    title: str  # phrase, 7 words max
    body: str

class HistoryItem(BaseModel):
    hasImplemented: bool
    title: str

class History(BaseModel):
    lastScan: List[HistoryItem]  # length: 1-5
    team: List[HistoryItem]  # length: 1-5
    overall: List[HistoryItem]  # length: 1-5

class ReasoningItem(BaseModel):
    title: str  # phrase, 7 words max
    evidence: str
    impact: str
    next: str
    questions: str

class Reasoning(BaseModel):
    perspectives: List[ReasoningItem]  # length: 1-3
    assumptions: List[ReasoningItem]
    logic: List[ReasoningItem]
    creativity: List[ReasoningItem]

class NextStepItem(BaseModel):
    title: str  # phrase, 7 words max
    body: str

class NextSteps(BaseModel):
    comp: List[NextStepItem]  # length: 5-10
    crit: List[NextStepItem] 