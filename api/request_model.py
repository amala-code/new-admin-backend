from pydantic import BaseModel, EmailStr

# Login & Signup request model

class User(BaseModel):
    email: EmailStr
    password: str

class UserCreate(User):
    email: EmailStr
    password: str
    phone: str
    fullname: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

from datetime import datetime

class EventCreate(BaseModel):
    title: str
    description: str
    date_time: str
    location: str
    category: str
    image: str