from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Questionnaire, User
from ..services.ml_model import model_available, predict, train

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/status")
def status():
    return {"model_available": model_available(), "version": "1.0", "type": "random_forest_classifier"}


@router.post("/predict")
def predict_pair(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Predicts compatibility between the current user and everyone else (or uses ml/predict via matching)."""
    return {"message": "Use GET /matching/recommendations for per-user predictions.", "model_available": model_available()}


@router.post("/retrain")
def retrain():
    result = train(n=5000)
    return {"trained": True, "details": result}
