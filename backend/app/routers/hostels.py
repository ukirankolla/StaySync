"""College / hostel room allocation: intake -> matching -> staff review -> final allocation.

Principles from the SyncStay deck: staff keep control (they can edit every suggestion and make the final
call), students consent before staff can see their answers, scores are suggestions not guarantees, and
students have a documented way to request a change.
"""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Hostel, HostelChangeRequest, HostelMember, Profile, Questionnaire, User
from ..questionnaire import WEIGHTS
from ..services import ratelimit
from ..services.events import track
from ..services.matching import compute_compatibility

router = APIRouter(prefix="/hostels", tags=["hostels"])

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
LIFESTYLE_CATS = [c for c in WEIGHTS if c != "budget_location"]  # allocation compares habits, not budgets


# ------------------------------------------------------------------ helpers
def _pair(qa: dict, qb: dict) -> dict:
    """Habit-only compatibility for two students (budget/location are irrelevant inside one hostel)."""
    res = compute_compatibility(qa, qb, {}, {})
    cats = res["category_scores"]
    used = [(cats[c], WEIGHTS[c]) for c in LIFESTYLE_CATS if cats.get(c) is not None]
    score = round(sum(s * w for s, w in used) / sum(w for _, w in used), 1) if used else None
    reasons = [r for r in res["reasons"] if "budget" not in r.lower() and "area" not in r.lower()]
    return {"score": score, "reasons": reasons}


