"""Roommate reviews. Only people who connected and actually chatted can review each other."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Connection, Message, Profile, RoommateReview, User
from ..services import ratelimit
from ..services.events import track

router = APIRouter(prefix="/reviews", tags=["reviews"])


class ReviewIn(BaseModel):
    connection_id: int
    rating: int = Field(ge=1, le=5)
    would_live_again: bool = True
    comment: str | None = Field(default=None, max_length=500)


def review_summary(db: Session, user_id: int) -> dict:
    count, avg = db.query(func.count(RoommateReview.id), func.avg(RoommateReview.rating)).filter(
        RoommateReview.reviewee_id == user_id).one()
    return {"count": count or 0, "average": round(float(avg), 1) if avg else None}


@router.post("")
def submit_review(payload: ReviewIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ratelimit.hit(f"review:{user.id}", 20, 3600, "Too many reviews. Please try again later.")
    conn = db.get(Connection, payload.connection_id)
    if not conn or user.id not in (conn.requester_id, conn.recipient_id) or conn.status != "accepted":
        raise HTTPException(status_code=404, detail="Connection not found")
    other = conn.recipient_id if conn.requester_id == user.id else conn.requester_id
    senders = {s for (s,) in db.query(Message.sender_id).filter(Message.connection_id == conn.id).distinct().all()}
    if not {user.id, other} <= senders:
        raise HTTPException(status_code=400, detail="You can review someone once you have both exchanged messages.")
    row = db.query(RoommateReview).filter(RoommateReview.reviewer_id == user.id,
                                          RoommateReview.connection_id == conn.id).first()
    comment = (payload.comment or "").strip() or None
    if row:
        row.rating, row.would_live_again, row.comment = payload.rating, payload.would_live_again, comment
    else:
        db.add(RoommateReview(reviewer_id=user.id, reviewee_id=other, connection_id=conn.id,
                              rating=payload.rating, would_live_again=payload.would_live_again, comment=comment))
    db.commit()
    track(db, user.id, "review_submitted", {"connection_id": conn.id, "rating": payload.rating})
    return {"saved": True}


@router.get("/mine")
def my_reviews(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Reviews I have written, keyed by connection id."""
    rows = db.query(RoommateReview).filter(RoommateReview.reviewer_id == user.id).all()
    return {r.connection_id: {"rating": r.rating, "would_live_again": r.would_live_again} for r in rows}


@router.get("/user/{user_id}")
def reviews_for(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target or not target.is_active or target.is_suspended:
        raise HTTPException(status_code=404, detail="User not found")
    rows = db.query(RoommateReview).filter(RoommateReview.reviewee_id == user_id).order_by(
        RoommateReview.created_at.desc()).limit(20).all()
    names = {p.user_id: p.full_name for p in db.query(Profile).filter(
        Profile.user_id.in_({r.reviewer_id for r in rows} or {0})).all()}
    total = db.query(func.count(RoommateReview.id)).filter(RoommateReview.reviewee_id == user_id).scalar() or 0
    yes = db.query(func.count(RoommateReview.id)).filter(RoommateReview.reviewee_id == user_id,
                                                         RoommateReview.would_live_again.is_(True)).scalar() or 0
    return {
        **review_summary(db, user_id),
        "would_live_again_pct": round(yes / total * 100) if total else None,
        "reviews": [{"reviewer": names.get(r.reviewer_id, "Member"), "rating": r.rating,
                     "would_live_again": r.would_live_again, "comment": r.comment,
                     "created_at": r.created_at.isoformat()} for r in rows],
    }
