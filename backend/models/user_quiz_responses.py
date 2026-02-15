from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base
import uuid

class UserQuizResponse(Base):
    __tablename__ = "user_quiz_responses"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    
    # Store which option number (1,2,3,4) the user picked
    selected_option = Column(Integer, nullable=False)
    
    # Whether it was right or wrong
    is_correct = Column(Boolean, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())