from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .routers import admin, auth, chat, groups, listings, matching, ml, moderation, profile, uploads
from .services import ml_model

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

MODEL_README = (
    "The ML model is not trained yet. Run `python scripts/train_model.py` "
    "or POST /api/ml/retrain to train it from synthetic data."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("[StaySync] Database ready")
    except Exception as exc:  # noqa: BLE001
        print(f"[StaySync] DATABASE STARTUP FAILED: {exc}")
    if settings.seed_on_start:
        try:
            from scripts.seed import seed
            seed()
        except Exception as exc:  # noqa: BLE001
            print(f"[StaySync] Seed on start failed: {exc}")
    if not ml_model.model_available():
        print("[StaySync] Training ML model on boot…")
        try:
            print(ml_model.train())
        except Exception as exc:  # noqa: BLE001
            print(f"[StaySync] ML training failed: {exc}")
        if not ml_model.model_available():
            print(f"[StaySync] ML model still unavailable: {MODEL_README}")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="StaySync backend — roommate compatibility and flat-finding platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, profile, matching, chat, groups, listings, moderation, admin, ml, uploads):
    app.include_router(r.router, prefix=settings.api_prefix)

if settings.storage_backend == "local":
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"app": "StaySync", "docs": "/docs", "api": settings.api_prefix}
