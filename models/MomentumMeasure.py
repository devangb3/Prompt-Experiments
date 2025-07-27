from pydantic import BaseModel
from typing import List
from .tiles.HistoryTile import HistoryTile

class MomentumMeasure(BaseModel):
    last_workout : List[HistoryTile]
    
    within_team : List[HistoryTile]

    accross_everything : List[HistoryTile]



    model_config = {
        "arbitrary_types_allowed": True
    }