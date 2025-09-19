from fastapi import APIRouter, HTTPException
from api.request_model import EventCreate
from api.utils.db import events_collection
from bson.objectid import ObjectId
from fastapi import UploadFile, File, Form
import shutil
import os
from uuid import uuid4
router = APIRouter()

@router.post("/create_event")
async def create_event(
    title: str = Form(...),
    description: str = Form(...),
    date_time: str = Form(...),
    location: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...)
):
    # Save image to a folder
    extension = os.path.splitext(image.filename)[1]
    image_filename = f"{uuid4().hex}{extension}"
    image_path = f"static/images/{image_filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    event_data = {
        "title": title,
        "description": description,
        "date_time": date_time,
        "location": location,
        "category": category,
        "image": image_filename
    }

    inserted_event = events_collection.insert_one(event_data)
    return {"message": "Event created successfully", "event_id": str(inserted_event.inserted_id)}

@router.get("/all_events")
async def get_all_events():
    events = []
    for event in events_collection.find():
        events.append({
            "id": str(event["_id"]),
            "title": event["title"],
            "description": event["description"],
            "date_time": event["date_time"],
            "location": event["location"],
            "category": event.get("category", "Gathering"),
            "image": event.get("image", "")  # safely get image field if it exists
        })
    return {"events": events}
