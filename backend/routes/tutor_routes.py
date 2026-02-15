from fastapi import Body
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user
from models.user_model import User
from models.question_model import Question
from models.ai_responses import AIResponse

from models.quiz_model import QuizModel
from models.question_model import Question
from models.ai_responses import AIResponse
from models.user_quiz_responses import UserQuizResponse
from schemas.quiz_schema import Quiz
from schemas.question_schema import Question as QuestionSchema
from database import get_db


# AI services (uncomment the one you want to use)
# from services.gemini_service import ask_tutor, ask_quick_tutor, analyze_student_performance
# from services.ollama_service import ask_tutor, ask_quick_tutor, analyze_student_performance
from services.groq_service import ask_tutor, ask_quick_tutor, analyze_student_performance

# text to speech service
from services.tts_service import generate_audio


router = APIRouter()

class TutorRequest(BaseModel):
    question: str

@router.post("/ask-tutor", status_code=status.HTTP_200_OK)
async def ask_tutor_route(request: TutorRequest, db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    response = ask_tutor(request.question)
    quiz_data = response.get("quiz")
    new_quiz=QuizModel(
        id=str(uuid.uuid4()),
        topic=response.get("topic"),
        created_by=current_user.id
    )

    try:
        db.add(new_quiz)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving quiz: {str(e)}")

    for question in quiz_data.keys():
        new_question=Question(
            id=str(uuid.uuid4()),
            quiz_id=new_quiz.id,
            question_number=question,
            question_text=quiz_data[question]["question"],
            option_1=quiz_data[question]["options"]["1"],
            option_2=quiz_data[question]["options"]["2"],
            option_3=quiz_data[question]["options"]["3"],
            option_4=quiz_data[question]["options"]["4"],
            correct_option=int(quiz_data[question]["answer"]) if isinstance(quiz_data[question]["answer"], str) else quiz_data[question]["answer"],
            difficulty=quiz_data[question]["difficulty"]
        )

        try:
            db.add(new_question)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving question: {str(e)}")

    db.commit()

    # ai response model
    ai_response = AIResponse(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        quiz_id=new_quiz.id,
        user_question=request.question,
        topic=response.get("topic"),
        answer_text=response.get("answer")
    )
    
    try:
        db.add(ai_response)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving AI response: {str(e)}")

    return {
        "message": "Tutor response generated and saved successfully",
        "user_id": current_user.id,
        "response_id": ai_response.id,
        "question": response.get("question"),
        "answer": response.get("answer"),
        "topic": response.get("topic"),
        "field": response.get("field"),
        "quiz": quiz_data,
    }

@router.get("/response/{response_id}", status_code=status.HTTP_200_OK)
async def get_response_detail(
    response_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Fetch the specific response
    response = db.query(AIResponse).filter(AIResponse.id == response_id).first()
    
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Security check: Ensure the user requesting this owns the data
    if response.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this response")

    return {
        "id": response.id,
        "topic": response.topic,
        "question": response.user_question,
        "answer": response.answer_text,
        "created_at": response.created_at
    }

@router.get("/quiz/{response_id}", status_code=status.HTTP_200_OK)
async def get_quiz(response_id: str, db: Session = Depends(get_db)):

    response=db.query(AIResponse).filter(AIResponse.id == response_id).first()

    quiz_id = response.quiz_id

    quiz=db.query(QuizModel).filter(QuizModel.id == quiz_id).first()

    if not quiz_id:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz = db.query(QuizModel).filter(QuizModel.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()


    quiz_data = Quiz(
        id=quiz.id,
        user_id=response.user_id,
        response_id=response_id,  
        question_ids=[q.id for q in questions],
        topic=quiz.topic
    )

    return quiz_data

@router.get("/question/{question_id}", status_code=status.HTTP_200_OK)
async def get_question(question_id: str, db: Session = Depends(get_db)):
    
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question_data = QuestionSchema(
        id=question.id,
        quiz_id=question.quiz_id,
        question_number=question.question_number,
        question_text=question.question_text,
        option_1=question.option_1,
        option_2=question.option_2,
        option_3=question.option_3,
        option_4=question.option_4,
        correct_option=question.correct_option,
        difficulty=question.difficulty
    )

    return question_data

@router.get("/user/topics", status_code=status.HTTP_200_OK)
async def get_user_topics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    responses = db.query(AIResponse).filter(AIResponse.user_id == current_user.id).order_by(AIResponse.created_at.desc()).all()
    topics = [
        {
            "topic": resp.topic,
            "response_id": resp.id
        }
        for resp in responses if resp.topic and resp.id
    ]
    return {"topics": topics}


@router.post("/ask-quick", status_code=status.HTTP_200_OK)
async def ask_quick_route(request: TutorRequest):

    text_answer = ask_quick_tutor(request.question)
    print(f"Generated Text Answer: {text_answer}")
    audio_data = generate_audio(text_answer)
    
    return {
        "answer": text_answer,
        "audio": audio_data  # Send Base64 audio string
    }

@router.post("/quiz/submit", status_code=status.HTTP_200_OK)
async def submit_quiz(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", []) 

    if not quiz_id or not answers:
        raise HTTPException(status_code=400, detail="Missing data")

    score = 0
    details = []

    # print(f"DEBUG: Received submission for Quiz ID: {quiz_id}")
    # print(f"DEBUG: Answers payload: {answers}")

    try:
        for ans in answers:
            qid = ans.get("question_id")
            # Convert answer to int to match DB column type safely
            try:
                user_choice = int(ans.get("answer")) 
            except ValueError:
                print(f"ERROR: User answer '{ans.get('answer')}' is not an integer.")
                continue

            # Verify Question Exists
            question = db.query(Question).filter(Question.id == qid).first()
            
            if not question:
                print(f"WARNING: Question ID {qid} NOT FOUND in database. Skipping save for this question.")
                details.append({"question_id": qid, "error": "Question not found in DB"})
                continue
                
            is_correct = (question.correct_option == user_choice)
            if is_correct:
                score += 1
                
            # Save User Response
            new_response = UserQuizResponse(
                id=str(uuid.uuid4()), 
                user_id=current_user.id,
                quiz_id=quiz_id,
                question_id=qid,
                selected_option=user_choice,
                is_correct=is_correct
            )
            db.add(new_response)
            details.append({"question_id": qid, "correct": is_correct})
        
        db.commit()
        print(f"SUCCESS: Saved quiz attempts for User {current_user.id}")

        return {"score": score, "total": len(answers), "details": details}

    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: {str(e)}")
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"Database Save Error: {str(e)}")

    
@router.get("/user/summary", status_code=status.HTTP_200_OK)
async def get_user_summary(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Fetch last 50 quiz responses for this user
    # We join with Question and Quiz tables to get the text context
    results = (
        db.query(UserQuizResponse, Question, QuizModel)
        .join(Question, UserQuizResponse.question_id == Question.id)
        .join(QuizModel, UserQuizResponse.quiz_id == QuizModel.id)
        .filter(UserQuizResponse.user_id == current_user.id)
        .order_by(UserQuizResponse.created_at.desc())
        .limit(50)
        .all()
    )

    if not results:
        return {"has_data": False, "message": "No quizzes attempted yet."}

    # Format data for the AI
    history_text = ""
    for resp, quest, quiz in results:
        status = "CORRECT" if resp.is_correct else "WRONG"
        history_text += f"Topic: {quiz.topic} | Question: {quest.question_text} | Status: {status}\n"

    # Sent to AI for analysis
    analysis = analyze_student_performance(history_text)

    return {
        "has_data": True,
        "analysis": analysis
    }