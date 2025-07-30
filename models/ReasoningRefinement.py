from pydantic import BaseModel, Field
from typing import List, Optional
from .tiles.FeedbackTile import FeedbackTile

class ReasoningRefinement(BaseModel):
    
    blind_spots: Optional[List[FeedbackTile]] = Field(default_factory=list, description="""List of FeedbackTiles - phrased as critiques not compliments-
                                            perspectives missing from user's answers that ought to have included""")

    unclear_assumptions: Optional[List[str]] = Field(default_factory=list, description="""List of 1-2 sentence long strs-
                                           assumptions that user's answers rely on that are unclear/vague or factually wrong
                                            or not always correct""")

    logic_issues: Optional[List[str]] = Field(default_factory=list, description="""List of 1-2 sentence long strs-
                                    logic flaws in answers (stuff like missing/unclear/irrelevant evidence, faulty reasoning)""")

    creativity_issues: Optional[List[str]] = Field(default_factory=list, description="""List of 1-2 sentence long strs-
                                         lack of risk taking in your answers (where your answers lacked original/unique thinking)""")

    model_config = {
        "arbitrary_types_allowed": True
    }