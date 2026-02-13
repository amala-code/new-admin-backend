import requests
import base64
import os
import io
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from bson import ObjectId
from api.utils.db import gallery_collection
from api.conf import IMGBB_API_KEY

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

MAX_IMAGES = 5
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB per image

router = APIRouter()

def compress_image(contents: bytes, max_size=(800, 800), quality=50, max_kb=200) -> bytes:
    try:
        img = Image.open(io.BytesIO(contents))

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail(max_size, Image.LANCZOS)

        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(list(img.getdata()))

        quality_current = quality
        while quality_current > 10:
            buffer = io.BytesIO()
            clean_img.save(buffer, format="JPEG", quality=quality_current, optimize=True)
            size_kb = buffer.tell() / 1024

            if size_kb <= max_kb:
                return buffer.getvalue()

            quality_current -= 5

        return buffer.getvalue()
    except Exception:
        return contents  # fallback to original if compression fails


def upload_to_imgbb(image_bytes: bytes, filename: str) -> dict:
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY, "image": b64},
            timeout=8
        )
        result = res.json()

        if not result.get("success"):
            return {"error": f"Upload failed for {filename}", "details": result}

        return {"filename": filename, "url": result["data"]["url"]}
    except requests.Timeout:
        return {"error": f"Upload timed out for {filename}"}
    except Exception as e:
        return {"error": f"Upload error for {filename}: {str(e)}"}


@router.post("/upload_gallery")
async def upload_gallery(
    title: str = Form(...),
    images: List[UploadFile] = File(...)
):
    # Validate image count
    if len(images) > MAX_IMAGES:
        raise HTTPException(status_code=400, detail=f"Max {MAX_IMAGES} images allowed per upload")

    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    uploaded_images = []
    failed_images = []

    for image in images:
        contents = await image.read()

        # Validate file size
        if len(contents) > MAX_FILE_SIZE:
            failed_images.append({"filename": image.filename, "error": "File too large (max 4MB)"})
            continue

        # Validate file type
        if image.content_type not in ["image/jpeg", "image/png", "image/webp", "image/gif"]:
            failed_images.append({"filename": image.filename, "error": "Invalid file type"})
            continue

        # Compress
        compressed = compress_image(contents)

        # Upload
        result = upload_to_imgbb(compressed, image.filename)

        if "error" in result:
            failed_images.append(result)
        else:
            uploaded_images.append(result)

    if not uploaded_images:
        raise HTTPException(status_code=500, detail="All uploads failed", headers={"failed": str(failed_images)})

    gallery_data = {
        "title": title.strip(),
        "images": uploaded_images,
        "total_images": len(uploaded_images)
    }

    inserted = gallery_collection.insert_one(gallery_data)

    response = {
        "message": f"{len(uploaded_images)} images uploaded successfully",
        "gallery_id": str(inserted.inserted_id)
    }

    if failed_images:
        response["failed"] = failed_images

    return response


@router.get("/galleries")
async def get_all_galleries():
    galleries = []
    for gallery in gallery_collection.find().sort("_id", -1):
        galleries.append({
            "id": str(gallery["_id"]),
            "title": gallery["title"],
            "images": gallery["images"],
            "total_images": gallery.get("total_images", len(gallery["images"]))
        })
    return galleries


@router.get("/gallery/{gallery_id}")
async def get_gallery(gallery_id: str):
    gallery = gallery_collection.find_one({"_id": ObjectId(gallery_id)})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    return {
        "id": str(gallery["_id"]),
        "title": gallery["title"],
        "images": gallery["images"],
        "total_images": gallery.get("total_images", len(gallery["images"]))
    }


@router.delete("/gallery/{gallery_id}")
async def delete_gallery(gallery_id: str):
    result = gallery_collection.delete_one({"_id": ObjectId(gallery_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Gallery not found")
    return {"message": "Gallery deleted successfully"}