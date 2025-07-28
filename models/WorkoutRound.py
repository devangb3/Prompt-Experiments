from pydantic import BaseModel, Field
from .Skill import Skill
class WorkoutRound(BaseModel):
    round_number: int
    skill: Skill = Field(description="Neural power skill")
    
    model_config = {
        "arbitrary_types_allowed": True
    }