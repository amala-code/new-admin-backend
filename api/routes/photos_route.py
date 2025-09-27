

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import List
from bson import ObjectId
import shutil
import os
import uuid
from pathlib import Path
from api.utils.db import images_collection

router = APIRouter()

# Use consistent directory structure
STATIC_DIR = "static"
IMAGES_DIR = "static/images"

# Ensure directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# --- BULK UPLOAD IMAGES ---
@router.post("/images/upload_bulk")
async def upload_bulk_images(files: List[UploadFile] = File(...)):
    try:
        uploaded_urls = []
        failed_uploads = []
        
        for file in files:
            try:
                # Validate file type
                if not file.content_type.startswith('image/'):
                    failed_uploads.append({
                        "filename": file.filename,
                        "error": "Not a valid image file"
                    })
                    continue
                
                # Generate unique filename to avoid conflicts
                file_extension = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                
                # Save to static/images/ directory (same as event route)
                file_path = os.path.join(IMAGES_DIR, unique_filename)
                
                # Save file
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Create URL that matches static file serving
                image_url = f"/static/images/{unique_filename}"
                
                # Save to database
                result = images_collection.insert_one({
                    "filename": file.filename,
                    "unique_filename": unique_filename,
                    "path": file_path,
                    "url": image_url
                })
                
                # Add URL to response (without leading slash for frontend)
                uploaded_urls.append(f"static/images/{unique_filename}")
                
            except Exception as e:
                failed_uploads.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        response_data = {
            "urls": uploaded_urls,
            "message": f"Successfully uploaded {len(uploaded_urls)} images"
        }
        
        if failed_uploads:
            response_data["failed"] = failed_uploads
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# --- FETCH IMAGE BY ID ---
@router.get("/images/{image_id}")
async def get_image(image_id: str):
    try:
        image = images_collection.find_one({"_id": ObjectId(image_id)})
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        return {
            "id": str(image["_id"]),
            "filename": image["filename"],
            "path": image["path"],
            "url": image.get("url", f"static/images/{image.get('unique_filename', image['filename'])}")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- DELETE IMAGE BY ID ---
@router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    try:
        image = images_collection.find_one({"_id": ObjectId(image_id)})
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # Delete file from storage
        if os.path.exists(image["path"]):
            os.remove(image["path"])

        # Remove from database
        images_collection.delete_one({"_id": ObjectId(image_id)})

        return {"message": "Image deleted successfully", "id": image_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- GET ALL IMAGES ---
@router.get("/images")
async def get_all_images():
    try:
        images = []
        for image in images_collection.find():
            images.append({
                "id": str(image["_id"]),
                "filename": image["filename"],
                "path": image["path"],
                "url": image.get("url", f"static/images/{image.get('unique_filename', image['filename'])}")
            })
        
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))