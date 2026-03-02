import logging
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Cloudinary Configuration only if credentials are provided
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    logger.info("Cloudinary configured successfully.")
else:
    logger.warning("Cloudinary credentials not set. File uploads will fail.")

def upload_to_cloudinary(file: UploadFile, folder: str = "crm_docs") -> str:
    """
    Uploads a file to Cloudinary and returns the secure URL.
    
    Args:
        file: The file object from FastAPI
        folder: The folder name in Cloudinary (e.g., 'clients/101')
        
    Returns:
        The secure URL of the uploaded file.
    """
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise HTTPException(
            status_code=503,
            detail="Cloudinary is not configured. Please set CLOUDINARY environment variables."
        )

    try:
        # Read the file content
        file_content = file.file.read()
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type="auto",  # Automatically detect if it's an image or PDF
            public_id=file.filename.split('.')[0]  # Optional: use original filename
        )
        
        # Reset the file pointer just in case it's needed elsewhere
        file.file.seek(0)
        
        # Return the secure SSL URL
        return upload_result.get("secure_url")

    except Exception as e:
        logger.error(f"Cloudinary Upload Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload document to Cloudinary: {str(e)}"
        )
