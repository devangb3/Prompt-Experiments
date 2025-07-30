from pydantic import BaseModel, Field
from typing import List, Optional
from .Skill import Skill
from .MomentumMeasure import MomentumMeasure
from .ReasoningRefinement import ReasoningRefinement
from .tiles.MilestoneTile import MilestoneTile
from .WorkoutRound import WorkoutRound

class BrainWorkoutResult(BaseModel):
    accomplishments: Optional[List[MilestoneTile]] = Field(default_factory=list, description="""A list of accomplishments that the user has achieved of exactly length 3,
                                                    accomplishment can be strategy-based (how they went about an answer - 
                                                    e.g. some creative approach to an answer) or content-based 
                                                    (e.g interesting answer content)""")

    skills: Optional[Skill] = Field(default=None, description="""
                    Primary Goal: Generate a complete, 3-level hierarchical skill assessment.
                    Make sure to fill out the subfields of each non-leaf node
                    1. Use this exact structure:
                    Your output must follow this nested tree structure for the `skills` field.
                    - Level 1 (Root): Neural Power
                        - Level 2: Critical Reasoning
                            - Level 3: Information Understanding
                            - Level 3: Argument Understanding
                            - Level 3: Argument Creation
                        - Level 2: Decision Making
                            - Level 3: Decision Goal Setting
                            - Level 3: Decision Comparison
                        - Level 2: Communication
                            - Level 3: Intent Matching
                            - Level 3: Clarity

                    2. Follow this summarization rule:
                    For each parent skill (e.g., "Critical Reasoning"), its `score_explanation` and feedback must be a concise summary derived from the assessments of its direct children (e.g., "Information Understanding," "Argument Understanding," etc.). The ultimate root, "Neural Power," should be a summary of its three children.
                    """)

    momentum_measure: Optional[MomentumMeasure] = Field(default=None, description="""A measure of the user's momentum,
                                               based on their last workout whose data is attached in request, 
                                                within team, and across everything""")

    reasoning: Optional[ReasoningRefinement] = Field(default=None)

    next_steps: Optional[List[MilestoneTile]] = Field(default_factory=list, description="""A list of all next steps from skill feedback and reasoning refinement feedback,
                                                            find common and merge into one item (title and detail)""")

    workout_rounds: Optional[List[WorkoutRound]] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True
    } 