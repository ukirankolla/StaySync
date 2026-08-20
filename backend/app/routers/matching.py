from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Block, Connection, Profile, Questionnaire, User
from ..schemas import (
    ConnectRequest,
    ConnectionOut,
    MatchResult,
)
from ..services.agents import get_agent
from ..services.chat_manager import chat_manager
from ..services.events import track
from ..services.location import nearby_cities
from ..services.matching import compute_compatibility
from ..services.ml_model import predict as ml_predict

router = APIRouter(prefix="/matching", tags=["matching"])


def _blocked_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(Block.blocked_id).filter(Block.blocker_id == user_id).all()
    rows2 = db.query(Block.blocker_id).filter(Block.blocked_id == user_id).all()
    return {r[0] for r in rows} | {r[0] for r in rows2}


def _load_pair(user: User, peer_id: int, db: Session):
    peer = db.get(User, peer_id)
    if not peer or peer.is_suspended or not peer.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    qa = db.query(Questionnaire).filter(Questionnaire.user_id == user.id).first()
    qb = db.query(Questionnaire).filter(Questionnaire.user_id == peer_id).first()
    pa = db.query(Profile).filter(Profile.user_id == user.id).first()
    pb = db.query(Profile).filter(Profile.user_id == peer_id).first()
    return peer, qa, qb, pa, pb


def _to_match_result(peer: User, qa: Questionnaire | None, qb: Questionnaire | None,
                     pa: Profile | None, pb: Profile | None, *,
                     is_fallback: bool = False, fallback_note: str | None = None) -> MatchResult:
    result = compute_compatibility(
        qa.answers if qa else {}, qb.answers if qb else {},
        pa.__dict__ if pa else {}, pb.__dict__ if pb else {},
    )
    ml = ml_predict(qa.answers if qa else {}, qb.answers if qb else {},
                    pa.__dict__ if pa else {}, pb.__dict__ if pb else {})
    return MatchResult(
        user_id=peer.id,
        full_name=pb.full_name if pb else "User",
        age=pb.age if pb else None,
        occupation=pb.occupation if pb else None,
        city=pb.city if pb else "",
        preferred_area=pb.preferred_area,
        budget_min=pb.budget_min,
        budget_max=pb.budget_max,
        move_in_date=pb.move_in_date,
        bio=pb.bio,
        photos=pb.photos if pb else [],
        is_verified=pb.is_verified if pb else False,
        is_fallback=is_fallback,
        fallback_note=fallback_note,
        score=result["score"],
        ml_score=round(ml * 100, 1) if ml is not None else None,
        category_scores=result["category_scores"],
        reasons=result["reasons"],
    )


def _run_recommendations(user: User, db: Session, mine_q: Questionnaire | None,
                         profile: Profile | None, blocked: set[int], connected: set[int],
                         loc_filter=None, max_budget: int | None = None,
                         is_fallback: bool = False,
                         fallback_note: str | None = None) -> list[MatchResult]:
    query = (
        select(User)
        .join(Profile, Profile.user_id == User.id)
        .join(Questionnaire, Questionnaire.user_id == User.id)
        .where(User.id != user.id, User.is_active.is_(True), User.is_suspended.is_(False),
               Profile.is_visible.is_(True), Questionnaire.completed_at.isnot(None))
    )
    if loc_filter is not None:
        query = query.where(loc_filter)
    if max_budget:
        query = query.where(Profile.budget_min <= max_budget)

    results: list[MatchResult] = []
    for peer in db.scalars(query).all():
        if peer.id in blocked or peer.id in connected:
            continue
        qb = db.query(Questionnaire).filter(Questionnaire.user_id == peer.id).first()
        pb = db.query(Profile).filter(Profile.user_id == peer.id).first()
        results.append(_to_match_result(peer, mine_q, qb, profile, pb,
                                        is_fallback=is_fallback, fallback_note=fallback_note))
    return results


@router.get("/recommendations", response_model=list[MatchResult])
def recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db),
                    area: str | None = None, city: str | None = None, max_budget: int | None = None):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    mine_q = db.query(Questionnaire).filter(Questionnaire.user_id == user.id).first()

    blocked = _blocked_ids(db, user.id)
    connected = {
        r for (r,) in db.query(Connection.requester_id).filter(Connection.recipient_id == user.id,
                                                               Connection.status.in_(["pending", "accepted"])).all()
    } | {
        r for (r,) in db.query(Connection.recipient_id).filter(Connection.requester_id == user.id,
                                                               Connection.status.in_(["pending", "accepted"])).all()
    }

    location_applied = bool(area or city)
    loc_filter = None
    if city:
        loc_filter = Profile.city.ilike(f"%{city}%")
    if area:
        like = f"%{area}%"
        area_like = or_(Profile.preferred_area.ilike(like), Profile.city.ilike(like))
        loc_filter = area_like if loc_filter is None else and_(loc_filter, area_like)

    results = _run_recommendations(user, db, mine_q, profile, blocked, connected,
                                   loc_filter=loc_filter, max_budget=max_budget)

    # Never dead-end: if an exact location search finds nothing, broaden it.
    if not results and location_applied:
        term = (area or city).strip()
        nearby = nearby_cities(term)
        if nearby:
            nearby_cities_list, state = nearby
            fb_filter = or_(*(Profile.city.ilike(f"%{c}%") for c in nearby_cities_list))
            note = f"No matches in “{term.title()}” yet — showing matches from {state} (nearby)"
            results = _run_recommendations(user, db, mine_q, profile, blocked, connected,
                                           loc_filter=fb_filter, max_budget=max_budget,
                                            is_fallback=True,
                                            fallback_note=note)
        if not results:
            note = f"No matches in “{term.title()}” yet — showing matches from other cities"
            results = _run_recommendations(user, db, mine_q, profile, blocked, connected,
                                           loc_filter=None, max_budget=max_budget,
                                           is_fallback=True,
                                           fallback_note=note)

    results.sort(key=lambda r: (r.ml_score if r.ml_score is not None else r.score), reverse=True)
    track(db, user.id, "recommendations_viewed",
          {"count": len(results), "fallback": bool(results and results[0].is_fallback),
           "area": area, "city": city})
    return results


