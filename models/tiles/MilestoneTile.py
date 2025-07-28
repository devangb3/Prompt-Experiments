from pydantic import BaseModel, Field

class MilestoneTile(BaseModel):
    title: str = Field(description="A short phrase no more than 3-4 words")
    detail: str = Field(description="A 1-2 sentence long summary and be be specific to moment when the accomplishment was achieved")
    

    model_config = {
        "arbitrary_types_allowed": True
    }