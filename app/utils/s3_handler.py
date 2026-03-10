import logging
import re
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize boto3 client
s3_client = None
if (
    settings.AWS_ACCESS_KEY_ID
    and settings.AWS_SECRET_ACCESS_KEY
    and settings.AWS_REGION_NAME
):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )


def sanitize_filename(filename: str) -> str:
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-]", "", name)
    return name or "file"


def get_file_extension(filename: str) -> str:
    if filename and "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def is_valid_bucket_name(name: str) -> bool:
    """Checks if the bucket name follows S3 naming conventions (no underscores, 3-63 chars)."""
    if not name or len(name) < 3 or len(name) > 63:
        return False
    # Only lowercase, numbers, hyphens and dots allowed
    return bool(re.match(r"^[a-z0-9.-]+$", name))


def ensure_bucket_exists():
    """Ensures the S3 bucket exists, attempting to create it if it doesn't."""
    if not s3_client or not settings.AWS_S3_BUCKET_NAME:
        logger.error("AWS S3 client or Bucket Name not configured.")
        return False
    
    if not is_valid_bucket_name(settings.AWS_S3_BUCKET_NAME):
        logger.error(f"Invalid S3 bucket name: '{settings.AWS_S3_BUCKET_NAME}'. S3 buckets cannot have underscores.")
        return False

    try:
        s3_client.head_bucket(Bucket=settings.AWS_S3_BUCKET_NAME)
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        
        # If 404 (doesn't exist) or 403 (exists but can't see it), try to create it.
        # Sometimes restricted IAM users can Create but not List/Head.
        if error_code in ['404', '403', 'NoSuchBucket']:
            logger.info(f"S3 bucket '{settings.AWS_S3_BUCKET_NAME}' inaccessible or missing (Code: {error_code}). Attempting to create...")
            try:
                if settings.AWS_REGION_NAME == "us-east-1":
                    s3_client.create_bucket(Bucket=settings.AWS_S3_BUCKET_NAME)
                else:
                    s3_client.create_bucket(
                        Bucket=settings.AWS_S3_BUCKET_NAME,
                        CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION_NAME},
                    )
                logger.info(f"S3 bucket '{settings.AWS_S3_BUCKET_NAME}' created successfully.")
                return True
            except ClientError as ce:
                ce_code = ce.response.get("Error", {}).get("Code")
                if ce_code == 'AccessDenied':
                    logger.error(f"CRITICAL: Your AWS IAM user does not have 's3:CreateBucket' permissions. "
                                 f"Please create the bucket '{settings.AWS_S3_BUCKET_NAME}' manually in the AWS Console "
                                 f"or update your IAM policy.")
                else:
                    logger.error(f"Failed to create bucket: {ce}")
        return False


def upload_to_s3(file: UploadFile, folder: str = "crm_docs") -> str:
    """
    Standard S3 upload. Ensures bucket exists first.
    """
    if not s3_client or not settings.AWS_S3_BUCKET_NAME:
        raise HTTPException(status_code=503, detail="AWS S3 is not configured.")

    # 1. Ensure bucket exists before proceeding
    if not ensure_bucket_exists():
        raise HTTPException(
            status_code=500,
            detail=f"S3 Bucket '{settings.AWS_S3_BUCKET_NAME}' is inaccessible or invalid (S3 buckets cannot have underscores)."
        )

    try:
        file_content = file.file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        clean_stem = sanitize_filename(file.filename)
        file_extension = get_file_extension(file.filename)
        content_type = file.content_type or "application/octet-stream"

        # 2. Construct the virtual path
        object_key = f"{folder}/{clean_stem}"
        if file_extension:
            object_key = f"{object_key}.{file_extension}"

        logger.info("Uploading %r to S3 bucket %s...", file.filename, settings.AWS_S3_BUCKET_NAME)

        # 3. Upload file
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=object_key,
            Body=file_content,
            ContentType=content_type
        )

        file.file.seek(0)
        logger.info("Uploaded %r successfully to key: %s", file.filename, object_key)
        return object_key

    except HTTPException:
        raise
    except Exception as e:
        logger.error("S3 Upload Error: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")


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
