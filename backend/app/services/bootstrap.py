"""Startup safety checks for accounts that ship with publicly known passwords."""
import secrets

from sqlalchemy import select

from ..config import DEFAULT_ADMIN_PASSWORD, settings
from ..database import SessionLocal
from ..models import User
from ..security import hash_password, verify_password

DEMO_PASSWORD = "demo1234"  # password of the seeded demo users (backend/scripts/seed.py)


def _log(msg: str) -> None:
    print(f"[StaySync] {msg}", flush=True)


def secure_accounts() -> None:
    """In production, make sure nobody can sign in with a password that is published in the repo.

    * Admins still using the old default password get the ADMIN_PASSWORD env value if one is set,
      otherwise they are locked (random password) until ADMIN_PASSWORD is configured.
    * Seeded demo users get a random password. Their content stays, but nobody can log in as them.
    """
    if not settings.is_production:
        return
    db = SessionLocal()
    try:
        env_pw_ok = settings.admin_password != DEFAULT_ADMIN_PASSWORD and len(settings.admin_password) >= 10
        for admin in db.scalars(select(User).where(User.role == "admin")).all():
            if admin.hashed_password and verify_password(DEFAULT_ADMIN_PASSWORD, admin.hashed_password):
                if env_pw_ok and admin.email == settings.admin_email:
                    admin.hashed_password = hash_password(settings.admin_password)
                    _log(f"Admin {admin.email} still used the default password: replaced with ADMIN_PASSWORD.")
                else:
                    admin.hashed_password = hash_password(secrets.token_urlsafe(32))
                    _log(f"CRITICAL: admin {admin.email} used the public default password and has been locked. "
                         f"Set ADMIN_EMAIL={admin.email} and a strong ADMIN_PASSWORD (10+ characters), then restart.")
        try:
            from scripts.seed import DEMO_USERS
            demo_emails = [d["email"] for d in DEMO_USERS]
        except Exception:  # noqa: BLE001 (scripts folder missing in some images)
            demo_emails = []
        for u in db.scalars(select(User).where(User.email.in_(demo_emails or ["-"]))).all():
            if u.hashed_password and verify_password(DEMO_PASSWORD, u.hashed_password):
                u.hashed_password = hash_password(secrets.token_urlsafe(32))
                _log(f"Demo account {u.email} had the public demo password: locked.")
        db.commit()
    finally:
        db.close()
