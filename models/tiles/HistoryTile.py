from pydantic import BaseModel, Field
from typing import Optional

class HistoryTile(BaseModel):
    title: Optional[str] = Field(default=None)
    hasImplemented: Optional[bool] = Field(default=None, description="Check the if this piece of feedback(mentioned in title) has been implemented in this workout. if (to a reasonable degree) it has, true. else, false. Use the titles, detail, next steps subsections of the previous feedback to determine")

    model_config = {
        "arbitrary_types_allowed": True
    }