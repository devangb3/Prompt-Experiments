from pydantic import BaseModel
from typing import List
from .base_models import Accomplishment, History, Reasoning, NextSteps
from .scores_models import Scores
from .scan_models import Scan

class BrainScanResult(BaseModel):
    # scan accomplishments
    accomplishments: List[Accomplishment]  # length always 3

    # scan momentum
    history: History

    # reasoning feedback for scan
    reasoning: Reasoning

    # next steps for scan
    next: NextSteps

    # scores w/ feedback for each construct/skill (across scan)
    scores: Scores

    # round feedback/scores (not including scan result data)
    scan: Scan

    model_config = {
        "arbitrary_types_allowed": True
    } 