from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from core.security import get_current_user
from models.user_model import User
from models.pdf_model import UserPDF
from services.rag_service import process_pdf, query_rag
import shutil
import os
import uuid
from pydantic import BaseModel

# from services.ollama_service import ask_pdf_tutor
# from services.gemini_service import ask_pdf_tutor
from services.groq_service import ask_pdf_tutor


router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class PDFChatRequest(BaseModel):
    pdf_id: str
    question: str

@router.post("/pdf/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Check if file exists for user 
    existing = db.query(UserPDF).filter(UserPDF.user_id == current_user.id, UserPDF.filename == file.filename).first()
    if existing:
        return {"message": "File already exists", "pdf_id": existing.id}

    # Save locally
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process RAG (Namespace = UserID_FileID to keep unique)
    namespace = f"{current_user.id}_{file_id}"
    try:
        process_pdf(file_path, namespace)
    except Exception as e:
        os.remove(file_path) # Cleanup on failure
        raise HTTPException(500, f"Error processing PDF: {str(e)}")

    # Save to DB
    new_pdf = UserPDF(
        id=file_id,
        user_id=current_user.id,
        filename=file.filename,
        pinecone_namespace=namespace
    )
    db.add(new_pdf)
    db.commit()
    
    return {"message": "PDF processed successfully", "pdf_id": file_id}

@router.get("/pdf/list", status_code=status.HTTP_200_OK)
async def list_pdfs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pdfs = db.query(UserPDF).filter(UserPDF.user_id == current_user.id).all()
    return [{"id": p.id, "filename": p.filename, "created_at": p.created_at} for p in pdfs]

@router.post("/pdf/chat", status_code=status.HTTP_200_OK)
async def chat_pdf(
    req: PDFChatRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    pdf = db.query(UserPDF).filter(UserPDF.id == req.pdf_id, UserPDF.user_id == current_user.id).first()
    if not pdf:
        raise HTTPException(404, "PDF not found")
    
    # Retrieve Context from Pinecone
    context = query_rag(req.question, pdf.pinecone_namespace)
    
    # 2. Ask LLM with Context
    answer = ask_pdf_tutor(req.question, context)
    
    return {"answer": answer, "context_used": context}