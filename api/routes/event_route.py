

import base64
import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form,Depends, requests
from api.routes.photos_route import compress_image
from api.utils.db import events_collection
from bson.objectid import ObjectId
import shutil
import os
from uuid import uuid4
from api.conf import IMGBB_API_KEY, SECRET_KEY
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from utils.db import ALGORITHM
import jwt
from datetime import datetime
import datetime

security = HTTPBearer()


router = APIRouter()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------- CREATE ----------
# @router.post("/create_event")
# async def create_event(
#     title: str = Form(...),
#     description: str = Form(...),
#     date_time: str = Form(...),
#     location: str = Form(...),
#     category: str = Form(...),
#     image: UploadFile = File(...),
#     popup: bool = Form(False),
#     popup_end_date: Optional[datetime.date] = Form(None)  # ✅ Date only
# ):
#     # Save image to a folder
#     extension = os.path.splitext(image.filename)[1]
#     image_filename = f"{uuid4().hex}{extension}"
#     image_path = f"static/images/{image_filename}"

#     with open(image_path, "wb") as buffer:
#         shutil.copyfileobj(image.file, buffer)

#     event_data = {
#         "title": title,
#         "description": description,
#         "date_time": date_time,
#         "location": location,
#         "category": category,
#         "image": image_filename,
#         "popup": popup,
#         "popup_end_date": popup_end_date
#     }



#     inserted_event = events_collection.insert_one(event_data)
#     return {"message": "Event created successfully", "event_id": str(inserted_event.inserted_id)}


@router.post("/create_event")
async def create_event(
    title: str = Form(...),
    description: str = Form(...),
    date_time: str = Form(...),
    location: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    popup: bool = Form(False),
    popup_end_date: str = Form(None)
):
    # Handle image upload
    contents = await image.read()
    compressed = compress_image(contents)
    b64 = base64.b64encode(compressed).decode("utf-8")

    res = requests.post("https://api.imgbb.com/1/upload", data={
        "key": IMGBB_API_KEY,
        "image": b64
    }, timeout=8)
    result = res.json()

    if not result.get("success"):
        raise HTTPException(status_code=500, detail="Image upload failed")

    event_data = {
        "title": title,
        "description": description,
        "date_time": date_time,
        "location": location,
        "category": category,
        "image": result["data"]["url"],
        "popup": popup,
    }

    if popup and popup_end_date:
        event_data["popup_end_date"] = datetime.strptime(popup_end_date, "%Y-%m-%d")

    inserted = events_collection.insert_one(event_data)
    return {"message": "Event created successfully", "event_id": str(inserted.inserted_id)}



@router.get("/popup-events")
async def get_active_popups():
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    events = list(events_collection.find({
        "popup": True,
        "popup_end_date": {"$gte": today}
    }))
    print(events)

    for event in events:
        event["_id"] = str(event["_id"])

    return {
        "count": len(events),
        "events": events
    }
# ---------- GET ALL ----------
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
            "image": event.get("image", ""),
            "popup": event.get("popup", False),
            "popup_end_date": event.get("popup_end_date")
        })
    return {"events": events}


# ---------- GET BY CATEGORY ----------
@router.get("/events/{category}")
async def get_events_by_category(category: str):
    events = []
    for event in events_collection.find({"category": category}):
        events.append({
            "id": str(event["_id"]),
            "title": event["title"],
            "description": event["description"],
            "date_time": event["date_time"],
            "location": event["location"],
            "category": event.get("category", "Gathering"),
            "image": event.get("image", "")
        })

    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for category '{category}'")

    return {"events": events}


# # ---------- UPDATE ----------
# @router.put("/update_event/{event_id}")
# async def update_event(
#     event_id: str,
#     title: str = Form(None),
#     description: str = Form(None),
#     date_time: str = Form(None),
#     location: str = Form(None),
#     category: str = Form(None),
#     image: UploadFile = File(None),
#     user=Depends(verify_token),

# ):
#     update_data = {}

#     if title: update_data["title"] = title
#     if description: update_data["description"] = description
#     if date_time: update_data["date_time"] = date_time
#     if location: update_data["location"] = location
#     if category: update_data["category"] = category

#     if image:
#         extension = os.path.splitext(image.filename)[1]
#         image_filename = f"{uuid4().hex}{extension}"
#         image_path = f"static/images/{image_filename}"
#         with open(image_path, "wb") as buffer:
#             shutil.copyfileobj(image.file, buffer)
#         update_data["image"] = image_filename

#     result = events_collection.update_one(
#         {"_id": ObjectId(event_id)}, {"$set": update_data}
#     )

#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Event not found")

#     return {"message": "Event updated successfully"}

from typing import Optional
from datetime import date
from fastapi import Form, File, UploadFile, Depends, HTTPException
from bson import ObjectId

@router.put("/update_event/{event_id}")
async def update_event(
    event_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    date_time: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    popup: Optional[bool] = Form(None),              # ✅ Added
    popup_end_date: Optional[date] = Form(None),     # ✅ Added (date only)
    image: Optional[UploadFile] = File(None),
    user=Depends(verify_token),
):
    update_data = {}

    if title is not None:
        update_data["title"] = title

    if description is not None:
        update_data["description"] = description

    if date_time is not None:
        update_data["date_time"] = date_time

    if location is not None:
        update_data["location"] = location

    if category is not None:
        update_data["category"] = category

    if popup is not None:
        update_data["popup"] = popup

    if popup_end_date is not None:
        update_data["popup_end_date"] = popup_end_date

    if image:
        extension = os.path.splitext(image.filename)[1]
        image_filename = f"{uuid4().hex}{extension}"
        image_path = f"static/images/{image_filename}"

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        update_data["image"] = image_filename

    # 🚨 Prevent empty update
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event updated successfully"}


# ---------- DELETE ----------
@router.delete("/delete_event/{event_id}")
async def delete_event(event_id: str, user=Depends(verify_token)):
    result = events_collection.delete_one({"_id": ObjectId(event_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event deleted successfully"}
