from pydantic import BaseModel, Field
from typing import List
from .tiles.FeedbackTile import FeedbackTile

class Skill(BaseModel):
    skill_name: str
    score_explanation: str
    strength_spotlights:List[FeedbackTile] = Field(description="A list of Constructive compliments (what the user did that they should keep doing in reference to the skill)")
    wisdom_whispers:List[FeedbackTile] = Field(description="A list of constructive criticism (what the user is doing wrong or not doing at all that they should change)")
    sub_skills:List['Skill'] = Field(default_factory=list)



    model_config = {
        "arbitrary_types_allowed": True
    }