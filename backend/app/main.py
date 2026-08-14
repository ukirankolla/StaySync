from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import admin, auth, chat, groups, listings, matching, ml, moderation, profile
from .services import ml_model

MODEL_README = (
    "The ML model is not trained yet. Run `python scripts/train_model.py` "
    "or POST /api/ml/retrain to train it from synthetic data."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if not ml_model.model_available():
        print(f"[StaySync] ML model missing: {MODEL_README}")
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, profile, matching, chat, groups, listings, moderation, admin, ml):
    app.include_router(r.router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"app": "StaySync", "docs": "/docs", "api": settings.api_prefix}
