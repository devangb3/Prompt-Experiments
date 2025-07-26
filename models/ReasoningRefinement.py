from pydantic import BaseModel
from typing import List
from .FeedbackTile import FeedbackTile

class ReasoningRefinement(BaseModel):
    
    blind_spots: List[FeedbackTile]

    unclear_assumptions: List[str]

    logic_issues: List[str]

    creativity_issues: List[str]


    model_config = {
        "arbitrary_types_allowed": True
    }