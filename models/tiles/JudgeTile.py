from pydantic import BaseModel, Field
from typing import Optional

class JudgeTile(BaseModel):
    score: Optional[int] = Field(
        default=None,
        description="The score of the judge tile ranging from 1 to 5 where 1 is very low and 5 is very high."
    )
    reason: Optional[str] = Field(
        default=None,
        description="One line reason for giving the score."
    )
