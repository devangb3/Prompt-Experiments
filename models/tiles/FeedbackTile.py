from pydantic import BaseModel

class FeedbackTile(BaseModel):
    title: str
    detail: str
    importance: str
    next_steps: str
    reflection_question: str
    evidence: str



    model_config = {
        "arbitrary_types_allowed": True
    }