import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from ..config import settings
from ..deps import get_current_user
from ..models import User

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

router = APIRouter(prefix="/upload", tags=["upload"])


async def _upload_to_supabase(filename: str, data: bytes, content_type: str):
    bucket = settings.supabase_storage_bucket
    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": content_type,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.put(url, content=data, headers=headers)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Supabase Storage upload failed ({resp.status_code})")


@router.post("/image")
async def upload_image(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    ext = ALLOWED_TYPES.get(file.content_type)
    if not ext:
        raise HTTPException(status_code=400, detail="Only JPG, PNG or WEBP images are allowed")
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
    filename = f"{uuid.uuid4().hex}{ext}"

    if settings.storage_backend == "supabase":
        await _upload_to_supabase(filename, data, file.content_type)
        return {"url": f"{settings.supabase_url.rstrip('/')}/storage/v1/object/public/{settings.supabase_storage_bucket}/{filename}"}

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(data)
    base = settings.public_base_url.rstrip("/") if settings.public_base_url else ""
    return {"url": f"{base}/uploads/{filename}"}
