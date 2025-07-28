from pydantic import BaseModel, Field
from typing import List
from .Skill import Skill
from .MomentumMeasure import MomentumMeasure
from .ReasoningRefinement import ReasoningRefinement
from .tiles.MilestoneTile import MilestoneTile
from .WorkoutRound import WorkoutRound

class BrainWorkoutResult(BaseModel):
    accomplishments: List[MilestoneTile] = Field(description="A list of accomplishments that the user has achieved of exactly length 3, accomplishment can be strategy-based (how they went about an answer - e.g. some creative approach to an answer) or content-based (e.g interesting answer content)")

    skills: Skill

    momentum_measure: MomentumMeasure = Field(description="A measure of the user's momentum, based on their last workout whose data is attached in request, within team, and across everything")

    reasoning: ReasoningRefinement

    next_steps: List[MilestoneTile] = Field(description="A list of all next steps from skill feedback and reasoning refinement feedback, find common and merge into one item (title and detail)")

    workout_rounds: List[WorkoutRound]

    model_config = {
        "arbitrary_types_allowed": True
    } 