import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter
from pydantic import  EmailStr
from typing import Optional
from conf import SECRET_KEY,DB_PASSWORD,DB_USERNAME
from utils.db import pwd_context,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter()


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(useremail: EmailStr, user_id: str, expires_delta: Optional[timedelta] = None):
    now = datetime.now()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": useremail, "user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)