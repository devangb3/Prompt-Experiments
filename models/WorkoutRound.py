from pydantic import BaseModel
from .Skill import Skill
class WorkoutRound(BaseModel):
    round_number: int
    skill: Skill
    
    model_config = {
        "arbitrary_types_allowed": True
    }