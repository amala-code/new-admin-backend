from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from PIL import Image
from pathlib import Path
import shutil
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from api.utils.db import photos_collection

router = APIRouter()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("public/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Synchronous conversion function
def convert_and_save_image(file_path: Path, output_path: Path):
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if needed (handles RGBA, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(output_path, "webp", quality=85, optimize=True)
        
        # Delete original temp file
        if file_path.exists():
            file_path.unlink()
        return True
    except Exception as e:
        print(f"Error converting image: {e}")
        # Clean up temp file if conversion fails
        if file_path.exists():
            file_path.unlink()
        return False

# ✅ Save to MongoDB
def save_image_to_db(url: str):
    try:
        photos_collection.insert_one({"url": url})
        return True
    except Exception as e:
        print(f"Error saving to DB: {e}")
        return False

# ✅ Main upload route with concurrent processing
@router.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    urls = []
    failed_files = []
    temp_files = []
    
    # Step 1: Save all uploaded files temporarily and validate
    for file in files:
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                failed_files.append(f"{file.filename}: Not an image file")
                continue
            
            # Generate unique filename
            temp_uuid = str(uuid.uuid4())
            temp_path = UPLOAD_DIR / f"{temp_uuid}.tmp"
            output_path = OUTPUT_DIR / f"{temp_uuid}.webp"
            
            # Save uploaded file to temp location
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Store file info for processing
            temp_files.append({
                'temp_path': temp_path,
                'output_path': output_path,
                'url': f"/images/{temp_uuid}.webp",
                'original_name': file.filename
            })
            
        except Exception as e:
            failed_files.append(f"{file.filename}: Upload error - {str(e)}")
    
    # Step 2: Convert all images concurrently
    if temp_files:
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            
            # Create conversion tasks
            conversion_tasks = [
                loop.run_in_executor(
                    executor, 
                    convert_and_save_image, 
                    file_info['temp_path'], 
                    file_info['output_path']
                )
                for file_info in temp_files
            ]
            
            # Wait for all conversions to complete
            results = await asyncio.gather(*conversion_tasks, return_exceptions=True)
        
        # Step 3: Process results and save to database
        for i, result in enumerate(results):
            file_info = temp_files[i]
            
            if result is True:  # Successful conversion
                # Save to database
                if save_image_to_db(file_info['url']):
                    urls.append(file_info['url'])
                else:
                    failed_files.append(f"{file_info['original_name']}: Database save failed")
                    # Clean up file if DB save fails
                    if file_info['output_path'].exists():
                        file_info['output_path'].unlink()
            else:
                # Conversion failed
                error_msg = str(result) if isinstance(result, Exception) else "Conversion failed"
                failed_files.append(f"{file_info['original_name']}: {error_msg}")
    
    # Step 4: Return response
    response_data = {
        "message": f"Processed {len(files)} files. {len(urls)} successful, {len(failed_files)} failed.",
        "urls": urls,
        "total_uploaded": len(urls)
    }
    
    if failed_files:
        response_data["failed"] = failed_files
    
    return JSONResponse(response_data)

# ✅ Mount static files AFTER defining routes
router.mount("/images", StaticFiles(directory="public/images"), name="images")


@router.get("/api/content/photos")
async def get_all_images(limit: Optional[int] = 50):
    try:
        # Get all images from photos collection
        images_cursor = photos_collection.find({}).sort("_id", -1).limit(limit)
        
        images = []
        for image in images_cursor:
            images.append({
                "id": str(image["_id"]),
                "url": image["url"],
                "uploaded_at": image.get("created_at", "")
            })

        return JSONResponse({
            "message": "Images fetched successfully",
            "images": images,
            "total": len(images)
        })

    except Exception as e:
        print(f"Error fetching images: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching images: {str(e)}")
