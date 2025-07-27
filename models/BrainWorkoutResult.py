from pydantic import BaseModel
from typing import List
from .Skill import Skill
from .MomentumMeasure import MomentumMeasure
from .ReasoningRefinement import ReasoningRefinement
from .tiles.MilestoneTile import MilestoneTile
from .WorkoutRound import WorkoutRound

class BrainWorkoutResult(BaseModel):
    accomplishments: List[MilestoneTile] 

    skills: Skill

    momentum_measure: MomentumMeasure

    reasoning: ReasoningRefinement

    next_steps: List[MilestoneTile]

    workout_rounds: List[WorkoutRound]

    model_config = {
        "arbitrary_types_allowed": True
    } 