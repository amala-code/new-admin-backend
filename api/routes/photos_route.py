

# # # from fastapi import APIRouter, UploadFile, File, HTTPException
# # # from fastapi.staticfiles import StaticFiles
# # # from typing import List
# # # from bson import ObjectId
# # # import shutil
# # # import os
# # # import uuid
# # # from pathlib import Path
# # # from api.utils.db import images_collection

# # # router = APIRouter()

# # # # Use consistent directory structure
# # # STATIC_DIR = "static"
# # # IMAGES_DIR = "static/images"

# # # # Ensure directories exist
# # # os.makedirs(STATIC_DIR, exist_ok=True)
# # # os.makedirs(IMAGES_DIR, exist_ok=True)

# # # # # --- BULK UPLOAD IMAGES ---
# # # # @router.post("/images/upload_bulk")
# # # # async def upload_bulk_images(files: List[UploadFile] = File(...)):
# # # #     try:
# # # #         uploaded_urls = []
# # # #         failed_uploads = []
        
# # # #         for file in files:
# # # #             try:
# # # #                 # Validate file type
# # # #                 if not file.content_type.startswith('image/'):
# # # #                     failed_uploads.append({
# # # #                         "filename": file.filename,
# # # #                         "error": "Not a valid image file"
# # # #                     })
# # # #                     continue
                
# # # #                 # Generate unique filename to avoid conflicts
# # # #                 file_extension = Path(file.filename).suffix
# # # #                 unique_filename = f"{uuid.uuid4()}{file_extension}"
                
# # # #                 # Save to static/images/ directory (same as event route)
# # # #                 file_path = os.path.join(IMAGES_DIR, unique_filename)
                
# # # #                 # Save file
# # # #                 with open(file_path, "wb") as buffer:
# # # #                     shutil.copyfileobj(file.file, buffer)
                
# # # #                 # Create URL that matches static file serving
# # # #                 image_url = f"/static/images/{unique_filename}"
                
# # # #                 # Save to database
# # # #                 result = images_collection.insert_one({
# # # #                     "filename": file.filename,
# # # #                     "unique_filename": unique_filename,
# # # #                     "path": file_path,
# # # #                     "url": image_url
# # # #                 })
                
# # # #                 # Add URL to response (without leading slash for frontend)
# # # #                 uploaded_urls.append(f"static/images/{unique_filename}")
                
# # # #             except Exception as e:
# # # #                 failed_uploads.append({
# # # #                     "filename": file.filename,
# # # #                     "error": str(e)
# # # #                 })
        
# # # #         response_data = {
# # # #             "urls": uploaded_urls,
# # # #             "message": f"Successfully uploaded {len(uploaded_urls)} images"
# # # #         }
        
# # # #         if failed_uploads:
# # # #             response_data["failed"] = failed_uploads
        
# # # #         return response_data
        
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# # # # --- BULK UPLOAD IMAGES ---
# # # @router.post("/images/upload_bulk")
# # # async def upload_bulk_images(files: List[UploadFile] = File(...)):
# # #     uploaded_urls = []
# # #     failed_uploads = []

# # #     for file in files:
# # #         try:
# # #             if not file.content_type.startswith("image/"):
# # #                 failed_uploads.append({
# # #                     "filename": file.filename,
# # #                     "error": "Not a valid image file"
# # #                 })
# # #                 continue

# # #             # Generate unique filename
# # #             file_extension = Path(file.filename).suffix
# # #             unique_filename = f"{uuid.uuid4()}{file_extension}"
# # #             image_path = f"static/images/{unique_filename}"

# # #             # Save file (same as event route)
# # #             with open(image_path, "wb") as buffer:
# # #                 shutil.copyfileobj(file.file, buffer)

# # #             image_url = f"static/images/{unique_filename}"

# # #             images_collection.insert_one({
# # #                 "filename": file.filename,
# # #                 "unique_filename": unique_filename,
# # #                 "path": image_path,
# # #                 "url": image_url
# # #             })

# # #             uploaded_urls.append(image_url)

# # #         except Exception as e:
# # #             failed_uploads.append({"filename": file.filename, "error": str(e)})

# # #     return {
# # #         "urls": uploaded_urls,
# # #         "message": f"Successfully uploaded {len(uploaded_urls)} images",
# # #         "failed": failed_uploads
# # #     }

