from pydantic import BaseModel, Field
from typing import List, Optional
from .tiles.HistoryTile import HistoryTile

class MomentumMeasure(BaseModel):
    last_workout: Optional[List[HistoryTile]] = Field(default_factory=list, description="""Use titles of strength spotlight and constructive criticisms for 'neural power' 
                                             from last workout""")
    
    within_team: Optional[List[HistoryTile]] = Field(default_factory=list, description="""Use titles of strength spotlight and constructive criticisms for feedback 
                                            from across all workouts in this team""")

    accross_everything: Optional[List[HistoryTile]] = Field(default_factory=list, description="""Use titles of strength spotlight and constructive criticisms 
                                                   for feedback from across all workouts in all teams""")

    model_config = {
        "arbitrary_types_allowed": True
    }