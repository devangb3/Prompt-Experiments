from pydantic import BaseModel, Field
from typing import List, Optional
from .tiles.FeedbackTile import FeedbackTile

class Skill(BaseModel):
    skill_name: Optional[str] = Field(default=None)
    score_explanation: Optional[str] = Field(default=None)
    strength_spotlights: Optional[List[FeedbackTile]] = Field(default_factory=list, description="A list of Constructive compliments (what the user did that they should keep doing in reference to the skill)")
    wisdom_whispers: Optional[List[FeedbackTile]] = Field(default_factory=list, description="A list of constructive criticism (what the user is doing wrong or not doing at all that they should change)")
    sub_skills: Optional[List['Skill']] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True
    }