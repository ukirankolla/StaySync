from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Block, Listing, Report, User
from ..schemas import BlockRequest, ReportCreate, ReportOut
from ..services.agents import get_agent
from ..services.events import track

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.post("/report", response_model=ReportOut)
def create_report(payload: ReportCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.target_type == "user":
        if not payload.target_user_id:
            raise HTTPException(status_code=400, detail="target_user_id required")
        target = db.get(User, payload.target_user_id)
        if not target:
            raise HTTPException(status_code=404, detail="Target user not found")
    elif payload.target_type == "listing":
        if not payload.listing_id:
            raise HTTPException(status_code=400, detail="listing_id required")
        listing = db.get(Listing, payload.listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
    else:
        raise HTTPException(status_code=400, detail="target_type must be user or listing")

    moderation = get_agent("moderation").run(payload.reason, payload.details)
    report = Report(reporter_id=user.id, target_user_id=payload.target_user_id,
                    listing_id=payload.listing_id, target_type=payload.target_type,
                    reason=payload.reason, details=payload.details, severity=moderation["severity"])
    db.add(report)
    db.commit()
    db.refresh(report)
    track(db, user.id, "report_created", {"report_id": report.id, "severity": report.severity})
    return ReportOut.model_validate(report)


@router.post("/block")
def block_user(payload: BlockRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    target = db.get(User, payload.user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.scalar(select(Block).where(Block.blocker_id == user.id, Block.blocked_id == payload.user_id))
    if not existing:
        db.add(Block(blocker_id=user.id, blocked_id=payload.user_id))
        db.commit()
    track(db, user.id, "user_blocked", {"blocked_id": payload.user_id})
    return {"blocked": True}


@router.get("/blocked", response_model=list[int])
def my_blocks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [b[0] for b in db.query(Block.blocked_id).filter(Block.blocker_id == user.id).all()]


def _resolve_report(db: Session, report: Report, action: str, admin: User) -> None:
    now = datetime.now(timezone.utc)
    if action == "resolve":
        report.status = "resolved"
        listing = db.get(Listing, report.listing_id) if report.listing_id else None
        if listing:
            listing.is_active = False
    elif action == "dismiss":
        report.status = "dismissed"
    elif action == "suspend_user":
        report.status = "resolved"
        if report.target_user_id:
            target = db.get(User, report.target_user_id)
            if target:
                target.is_suspended = True
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    report.resolved_by = admin.id
    report.resolved_at = now
