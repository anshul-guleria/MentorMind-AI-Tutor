from typing import List
from pydantic import BaseModel


class Quiz(BaseModel):
    id: str
    user_id: str
    response_id: str
    question_ids: List[str]
    topic: str

