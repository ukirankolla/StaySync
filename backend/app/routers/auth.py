from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import (
    Block,
    Connection,
    Listing,
    ListingResident,
    Message,
    OtpCode,
    Profile,
    Questionnaire,
    RoomGroup,
    User,
)
from ..schemas import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    OtpRequest,
    OtpVerifyRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from ..security import create_access_token, generate_otp, hash_password, otp_expiry, verify_password
from ..config import settings
from ..services.events import track
from ..services.notify import send_otp, send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_to_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.id, user.role), user=UserOut.model_validate(user))


def _find_user(db: Session, email: str | None, phone: str | None) -> User | None:
    if email:
        return db.scalar(select(User).where(User.email == email.lower()))
    if phone:
        return db.scalar(select(User).where(User.phone == phone))
    return None


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower() if payload.email else None
    if not email and not payload.phone:
        raise HTTPException(status_code=400, detail="Email or phone is required")
    if _find_user(db, email, payload.phone):
        raise HTTPException(status_code=409, detail="Account already exists")
    user = User(email=email, phone=payload.phone, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    from ..models import Profile
    db.add(Profile(user_id=user.id, full_name=payload.full_name, city=""))
    db.commit()
    track(db, user.id, "registration", {"method": "password"})
    if email:
        send_welcome_email(email, payload.full_name)
    return _user_to_response(user)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = _find_user(db, payload.email.lower() if payload.email else None, payload.phone)
    if not user:
        raise HTTPException(status_code=401, detail="No account found with this email or phone. Please register first.")
    if not user.hashed_password:
        raise HTTPException(status_code=401, detail="This account was created via OTP and has no password. Use 'Log in with OTP' or 'Forgot password' to set a new password.")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password. Try again or use 'Forgot password' to reset it.")
    if user.is_suspended:
        raise HTTPException(status_code=403, detail="Account suspended")
    track(db, user.id, "login", {})
    resp = _user_to_response(user)
    return resp.model_dump()


@router.post("/otp/request")
def request_otp(payload: OtpRequest, db: Session = Depends(get_db)):
    if not payload.identifier.strip():
        raise HTTPException(status_code=400, detail="Identifier required")
    code = generate_otp()
    db.add(OtpCode(identifier=payload.identifier.strip().lower(), code=code,
                   purpose=payload.purpose, expires_at=otp_expiry()))
    db.commit()
    delivery = send_otp(payload.identifier.strip(), code)
    otp_code = code if not delivery["delivered"] else None
    return {"message": "OTP sent", "channel": delivery["channel"], "delivered": delivery["delivered"],
            "otp_code": otp_code}


@router.post("/otp/verify", response_model=TokenResponse)
def verify_otp(payload: OtpVerifyRequest, db: Session = Depends(get_db)):
    ident = payload.identifier.strip().lower()
    _consume_otp(db, ident, payload.purpose, payload.code)

    email = ident if "@" in ident else None
    phone = None if email else ident
    user = _find_user(db, email, phone)
    is_new = user is None
    if is_new:
        user = User(email=email, phone=phone)
        db.add(user)
        db.flush()
        from ..models import Profile
        db.add(Profile(user_id=user.id, full_name="", city=""))
    user.is_suspended = False
    db.commit()
    db.refresh(user)
    track(db, user.id, "registration" if is_new else "login", {"method": "otp"})
    if is_new and email:
        send_welcome_email(email)
    return _user_to_response(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.delete("/me")
def delete_account(payload: DeleteAccountRequest, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Permanently delete the caller's account (required by the App Store and Google Play).

    Personal data is erased: login identifiers, profile, questionnaire, chats, connections,
    group memberships and resident links are removed and the user's listings are taken down.
    The bare user row is kept (inactive, no email/phone/password) so reports and analytics
    that reference it stay consistent. The same email/phone can register again afterwards.
    """
    if payload.confirm.strip().upper() != "DELETE":
        raise HTTPException(status_code=400, detail="Type DELETE to confirm")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Admin accounts can't be deleted from the app")

    track(db, user.id, "account_deleted", {})
    uid = user.id

    conn_ids = [c.id for c in db.query(Connection.id).filter(
        (Connection.requester_id == uid) | (Connection.recipient_id == uid)).all()]
    if conn_ids:
        db.query(Message).filter(Message.connection_id.in_(conn_ids)).delete(synchronize_session=False)
        db.query(Connection).filter(Connection.id.in_(conn_ids)).delete(synchronize_session=False)
    db.query(Message).filter(Message.sender_id == uid).delete(synchronize_session=False)
    db.query(Block).filter((Block.blocker_id == uid) | (Block.blocked_id == uid)).delete(synchronize_session=False)

    for group in db.query(RoomGroup).filter(RoomGroup.members.any(User.id == uid)).all():
        group.members.remove(user)
        if not group.members:
            group.status = "disbanded"

    own_listing_ids = [l.id for l in db.query(Listing.id).filter(Listing.owner_id == uid).all()]
    db.query(Listing).filter(Listing.owner_id == uid).update({"is_active": False}, synchronize_session=False)
    db.query(ListingResident).filter(
        (ListingResident.user_id == uid) | (ListingResident.listing_id.in_(own_listing_ids or [-1]))
    ).delete(synchronize_session=False)

    db.query(Questionnaire).filter(Questionnaire.user_id == uid).delete(synchronize_session=False)
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    if profile:
        profile.full_name, profile.city = "Deleted user", ""
        profile.age = profile.occupation_detail = profile.bio = profile.preferred_area = None
        profile.budget_min = profile.budget_max = profile.move_in_date = None
        profile.photos, profile.privacy = [], {}
        profile.is_visible = profile.is_verified = False

    identifiers = [i for i in (user.email, user.phone) if i]
    if identifiers:
        db.query(OtpCode).filter(OtpCode.identifier.in_(identifiers)).delete(synchronize_session=False)
    user.email = user.phone = user.hashed_password = None
    user.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/forgot")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    ident = payload.identifier.strip().lower()
    email = ident if "@" in ident else None
    user = _find_user(db, email, None if email else ident)
    if not user:
        # do not leak whether an account exists
        return {"message": "If an account exists, an OTP has been sent"}
    code = generate_otp()
    db.add(OtpCode(identifier=ident, code=code, purpose="reset", expires_at=otp_expiry()))
    db.commit()
    delivery = send_otp(ident, code)
    return {"message": "If an account exists, an OTP has been sent",
            "delivered": delivery["delivered"],
            "otp_code": code if not delivery["delivered"] else None}


@router.post("/reset")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    ident = payload.identifier.strip().lower()
    otp = _consume_otp(db, ident, "reset", payload.code)
    email = ident if "@" in ident else None
    user = _find_user(db, email, None if email else ident)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    track(db, user.id, "password_reset", {})
    return {"message": "Password updated. You can log in now."}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not user.hashed_password or not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    track(db, user.id, "password_changed", {})
    return {"message": "Password updated"}


def _consume_otp(db: Session, identifier: str, purpose: str, code: str) -> OtpCode:
    now = datetime.now(timezone.utc)
    otp = db.scalar(
        select(OtpCode)
        .where(OtpCode.identifier == identifier, OtpCode.purpose == purpose, OtpCode.is_used.is_(False))
        .order_by(OtpCode.created_at.desc())
    )
    if not otp or otp.expires_at.replace(tzinfo=timezone.utc) < now or otp.code != code:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    otp.is_used = True
    return otp
