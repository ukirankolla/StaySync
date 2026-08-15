from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import (
    Connection,
    Event,
    Listing,
    Message,
    Profile,
    Questionnaire,
    Report,
    RoomGroup,
    User,
    Verification,
)
from ..schemas import AdminVerificationOut, ReportOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    suspended = db.query(func.count(User.id)).filter(User.is_suspended.is_(True)).scalar()
    questionnaire_completed = db.query(func.count(Questionnaire.id)).filter(Questionnaire.completed_at.isnot(None)).scalar()
    with_profiles = db.query(func.count(Profile.id)).filter(Profile.city != "").scalar()
    total_connections = db.query(func.count(Connection.id)).scalar()
    accepted_connections = db.query(func.count(Connection.id)).filter(Connection.status == "accepted").scalar()
    total_messages = db.query(func.count(Message.id)).scalar()
    total_groups = db.query(func.count(RoomGroup.id)).scalar()
    total_listings = db.query(func.count(Listing.id)).scalar()
    approved_listings = db.query(func.count(Listing.id)).filter(Listing.status == "approved").scalar()
    pending_reports = db.query(func.count(Report.id)).filter(Report.status == "pending").scalar()
    pending_verifications = db.query(func.count(Verification.id)).filter(Verification.status == "pending").scalar()
    id_verified_users = db.query(func.count(Profile.id)).filter(Profile.is_id_verified.is_(True)).scalar()

    by_city = db.query(Profile.city, func.count(Profile.id)).filter(Profile.city != "").group_by(Profile.city).all()
    registrations_per_day = (
        db.query(func.date(Event.created_at), func.count(Event.id))
        .filter(Event.event_type == "registration")
        .group_by(func.date(Event.created_at))
        .order_by(func.date(Event.created_at))
        .all()
    )

    return {
        "total_users": total_users,
        "suspended_users": suspended,
        "profiles_completed": with_profiles,
        "questionnaire_completed": questionnaire_completed,
        "total_connections": total_connections,
        "accepted_connections": accepted_connections,
        "total_messages": total_messages,
        "total_groups": total_groups,
        "total_listings": total_listings,
        "approved_listings": approved_listings,
        "pending_reports": pending_reports,
        "pending_verifications": pending_verifications,
        "id_verified_users": id_verified_users,
        "users_by_city": [{"city": c, "count": n} for c, n in by_city],
        "registrations_per_day": [{"date": str(d), "count": n} for d, n in registrations_per_day],
    }


@router.get("/users")
def list_users(search: str | None = None, db: Session = Depends(get_db)):
    query = db.query(User).order_by(User.created_at.desc()).limit(200)
    if search:
        query = db.query(User).filter(
            (User.email.ilike(f"%{search}%")) | (User.phone.ilike(f"%{search}%"))
        ).order_by(User.created_at.desc()).limit(200)
    return [
        {
            "id": u.id,
            "email": u.email,
            "phone": u.phone,
            "role": u.role,
            "is_suspended": u.is_suspended,
            "created_at": u.created_at,
        }
        for u in query.all()
    ]


@router.post("/users/{user_id}/suspend")
def suspend_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user:
        user.is_suspended = True
        db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/unsuspend")
def unsuspend_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user:
        user.is_suspended = False
        db.commit()
    return {"ok": True}


@router.get("/reports", response_model=list[ReportOut])
def list_reports(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Report).order_by(Report.created_at.desc()).limit(200)
    if status:
        query = query.filter(Report.status == status)
    return query.all()


@router.post("/reports/{report_id}/review")
def review_report(report_id: int, action: str, db: Session = Depends(get_db)):
    from ..routers.moderation import _resolve_report

    report = db.get(Report, report_id)
    if not report:
        return {"error": "not found"}
    _resolve_report(db, report, action, admin=None)
    db.commit()
    return {"ok": True}


@router.get("/listings")
def admin_listings(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Listing).order_by(Listing.created_at.desc()).limit(200)
    if status:
        query = query.filter(Listing.status == status)
    return [
        {
            "id": l.id,
            "title": l.title,
            "city": l.city,
            "area": l.area,
            "rent": l.rent,
            "status": l.status,
            "is_active": l.is_active,
            "is_verified": l.is_verified,
            "owner_id": l.owner_id,
            "created_at": l.created_at,
        }
        for l in query.all()
    ]


@router.post("/listings/{listing_id}/review")
def review_listing(listing_id: int, action: str, db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing:
        return {"error": "not found"}
    if action == "approve":
        listing.status = "approved"
        listing.is_active = True
    elif action == "reject":
        listing.status = "rejected"
        listing.is_active = False
    db.commit()
    return {"ok": True}


@router.get("/verifications", response_model=list[AdminVerificationOut])
def list_verifications(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Verification)
    if status:
        query = query.filter(Verification.status == status)
    query = query.order_by(Verification.created_at.desc()).limit(200)
    out = []
    for v in query.all():
        user = db.get(User, v.user_id)
        profile = db.query(Profile).filter(Profile.user_id == v.user_id).first()
        out.append(AdminVerificationOut(
            id=v.id,
            user_id=v.user_id,
            id_type=v.id_type,
            id_number=v.id_number,
            document_url=v.document_url,
            status=v.status,
            admin_note=v.admin_note,
            created_at=v.created_at,
            reviewed_at=v.reviewed_at,
            full_name=profile.full_name if profile else "",
            email=user.email if user else None,
            phone=user.phone if user else None,
        ))
    return out


@router.post("/verifications/{verification_id}/review")
def review_verification(verification_id: int, action: str, note: str | None = None,
                        db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if action not in ("approve", "reject"):
        return {"error": "action must be approve or reject"}
    record = db.get(Verification, verification_id)
    if not record:
        return {"error": "not found"}
    if record.status != "pending":
        return {"error": f"already {record.status}"}

    record.status = "approved" if action == "approve" else "rejected"
    record.admin_note = note or None
    record.reviewed_at = datetime.now(timezone.utc)
    record.reviewed_by = admin.id

    profile = db.query(Profile).filter(Profile.user_id == record.user_id).first()
    if profile:
        profile.is_id_verified = action == "approve"

    db.commit()
    from ..services.events import track

    track(db, record.user_id, "id_verification_reviewed",
          {"verification_id": record.id, "action": action, "note": note})
    return {"ok": True, "status": record.status}
