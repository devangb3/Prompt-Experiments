from pydantic import BaseModel
from typing import List
from models.Accomplishment import Accomplishment
from models.Category import Category
from models.ReasoningRefinements import ReasoningRefinement

class BrainScanResult(BaseModel):
    scan_id: int
    accomplishments: List[Accomplishment]
    categories: List[Category]
    reasoning_refinement: List[ReasoningRefinement]

    model_config = {
        "arbitrary_types_allowed": True
    }
