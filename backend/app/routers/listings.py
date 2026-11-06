import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError
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
from ..services import ratelimit
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


def _serialize_many(listings: list[Listing], viewer: User, db: Session) -> list[ListingOut]:
    """ListingOut plus owner name and the people already living there.

    Owners, residents, their users and profiles are fetched in bulk (a handful of queries
    for the whole page) instead of several queries per listing.
    """
    if not listings:
        return []
    ids = [l.id for l in listings]
    owner_ids = {l.owner_id for l in listings}

    rows = db.query(ListingResident).filter(ListingResident.listing_id.in_(ids)).order_by(ListingResident.created_at).all()
    resident_ids = {r.user_id for r in rows}
    users = {u.id: u for u in db.query(User).filter(User.id.in_(owner_ids | resident_ids)).all()} if (owner_ids | resident_ids) else {}
    profiles = {p.user_id: p for p in db.query(Profile).filter(Profile.user_id.in_(owner_ids | resident_ids)).all()}
    by_listing: dict[int, list[ListingResident]] = {}
    for r in rows:
        by_listing.setdefault(r.listing_id, []).append(r)

    score_cache: dict[int, tuple[float | None, list[str]]] = {}
    block_cache: dict[int, bool] = {}

    outs: list[ListingOut] = []
    for listing in listings:
        out = ListingOut.model_validate(listing)
        op = profiles.get(listing.owner_id)
        out.owner_name = op.full_name if op else None
        is_owner = viewer.id == listing.owner_id

        residents: list[ResidentOut] = []
        for r in by_listing.get(listing.id, []):
            if is_owner:
                if r.status == "declined":
                    continue
            elif not (r.status == "accepted" or r.user_id == viewer.id):
                # Others only see confirmed residents (and their own pending invite, so they can answer it).
                continue
            u = users.get(r.user_id)
            if not u or u.is_suspended or not u.is_active:
                continue
            if r.user_id != viewer.id:
                if r.user_id not in block_cache:
                    block_cache[r.user_id] = _blocked(db, viewer.id, r.user_id)
                if block_cache[r.user_id]:
                    continue
            prof = profiles.get(r.user_id)
            if r.user_id == viewer.id:
                score, reasons = None, []
            else:
                if r.user_id not in score_cache:
                    score_cache[r.user_id] = _pair_score(db, viewer.id, r.user_id)
                score, reasons = score_cache[r.user_id]
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
        outs.append(out)
    return outs


def _serialize(listing: Listing, viewer: User, db: Session) -> ListingOut:
    return _serialize_many([listing], viewer, db)[0]


@router.get("", response_model=list[ListingOut])
def search_listings(city: str | None = Query(None), area: str | None = Query(None),
                    max_rent: int | None = Query(None), q: str | None = Query(None),
                    limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
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
    listings = query.order_by(Listing.created_at.desc()).offset(offset).limit(limit).all()
    track(db, user.id, "listings_searched", {"city": city})
    return _serialize_many(listings, user, db)


@router.post("", response_model=ListingOut)
def create_listing(payload: ListingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = Listing(owner_id=user.id, **payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    track(db, user.id, "listing_created", {"listing_id": listing.id})
    return _serialize(listing, user, db)


MAX_IMPORT_ROWS = 200
IMPORT_COLUMNS = ["title", "city", "area", "address", "rent", "deposit", "room_type", "bhk",
                  "amenities", "photos", "description", "available_from", "looking_for"]


class ListingImport(BaseModel):
    csv: str = Field(min_length=1, max_length=1_000_000)


def _split(value: str | None) -> list[str]:
    return [x.strip() for x in (value or "").replace("|", ";").split(";") if x.strip()]


def _num(value: str | None):
    v = (value or "").replace(",", "").replace("₹", "").strip()
    return int(float(v)) if v else None


@router.post("/import")
def import_listings(payload: ListingImport, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Bulk-create listings from CSV text. Header row required; see IMPORT_COLUMNS.

    Rows are validated one by one; valid rows are saved, invalid rows are reported with their line number.
    Admin imports are published immediately, everyone else's wait for approval like normal listings.
    """
    ratelimit.hit(f"import:{user.id}", 10, 3600, "Too many imports. Please try again later.")
    reader = csv.DictReader(io.StringIO(payload.csv.lstrip("\ufeff")))
    if not reader.fieldnames or "title" not in [h.strip().lower() for h in reader.fieldnames]:
        raise HTTPException(status_code=400, detail="CSV needs a header row with at least: title, city, rent")

    created, errors, seen = 0, [], 0
    status = "approved" if user.role == "admin" else "pending"
    for line_no, raw in enumerate(reader, start=2):
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items() if k}
        if not any(row.values()):
            continue
        seen += 1
        if seen > MAX_IMPORT_ROWS:
            errors.append({"row": line_no, "error": f"Only the first {MAX_IMPORT_ROWS} rows are imported"})
            break
        try:
            data = ListingCreate(
                title=row.get("title", ""), city=row.get("city", ""), rent=_num(row.get("rent")) or 0,
                area=row.get("area") or None, address=row.get("address") or None,
                deposit=_num(row.get("deposit")), room_type=row.get("room_type") or "private",
                bhk=row.get("bhk") or None, amenities=_split(row.get("amenities")),
                photos=_split(row.get("photos")), description=row.get("description") or None,
                available_from=row.get("available_from") or None, looking_for=_num(row.get("looking_for")),
            )
        except (ValidationError, ValueError) as exc:
            msg = exc.errors()[0]["msg"] if isinstance(exc, ValidationError) else "Invalid number"
            loc = ".".join(str(x) for x in exc.errors()[0]["loc"]) if isinstance(exc, ValidationError) else ""
            errors.append({"row": line_no, "error": f"{loc}: {msg}" if loc else msg})
            continue
        db.add(Listing(owner_id=user.id, status=status, **data.model_dump()))
        created += 1
    db.commit()
    track(db, user.id, "listings_imported", {"created": created, "errors": len(errors)})
    return {"created": created, "status": status, "errors": errors[:50]}


@router.get("/mine", response_model=list[ListingOut])
def my_listings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Listing).filter(Listing.owner_id == user.id).order_by(Listing.created_at.desc()).all()
    return _serialize_many(rows, user, db)


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
    # Pending / rejected / deactivated listings are only visible to their owner (and admins).
    visible = listing.is_active and listing.status == "approved"
    if not visible and listing.owner_id != user.id and not user.role == "admin":
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != user.id and _blocked(db, user.id, listing.owner_id):
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
    if _blocked(db, user.id, listing.owner_id):
        raise HTTPException(status_code=404, detail="Listing not found")

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
