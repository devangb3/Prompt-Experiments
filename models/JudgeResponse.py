from pydantic import BaseModel, Field
from typing import  Optional
from models.tiles.JudgeTile import JudgeTile

class JudgeResponse(BaseModel):
    clarity: Optional[JudgeTile] = Field(
        default=None,
        description="""REQUIRED: Rate the clarity of the feedback on a scale of 1 to 5.
        Clarity refers to how easy the feedback is to understand and whether it leaves any ambiguity.
        """
    )
    specificity: Optional[JudgeTile] = Field(
        default=None,
        description="""REQUIRED: Rate the specificity of the feedback on a scale of 1 to 5.
        Specificity refers to how well the feedback pinpoints exact instances, examples, behaviors, or situations.
        """
    )
    relevance: Optional[JudgeTile] = Field(
        default=None,
        description="""REQUIRED: Rate the relevance of the feedback on a scale of 1 to 5.
        Relevance refers to how closely the feedback relates to the individual's goals, context, activities, and contributions in the workout.
        """
    )
    actionability: Optional[JudgeTile] = Field(
        default=None,
        description="""REQUIRED: Rate the actionability of the feedback on a scale of 1 to 5.
        Actionability refers to how well the feedback provides clear, specific guidance that the user can act upon to improve.
        """
    )
    approachability: Optional[JudgeTile] = Field(
        default=None,
        description="""REQUIRED: Rate the approachability of the feedback on a scale of 1 to 5.
        Approachability refers to the tone and framing of the feedback, making it feel supportive, constructive, and motivating rather than discouraging or judgmental."""
    )

    model_config = {
        "arbitrary_types_allowed": True
    } 