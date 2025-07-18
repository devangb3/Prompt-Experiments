from pydantic import BaseModel

class Accomplishment(BaseModel):
    title: str
    detail: str

    model_config = {
        "arbitrary_types_allowed": True
    }