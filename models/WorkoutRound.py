from pydantic import BaseModel, Field
from typing import Optional
from .Skill import Skill

class WorkoutRound(BaseModel):
    round_number: Optional[int] = Field(default=None)
    skill: Optional[Skill] = Field(default=None, description="Neural power skill")
    
    model_config = {
        "arbitrary_types_allowed": True
    }