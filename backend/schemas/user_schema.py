from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone_number: str
    password: str
    verify_password: str
    student: bool
    tutor: bool

class LoginUser(BaseModel):
    email: EmailStr
    password: str
