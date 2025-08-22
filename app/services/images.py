import os
import uuid
from typing import Tuple
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.config import MEDIA_ROOT, THUMBNAIL_SIZE


def _ensure_company_dirs(company_id: int) -> Tuple[str, str]:
    company_dir = os.path.join(MEDIA_ROOT, "companies", str(company_id))
    originals_dir = os.path.join(company_dir, "originals")
    thumbs_dir = os.path.join(company_dir, "thumbs")
    os.makedirs(originals_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)
    return originals_dir, thumbs_dir


def _validate_image_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
        )
    # Basic content-type check
    if not (file.content_type and file.content_type.startswith("image/")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only image uploads are allowed",
        )


async def save_company_image(company_id: int, file: UploadFile) -> Tuple[str, str, str]:
    _validate_image_upload(file)

    originals_dir, thumbs_dir = _ensure_company_dirs(company_id)

    _, ext = os.path.splitext(file.filename)
    ext = ext.lower() or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"

    orig_path_fs = os.path.join(originals_dir, unique_name)
    thumb_path_fs = os.path.join(thumbs_dir, unique_name)

    # Save original file to disk
    with open(orig_path_fs, "wb") as out:
        content = await file.read()
        out.write(content)

    # Verify and create thumbnail
    try:
        with Image.open(orig_path_fs) as img:
            img = img.convert("RGB")  # ensure compatible mode for common formats
            img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
            # Save thumbnail, let Pillow infer format from extension
            img.save(thumb_path_fs, quality=85)
    except Exception:
        # Cleanup saved file if image processing fails
        try:
            os.remove(orig_path_fs)
        except OSError:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file"
        )

    # Public URL paths (served by /media mount)
    rel_orig_url = f"/media/companies/{company_id}/originals/{unique_name}"
    rel_thumb_url = f"/media/companies/{company_id}/thumbs/{unique_name}"

    return unique_name, rel_orig_url, rel_thumb_url


def delete_company_image_files(filepath: str, thumbpath: str) -> None:
    """Best-effort cleanup of saved files by public URL paths."""

    def _to_fs(path: str) -> str:
        if path.startswith("/media/"):
            rel = path[len("/media/") :]
            return os.path.join(MEDIA_ROOT, rel)
        return path

    for path in (filepath, thumbpath):
        try:
            fs_path = _to_fs(path)
            if os.path.exists(fs_path):
                os.remove(fs_path)
        except OSError:
            # Ignore filesystem errors during cleanup
            pass
