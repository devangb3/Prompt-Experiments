from pydantic import BaseModel, Field

class HistoryTile(BaseModel):
    title: str
    hasImplemented: bool = Field(description="Check the if this piece of feedback(mentioned in title) has been implemented in this workout. if (to a reasonable degree) it has, true. else, false. Use the titles, detail, next steps subsections of the previous feedback to determine")

    model_config = {
        "arbitrary_types_allowed": True
    }