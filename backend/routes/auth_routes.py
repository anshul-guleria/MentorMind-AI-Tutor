import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from schemas.user_schema import RegisterUser, LoginUser
from core.security import hash_password, verify_password, create_access_token, decode_access_token
from sqlalchemy.orm import Session
from models.user_model import User

router = APIRouter()

@router.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user: RegisterUser, db:Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not user.student and not user.tutor:
        raise HTTPException(status_code=400, detail="User must be either a student or a tutor")

    if not user.password == user.verify_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    hashed_password = hash_password(user.password)
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
        is_student=user.student,
        is_tutor=user.tutor
    )

    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

    return {"message": "User registered successfully"}


@router.post("/api/auth/login", status_code=status.HTTP_200_OK)
async def login(user: LoginUser, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={
        "sub": existing_user.email,
        "user_id": existing_user.id,
        "email": existing_user.email,
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": existing_user.id,
            "email": existing_user.email,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "is_student": existing_user.is_student,
            "is_tutor": existing_user.is_tutor,
        },
    }


