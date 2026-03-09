import logging
import re
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Cloudinary if credentials are provided
if (
    settings.CLOUDINARY_CLOUD_NAME
    and settings.CLOUDINARY_API_KEY
    and settings.CLOUDINARY_API_SECRET
):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    logger.info("Cloudinary configured successfully.")
else:
    logger.warning("Cloudinary credentials not set. File uploads will fail.")


def sanitize_filename(filename: str) -> str:
    """
    Remove spaces and special characters from filename
    """
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\s+", "_", name)          # replace spaces with underscore
    name = re.sub(r"[^\w\-]", "", name)       # remove special characters
    return name


def upload_to_cloudinary(file: UploadFile, folder: str = "crm_docs") -> str:
    """
    Uploads a file to Cloudinary and returns the secure URL.

    Args:
        file: FastAPI UploadFile object
        folder: Target folder in Cloudinary

    Returns:
        Secure URL of uploaded file
    """

    if not settings.CLOUDINARY_CLOUD_NAME:
        raise HTTPException(
            status_code=503,
            detail="Cloudinary is not configured. Please set CLOUDINARY environment variables."
        )

    try:
        # Read file content
        file_content = file.file.read()

        # Clean filename
        clean_filename = sanitize_filename(file.filename)

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type="auto",     # Automatically detect image/pdf/other
            public_id=clean_filename,
            use_filename=True,
            unique_filename=True
        )

        # Reset file pointer if needed later
        file.file.seek(0)

        # Return secure URL
        return upload_result.get("secure_url")

    except Exception as e:
        logger.error(f"Cloudinary Upload Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document to Cloudinary: {str(e)}"
        )