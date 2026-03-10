import logging
import re
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize boto3 client
if (
    settings.AWS_ACCESS_KEY_ID
    and settings.AWS_SECRET_ACCESS_KEY
    and settings.AWS_REGION_NAME
    and settings.AWS_S3_BUCKET_NAME
):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )
    
    # Ensure bucket exists
    try:
        s3_client.head_bucket(Bucket=settings.AWS_S3_BUCKET_NAME)
        logger.info(f"S3 bucket '{settings.AWS_S3_BUCKET_NAME}' already exists and is accessible.")
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            logger.info(f"S3 bucket '{settings.AWS_S3_BUCKET_NAME}' does not exist. Creating it programmatically.")
            try:
                # If region is not us-east-1, LocationConstraint is required
                if settings.AWS_REGION_NAME == "us-east-1":
                    s3_client.create_bucket(Bucket=settings.AWS_S3_BUCKET_NAME)
                else:
                    s3_client.create_bucket(
                        Bucket=settings.AWS_S3_BUCKET_NAME,
                        CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION_NAME},
                    )
                logger.info(f"S3 bucket '{settings.AWS_S3_BUCKET_NAME}' created successfully.")
            except Exception as create_error:
                logger.error(f"Failed to create S3 bucket: {create_error}")
        else:
            logger.error(f"Error accessing S3 bucket: {e}")
            
    logger.info("AWS S3 configured successfully.")
else:
    s3_client = None
    logger.warning("AWS S3 credentials not fully set. File uploads will fail.")


def sanitize_filename(filename: str) -> str:
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-]", "", name)
    return name or "file"


def get_file_extension(filename: str) -> str:
    if filename and "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def upload_to_s3(file: UploadFile, folder: str = "crm_docs") -> str:
    """
    Standard S3 upload.
    Returns the Object Key, NOT the secure URL.
    """
    if not s3_client or not settings.AWS_S3_BUCKET_NAME:
        raise HTTPException(
            status_code=503,
            detail="AWS S3 is not configured. Please set AWS environment variables."
        )

    try:
        file_content = file.file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        clean_stem = sanitize_filename(file.filename)
        file_extension = get_file_extension(file.filename)
        content_type = file.content_type or "application/octet-stream"

        # Construct S3 Object Key
        object_key = f"{folder}/{clean_stem}"
        if file_extension:
            object_key = f"{object_key}.{file_extension}"

        logger.info("Uploading %r with content_type=%s to S3 bucket=%s key=%s", 
                    file.filename, content_type, settings.AWS_S3_BUCKET_NAME, object_key)

        # Upload file using put_object
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=object_key,
            Body=file_content,
            ContentType=content_type,
            # We don't set ACL='public-read' to keep it private as requested
        )

        file.file.seek(0)

        logger.info("Uploaded %r → %s [S3 Object Key]", file.filename, object_key)
        return object_key  # Return the object key instead of a full URL

    except HTTPException:
        raise
    except Exception as e:
        logger.error("S3 Upload Error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document to S3: {str(e)}"
        )


def generate_presigned_url(object_key: str, expiration: int = None) -> str:
    """
    Generate a presigned URL for the S3 object.
    """
    if not s3_client or not settings.AWS_S3_BUCKET_NAME:
         logger.warning("AWS S3 is not configured, returning original key as url fallback.")
         return object_key
         
    # Skip URL generation if it looks like an old Cloudinary HTTP URL
    if object_key.startswith("http://") or object_key.startswith("https://"):
        return object_key

    try:
        expiry = expiration or settings.S3_PRESIGNED_URL_EXPIRY_SECONDS
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_S3_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=expiry
        )
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL for {object_key}: {e}")
        return object_key # Return raw key on error so UI handles it gracefully
