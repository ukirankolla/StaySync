"""Post-connection feedback: the deck measures outcomes (fit, conversations, living together)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Connection, MatchFeedback, User
from ..services.events import track

router = APIRouter(prefix="/feedback", tags=["feedback"])

OUTCOMES = {"talking", "viewing", "living_together", "not_continuing"}


class FeedbackIn(BaseModel):
    connection_id: int
    fits: bool
    outcome: str = "talking"
    comment: str | None = Field(default=None, max_length=1000)


@router.post("")
def submit_feedback(payload: FeedbackIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.outcome not in OUTCOMES:
        raise HTTPException(status_code=400, detail=f"outcome must be one of {sorted(OUTCOMES)}")
    conn = db.get(Connection, payload.connection_id)
    if not conn or user.id not in (conn.requester_id, conn.recipient_id) or conn.status != "accepted":
        raise HTTPException(status_code=404, detail="Connection not found")
    row = db.query(MatchFeedback).filter(MatchFeedback.user_id == user.id,
                                         MatchFeedback.connection_id == conn.id).first()
    if row:  # users can update their answer
        row.fits, row.outcome, row.comment = payload.fits, payload.outcome, payload.comment
    else:
        db.add(MatchFeedback(user_id=user.id, connection_id=conn.id, fits=payload.fits,
                             outcome=payload.outcome, comment=payload.comment))
    db.commit()
    track(db, user.id, "match_feedback", {"connection_id": conn.id, "fits": payload.fits, "outcome": payload.outcome})
    return {"saved": True}


@router.get("/mine")
def my_feedback(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(MatchFeedback).filter(MatchFeedback.user_id == user.id).all()
    return {r.connection_id: {"fits": r.fits, "outcome": r.outcome} for r in rows}
