from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pymongo import MongoClient
from conf import DB_PASSWORD,DB_USERNAME

MONGO_URI = f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster0.is3v706.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client[DB_USERNAME]  
users_collection = db.users  
members_collection = db.members
events_collection = db.events
non_members_collection = db.non_members  # 👈 new collection

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")