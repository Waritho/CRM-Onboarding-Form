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
    Return a clean filename stem (no extension) safe for use as a Cloudinary
    public_id:  spaces → underscores, all non-word / non-dash chars removed.
    """
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-]", "", name)
    return name or "file"


def get_resource_type(content_type: str) -> str:
    """
    Map a MIME type to the matching Cloudinary resource_type.

    - image/*            → "image"
    - everything else    → "raw"   (PDFs, Word docs, spreadsheets, zips …)

    NOTE: Do NOT use resource_type="auto" for documents.  When Cloudinary
    detects a PDF via auto-detection it stores it as resource_type="image",
    which then generates a URL ending in ".pdf" that Cloudinary's CDN blocks
    with HTTP 401 unless specific delivery rules are configured on the account.
    """
    if content_type and content_type.startswith("image/"):
        return "image"
    return "raw"


def get_file_extension(filename: str) -> str:
    """Return the lowercased extension of *filename* without the leading dot."""
    if filename and "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def upload_to_cloudinary(file: UploadFile, folder: str = "crm_docs") -> str:
    """
    Upload a file to Cloudinary and return the accessible secure URL.

    Design decisions
    ----------------
    * **raw public_id must never contain the file extension.**
      When a raw asset's public_id ends with a recognised extension
      (e.g. ".pdf") Cloudinary's CDN returns HTTP 401 / 403 unless the
      account has explicit delivery-profile allow-list rules.  By omitting
      the extension from public_id we get a stable 200 OK URL for raw files.

    * **The file extension is stored separately** (appended to the URL as a
      custom query parameter ``?ext=pdf``).  This lets our proxy endpoint
      ``GET /documents/view`` reconstruct the correct Content-Type when
      streaming the file to the browser.

    Returns
    -------
    str
        The secure Cloudinary URL, e.g.
        ``https://res.cloudinary.com/.../raw/upload/v1/folder/my_doc?ext=pdf``
        for raw files, or a plain image URL for images.
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

        # ── public_id: stem only, never include the extension ──────────────
        clean_stem      = sanitize_filename(file.filename)
        file_extension  = get_file_extension(file.filename)
        content_type    = file.content_type or ""
        resource_type   = get_resource_type(content_type)

        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type=resource_type,
            public_id=clean_stem,       # ← NO extension here
            overwrite=True,
        )

        file.file.seek(0)

        secure_url: str = upload_result.get("secure_url", "")

        if not secure_url:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary did not return a valid URL."
            )

        # For raw assets, embed the original extension as a query param so the
        # frontend / proxy can serve the file with the correct Content-Type
        # (e.g. application/pdf) without needing it in the path.
        if resource_type == "raw" and file_extension:
            secure_url = f"{secure_url}?ext={file_extension}"

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