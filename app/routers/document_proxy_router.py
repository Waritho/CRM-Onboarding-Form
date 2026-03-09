"""
document_proxy_router.py
────────────────────────
Provides GET /documents/view  — a lightweight proxy that fetches a raw
Cloudinary asset and re-serves it to the browser with the correct
Content-Type so that PDFs (and other documents) open inline instead of
being silently blocked or downloaded with the wrong MIME type.

Why is this needed?
───────────────────
Cloudinary stores non-image files as `resource_type="raw"`.  For the CDN
URL to remain publicly accessible (HTTP 200), the public_id must NOT include
the file extension (e.g. ".pdf").  Without the extension, however, Cloudinary
serves the file as `application/octet-stream`, which causes browsers to
download the file rather than render it inline.

This proxy solves both problems:
  1. The Cloudinary URL (stored in the DB) always returns HTTP 200.
  2. The browser gets the correct Content-Type (e.g. application/pdf) and
     can render the document inline.

Usage (frontend)
────────────────
Instead of pointing an <iframe> / <a> directly at the Cloudinary URL, use:

    /documents/view?url=<cloudinary_url_with_ext_param>

The ?ext=pdf query param is automatically appended by upload_to_cloudinary().
"""

import urllib.request
import urllib.error
import mimetypes

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/documents",
    tags=["Document Proxy"]
)

# Map of extensions to MIME types (supplements Python's mimetypes module)
MIME_OVERRIDES = {
    "pdf":  "application/pdf",
    "doc":  "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls":  "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt":  "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "png":  "image/png",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "gif":  "image/gif",
    "webp": "image/webp",
    "txt":  "text/plain",
    "csv":  "text/csv",
    "zip":  "application/zip",
}


def _resolve_mime(ext: str) -> str:
    """Return the MIME type for *ext* (without leading dot, lowercased)."""
    ext = ext.lower().lstrip(".")
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    guessed, _ = mimetypes.guess_type(f"file.{ext}")
    return guessed or "application/octet-stream"


def _strip_ext_param(url: str):
    """
    Split off our custom ``?ext=<ext>`` query param from a Cloudinary URL.

    Returns (clean_url, ext_or_empty_string).
    """
    if "?ext=" in url:
        clean_url, ext = url.rsplit("?ext=", 1)
        # Remove any further query params appended after the ext value
        ext = ext.split("&")[0]
        return clean_url, ext
    return url, ""


@router.get("/view")
def view_document(
    url: str = Query(..., description="Cloudinary URL (with optional ?ext=pdf)")
):
    """
    Fetch a Cloudinary raw asset and stream it to the client with the
    correct Content-Type so the browser can render it inline.

    Parameters
    ----------
    url : str
        The full Cloudinary URL, optionally including ``?ext=<extension>``
        as appended by ``upload_to_cloudinary()``.
    """
    cloudinary_url, ext = _strip_ext_param(url)

    if not cloudinary_url.startswith("https://res.cloudinary.com/"):
        raise HTTPException(status_code=400, detail="Invalid document URL.")

    content_type = _resolve_mime(ext) if ext else "application/octet-stream"

    try:
        req = urllib.request.Request(
            cloudinary_url,
            headers={"User-Agent": "CRM-Document-Proxy/1.0"},
        )
        response = urllib.request.urlopen(req, timeout=15)
        data = response.read()

    except urllib.error.HTTPError as e:
        raise HTTPException(
            status_code=e.code,
            detail=f"Could not fetch document from storage (HTTP {e.code})."
        )
    except urllib.error.URLError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach document storage: {e.reason}"
        )

    return StreamingResponse(
        iter([data]),
        media_type=content_type,
        headers={
            # "inline" → browser tries to render; "attachment" → forces download
            "Content-Disposition": f'inline; filename="document.{ext or "bin"}"',
            "Content-Length": str(len(data)),
            # Allow the frontend (any origin) to request this endpoint
            "Access-Control-Allow-Origin": "*",
        }
    )
