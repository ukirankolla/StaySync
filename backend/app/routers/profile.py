from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import OtpCode, Profile, Questionnaire, User
from ..questionnaire import QUESTIONNAIRE
from ..schemas import (
    ProfileOut,
    ProfileUpdate,
    QuestionnaireAnswerRequest,
    QuestionnaireOut,
    VerifyProfileRequest,
)
from ..security import generate_otp, otp_expiry
from ..config import settings
from ..services.agents import get_agent
from ..services.events import track
from ..services.notify import send_otp

router = APIRouter(prefix="/profile", tags=["profile"])


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
    return {"answers": q.answers if q else {}, "completed": bool(q and q.completed_at)}


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
    return _mask_private(profile)


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


@router.post("/verify/request")
def request_verification(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    identifier = user.email or user.phone
    if not identifier:
        raise HTTPException(status_code=400, detail="Add an email or phone to your account first")
    code = generate_otp()
    db.add(OtpCode(identifier=identifier, code=code, purpose="verify", expires_at=otp_expiry()))
    db.commit()
    delivery = send_otp(identifier, code)
    return {"message": f"Verification code sent to {identifier}", "channel": delivery["channel"],
            "delivered": delivery["delivered"],
            "dev_code": code if (not delivery["delivered"] and settings.env == "development") else None}


@router.post("/verify/confirm", response_model=ProfileOut)
def confirm_verification(payload: VerifyProfileRequest, user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    identifier = user.email or user.phone
    if not identifier:
        raise HTTPException(status_code=400, detail="Add an email or phone to your account first")
    now = datetime.now(timezone.utc)
    otp = db.query(OtpCode).filter(
        OtpCode.identifier == identifier, OtpCode.purpose == "verify", OtpCode.is_used.is_(False)
    ).order_by(OtpCode.created_at.desc()).first()
    if not otp or otp.expires_at.replace(tzinfo=timezone.utc) < now or otp.code != payload.code:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    otp.is_used = True
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    profile.is_verified = True
    db.commit()
    track(db, user.id, "profile_verified", {})
    return ProfileOut.model_validate(profile)
