from pydantic import BaseModel
from typing import List, Optional, Union
from typing_extensions import Literal

class ColorTheme(BaseModel):
    text: str  
    highlight: str  
    contrast: str  

class Theme(BaseModel):
    color: ColorTheme

class ScoreNumbers(BaseModel):
    low: Optional[float] = None  # lower limit raw score
    mid: float  # most likely raw score
    high: Optional[float] = None  # upper limit raw score

class FeedbackTile(BaseModel):
    id: str  # comp/crit id encrypted
    title: str  # comp/crit title
    num: float  # comp/crit freq num
    what: str  # comp/crit what/where detail
    why: str  # comp/crit importance
    action: str  # what to do in life
    que: str  # questions to ask in life

class FeedbackSection(BaseModel):
    tiles: List[FeedbackTile]  # length: 1-3

class Feedback(BaseModel):
    compliments: FeedbackSection
    criticisms: FeedbackSection 