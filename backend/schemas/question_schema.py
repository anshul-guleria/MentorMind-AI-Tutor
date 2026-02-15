from pydantic import BaseModel

class Question(BaseModel):
    id: str
    quiz_id: str
    question_number: str
    question_text: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_option: int
    difficulty: str