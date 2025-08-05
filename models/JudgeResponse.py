from pydantic import BaseModel, Field
from typing import List, Optional


class JudgeResponse(BaseModel):
    clarity: Optional[int] = Field(
        default=None,
        description="""REQUIRED: Rate the clarity of the feedback on a scale of 1 to 5.

        Clarity refers to how easy the feedback is to understand and whether it leaves any ambiguity.

        RATING SCALE:
        1 - Very Low: Feedback is confusing, vague, or uses unclear language. It is very difficult to understand the intended message.
        2 - Low: Feedback is somewhat unclear. The main points are obscured by jargon, poor structure, or ambiguous phrasing.
        3 - Medium: Feedback is generally understandable, but some parts may require re-reading or interpretation. It is mostly clear but could be more direct.
        4 - High: Feedback is clear, well-structured, and uses precise language. The message is easy to understand with minimal effort.
        5 - Very High: Feedback is exceptionally clear, direct, and unambiguous. The language is simple and precise, leaving no room for misinterpretation."""
    )
    specificity: Optional[int] = Field(
        default=None,
        description="""REQUIRED: Rate the specificity of the feedback on a scale of 1 to 5.

        Specificity refers to how well the feedback pinpoints exact instances, examples, behaviors, or situations.

        RATING SCALE:
        1 - Very Low: Feedback is highly generic and lacks any concrete examples. It consists of broad, vague statements (e.g., "Good job").
        2 - Low: Feedback makes general points but provides no specific examples or evidence from the user's work.
        3 - Medium: Feedback refers to general areas but provides only limited, non-specific examples. It hints at specific behaviors but doesn't detail them.
        4 - High: Feedback includes specific examples and references concrete behaviors or statements from the user's work. It clearly links the assessment to observable actions.
        5 - Very High: Feedback is deeply specific, quoting exact phrases or pointing to precise moments. It provides rich, detailed examples that perfectly illustrate the point being made."""
    )
    relevance: Optional[int] = Field(
        default=None,
        description="""REQUIRED: Rate the relevance of the feedback on a scale of 1 to 5.

        Relevance refers to how closely the feedback relates to the individual's goals, context, activities, and contributions in the workout.

        RATING SCALE:
        1 - Very Low: Feedback is completely disconnected from the user's performance, goals, or the workout's context. It seems generic or misapplied.
        2 - Low: Feedback has a weak connection to the user's activities. It touches on tangential points but misses the core issues.
        3 - Medium: Feedback is generally relevant to the workout but may not align perfectly with the user's specific performance or development needs.
        4 - High: Feedback is clearly relevant and directly connected to the user's actions, responses, and the stated goals of the workout.
        5 - Very High: Feedback is perfectly tailored to the user's context, addressing their most critical development areas and performance moments with exceptional precision."""
    )
    actionability: Optional[int] = Field(
        default=None,
        description="""REQUIRED: Rate the actionability of the feedback on a scale of 1 to 5.

        Actionability refers to how well the feedback provides clear, specific guidance that the user can act upon to improve.

        RATING SCALE:
        1 - Very Low: Feedback offers no clear guidance on what to do next. It identifies an issue but gives no suggestions for improvement.
        2 - Low: Feedback offers vague suggestions (e.g., "Be more creative") without explaining how to do so.
        3 - Medium: Feedback provides some direction, but the next steps are not fully concrete or may be difficult to implement without further clarification.
        4 - High: Feedback provides clear, specific, and practical steps the user can take. The guidance is concrete and easy to follow.
        5 - Very High: Feedback provides exceptionally clear, step-by-step guidance, including practical strategies, resources, or reflection questions that make implementation straightforward and effective."""
    )
    approachability: Optional[int] = Field(
        default=None,
        description="""REQUIRED: Rate the approachability of the feedback on a scale of 1 to 5.

        Approachability refers to the tone and framing of the feedback, making it feel supportive, constructive, and motivating rather than discouraging or judgmental.

        RATING SCALE:
        1 - Very Low: Feedback is delivered with a harsh, judgmental, or discouraging tone. It is likely to make the user feel defensive.
        2 - Low: Feedback is blunt or lacks supportive language. While it may be accurate, its delivery may hinder reception.
        3 - Medium: Feedback is neutral in tone. It is neither overly harsh nor particularly supportive. It gets the point across without much finesse.
        4 - High: Feedback is framed constructively and supportively. It uses encouraging language and focuses on growth, making it easy for the user to accept.
        5 - Very High: Feedback is exceptionally approachable. It masterfully balances directness with empathy, inspiring motivation and a genuine desire to improve. The tone is highly supportive and empowering."""
    )

    model_config = {
        "arbitrary_types_allowed": True
    } 