

# from fastapi import APIRouter, HTTPException, UploadFile, File, Form,Depends
# from api.utils.db import events_collection
# from bson.objectid import ObjectId
# import shutil
# import os
# from uuid import uuid4
# from api.conf import SECRET_KEY
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# from utils.db import ALGORITHM
# import jwt

# security = HTTPBearer()


# router = APIRouter()

# async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     try:
#         token = credentials.credentials
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if not payload.get("sub"):
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return payload
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# # ---------- CREATE ----------
# @router.post("/create_event")
# async def create_event(
#     title: str = Form(...),
#     description: str = Form(...),
#     date_time: str = Form(...),
#     location: str = Form(...),
#     category: str = Form(...),
#     image: UploadFile = File(...)
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
#         "image": image_filename
#     }

#     inserted_event = events_collection.insert_one(event_data)
#     return {"message": "Event created successfully", "event_id": str(inserted_event.inserted_id)}


# # ---------- GET ALL ----------
# @router.get("/all_events")
# async def get_all_events():
#     events = []
#     for event in events_collection.find():
#         events.append({
#             "id": str(event["_id"]),
#             "title": event["title"],
#             "description": event["description"],
#             "date_time": event["date_time"],
#             "location": event["location"],
#             "category": event.get("category", "Gathering"),
#             "image": event.get("image", "")
#         })
#     return {"events": events}


# # ---------- GET BY CATEGORY ----------
# @router.get("/events/{category}")
# async def get_events_by_category(category: str):
#     events = []
#     for event in events_collection.find({"category": category}):
#         events.append({
#             "id": str(event["_id"]),
#             "title": event["title"],
#             "description": event["description"],
#             "date_time": event["date_time"],
#             "location": event["location"],
#             "category": event.get("category", "Gathering"),
#             "image": event.get("image", "")
#         })

#     if not events:
#         raise HTTPException(status_code=404, detail=f"No events found for category '{category}'")

#     return {"events": events}


# # # ---------- UPDATE ----------
# # @router.put("/update_event/{event_id}")
# # async def update_event(
# #     event_id: str,
# #     title: str = Form(None),
# #     description: str = Form(None),
# #     date_time: str = Form(None),
# #     location: str = Form(None),
# #     category: str = Form(None),
# #     image: UploadFile = File(None),
# #     user=Depends(verify_token),

# # ):
# #     update_data = {}

# #     if title: update_data["title"] = title
# #     if description: update_data["description"] = description
# #     if date_time: update_data["date_time"] = date_time
# #     if location: update_data["location"] = location
# #     if category: update_data["category"] = category

# #     if image:
# #         extension = os.path.splitext(image.filename)[1]
# #         image_filename = f"{uuid4().hex}{extension}"
# #         image_path = f"static/images/{image_filename}"
# #         with open(image_path, "wb") as buffer:
# #             shutil.copyfileobj(image.file, buffer)
# #         update_data["image"] = image_filename

# #     result = events_collection.update_one(
# #         {"_id": ObjectId(event_id)}, {"$set": update_data}
# #     )

# #     if result.matched_count == 0:
# #         raise HTTPException(status_code=404, detail="Event not found")

# #     return {"message": "Event updated successfully"}

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

#     if title is not None:
#         update_data["title"] = title
#     if description is not None:
#         update_data["description"] = description
#     if date_time is not None:
#         update_data["date_time"] = date_time
#     if location is not None:
#         update_data["location"] = location
#     if category is not None:
#         update_data["category"] = category

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



# # ---------- DELETE ----------
# @router.delete("/delete_event/{event_id}")
# async def delete_event(event_id: str, user=Depends(verify_token)):
#     result = events_collection.delete_one({"_id": ObjectId(event_id)})

#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Event not found")

#     return {"message": "Event deleted successfully"}


from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from api.utils.db import events_collection
from bson.objectid import ObjectId
import shutil
import os
from uuid import uuid4
from api.conf import SECRET_KEY
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from utils.db import ALGORITHM
import jwt

security = HTTPBearer()
router = APIRouter()

# Use the same directory structure as your image router for consistency
STATIC_DIR = "/tmp/static"
IMAGES_DIR = "/tmp/static/images"

# Ensure directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

@router.post("/create_event")
async def create_event(
    title: str = Form(...),
    description: str = Form(...),
    date_time: str = Form(...),
    location: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        # Validate image file
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save image to writable directory (/tmp/static/images/)
        extension = os.path.splitext(image.filename)[1]
        image_filename = f"{uuid4().hex}{extension}"
        image_path = os.path.join(IMAGES_DIR, image_filename)  # This goes to /tmp/static/images/

        # Save the file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        event_data = {
            "title": title,
            "description": description,
            "date_time": date_time,
            "location": location,
            "category": category,
            "image": image_filename,  # Store just the filename
            "image_path": image_path,  # Store full path for internal use
            "image_url": f"/static/images/{image_filename}"  # URL that works with static mount
        }

        inserted_event = events_collection.insert_one(event_data)
        return {
            "message": "Event created successfully", 
            "event_id": str(inserted_event.inserted_id),
            "image_url": f"/static/images/{image_filename}"
        }
    
    except Exception as e:
        # Clean up the file if it was created but database insert failed
        if 'image_path' in locals() and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")



