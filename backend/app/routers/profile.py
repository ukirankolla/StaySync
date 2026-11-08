from datetime import datetime, timezone

import secrets as _secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import OtpCode, Profile, Questionnaire, User
from ..questionnaire import QUESTIONNAIRE, normalize_answers
from ..services.demo import is_demo_email
from ..services.matching import lifestyle_badges
from ..schemas import (
    ProfileOut,
    ProfileUpdate,
    QuestionnaireAnswerRequest,
    QuestionnaireOut,
)
from ..security import generate_otp, otp_expiry
from ..config import settings
from ..services.agents import get_agent
from ..services import ratelimit
from ..services.events import track
from ..services.notify import send_otp

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me/strength")
def profile_strength(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """How complete the profile is, and what to add next (complete profiles get better matches)."""
    p = db.query(Profile).filter(Profile.user_id == user.id).first()
    q = db.query(Questionnaire).filter(Questionnaire.user_id == user.id).first()
    checks = [
        ("name", "Add your name", 5, bool(p and p.full_name)),
        ("age", "Add your age", 10, bool(p and p.age)),
        ("city", "Add your city", 10, bool(p and p.city)),
        ("budget", "Set your budget", 10, bool(p and p.budget_min)),
        ("move_in", "Add your move-in date", 5, bool(p and p.move_in_date)),
        ("bio", "Write a short bio", 10, bool(p and p.bio)),
        ("photo", "Add a photo", 15, bool(p and p.photos)),
        ("questionnaire", "Complete the lifestyle questionnaire", 35, bool(q and q.completed_at)),
    ]
    return {
        "percent": sum(pts for _, _, pts, ok in checks if ok),
        "missing": [{"key": k, "label": label, "points": pts} for k, label, pts, ok in checks if not ok],
    }


@router.get("/me", response_model=ProfileOut)
def get_my_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOut.model_validate(profile)


@router.put("/me", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id, full_name="", city="")
        db.add(profile)
        db.flush()
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    track(db, user.id, "profile_updated", {})
    return ProfileOut.model_validate(profile)


@router.get("/questionnaire", response_model=QuestionnaireOut)
def get_questionnaire():
    return QuestionnaireOut()


@router.get("/questionnaire/answers", response_model=dict)
def get_my_answers(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Questionnaire).filter(Questionnaire.user_id == user.id).first()
    return {"answers": normalize_answers(q.answers) if q else {}, "completed": bool(q and q.completed_at)}


@router.put("/questionnaire", response_model=dict)
def save_questionnaire(payload: QuestionnaireAnswerRequest, user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    allowed = {q["key"] for q in QUESTIONNAIRE}
    unknown = set(payload.answers) - allowed
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown question keys: {sorted(unknown)}")

    q = db.query(Questionnaire).filter(Questionnaire.user_id == user.id).first()
    if not q:
        q = Questionnaire(user_id=user.id, answers={})
        db.add(q)
    q.answers = payload.answers

    q.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(q)

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    progress = get_agent("onboarding").run(
        profile={k: getattr(profile, k, None) for k in
                 ("full_name", "city", "budget_min", "move_in_date")} if profile else {},
        answers=payload.answers,
    )
    track(db, user.id, "questionnaire_completed", {})
    return {"answers": q.answers, "completed": True, "onboarding": progress}


@router.get("/{user_id}", response_model=ProfileOut)
def get_public_profile(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == user.id:
        return get_my_profile(user, db)
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile or not profile.is_visible:
        raise HTTPException(status_code=404, detail="Profile not found")
    out = _mask_private(profile)
    owner = db.get(User, user_id)
    out.is_demo = is_demo_email(owner.email if owner else None)
    if (profile.privacy or {}).get("lifestyle") is not False:
        q = db.query(Questionnaire).filter(Questionnaire.user_id == user_id).first()
        out.badges = lifestyle_badges(q.answers if q else {})
    return out


def _mask_private(profile: Profile) -> ProfileOut:
    """Hide fields the owner marked private when viewed by other users."""
    out = ProfileOut.model_validate(profile)
    priv = profile.privacy or {}
    if priv.get("age") is False:
        out.age = None
    if priv.get("occupation") is False:
        out.occupation = None
        out.occupation_detail = None
    if priv.get("budget") is False:
        out.budget_min = None
        out.budget_max = None
    if priv.get("bio") is False:
        out.bio = None
    if priv.get("move_in_date") is False:
        out.move_in_date = None
    if priv.get("photos") is False:
        out.photos = []
    return out
