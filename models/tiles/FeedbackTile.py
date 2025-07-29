from pydantic import BaseModel, Field
from typing import Optional

class FeedbackTile(BaseModel):
    title: Optional[str] = Field(default=None, description="Few words long summarizing the feedback")
    detail: Optional[str] = Field(default=None, description="An explanation of the action item")
    importance: Optional[str] = Field(default=None, description="What are the importance of doing(for strength spotlights) and not doing(for wisdom whispers) this action item")
    next_steps: Optional[str] = Field(default=None, description="What specifically they should keep doing(for strength spotlights) or change(for wisdom whispers)")
    reflection_question: Optional[str] = Field(default=None, description="In the next scan, what questions should they ask themseleves as they answer in order to continue doing the thing(for strength spotlights) or implement the change in their work(for wisdom whispers) (e.g. In the next scan, ask yourself 'is this enough explanation' as you answer).")
    evidence: Optional[str] = Field(default=None, description="Quote specific answers (phrases/sentences/etc) in the round where they demonstrate this action")

    model_config = {
        "arbitrary_types_allowed": True
    }