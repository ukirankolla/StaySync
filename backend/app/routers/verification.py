from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Profile, User, Verification
from ..schemas import VerificationOut, VerificationSubmit
from ..services.events import track

router = APIRouter(prefix="/verification", tags=["verification"])

ID_TYPES = {"passport", "driving_license", "national_id", "student_id", "other"}


@router.get("/me", response_model=VerificationOut | None)
def my_verification(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    latest = (
        db.query(Verification)
        .filter(Verification.user_id == user.id)
        .order_by(Verification.created_at.desc())
        .first()
    )
    return VerificationOut.model_validate(latest) if latest else None


@router.post("/submit", response_model=VerificationOut)
def submit_verification(payload: VerificationSubmit, user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if payload.id_type not in ID_TYPES:
        raise HTTPException(status_code=400, detail=f"id_type must be one of: {sorted(ID_TYPES)}")

    pending = (
        db.query(Verification)
        .filter(Verification.user_id == user.id, Verification.status == "pending")
        .first()
    )
    if pending:
        raise HTTPException(status_code=409, detail="You already have a verification under review")

    record = Verification(
        user_id=user.id,
        id_type=payload.id_type,
        id_number=payload.id_number.strip() if payload.id_number else None,
        document_url=payload.document_url,
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    track(db, user.id, "id_verification_submitted", {"id_type": payload.id_type})
    return VerificationOut.model_validate(record)
