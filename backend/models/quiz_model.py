from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base


class QuizModel(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True)

    topic = Column(String, nullable=False)

    created_by = Column(String, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
