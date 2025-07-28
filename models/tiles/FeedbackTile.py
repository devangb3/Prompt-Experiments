from pydantic import BaseModel, Field

class FeedbackTile(BaseModel):
    title: str = Field(description="Few words long summarizing the feedback")
    detail: str = Field(description="An explanation of the action item")
    importance: str = Field(description="What are the importance of doing(for strength spotlights) and not doing(for wisdom whispers) this action item")
    next_steps: str = Field(description="What specifically they should keep doing(for strength spotlights) or change(for wisdom whispers)")
    reflection_question: str = Field(description="In the next scan, what questions should they ask themseleves as they answer in order to continue doing the thing(for strength spotlights) or implement the change in their work(for wisdom whispers) (e.g. In the next scan, ask yourself 'is this enough explanation' as you answer).")
    evidence: str = Field(description="Quote specific answers (phrases/sentences/etc) in the round where they demonstrate this action")



    model_config = {
        "arbitrary_types_allowed": True
    }