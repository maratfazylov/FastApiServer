from fastapi import FastAPI, UploadFile, HTTPException, File, Query
from fastapi.responses import FileResponse, Response
import os
import uuid
import aiofiles
import filetype
from pathlib import Path
from PIL import Image
import io
import shutil
from typing import Optional, List

app = FastAPI(title="File Upload Service")

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create cache directory for thumbnails
THUMBNAIL_DIR = Path("thumbnails")
THUMBNAIL_DIR.mkdir(exist_ok=True)

# Supported mime types
SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
SUPPORTED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"]

@app.get("/")
async def root():
    """Root endpoint returning a welcome message"""
    return {"message": "Welcome to File Upload API", "version": "1.0.0"}

async def validate_file(file: UploadFile, file_type: str) -> bool:
    """
    Validate file based on its actual content (not just extension)
    
    Args:
        file: The uploaded file
        file_type: Either 'image' or 'video'
    
    Returns:
        bool: True if file is valid, False otherwise
    """
    # Read the first chunk of the file to detect its type
    content = await file.read(1024)
    # Reset file pointer to the beginning
    await file.seek(0)
    
    kind = filetype.guess(content)
    
    if not kind:
        return False
    
    if file_type == 'image':
        return kind.mime in SUPPORTED_IMAGE_TYPES
    elif file_type == 'video':
        return kind.mime in SUPPORTED_VIDEO_TYPES
    
    return False

@app.put("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Query(..., description="Type of file: 'image' or 'video'")
):
    """
    Upload a file with validation based on file type
    
    Args:
        file: The file to upload
        file_type: The type of file ('image' or 'video')
    
    Returns:
        dict: Object with file information including UUID
    """
    # Validate file_type parameter
    if file_type not in ['image', 'video']:
        raise HTTPException(status_code=400, detail="file_type must be 'image' or 'video'")
    
    # Validate file content
    is_valid = await validate_file(file, file_type)
    if not is_valid:
        valid_types = SUPPORTED_IMAGE_TYPES if file_type == 'image' else SUPPORTED_VIDEO_TYPES
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid {file_type} file. Supported types: {', '.join(valid_types)}"
        )
    
    # Generate UUID for the file
    file_uuid = str(uuid.uuid4())
    
    # Get file extension from content type
    content = await file.read(1024)
    await file.seek(0)
    kind = filetype.guess(content)
    extension = kind.extension if kind else file.filename.split('.')[-1]
    
    # Create file path with UUID
    file_path = UPLOAD_DIR / f"{file_uuid}.{extension}"
    
    # Save the file
    async with aiofiles.open(file_path, 'wb') as out_file:
        # Read the file in chunks and write to disk
        while content := await file.read(1024):
            await out_file.write(content)
    
    return {
        "uuid": file_uuid,
        "filename": file.filename,
        "file_type": file_type,
        "content_type": kind.mime if kind else "unknown",
        "size": os.path.getsize(file_path)
    }

def find_file_by_uuid(file_uuid: str):
    """
    Find a file in the upload directory by UUID
    
    Args:
        file_uuid: The UUID of the file to find
    
    Returns:
        Path: The path to the file if found, None otherwise
    """
    for file_path in UPLOAD_DIR.glob(f"{file_uuid}.*"):
        return file_path
    return None

def create_thumbnail(file_path: Path, width: int, height: int) -> Path:
    """
    Create a thumbnail for an image
    
    Args:
        file_path: Path to the image file
        width: Desired width
        height: Desired height
    
    Returns:
        Path: Path to the thumbnail
    """
    # Create thumbnail name based on original file name and dimensions
    thumbnail_name = f"{file_path.stem}_{width}x{height}.jpg"
    thumbnail_path = THUMBNAIL_DIR / thumbnail_name
    
    # Check if thumbnail already exists
    if thumbnail_path.exists():
        return thumbnail_path
    
    # Create thumbnail
    image = Image.open(file_path)
    image.thumbnail((width, height))
    image.save(thumbnail_path, format="JPEG")
    
    return thumbnail_path

@app.get("/api/{file_uuid}")
async def get_file(
    file_uuid: str,
    width: Optional[int] = None,
    height: Optional[int] = None
):
    """
    Get a file by its UUID, with optional thumbnail generation
    
    Args:
        file_uuid: The UUID of the file
        width: Optional width for thumbnail
        height: Optional height for thumbnail
    
    Returns:
        FileResponse: The requested file or thumbnail
    """
    # Find the file by UUID
    file_path = find_file_by_uuid(file_uuid)
    
    if not file_path:
        raise HTTPException(status_code=404, detail=f"File with UUID {file_uuid} not found")
    
    # Get file content type
    kind = filetype.guess(file_path)
    
    # If this is an image and width/height are specified, generate a thumbnail
    if kind and kind.mime in SUPPORTED_IMAGE_TYPES and (width or height):
        # Set default values if either dimension is missing
        width = width or 200
        height = height or 200
        
        # Create thumbnail
        thumbnail_path = create_thumbnail(file_path, width, height)
        
        return FileResponse(
            thumbnail_path,
            media_type="image/jpeg",
            filename=f"{file_uuid}_thumbnail.jpg"
        )
    
    # If this is a video with width/height, we would generate a video thumbnail here
    # This would require additional libraries like ffmpeg
    
    # Return the original file
    return FileResponse(
        file_path,
        media_type=kind.mime if kind else "application/octet-stream",
        filename=file_path.name
    ) 