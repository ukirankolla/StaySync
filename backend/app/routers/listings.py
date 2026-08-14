from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Listing, User
from ..schemas import ListingCreate, ListingOut, ListingUpdate
from ..services.agents import get_agent
from ..services.events import track

router = APIRouter(prefix="/listings", tags=["listings"])


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
    return listings


@router.post("", response_model=ListingOut)
def create_listing(payload: ListingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = Listing(owner_id=user.id, **payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    track(db, user.id, "listing_created", {"listing_id": listing.id})
    return listing


@router.get("/mine", response_model=list[ListingOut])
def my_listings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Listing).filter(Listing.owner_id == user.id).order_by(Listing.created_at.desc()).all()


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


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
    return listing


@router.delete("/{listing_id}")
def delete_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.is_active = False
    db.commit()
    return {"ok": True}
