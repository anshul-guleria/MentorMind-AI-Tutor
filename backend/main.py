from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

from models.user_model import User
from models.ai_responses import AIResponse
from models.quiz_model import QuizModel
from models.question_model import Question
from models.pdf_model import UserPDF
from models.user_quiz_responses import UserQuizResponse 
# ----------------------------------------

from routes.auth_routes import router as auth_router
from routes.tutor_routes import router as tutor_router
from routes.pdf_routes import router as pdf_router

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8501", "http://localhost:8502"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tutor_router)
app.include_router(pdf_router)

@app.get("/")
def read_root():
    return {"message": "Server is running"}