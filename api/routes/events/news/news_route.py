from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from api.utils.db import news_collection
router = APIRouter()

class NewsCreateRequest(BaseModel):
    title: str
    description: str
    date_time: str
    location: str
    category: str

@router.post("/create_news")
async def create_event(news: NewsCreateRequest):
    event_data = news.model_dump()
    inserted_event = news_collection.insert_one(event_data)
    return {"message": "Event created successfully", "event_id": str(inserted_event.inserted_id)}
