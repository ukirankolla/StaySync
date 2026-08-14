from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import OtpCode, User
from ..schemas import (
    LoginRequest,
    OtpRequest,
    OtpVerifyRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from ..security import create_access_token, generate_otp, hash_password, otp_expiry, verify_password
from ..services.events import track

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
    # DEV: log OTP to console. In production, send via SMS/email provider.
    print(f"[STAYSYNC-OTP] {payload.identifier} -> {code}")
    return {"message": "OTP sent", "dev_code": code}


@router.post("/otp/verify", response_model=TokenResponse)
def verify_otp(payload: OtpVerifyRequest, db: Session = Depends(get_db)):
    ident = payload.identifier.strip().lower()
    now = datetime.now(timezone.utc)
    otp = db.scalar(
        select(OtpCode)
        .where(OtpCode.identifier == ident, OtpCode.purpose == payload.purpose, OtpCode.is_used.is_(False))
        .order_by(OtpCode.created_at.desc())
    )
    if not otp or otp.expires_at.replace(tzinfo=timezone.utc) < now or otp.code != payload.code:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    otp.is_used = True

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
    return _user_to_response(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
