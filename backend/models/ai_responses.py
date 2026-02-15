from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base


class AIResponse(Base): 
    __tablename__ = "ai_responses"

    id = Column(String, primary_key=True, index=True)

    user_id = Column(String, ForeignKey("users.id"))

    quiz_id = Column(String, ForeignKey("quizzes.id"))

    user_question= Column(String, nullable=False)

    topic = Column(String, nullable=False)

    answer_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())