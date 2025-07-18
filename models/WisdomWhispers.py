from pydantic import BaseModel

class WisdomWhispers(BaseModel):
    title: str
    detail: str
    importance: str
    what_to_do_next_time: str
    questions_to_ask_next_time: str

    model_config = {
        "arbitrary_types_allowed": True
    }