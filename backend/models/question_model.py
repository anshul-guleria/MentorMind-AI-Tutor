from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True)

    quiz_id = Column(String, ForeignKey("quizzes.id"))

    question_number = Column(String, nullable=False)
    
    question_text = Column(Text, nullable=False)

    option_1 = Column(String, nullable=False)
    option_2 = Column(String, nullable=False)
    option_3 = Column(String, nullable=False)
    option_4 = Column(String, nullable=False)

    correct_option = Column(Integer, nullable=False)

    difficulty = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())