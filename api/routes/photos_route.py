from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from bson import ObjectId
import shutil
import os
from api.utils.db import images_collection

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- BULK UPLOAD IMAGES ---
@router.post("/images/upload_bulk")
async def upload_bulk_images(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append({"filename": file.filename, "path": file_path})

        # If saving to DB:
        images_collection.insert_one({
            "filename": file.filename,
            "path": file_path
        })

    return {"uploaded": uploaded_files}


# --- FETCH IMAGE BY ID ---
@router.get("/images/{image_id}")
async def get_image(image_id: str):
    image = images_collection.find_one({"_id": ObjectId(image_id)})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "id": str(image["_id"]),
        "filename": image["filename"],
        "path": image["path"]
    }


# --- DELETE IMAGE BY ID ---
@router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    image = images_collection.find_one({"_id": ObjectId(image_id)})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # delete file from storage
    if os.path.exists(image["path"]):
        os.remove(image["path"])

    # remove from db
    images_collection.delete_one({"_id": ObjectId(image_id)})

    return {"message": "Image deleted successfully", "id": image_id}


@router.get("/images")
async def get_all_images():
    images = []
    for image in images_collection.find():
        images.append({
            "id": str(image["_id"]),
            "filename": image["filename"],
            "path": image["path"]
        })
    
    if not images:
        raise HTTPException(status_code=404, detail="No images found")
    
    return {"images": images}