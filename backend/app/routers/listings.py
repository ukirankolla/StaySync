from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Block, Connection, Listing, ListingResident, Profile, Questionnaire, User
from ..schemas import (
    ListingCreate,
    ListingOut,
    ListingUpdate,
    ResidentAdd,
    ResidentInvitation,
    ResidentOut,
)
from ..services.chat_manager import chat_manager
from ..services.events import track
from ..services.matching import compute_compatibility

router = APIRouter(prefix="/listings", tags=["listings"])


def _blocked(db: Session, a: int, b: int) -> bool:
    return db.query(Block.id).filter(
        ((Block.blocker_id == a) & (Block.blocked_id == b)) | ((Block.blocker_id == b) & (Block.blocked_id == a))
    ).first() is not None


def _pair_score(db: Session, viewer_id: int, peer_id: int) -> tuple[float | None, list[str]]:
    """Compatibility between two users; None if either has not filled the questionnaire."""
    qa = db.query(Questionnaire).filter(Questionnaire.user_id == viewer_id).first()
    qb = db.query(Questionnaire).filter(Questionnaire.user_id == peer_id).first()
    if not qa or not qb or not qa.answers or not qb.answers:
        return None, []
    pa = db.query(Profile).filter(Profile.user_id == viewer_id).first()
    pb = db.query(Profile).filter(Profile.user_id == peer_id).first()
    result = compute_compatibility(qa.answers, qb.answers, pa.__dict__ if pa else {}, pb.__dict__ if pb else {})
    return result["score"], result["reasons"][:3]


def _serialize(listing: Listing, viewer: User, db: Session) -> ListingOut:
    """ListingOut plus owner name and the people already living there."""
    out = ListingOut.model_validate(listing)
    owner_profile = db.query(Profile).filter(Profile.user_id == listing.owner_id).first()
    out.owner_name = owner_profile.full_name if owner_profile else None

    is_owner = viewer.id == listing.owner_id
    rows = db.query(ListingResident).filter(ListingResident.listing_id == listing.id)
    if not is_owner:
        # Others only see confirmed residents (and the viewer's own pending invite, so they can answer it).
        rows = rows.filter(or_(ListingResident.status == "accepted", ListingResident.user_id == viewer.id))
    else:
        rows = rows.filter(ListingResident.status != "declined")

    residents: list[ResidentOut] = []
    for r in rows.order_by(ListingResident.created_at).all():
        user = db.get(User, r.user_id)
        if not user or user.is_suspended or not user.is_active:
            continue
        if r.user_id != viewer.id and _blocked(db, viewer.id, r.user_id):
            continue
        prof = db.query(Profile).filter(Profile.user_id == r.user_id).first()
        score, reasons = (None, []) if r.user_id == viewer.id else _pair_score(db, viewer.id, r.user_id)
        residents.append(ResidentOut(
            id=r.id, user_id=r.user_id, status=r.status,
            full_name=prof.full_name if prof else "Resident",
            age=prof.age if prof else None,
            occupation=prof.occupation if prof else None,
            occupation_detail=prof.occupation_detail if prof else None,
            bio=prof.bio if prof else None,
            photos=prof.photos if prof and prof.photos else [],
            is_verified=prof.is_verified if prof else False,
            score=score, reasons=reasons, is_you=r.user_id == viewer.id,
        ))
    out.residents = residents
    return out


@router.get("", response_model=list[ListingOut])
def search_listings(city: str | None = Query(None), area: str | None = Query(None),
                    max_rent: int | None = Query(None), q: str | None = Query(None),
                    user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Listing).filter(Listing.is_active.is_(True), Listing.status == "approved")
    if city:
        query = query.filter(Listing.city.ilike(f"%{city}%"))
    if area:
        query = query.filter(or_(Listing.area.ilike(f"%{area}%"), Listing.address.ilike(f"%{area}%")))
    if max_rent:
        query = query.filter(Listing.rent <= max_rent)
    if q:
        query = query.filter(or_(Listing.title.ilike(f"%{q}%"), Listing.description.ilike(f"%{q}%")))
    listings = query.order_by(Listing.created_at.desc()).all()
    track(db, user.id, "listings_searched", {"city": city})
    return [_serialize(l, user, db) for l in listings]