# # # # --- FETCH IMAGE BY ID ---
# # # @router.get("/images/{image_id}")
# # # async def get_image(image_id: str):
# # #     try:
# # #         image = images_collection.find_one({"_id": ObjectId(image_id)})
# # #         if not image:
# # #             raise HTTPException(status_code=404, detail="Image not found")

# # #         return {
# # #             "id": str(image["_id"]),
# # #             "filename": image["filename"],
# # #             "path": image["path"],
# # #             "url": image.get("url", f"static/images/{image.get('unique_filename', image['filename'])}")
# # #         }
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=str(e))


# # # # --- DELETE IMAGE BY ID ---
# # # @router.delete("/images/{image_id}")
# # # async def delete_image(image_id: str):
# # #     try:
# # #         image = images_collection.find_one({"_id": ObjectId(image_id)})
# # #         if not image:
# # #             raise HTTPException(status_code=404, detail="Image not found")

# # #         # Delete file from storage
# # #         if os.path.exists(image["path"]):
# # #             os.remove(image["path"])

# # #         # Remove from database
# # #         images_collection.delete_one({"_id": ObjectId(image_id)})

# # #         return {"message": "Image deleted successfully", "id": image_id}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=str(e))


# # # # --- GET ALL IMAGES ---
# # # @router.get("/images")
# # # async def get_all_images():
# # #     try:
# # #         images = []
# # #         for image in images_collection.find():
# # #             images.append({
# # #                 "id": str(image["_id"]),
# # #                 "filename": image["filename"],
# # #                 "path": image["path"],
# # #                 "url": image.get("url", f"static/images/{image.get('unique_filename', image['filename'])}")
# # #             })
        
# # #         return {"images": images}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=str(e))


# # # Updated photos_route.py - Only fixing the images upload issue
# # from fastapi import APIRouter, UploadFile, File, HTTPException
# # from typing import List
# # from bson import ObjectId
# # import shutil
# # import os
# # import uuid
# # from pathlib import Path
# # from api.utils.db import images_collection

# # router = APIRouter()

# # # Use writable directory for deployment environments
# # # /tmp is usually writable in most cloud platforms
# # STATIC_DIR = "/tmp/static"
# # IMAGES_DIR = "/tmp/static/images"

# # # Ensure directories exist
# # os.makedirs(STATIC_DIR, exist_ok=True)
# # os.makedirs(IMAGES_DIR, exist_ok=True)

# # # --- BULK UPLOAD IMAGES ---
# # @router.post("/images/upload_bulk")
# # async def upload_bulk_images(files: List[UploadFile] = File(...)):
# #     uploaded_urls = []
# #     failed_uploads = []

# #     for file in files:
# #         try:
# #             if not file.content_type.startswith("image/"):
# #                 failed_uploads.append({
# #                     "filename": file.filename,
# #                     "error": "Not a valid image file"
# #                 })
# #                 continue

# #             # Generate unique filename
# #             file_extension = Path(file.filename).suffix
# #             unique_filename = f"{uuid.uuid4()}{file_extension}"
            
# #             # Save to writable directory (/tmp)
# #             image_path = os.path.join(IMAGES_DIR, unique_filename)

# #             # Save file to the writable directory
# #             with open(image_path, "wb") as buffer:
# #                 shutil.copyfileobj(file.file, buffer)

# #             # Store relative URL for serving (this will be used by your static file serving)
# #             image_url = f"/static/images/{unique_filename}"

# #             # Save to database with both paths
# #             images_collection.insert_one({
# #                 "filename": file.filename,
# #                 "unique_filename": unique_filename,
# #                 "path": image_path,  # Full path where file is actually stored
# #                 "url": image_url,    # Relative URL for serving
# #                 "storage_location": "tmp"  # Track where it's stored
# #             })

# #             uploaded_urls.append(image_url)

# #         except Exception as e:
# #             failed_uploads.append({"filename": file.filename, "error": str(e)})

# #     return {
# #         "urls": uploaded_urls,
# #         "message": f"Successfully uploaded {len(uploaded_urls)} images",
# #         "failed": failed_uploads
# #     }

# # # --- FETCH IMAGE BY ID ---
# # @router.get("/images/{image_id}")
# # async def get_image(image_id: str):
# #     try:
# #         image = images_collection.find_one({"_id": ObjectId(image_id)})
# #         if not image:
# #             raise HTTPException(status_code=404, detail="Image not found")

