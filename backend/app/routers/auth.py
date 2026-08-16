from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import OtpCode, User
from ..schemas import (
    ChangePasswordRequest,
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


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = _find_user(db, payload.email.lower() if payload.email else None, payload.phone)
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.is_suspended:
        raise HTTPException(status_code=403, detail="Account suspended")
    track(db, user.id, "login", {})
    return _user_to_response(user)


@router.post("/otp/request")
def request_otp(payload: OtpRequest, db: Session = Depends(get_db)):
    if not payload.identifier.strip():
        raise HTTPException(status_code=400, detail="Identifier required")
    code = generate_otp()
    db.add(OtpCode(identifier=payload.identifier.strip().lower(), code=code,
                   purpose=payload.purpose, expires_at=otp_expiry()))
    db.commit()
    delivery = send_otp(payload.identifier.strip(), code)
    dev_code = code if (not delivery["delivered"] and settings.env == "development") else None
    return {"message": "OTP sent", "channel": delivery["channel"], "delivered": delivery["delivered"],
            "dev_code": dev_code}


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
            "dev_code": code if (not delivery["delivered"] and settings.env == "development") else None}


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
