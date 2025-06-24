import os
import logging
import uuid
from fastapi import UploadFile
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Define allowed file types and sizes
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
ALLOWED_SPREADSHEET_TYPES = ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Base upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

def validate_file(file: UploadFile, allowed_types: list = None, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, str]:
    """
    Validate a file based on its type and size
    
    Args:
        file: The uploaded file
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if file is None:
        return True, ""
        
    # If no specific allowed types are provided, allow all types
    if allowed_types is None:
        allowed_types = ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES + ALLOWED_SPREADSHEET_TYPES
    
    # Check file type
    content_type = file.content_type
    if content_type not in allowed_types:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
    
    # Check file size
    file_contents = file.file.read()
    file_size = len(file_contents)
    
    if file_size > max_size:
        return False, f"File size exceeds maximum allowed ({max_size / (1024 * 1024):.1f}MB)"
    
    return True, ""

async def save_file(file: UploadFile, subdirectory: str) -> Optional[str]:
    """
    Save an uploaded file to a specified subdirectory
    
    Args:
        file: The uploaded file
        subdirectory: The subdirectory to save the file in
        
    Returns:
        The file path or None if file could not be saved
    """
    if file is None:
        return None
    
    # Create directory if it doesn't exist
    directory = os.path.join(UPLOAD_DIR, subdirectory)
    os.makedirs(directory, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(directory, new_filename)
    
    try:
        # Write file contents
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Return the relative path
        return os.path.join(subdirectory, new_filename)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return None 