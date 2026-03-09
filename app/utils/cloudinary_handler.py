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
    name = re.sub(r"\s+", "_", name)       # replace spaces with underscore
    name = re.sub(r"[^\w\-]", "", name)    # remove special characters
    return name


def get_resource_type(content_type: str) -> str:
    """
    Determine Cloudinary resource type based on MIME type.
    """
    if content_type.startswith("image/"):
        return "image"

    if content_type == "application/pdf":
        return "raw"

    # fallback for docs, zip, etc.
    return "raw"


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.
    """
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


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

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # Clean filename
        clean_filename = sanitize_filename(file.filename)
        
        # Get file extension
        file_extension = get_file_extension(file.filename)

        # Determine resource type
        resource_type = get_resource_type(file.content_type)

        # For raw files, include extension in public_id for proper content-type handling
        public_id = clean_filename
        if resource_type == "raw" and file_extension:
            public_id = f"{clean_filename}.{file_extension}"

        # Upload file to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type=resource_type,
            public_id=public_id,
            overwrite=True,  # Allow overwriting if file with same name exists
            resource_type_format="auto",  # Let Cloudinary automatically detect format
        )

        # Reset file pointer (important if reused later)
        file.file.seek(0)

        # Extract secure URL
        secure_url = upload_result.get("secure_url")

        if not secure_url:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary did not return a valid URL."
            )

        return secure_url

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Cloudinary Upload Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document to Cloudinary: {str(e)}"
        )