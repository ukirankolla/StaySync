"""Seed the database with demo users, profiles, questionnaires, listings, and activity.

Run: python scripts/seed.py
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    Connection,
    Listing,
    Message,
    Profile,
    Questionnaire,
    Report,
    RoomGroup,
    User,
    group_members,
)
from app.security import hash_password  # noqa: E402

ADMIN_EMAIL = "admin@staysync.dev"
ADMIN_PASSWORD = "admin123"

DEMO_USERS = [
    {
        "email": "arya@example.com", "full_name": "Arya Sharma", "age": 24,
        "occupation": "professional", "occupation_detail": "Software Engineer",
        "city": "Bengaluru", "preferred_area": "Koramangala", "budget_min": 12000, "budget_max": 18000,
        "move_in_date": "2026-09-01", "bio": "Foodie, early riser, love quiet evenings.",
        "answers": {
            "cleanliness": 4, "sleep_time": "10 PM – 11 PM", "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 2, "quiet_after": "Quiet after 10 PM", "smoking": "Never",
            "drinking": "Occasionally", "food_pref": "Vegetarian", "guests": 2,
            "work_routine": 4, "social_pref": 2, "pets": "No pets please",
        },
    },
    {
        "email": "bharat@example.com", "full_name": "Bharat Nair", "age": 26,
        "occupation": "professional", "occupation_detail": "Product Manager",
        "city": "Bengaluru", "preferred_area": "Koramangala", "budget_min": 14000, "budget_max": 20000,
        "move_in_date": "2026-09-15", "bio": "Gym in the morning, books at night.",
        "answers": {
            "cleanliness": 4, "sleep_time": "10 PM – 11 PM", "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 2, "quiet_after": "Quiet after 10 PM", "smoking": "Never",
            "drinking": "Never", "food_pref": "Vegetarian", "guests": 2,
            "work_routine": 4, "social_pref": 3, "pets": "Open to pets",
        },
    },
    {
        "email": "chetan@example.com", "full_name": "Chetan Rao", "age": 22,
        "occupation": "student", "occupation_detail": "MBA student",
        "city": "Bengaluru", "preferred_area": "HSR", "budget_min": 8000, "budget_max": 13000,
        "move_in_date": "2026-08-20", "bio": "Late-night coder, love hosting board-game nights.",
        "answers": {
            "cleanliness": 3, "sleep_time": "12 AM – 2 AM", "wake_time": "8 AM – 10 AM",
            "noise_tolerance": 4, "quiet_after": "No preference", "smoking": "Sometimes",
            "drinking": "Regular", "food_pref": "Non-vegetarian", "guests": 4,
            "work_routine": 2, "social_pref": 4, "pets": "Open to pets",
        },
    },
    {
        "email": "divya@example.com", "full_name": "Divya Menon", "age": 23,
        "occupation": "professional", "occupation_detail": "Data Analyst",
        "city": "Bengaluru", "preferred_area": "Indiranagar", "budget_min": 15000, "budget_max": 22000,
        "move_in_date": "2026-10-01", "bio": "Runner, vegetarian, very organised.",
        "answers": {
            "cleanliness": 5, "sleep_time": "Before 10 PM", "wake_time": "Before 6 AM",
            "noise_tolerance": 1, "quiet_after": "Quiet after 10 PM", "smoking": "Never",
            "drinking": "Never", "food_pref": "Vegetarian", "guests": 1,
            "work_routine": 5, "social_pref": 1, "pets": "No pets please",
        },
    },
    {
        "email": "esha@example.com", "full_name": "Esha Gupta", "age": 21,
        "occupation": "student", "occupation_detail": "Engineering student",
        "city": "Bengaluru", "preferred_area": "HSR", "budget_min": 9000, "budget_max": 14000,
        "move_in_date": "2026-08-25", "bio": "Artsy, loves cats, easy-going.",
        "answers": {
            "cleanliness": 3, "sleep_time": "11 PM – 12 AM", "wake_time": "8 AM – 10 AM",
            "noise_tolerance": 3, "quiet_after": "No preference", "smoking": "Never",
            "drinking": "Occasionally", "food_pref": "Eggetarian", "guests": 3,
            "work_routine": 3, "social_pref": 3, "pets": "Love pets / have pets",
        },
    },
]

LISTINGS = [
    {
        "title": "Bright 2BHK near Koramangala 5th Block",
        "description": "Fully furnished flat, near Metro and tech parks. Two flatmates needed.",
        "city": "Bengaluru", "area": "Koramangala", "address": "5th Block, Koramangala",
        "rent": 25000, "deposit": 50000, "room_type": "private", "bhk": "2BHK",
        "amenities": ["WiFi", "Gym", "Parking"], "photos": [], "available_from": "2026-09-01",
        "looking_for": 2, "status": "approved",
    },
    {
        "title": "Budget PG / shared room HSR Layout",
        "description": "Clean PG with food included. Students welcome. Single sharing available.",
        "city": "Bengaluru", "area": "HSR", "address": "27th Main, HSR Layout",
        "rent": 11000, "deposit": 10000, "room_type": "shared", "bhk": "3BHK",
        "amenities": ["Food", "WiFi", "Laundry"], "photos": [], "available_from": "2026-08-20",
        "looking_for": 3, "status": "pending",
    },
    {
        "title": "Spacious 3BHK Indiranagar for flatmates",
        "description": "Semi-furnished, pet-friendly, close to 100 Feet Road. 2 rooms available.",
        "city": "Bengaluru", "area": "Indiranagar", "address": "100 Feet Road, Indiranagar",
        "rent": 32000, "deposit": 64000, "room_type": "private", "bhk": "3BHK",
        "amenities": ["Pet friendly", "WiFi", "Furnished"], "photos": [], "available_from": "2026-10-01",
        "looking_for": 2, "status": "approved",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Database already has users. Skipping seed.")
        db.close()
        return

    admin = User(email=ADMIN_EMAIL, hashed_password=hash_password(ADMIN_PASSWORD), role="admin")
    db.add(admin)
    db.flush()

    profiles = []
    for d in DEMO_USERS:
        user = User(email=d["email"], hashed_password=hash_password("demo123"))
        db.add(user)
        db.flush()
        profile = Profile(
            user_id=user.id, full_name=d["full_name"], age=d["age"], occupation=d["occupation"],
            occupation_detail=d["occupation_detail"], city=d["city"], preferred_area=d["preferred_area"],
            budget_min=d["budget_min"], budget_max=d["budget_max"], move_in_date=d["move_in_date"],
            bio=d["bio"], is_visible=True,
        )
        db.add(profile)
        q = Questionnaire(user_id=user.id, answers=d["answers"], completed_at=datetime.now(timezone.utc))
        db.add(q)
        profiles.append(user.id)
    db.flush()

    # A connection + messages between Arya and Bharat
    conn = Connection(requester_id=profiles[0], recipient_id=profiles[1], status="accepted")
    db.add(conn)
    db.flush()
    db.add(Message(connection_id=conn.id, sender_id=profiles[0], content="Hey! Your profile looks like a great match."))
    db.add(Message(connection_id=conn.id, sender_id=profiles[1], content="Thanks! Want to check out flats near Koramangala?"))

    # A roommate group for Arya + Bharat + Divya
    group = RoomGroup(name="Koramangala 2BHK Crew", owner_id=profiles[0], city="Bengaluru",
                      target_area="Koramangala", budget_min=12000, budget_max=20000)
    db.add(group)
    db.flush()
    for uid in (profiles[0], profiles[1], profiles[3]):
        db.execute(group_members.insert().values(group_id=group.id, user_id=uid))

    # Listings owned by demo users (except pending one owned by Chetan)
    for i, ld in enumerate(LISTINGS):
        owner = profiles[2] if i == 1 else profiles[0]
        db.add(Listing(owner_id=owner, **ld))

    # A sample report against Chetan (from Arya) flagged by moderation agent
    db.add(Report(reporter_id=profiles[0], target_user_id=profiles[2], target_type="user",
                  reason="Offensive language", details="Used rude language in chat.", severity="medium",
                  status="pending"))

    db.commit()
    db.close()

    print("Seeded:")
    print(f"  Admin:  {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"  Users:  {len(DEMO_USERS)} demo users (email / demo123)")
    print("  Listings: 3, Connections: 1, Group: 1, Report: 1")


if __name__ == "__main__":
    seed()
