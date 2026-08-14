"""Bootstrap the admin account on a fresh database.

This is the only seed step: it creates the admin user (the owner's login)
if it does not exist yet. All other users are real registrations from the
app — no demo data is ever inserted.

Run: python scripts/seed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import User  # noqa: E402
from app.security import hash_password  # noqa: E402


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.admin_email).first()
        if existing:
            print("Admin account already exists. Skipping seed.")
            return
        admin = User(email=settings.admin_email,
                     hashed_password=hash_password(settings.admin_password), role="admin")
        db.add(admin)
        db.commit()
        print("Seeded admin account (owner login).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
