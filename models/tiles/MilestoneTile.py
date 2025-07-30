from pydantic import BaseModel, Field
from typing import Optional

class MilestoneTile(BaseModel):
    title: Optional[str] = Field(default=None, description="A short phrase no more than 3-4 words")
    detail: Optional[str] = Field(default=None, description="A 1-2 sentence long summary and be be specific to moment when the accomplishment was achieved")
    
    model_config = {
        "arbitrary_types_allowed": True
    }