# #         return {
# #             "id": str(image["_id"]),
# #             "filename": image["filename"],
# #             "path": image["path"],
# #             "url": image.get("url", f"static/images/{image.get('unique_filename', image['filename'])}")
# #         }
# #     except Exception as e:
# #         if "Image not found" in str(e):
# #             raise e
# #         raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")

# # # --- DELETE IMAGE BY ID ---
# # @router.delete("/images/{image_id}")
# # async def delete_image(image_id: str):
# #     try:
# #         image = images_collection.find_one({"_id": ObjectId(image_id)})
# #         if not image:
# #             raise HTTPException(status_code=404, detail="Image not found")

# #         # Delete file from storage
# #         if os.path.exists(image["path"]):
# #             try:
# #                 os.remove(image["path"])
# #             except Exception as e:
# #                 print(f"Warning: Could not delete file: {e}")

# #         # Remove from database
# #         images_collection.delete_one({"_id": ObjectId(image_id)})

# #         return {"message": "Image deleted successfully", "id": image_id}
# #     except Exception as e:
# #         if "Image not found" in str(e):
# #             raise e
# #         raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

# # # --- GET ALL IMAGES ---
# # @router.get("/images")
# # async def get_all_images():
# #     try:
# #         images = []
# #         for image in images_collection.find():
# #             images.append({
# #                 "id": str(image["_id"]),
# #                 "filename": image["filename"],
# #                 "path": image["path"],
# #                 "url": image.get("url", f"static/images/{image.get('unique_filename', image['filename'])}")
# #             })
        
# #         return {"images": images}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error fetching images: {str(e)}")

# # # --- SERVE IMAGE FILES ---
# # # This endpoint will serve images from the /tmp directory
# # @router.get("/serve/images/{filename}")
# # async def serve_image(filename: str):
# #     """Serve images from the /tmp directory"""
# #     try:
# #         file_path = os.path.join(IMAGES_DIR, filename)
        
# #         if not os.path.exists(file_path):
# #             raise HTTPException(status_code=404, detail="Image not found")
        
# #         # Import here to avoid dependency issues
# #         from fastapi.responses import FileResponse
# #         return FileResponse(file_path)
        
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

# from fastapi import APIRouter, UploadFile, File, HTTPException
# from typing import List
# from bson import ObjectId
# import shutil
# import os
# import uuid
# from pathlib import Path
# from api.utils.db import images_collection

# router = APIRouter()

# # Use writable directory for deployment environments
# STATIC_DIR = "/tmp/static"
# IMAGES_DIR = "/tmp/static/images"

# # Ensure directories exist
# os.makedirs(STATIC_DIR, exist_ok=True)
# os.makedirs(IMAGES_DIR, exist_ok=True)

# # --- BULK UPLOAD IMAGES ---
# @router.post("/images/upload_bulk")
# async def upload_bulk_images(files: List[UploadFile] = File(...)):
#     uploaded_urls = []
#     failed_uploads = []

#     for file in files:
#         try:
#             if not file.content_type.startswith("image/"):
#                 failed_uploads.append({
#                     "filename": file.filename,
#                     "error": "Not a valid image file"
#                 })
#                 continue

#             # Generate unique filename
#             file_extension = Path(file.filename).suffix
#             unique_filename = f"{uuid.uuid4()}{file_extension}"
            
#             # Save to writable directory (/tmp)
#             image_path = os.path.join(IMAGES_DIR, unique_filename)

#             # Save file to the writable directory
#             with open(image_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)

#             # FIXED: Use the serve endpoint URL consistently
#             image_url = f"/serve/images/{unique_filename}"

#             # Save to database
#             images_collection.insert_one({
#                 "filename": file.filename,
#                 "unique_filename": unique_filename,
#                 "path": image_path,  # Full path where file is actually stored
#                 "url": image_url,    # URL that points to serve endpoint
#                 "storage_location": "tmp"
#             })

#             uploaded_urls.append(image_url)

#         except Exception as e:
#             failed_uploads.append({"filename": file.filename, "error": str(e)})

#     return {
#         "urls": uploaded_urls,
#         "message": f"Successfully uploaded {len(uploaded_urls)} images",
#         "failed": failed_uploads
#     }

