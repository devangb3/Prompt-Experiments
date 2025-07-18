from pydantic import BaseModel

class ReasoningRefinement(BaseModel):
    blind_spots: list[str]
    unclear_assumptions: list[str]
    logic_issues: list[str]
    creativity_issues: list[str]

    model_config = {
        "arbitrary_types_allowed": True
    }