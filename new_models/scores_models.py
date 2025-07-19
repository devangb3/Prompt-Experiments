from pydantic import BaseModel
from .construct_models import Construct

class Scores(BaseModel):
    c0: Construct