@router.get("/score/{peer_id}", response_model=dict)
def score_with(peer_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    peer, qa, qb, pa, pb = _load_pair(user, peer_id, db)
    result = compute_compatibility(
        qa.answers if qa else {}, qb.answers if qb else {},
        pa.__dict__ if pa else {}, pb.__dict__ if pb else {},
    )
    ml = ml_predict(qa.answers if qa else {}, qb.answers if qb else {},
                    pa.__dict__ if pa else {}, pb.__dict__ if pb else {})
    explanation = get_agent("match_reason").run(result["reasons"], result["category_scores"], result["score"])
    return {
        "peer_id": peer.id,
        **result,
        "ml_score": round(ml * 100, 1) if ml is not None else None,
        "explanation": explanation,
    }


@router.post("/connect")
async def connect(payload: ConnectRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.recipient_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot connect with yourself")
    peer, qa, qb, pa, pb = _load_pair(user, payload.recipient_id, db)
    existing = db.query(Connection).filter(
        (Connection.requester_id == user.id) & (Connection.recipient_id == payload.recipient_id)
        | (Connection.recipient_id == user.id) & (Connection.requester_id == payload.recipient_id)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Connection already exists")

    result = compute_compatibility(
        qa.answers if qa else {}, qb.answers if qb else {},
        pa.__dict__ if pa else {}, pb.__dict__ if pb else {},
    )
    conn = Connection(requester_id=user.id, recipient_id=payload.recipient_id, status="pending",
                      score_at_connect=result["score"])
    db.add(conn)
    db.commit()
    track(db, user.id, "connect_requested", {"recipient_id": payload.recipient_id})

    requester_name = pa.full_name if pa else "Someone"
    await chat_manager.send_to_user(payload.recipient_id, {
        "type": "connection",
        "event": "requested",
        "data": {"peer_id": user.id, "peer_name": requester_name, "connection_id": conn.id},
    })
    return {"id": conn.id, "status": conn.status, "score": conn.score_at_connect}


@router.get("/connections", response_model=list[ConnectionOut])
def my_connections(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conns = db.query(Connection).filter(
        (Connection.requester_id == user.id) | (Connection.recipient_id == user.id)
    ).order_by(Connection.created_at.desc()).all()

    from ..models import Message

    out = []
    for c in conns:
        peer_id = c.recipient_id if c.requester_id == user.id else c.requester_id
        peer = db.get(User, peer_id)
        if not peer:
            continue
        peer_profile = db.query(Profile).filter(Profile.user_id == peer_id).first()
        last = db.query(Message).filter(Message.connection_id == c.id).order_by(Message.created_at.desc()).first()
        unread = db.query(Message).filter(
            Message.connection_id == c.id, Message.sender_id != user.id, Message.is_read.is_(False)
        ).count()
        out.append(ConnectionOut(
            id=c.id,
            peer_id=peer_id,
            peer_name=peer_profile.full_name if peer_profile else "User",
            status=c.status,
            last_message=last.content if last else None,
            unread_count=unread,
            created_at=c.created_at,
        ))
    return out


@router.post("/connections/{connection_id}/respond", response_model=dict)
async def respond(connection_id: int, action: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conn = db.get(Connection, connection_id)
    if not conn or conn.recipient_id != user.id:
        raise HTTPException(status_code=404, detail="Connection not found")
    if action not in ("accept", "decline"):
        raise HTTPException(status_code=400, detail="Action must be accept or decline")
    conn.status = "accepted" if action == "accept" else "declined"
    conn.responded_at = datetime.now(timezone.utc)
    db.commit()
    track(db, user.id, f"connection_{conn.status}", {"connection_id": connection_id})

    peer_profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    await chat_manager.send_to_user(conn.requester_id, {
        "type": "connection",
        "event": conn.status,
        "data": {"peer_id": user.id, "peer_name": peer_profile.full_name if peer_profile else "Someone",
                 "connection_id": conn.id},
    })
    return {"id": conn.id, "status": conn.status}


@router.get("/agents/onboarding")
def onboarding(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    q = db.query(Questionnaire).filter(Questionnaire.user_id == user.id).first()
    return get_agent("onboarding").run(
        profile={k: getattr(profile, k, None) for k in ("full_name", "city", "budget_min", "move_in_date")} if profile else {},
        answers=q.answers if q else {},
    )


@router.get("/presence")
def presence(user: User = Depends(get_current_user)):
    from ..services.chat_manager import chat_manager
    return {"online": chat_manager.online_ids()}
