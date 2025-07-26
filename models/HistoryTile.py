from pydantic import BaseModel

class HistoryTile(BaseModel):
    title: str
    hasImplemented: bool

    model_config = {
        "arbitrary_types_allowed": True
    }