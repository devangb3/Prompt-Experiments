from pydantic import BaseModel, Field
from typing import List
from .FeedbackTile import FeedbackTile

class Skill(BaseModel):
    skill_name: str
    score_explanation: str
    strength_spotlights:List[FeedbackTile]
    wisdom_whispers:List[FeedbackTile]
    sub_skills:List['Skill'] = Field(default_factory=list)



    model_config = {
        "arbitrary_types_allowed": True
    }