@router.post("", response_model=ListingOut)
def create_listing(payload: ListingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = Listing(owner_id=user.id, **payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    track(db, user.id, "listing_created", {"listing_id": listing.id})
    return _serialize(listing, user, db)


@router.get("/mine", response_model=list[ListingOut])
def my_listings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Listing).filter(Listing.owner_id == user.id).order_by(Listing.created_at.desc()).all()
    return [_serialize(l, user, db) for l in rows]


@router.get("/residents/invitations", response_model=list[ResidentInvitation])
def my_invitations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Listings whose poster says you live there, waiting for your confirmation."""
    rows = db.query(ListingResident).filter(ListingResident.user_id == user.id,
                                            ListingResident.status == "pending").all()
    out = []
    for r in rows:
        l = db.get(Listing, r.listing_id)
        if not l or not l.is_active:
            continue
        owner = db.query(Profile).filter(Profile.user_id == l.owner_id).first()
        out.append(ResidentInvitation(id=r.id, listing_id=l.id, listing_title=l.title, city=l.city,
                                      area=l.area, invited_by=owner.full_name if owner else None))
    return out


@router.post("/residents/{resident_id}/respond")
def respond_to_invitation(resident_id: int, action: str = Query(..., pattern="^(accept|decline)$"),
                          user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.get(ListingResident, resident_id)
    if not r or r.user_id != user.id or r.status != "pending":
        raise HTTPException(status_code=404, detail="Invitation not found")
    r.status = "accepted" if action == "accept" else "declined"
    r.responded_at = datetime.now(timezone.utc)
    db.commit()
    track(db, user.id, "listing_resident_" + r.status, {"listing_id": r.listing_id})
    return {"ok": True, "status": r.status}


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _serialize(listing, user, db)


@router.put("/{listing_id}", response_model=ListingOut)
def update_listing(listing_id: int, payload: ListingUpdate, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Listing not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return _serialize(listing, user, db)


@router.delete("/{listing_id}")
def delete_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/{listing_id}/contact")
def contact_owner(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send a connection request to a listing owner so you can chat about the flat."""
    listing = db.get(Listing, listing_id)
    if not listing or not listing.is_active or listing.status != "approved":
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id == user.id:
        raise HTTPException(status_code=400, detail="This is your own listing")

    existing = db.query(Connection).filter(
        ((Connection.requester_id == user.id) & (Connection.recipient_id == listing.owner_id))
        | ((Connection.recipient_id == user.id) & (Connection.requester_id == listing.owner_id))
    ).first()
    if existing:
        return {"connection_id": existing.id, "status": existing.status}

    conn = Connection(requester_id=user.id, recipient_id=listing.owner_id, status="pending")
    db.add(conn)
    db.commit()
    db.refresh(conn)
    track(db, user.id, "listing_contact", {"listing_id": listing_id, "owner_id": listing.owner_id})
    return {"connection_id": conn.id, "status": conn.status}


@router.post("/{listing_id}/residents")
async def add_resident(listing_id: int, payload: ResidentAdd, user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """Poster lists someone (a registered user) as already living here. They must confirm."""
    listing = db.get(Listing, listing_id)
    if not listing or listing.owner_id != user.id or not listing.is_active:
        raise HTTPException(status_code=404, detail="Listing not found")
    ident = payload.identifier.strip().lower()
    target = db.query(User).filter(or_(User.email == ident, User.phone == payload.identifier.strip())).first()
    if not target or target.is_suspended or not target.is_active:
        raise HTTPException(status_code=404, detail="No registered StaySync user with that email/phone")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="You're already the poster of this listing")
    if _blocked(db, user.id, target.id):
        raise HTTPException(status_code=400, detail="You can't add this user")
    existing = db.query(ListingResident).filter(ListingResident.listing_id == listing_id,
                                                ListingResident.user_id == target.id).first()
    if existing and existing.status != "declined":
        raise HTTPException(status_code=409, detail="Already added")
    if existing:  # previously declined: allow re-inviting
        existing.status, existing.responded_at = "pending", None
        row = existing
    else:
        row = ListingResident(listing_id=listing_id, user_id=target.id, status="pending")
        db.add(row)
    db.commit()
    track(db, user.id, "listing_resident_invited", {"listing_id": listing_id, "user_id": target.id})
    owner_profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    await chat_manager.send_to_user(target.id, {
        "type": "listing_invite",
        "data": {"resident_id": row.id, "listing_id": listing_id, "listing_title": listing.title,
                 "invited_by": owner_profile.full_name if owner_profile else "Someone"},
    })
    return {"id": row.id, "status": row.status}


@router.delete("/{listing_id}/residents/{user_id}")
def remove_resident(listing_id: int, user_id: int, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """The poster can remove a resident, and a resident can remove themselves."""
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if user.id != listing.owner_id and user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    row = db.query(ListingResident).filter(ListingResident.listing_id == listing_id,
                                           ListingResident.user_id == user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.post("/{listing_id}/residents/{user_id}/contact")
async def contact_resident(listing_id: int, user_id: int, user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Ask someone who already lives in this room/flat to chat (same request flow as the owner)."""
    listing = db.get(Listing, listing_id)
    if not listing or not listing.is_active or listing.status != "approved":
        raise HTTPException(status_code=404, detail="Listing not found")
    row = db.query(ListingResident).filter(ListingResident.listing_id == listing_id,
                                           ListingResident.user_id == user_id,
                                           ListingResident.status == "accepted").first()
    if not row:
        raise HTTPException(status_code=404, detail="Resident not found")
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="That's you")
    peer = db.get(User, user_id)
    if not peer or peer.is_suspended or not peer.is_active or _blocked(db, user.id, user_id):
        raise HTTPException(status_code=404, detail="Resident not found")

    existing = db.query(Connection).filter(
        ((Connection.requester_id == user.id) & (Connection.recipient_id == user_id))
        | ((Connection.recipient_id == user.id) & (Connection.requester_id == user_id))
    ).first()
    if existing:
        return {"connection_id": existing.id, "status": existing.status}

    score, _ = _pair_score(db, user.id, user_id)
    conn = Connection(requester_id=user.id, recipient_id=user_id, status="pending", score_at_connect=score)
    db.add(conn)
    db.commit()
    db.refresh(conn)
    track(db, user.id, "listing_resident_contact", {"listing_id": listing_id, "resident_id": user_id})
    me = db.query(Profile).filter(Profile.user_id == user.id).first()
    await chat_manager.send_to_user(user_id, {
        "type": "connection", "event": "requested",
        "data": {"peer_id": user.id, "peer_name": me.full_name if me else "Someone", "connection_id": conn.id},
    })
    return {"connection_id": conn.id, "status": conn.status}
