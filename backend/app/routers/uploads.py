import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from ..config import settings
from ..services import ratelimit
from ..deps import get_current_user
from ..models import User

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

router = APIRouter(prefix="/upload", tags=["upload"])


def _looks_like(content_type: str, data: bytes) -> bool:
    """Check the file's magic bytes: the Content-Type header is chosen by the client and can lie."""
    if content_type == "image/jpeg":
        return data[:3] == b"\xff\xd8\xff"
    if content_type == "image/png":
        return data[:8] == b"\x89PNG\r\n\x1a\n"
    if content_type == "image/webp":
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False


async def _upload_to_supabase(filename: str, data: bytes, content_type: str):
    if not settings.supabase_url or not settings.supabase_service_key.strip():
        print("[StaySync] Photo upload unavailable: SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
        raise HTTPException(status_code=503, detail="Photo uploads are temporarily unavailable.")
    bucket = settings.supabase_storage_bucket
    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{bucket}/{filename}"
    headers = {
        # Works with both the legacy service_role JWT and the newer sb_secret_ keys.
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": content_type,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.put(url, content=data, headers=headers)
    except httpx.HTTPError as exc:
        print(f"[StaySync] Supabase Storage request failed: {exc.__class__.__name__}")
        raise HTTPException(status_code=502, detail="Photo storage is unreachable. Please try again.")
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Supabase Storage upload failed ({resp.status_code})")


@router.post("/image")
async def upload_image(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    ext = ALLOWED_TYPES.get(file.content_type)
    if not ext:
        raise HTTPException(status_code=400, detail="Only JPG, PNG or WEBP images are allowed")
    ratelimit.hit(f"upload:{user.id}", 30, 600, "Too many uploads. Please wait a few minutes.")
    data = await file.read(MAX_SIZE + 1)
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
    if not _looks_like(file.content_type, data):
        raise HTTPException(status_code=400, detail="That file isn't a valid JPG, PNG or WEBP image")
    filename = f"{uuid.uuid4().hex}{ext}"

    if settings.storage_backend == "supabase":
        await _upload_to_supabase(filename, data, file.content_type)
        return {"url": f"{settings.supabase_url.rstrip('/')}/storage/v1/object/public/{settings.supabase_storage_bucket}/{filename}"}

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(data)
    base = settings.public_base_url.rstrip("/") if settings.public_base_url else ""
    return {"url": f"{base}/uploads/{filename}"}