# ---------- CREATE ----------
@router.post("/create_event/old")
async def create_event(
    title: str = Form(...),
    description: str = Form(...),
    date_time: str = Form(...),
    location: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        # Validate image file
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save image to writable directory
        extension = os.path.splitext(image.filename)[1]
        image_filename = f"{uuid4().hex}{extension}"
        image_path = os.path.join(IMAGES_DIR, image_filename)

        # Save the file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        event_data = {
            "title": title,
            "description": description,
            "date_time": date_time,
            "location": location,
            "category": category,
            "image": image_filename,  # Store just the filename
            "image_path": image_path,  # Store full path for internal use
            "image_url": f"/serve/images/{image_filename}"  # URL for frontend
        }

        inserted_event = events_collection.insert_one(event_data)
        return {
            "message": "Event created successfully", 
            "event_id": str(inserted_event.inserted_id),
            "image_url": f"/serve/images/{image_filename}"
        }
    
    except Exception as e:
        # Clean up the file if it was created but database insert failed
        if 'image_path' in locals() and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

# ---------- GET ALL ----------
@router.get("/all_events")
async def get_all_events():
    try:
        events = []
        for event in events_collection.find():
            # Handle both old and new image storage formats
            image_filename = event.get("image", "")
            if image_filename:
                # Check if it's new format with image_url
                if "image_url" in event:
                    image_url = event["image_url"]
                else:
                    # Old format - generate URL
                    image_url = f"/serve/images/{image_filename}"
            else:
                image_url = ""
            
            events.append({
                "id": str(event["_id"]),
                "title": event["title"],
                "description": event["description"],
                "date_time": event["date_time"],
                "location": event["location"],
                "category": event.get("category", "Gathering"),
                "image": image_filename,
                "image_url": image_url
            })
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

# ---------- GET BY CATEGORY ----------
@router.get("/events/{category}")
async def get_events_by_category(category: str):
    try:
        events = []
        for event in events_collection.find({"category": category}):
            # Handle both old and new image storage formats
            image_filename = event.get("image", "")
            if image_filename:
                # Check if it's new format with image_url
                if "image_url" in event:
                    image_url = event["image_url"]
                else:
                    # Old format - generate URL
                    image_url = f"/serve/images/{image_filename}"
            else:
                image_url = ""
            
            events.append({
                "id": str(event["_id"]),
                "title": event["title"],
                "description": event["description"],
                "date_time": event["date_time"],
                "location": event["location"],
                "category": event.get("category", "Gathering"),
                "image": image_filename,
                "image_url": image_url
            })

        if not events:
            raise HTTPException(status_code=404, detail=f"No events found for category '{category}'")

        return {"events": events}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events by category: {str(e)}")

# ---------- UPDATE ----------
@router.put("/update_event/{event_id}")
async def update_event(
    event_id: str,
    title: str = Form(None),
    description: str = Form(None),
    date_time: str = Form(None),
    location: str = Form(None),
    category: str = Form(None),
    image: UploadFile = File(None),
    user=Depends(verify_token),
):
    try:
        # Validate event_id
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID")
        
        # Check if event exists
        existing_event = events_collection.find_one({"_id": ObjectId(event_id)})
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
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

        # Handle image update
        if image:
            # Validate image file
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Delete old image if it exists
            old_image_filename = existing_event.get("image")
            if old_image_filename:
                old_image_path = existing_event.get("image_path")
                if old_image_path and os.path.exists(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except Exception as e:
                        print(f"Warning: Could not delete old image: {e}")
            
            # Save new image
            extension = os.path.splitext(image.filename)[1]
            image_filename = f"{uuid4().hex}{extension}"
            image_path = os.path.join(IMAGES_DIR, image_filename)
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            update_data["image"] = image_filename
            update_data["image_path"] = image_path
            update_data["image_url"] = f"/serve/images/{image_filename}"

        # Update the event
        result = events_collection.update_one(
            {"_id": ObjectId(event_id)}, {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")

        return {"message": "Event updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating event: {str(e)}")

# ---------- DELETE ----------
@router.delete("/delete_event/{event_id}")
async def delete_event(event_id: str, user=Depends(verify_token)):
    try:
        # Validate event_id
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID")
        
        # Get event details before deletion to clean up image
        event = events_collection.find_one({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Delete associated image file
        image_path = event.get("image_path")
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Warning: Could not delete image file: {e}")
        
        # Delete the event from database
        result = events_collection.delete_one({"_id": ObjectId(event_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")

        return {"message": "Event deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting event: {str(e)}")

# ---------- GET SINGLE EVENT ----------
@router.get("/event/{event_id}")
async def get_event(event_id: str):
    try:
        # Validate event_id
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID")
        
        event = events_collection.find_one({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Handle both old and new image storage formats
        image_filename = event.get("image", "")
        if image_filename:
            if "image_url" in event:
                image_url = event["image_url"]
            else:
                image_url = f"/serve/images/{image_filename}"
        else:
            image_url = ""
        
        return {
            "id": str(event["_id"]),
            "title": event["title"],
            "description": event["description"],
            "date_time": event["date_time"],
            "location": event["location"],
            "category": event.get("category", "Gathering"),
            "image": image_filename,
            "image_url": image_url
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching event: {str(e)}")