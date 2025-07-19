from pydantic import BaseModel
from typing import List, Optional, Union
from typing_extensions import Literal
from .score_models import ScoreNumbers, Theme, Feedback

class SubConstruct(BaseModel):
    icon: str  # tabler svg code for icon
    title: str  # construct title
    num: ScoreNumbers
    theme: Theme
    explanation: str  # explanation for score
    feedback: Feedback
    subConstructs: List['SubConstruct'] = []  # likely empty for deepest level

class Construct(BaseModel):
    id: int  # construct id
    icon: str  # tabler svg code for icon
    title: str = "Neural Power"  # construct title, default: Neural Power
    num: ScoreNumbers
    theme: Theme
    explanation: str  # explanation for score
    feedback: Feedback
    subConstructs: List[SubConstruct]  # likely length == 3

# Update forward references
SubConstruct.model_rebuild()
Construct.model_rebuild() 