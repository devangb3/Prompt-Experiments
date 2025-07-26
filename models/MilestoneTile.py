from pydantic import BaseModel

class MilestoneTile(BaseModel):
    title: str
    detail: str
    

    model_config = {
        "arbitrary_types_allowed": True
    }