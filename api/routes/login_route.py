import jwt
from fastapi import Depends, HTTPException, APIRouter
from bson.objectid import ObjectId
from conf import SECRET_KEY
from request_model import User, UserCreate, Token
from services.login_service import create_access_token, hash_password, verify_password
from utils.db import users_collection, oauth2_scheme,ALGORITHM

router = APIRouter()

@router.post("/signup")
async def signup(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = hash_password(user.password)
    user_data = {
        "phone": user.phone,  # Fixed typo in key name
        "fullname": user.fullname,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    inserted_user = users_collection.insert_one(user_data)
    return {"message": "User created successfully", "user_id": str(inserted_user.inserted_id)}

@router.post("/login", response_model=Token)  # Changed from User to Token
async def login(request: User):
    user = users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(useremail=request.email, user_id=str(user["_id"]))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"message": f"Welcome, {user['fullname']}!"}  # Changed username to fullname
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    