import logging
import re
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

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
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-]", "", name)
    return name or "file"


def get_resource_type(content_type: str) -> str:
    if content_type and content_type.startswith("image/"):
        return "image"
    return "raw"


def get_file_extension(filename: str) -> str:
    if filename and "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def upload_to_cloudinary(file: UploadFile, folder: str = "crm_docs") -> str:
    """
    Standard Cloudinary upload.
    Files matching "image/*" go to resource_type "image".
    PDFs/documents go to "raw", WITH their original file extension appended 
    to tracking public_id natively, so browsers can render it correctly.
    """
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise HTTPException(
            status_code=503,
            detail="Cloudinary is not configured. Please set CLOUDINARY environment variables."
        )

    try:
        file_content = file.file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        clean_stem = sanitize_filename(file.filename)
        file_extension = get_file_extension(file.filename)
        content_type = file.content_type or ""
        resource_type = get_resource_type(content_type)

        # For proper Content-Type serving (making PDFs open in-browser), 
        # Cloudinary needs the extension in the public_id for "raw" assets.
        public_id = clean_stem
        if resource_type == "raw" and file_extension:
            public_id = f"{clean_stem}.{file_extension}"

        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type=resource_type,
            public_id=public_id,
            overwrite=True,
            # Removed invalid "resource_type_format" flag which caused errors.
        )

        file.file.seek(0)
        secure_url = upload_result.get("secure_url", "")

        if not secure_url:
            raise HTTPException(status_code=500, detail="Cloudinary did not return a valid URL.")

        logger.info("Uploaded %r → %s", file.filename, secure_url)
        return secure_url

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Cloudinary Upload Error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document to Cloudinary: {str(e)}"
        )