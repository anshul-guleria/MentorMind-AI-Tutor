from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base
import uuid

class UserPDF(Base):
    __tablename__ = "user_pdfs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=True) # Optional: if you store file in S3/Local
    pinecone_namespace = Column(String, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())