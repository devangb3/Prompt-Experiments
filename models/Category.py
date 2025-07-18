from pydantic import BaseModel
from typing import List
from models.StrengthSpotlight import StrengthSpotlight
from models.WisdomWhispers import WisdomWhispers

class Category(BaseModel):
    title: str
    strength_spotlight: List[StrengthSpotlight]
    wisdom_whispers: List[WisdomWhispers]

    model_config = {
        "arbitrary_types_allowed": True
    }