def _get_hostel(db: Session, hostel_id: int) -> Hostel:
    h = db.get(Hostel, hostel_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hostel not found")
    return h


def _is_staff(user: User, h: Hostel) -> bool:
    return user.id == h.owner_id or user.role == "admin"


def _require_staff(db: Session, user: User, hostel_id: int) -> Hostel:
    h = _get_hostel(db, hostel_id)
    if not _is_staff(user, h):
        raise HTTPException(status_code=404, detail="Hostel not found")  # don't reveal it exists
    return h


def _answers(db: Session, user_id: int) -> dict:
    q = db.query(Questionnaire).filter(Questionnaire.user_id == user_id).first()
    return q.answers if q and q.completed_at else {}


def _name(db: Session, user_id: int) -> str:
    p = db.query(Profile).filter(Profile.user_id == user_id).first()
    return p.full_name if p else "Student"


def _rooms(db: Session, h: Hostel, members: list[HostelMember]) -> list[dict]:
    by_room: dict[str, list[HostelMember]] = {}
    for m in members:
        if m.room_no:
            by_room.setdefault(m.room_no, []).append(m)
    out = []
    for room_no in sorted(by_room, key=lambda r: (len(r), r)):
        ms = by_room[room_no]
        pairs = []
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                p = _pair(_answers(db, ms[i].user_id), _answers(db, ms[j].user_id))
                pairs.append({"a": _name(db, ms[i].user_id), "b": _name(db, ms[j].user_id), **p})
        scores = [p["score"] for p in pairs if p["score"] is not None]
        out.append({
            "room_no": room_no,
            "block": ms[0].block,
            "status": "approved" if all(m.status == "approved" for m in ms) else "suggested",
            "members": [{"user_id": m.user_id, "name": _name(db, m.user_id), "special_request": m.special_request}
                        for m in ms],
            "score": round(sum(scores) / len(scores), 1) if scores else None,
            "reasons": list(dict.fromkeys(r for p in pairs for r in p["reasons"]))[:4],
            "needs_attention": bool(scores) and min(scores) < 60,
            "over_capacity": len(ms) > h.room_size,
        })
    return out


# ------------------------------------------------------------------ schemas
class HostelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    institution: str | None = Field(default=None, max_length=160)
    room_size: int = Field(default=2, ge=2, le=6)


class JoinRequest(BaseModel):
    code: str = Field(min_length=4, max_length=12)
    block: str = Field(default="General", min_length=1, max_length=80)
    special_request: str | None = Field(default=None, max_length=500)
    consent: bool


class MemberUpdate(BaseModel):
    room_no: str | None = Field(default=None, max_length=32)
    block: str | None = Field(default=None, max_length=80)


class ChangeRequestIn(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class ChangeDecision(BaseModel):
    decision: str  # approve | decline
    staff_note: str | None = Field(default=None, max_length=1000)


# ------------------------------------------------------------------ endpoints
@router.post("")
def create_hostel(payload: HostelCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ratelimit.hit(f"hostel:{user.id}", 10, 3600, "Too many hostels created. Please try again later.")
    code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(8))
    h = Hostel(owner_id=user.id, name=payload.name.strip(), institution=payload.institution,
               room_size=payload.room_size, join_code=code)
    db.add(h)
    db.commit()
    db.refresh(h)
    track(db, user.id, "hostel_created", {"hostel_id": h.id})
    return {"id": h.id, "name": h.name, "join_code": h.join_code, "room_size": h.room_size}


@router.get("")
def my_hostels(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    run = db.query(Hostel).filter(Hostel.owner_id == user.id).all()
    joined = (db.query(Hostel, HostelMember).join(HostelMember, HostelMember.hostel_id == Hostel.id)
              .filter(HostelMember.user_id == user.id).all())
    return {
        "managed": [{"id": h.id, "name": h.name, "institution": h.institution, "join_code": h.join_code,
                     "room_size": h.room_size, "allocation_final": h.allocation_final,
                     "students": db.query(HostelMember).filter(HostelMember.hostel_id == h.id).count()}
                    for h in run],
        "joined": [{"id": h.id, "name": h.name, "institution": h.institution,
                    "allocation_final": h.allocation_final, "status": m.status, "block": m.block}
                   for h, m in joined],
    }


@router.post("/join")
def join_hostel(payload: JoinRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ratelimit.hit(f"hostel-join:{user.id}", 10, 3600, "Too many attempts. Please try again later.")
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Please agree to share your lifestyle answers with the hostel staff.")
    h = db.query(Hostel).filter(Hostel.join_code == payload.code.strip().upper()).first()
    if not h:
        raise HTTPException(status_code=404, detail="That code doesn't match any hostel.")
    if h.owner_id == user.id:
        raise HTTPException(status_code=400, detail="You run this hostel; students join with the code.")
    if not _answers(db, user.id):
        raise HTTPException(status_code=400, detail="Complete the lifestyle questionnaire first, then join.")
    if h.allocation_final:
        raise HTTPException(status_code=400, detail="Allocation for this hostel is already final. Ask the hostel staff.")
    m = db.query(HostelMember).filter(HostelMember.hostel_id == h.id, HostelMember.user_id == user.id).first()
    if m:
        m.block, m.special_request = payload.block.strip(), payload.special_request
    else:
        db.add(HostelMember(hostel_id=h.id, user_id=user.id, block=payload.block.strip(),
                            special_request=payload.special_request))
    db.commit()
    track(db, user.id, "hostel_joined", {"hostel_id": h.id})
    return {"joined": True, "hostel_id": h.id, "name": h.name}


@router.delete("/{hostel_id}/membership")
def leave_hostel(hostel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Students can withdraw and delete the data they shared with this hostel."""
    m = db.query(HostelMember).filter(HostelMember.hostel_id == hostel_id, HostelMember.user_id == user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Not a member")
    db.delete(m)
    db.commit()
    return {"left": True}


@router.get("/{hostel_id}")
def hostel_detail(hostel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = _get_hostel(db, hostel_id)
    members = db.query(HostelMember).filter(HostelMember.hostel_id == h.id).all()
    if _is_staff(user, h):
        changes = db.query(HostelChangeRequest).filter(HostelChangeRequest.hostel_id == h.id).order_by(
            HostelChangeRequest.created_at.desc()).all()
        return {
            "role": "staff",
            "hostel": {"id": h.id, "name": h.name, "institution": h.institution, "join_code": h.join_code,
                       "room_size": h.room_size, "allocation_final": h.allocation_final},
            "unassigned": [{"user_id": m.user_id, "name": _name(db, m.user_id), "block": m.block,
                            "special_request": m.special_request} for m in members if not m.room_no],
            "rooms": _rooms(db, h, members),
            "change_requests": [{"id": c.id, "student": _name(db, c.user_id), "user_id": c.user_id,
                                 "reason": c.reason, "status": c.status, "staff_note": c.staff_note}
                                for c in changes],
        }
    mine = next((m for m in members if m.user_id == user.id), None)
    if not mine:
        raise HTTPException(status_code=404, detail="Hostel not found")
    roommates, room_score, reasons = [], None, []
    if h.allocation_final and mine.room_no and mine.status == "approved":  # only share once staff finalise
        mates = [m for m in members if m.room_no == mine.room_no and m.user_id != user.id]
        roommates = [_name(db, m.user_id) for m in mates]
        pairs = [_pair(_answers(db, user.id), _answers(db, m.user_id)) for m in mates]
        sc = [p["score"] for p in pairs if p["score"] is not None]
        room_score = round(sum(sc) / len(sc), 1) if sc else None
        reasons = list(dict.fromkeys(r for p in pairs for r in p["reasons"]))[:4]
    my_changes = db.query(HostelChangeRequest).filter(HostelChangeRequest.hostel_id == h.id,
                                                      HostelChangeRequest.user_id == user.id).all()
    return {
        "role": "student",
        "hostel": {"id": h.id, "name": h.name, "institution": h.institution, "allocation_final": h.allocation_final},
        "my": {"block": mine.block, "status": mine.status, "room_no": mine.room_no if h.allocation_final else None},
        "roommates": roommates, "room_score": room_score, "reasons": reasons,
        "change_requests": [{"id": c.id, "reason": c.reason, "status": c.status, "staff_note": c.staff_note}
                            for c in my_changes],
    }


@router.post("/{hostel_id}/suggest")
def suggest_rooms(hostel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Group students into rooms by habit compatibility, respecting capacity and each student's block."""
    h = _require_staff(db, user, hostel_id)
    if h.allocation_final:
        raise HTTPException(status_code=400, detail="Allocation is final. Reopen it before re-running suggestions.")
    members = db.query(HostelMember).filter(HostelMember.hostel_id == h.id).all()
    locked = [m for m in members if m.status == "approved"]
    pool = [m for m in members if m.status != "approved"]
    answers = {m.user_id: _answers(db, m.user_id) for m in pool}
    used = {m.room_no for m in locked if m.room_no}
    counter = 0

    def next_room() -> str:
        nonlocal counter
        while True:
            counter += 1
            if f"R{counter}" not in used:
                used.add(f"R{counter}")
                return f"R{counter}"

    by_block: dict[str, list[HostelMember]] = {}
    for m in pool:
        by_block.setdefault(m.block, []).append(m)
    for block_members in by_block.values():
        todo = sorted(block_members, key=lambda m: m.user_id)
        while todo:
            room = [todo.pop(0)]
            while len(room) < h.room_size and todo:
                best = max(todo, key=lambda c: sum((_pair(answers[r.user_id], answers[c.user_id])["score"] or 0)
                                                   for r in room) / len(room))
                todo.remove(best)
                room.append(best)
            rn = next_room()
            for m in room:
                m.room_no, m.status = rn, "suggested"
    db.commit()
    track(db, user.id, "hostel_suggested", {"hostel_id": h.id, "students": len(pool)})
    return {"suggested": len(pool)}


@router.patch("/{hostel_id}/members/{student_id}")
def edit_member(hostel_id: int, student_id: int, payload: MemberUpdate,
                user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Staff exceptions: move a student to another room (or unassign) / change their block."""
    h = _require_staff(db, user, hostel_id)
    if h.allocation_final:
        raise HTTPException(status_code=400, detail="Allocation is final. Reopen it to make changes.")
    m = db.query(HostelMember).filter(HostelMember.hostel_id == h.id, HostelMember.user_id == student_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Student not found")
    fields = payload.model_fields_set
    if "room_no" in fields:
        m.room_no = (payload.room_no or "").strip() or None
        m.status = "suggested" if m.room_no else "intake"
    if payload.block:
        m.block = payload.block.strip()
    db.commit()
    return {"updated": True}


@router.post("/{hostel_id}/finalize")
def finalize(hostel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """The institution's final call. Students see their roommates only after this."""
    h = _require_staff(db, user, hostel_id)
    members = db.query(HostelMember).filter(HostelMember.hostel_id == h.id).all()
    if any(m.room_no is None for m in members):
        raise HTTPException(status_code=400, detail="Some students have no room yet. Assign them before finalising.")
    counts: dict[str, int] = {}
    for m in members:
        counts[m.room_no] = counts.get(m.room_no, 0) + 1
    if any(n > h.room_size for n in counts.values()):
        raise HTTPException(status_code=400, detail="A room is over capacity. Fix it before finalising.")
    for m in members:
        m.status = "approved"
    h.allocation_final = True
    db.commit()
    track(db, user.id, "hostel_finalized", {"hostel_id": h.id})
    return {"finalized": True}


@router.post("/{hostel_id}/reopen")
def reopen(hostel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = _require_staff(db, user, hostel_id)
    h.allocation_final = False
    db.commit()
    return {"reopened": True}


@router.post("/{hostel_id}/change-requests")
def request_change(hostel_id: int, payload: ChangeRequestIn,
                   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ratelimit.hit(f"hostel-change:{user.id}", 5, 3600, "Too many requests. Please try again later.")
    m = db.query(HostelMember).filter(HostelMember.hostel_id == hostel_id, HostelMember.user_id == user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Hostel not found")
    db.add(HostelChangeRequest(hostel_id=hostel_id, user_id=user.id, reason=payload.reason.strip()))
    db.commit()
    return {"submitted": True}


@router.patch("/{hostel_id}/change-requests/{request_id}")
def decide_change(hostel_id: int, request_id: int, payload: ChangeDecision,
                  user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_staff(db, user, hostel_id)
    if payload.decision not in ("approve", "decline"):
        raise HTTPException(status_code=400, detail="decision must be approve or decline")
    c = db.get(HostelChangeRequest, request_id)
    if not c or c.hostel_id != hostel_id:
        raise HTTPException(status_code=404, detail="Request not found")
    c.status = "approved" if payload.decision == "approve" else "declined"
    c.staff_note = payload.staff_note
    c.decided_at = datetime.now(timezone.utc)
    if c.status == "approved":  # approved change: student goes back to the pool for re-assignment
        m = db.query(HostelMember).filter(HostelMember.hostel_id == hostel_id, HostelMember.user_id == c.user_id).first()
        if m:
            m.room_no, m.status = None, "intake"
            db.query(Hostel).filter(Hostel.id == hostel_id).update({"allocation_final": False})
    db.commit()
    return {"status": c.status}


@router.get("/{hostel_id}/insights")
def insights(hostel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aggregate preferences across the cohort (no individual answers)."""
    h = _require_staff(db, user, hostel_id)
    members = db.query(HostelMember).filter(HostelMember.hostel_id == h.id).all()
    tallies: dict[str, dict[str, int]] = {}
    for m in members:
        for k, v in _answers(db, m.user_id).items():
            tallies.setdefault(k, {})
            tallies[k][str(v)] = tallies[k].get(str(v), 0) + 1
    changes = db.query(HostelChangeRequest).filter(HostelChangeRequest.hostel_id == h.id).count()
    return {"students": len(members), "room_change_requests": changes, "preferences": tallies}