# # --- FETCH IMAGE BY ID ---
# @router.get("/images/{image_id}")
# async def get_image(image_id: str):
#     try:
#         image = images_collection.find_one({"_id": ObjectId(image_id)})
#         if not image:
#             raise HTTPException(status_code=404, detail="Image not found")

#         # FIXED: Generate consistent URL based on storage location
#         unique_filename = image.get("unique_filename", image["filename"])
        
#         # Check if it's stored in /tmp (new storage) or old static directory
#         if image.get("storage_location") == "tmp" or image["path"].startswith("/tmp"):
#             image_url = f"/serve/images/{unique_filename}"
#         else:
#             # For old images in static directory, use static URL
#             image_url = f"/static/images/{unique_filename}"

#         return {
#             "id": str(image["_id"]),
#             "filename": image["filename"],
#             "path": image["path"],
#             "url": image_url
#         }
#     except Exception as e:
#         if "Image not found" in str(e):
#             raise e
#         raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")

# # --- DELETE IMAGE BY ID ---
# @router.delete("/images/{image_id}")
# async def delete_image(image_id: str):
#     try:
#         image = images_collection.find_one({"_id": ObjectId(image_id)})
#         if not image:
#             raise HTTPException(status_code=404, detail="Image not found")

#         # Delete file from storage
#         if os.path.exists(image["path"]):
#             try:
#                 os.remove(image["path"])
#             except Exception as e:
#                 print(f"Warning: Could not delete file: {e}")

#         # Remove from database
#         images_collection.delete_one({"_id": ObjectId(image_id)})

#         return {"message": "Image deleted successfully", "id": image_id}
#     except Exception as e:
#         if "Image not found" in str(e):
#             raise e
#         raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

# # --- GET ALL IMAGES ---
# @router.get("/images")
# async def get_all_images():
#     try:
#         images = []
#         for image in images_collection.find():
#             # FIXED: Generate consistent URL based on storage location
#             unique_filename = image.get("unique_filename", image["filename"])
            
#             # Check if it's stored in /tmp (new storage) or old static directory
#             if image.get("storage_location") == "tmp" or image["path"].startswith("/tmp"):
#                 image_url = f"/serve/images/{unique_filename}"
#             else:
#                 # For old images in static directory, use static URL
#                 image_url = f"/static/images/{unique_filename}"
            
#             images.append({
#                 "id": str(image["_id"]),
#                 "filename": image["filename"],
#                 "path": image["path"],
#                 "url": image_url
#             })
        
#         return {"images": images}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching images: {str(e)}")

# # --- SERVE IMAGE FILES ---
# @router.get("/serve/images/{filename}")
# async def serve_image(filename: str):
#     """Serve images from the /tmp directory"""
#     try:
#         file_path = os.path.join(IMAGES_DIR, filename)
        
#         if not os.path.exists(file_path):
#             raise HTTPException(status_code=404, detail="Image not found")
        
#         from fastapi.responses import FileResponse
#         return FileResponse(file_path)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

# # --- MIGRATION ENDPOINT (Optional) ---
# @router.post("/images/migrate-to-tmp")
# async def migrate_images_to_tmp():
#     """
#     Optional endpoint to migrate old images from static/ to /tmp/static/
#     """
#     try:
#         migrated_count = 0
#         for image in images_collection.find({"storage_location": {"$ne": "tmp"}}):
#             old_path = image["path"]
            
#             # Skip if already in tmp or file doesn't exist
#             if old_path.startswith("/tmp") or not os.path.exists(old_path):
#                 continue
                
#             # Generate new path in /tmp
#             unique_filename = image.get("unique_filename", image["filename"])
#             new_path = os.path.join(IMAGES_DIR, unique_filename)
            
#             try:
#                 # Copy file to new location
#                 shutil.copy2(old_path, new_path)
                
#                 # Update database record
#                 images_collection.update_one(
#                     {"_id": image["_id"]},
#                     {
#                         "$set": {
#                             "path": new_path,
#                             "url": f"/serve/images/{unique_filename}",
#                             "storage_location": "tmp"
#                         }
#                     }
#                 )
                
#                 # Optionally remove old file
#                 # os.remove(old_path)
                
#                 migrated_count += 1
                
#             except Exception as e:
#                 print(f"Failed to migrate {old_path}: {e}")
#                 continue
        
#         return {"message": f"Migrated {migrated_count} images to /tmp storage"}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Migration error: {str(e)}")