"""Seed admin account and demo users for the StaySync platform.

Creates the admin account and a set of demo users with complete profiles
and questionnaire answers so the matching algorithm has data to work with.

Run: python scripts/seed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Profile, Questionnaire, User  # noqa: E402
from app.security import hash_password  # noqa: E402

DEMO_USERS = [
    {
        "email": "priya@example.com",
        "full_name": "Priya Sharma",
        "age": 23,
        "occupation": "student",
        "occupation_detail": "MBA Student",
        "city": "Hyderabad",
        "preferred_area": "Koramangala",
        "budget_min": 12000,
        "budget_max": 18000,
        "move_in_date": "2026-09-01",
        "bio": "Early riser, love cooking, very organized. Looking for a quiet, tidy flatmate.",
        "answers": {
            "cleanliness": 5,
            "sleep_time": "Before 10 PM",
            "wake_time": "Before 6 AM",
            "noise_tolerance": 2,
            "quiet_after": "Quiet after 10 PM",
            "smoking": "Never",
            "drinking": "Never",
            "food_pref": "Vegetarian",
            "guests": 2,
            "work_routine": 5,
            "social_pref": 2,
            "pets": "No pets please",
        },
    },
    {
        "email": "arjun@example.com",
        "full_name": "Arjun Joshi",
        "age": 25,
        "occupation": "professional",
        "occupation_detail": "Software Engineer",
        "city": "Hyderabad",
        "preferred_area": "Madhapur",
        "budget_min": 15000,
        "budget_max": 22000,
        "move_in_date": "2026-09-01",
        "bio": "Work from home on weekdays, chai person, respect quiet hours.",
        "answers": {
            "cleanliness": 4,
            "sleep_time": "10 PM – 11 PM",
            "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 3,
            "quiet_after": "Quiet after 10 PM",
            "smoking": "Never",
            "drinking": "Occasionally",
            "food_pref": "Non-vegetarian",
            "guests": 3,
            "work_routine": 4,
            "social_pref": 3,
            "pets": "Open to pets",
        },
    },
    {
        "email": "aditya@example.com",
        "full_name": "Aditya Singh",
        "age": 24,
        "occupation": "student",
        "occupation_detail": "MCA Student",
        "city": "Bangalore",
        "preferred_area": "HSR Layout",
        "budget_min": 10000,
        "budget_max": 15000,
        "move_in_date": "2026-08-15",
        "bio": "Night owl, gamer, love ordering in. Looking for someone chill.",
        "answers": {
            "cleanliness": 2,
            "sleep_time": "12 AM – 2 AM",
            "wake_time": "8 AM – 10 AM",
            "noise_tolerance": 5,
            "quiet_after": "No preference",
            "smoking": "Sometimes",
            "drinking": "Occasionally",
            "food_pref": "Non-vegetarian",
            "guests": 4,
            "work_routine": 2,
            "social_pref": 4,
            "pets": "Love pets / have pets",
        },
    },
    {
        "email": "neha@example.com",
        "full_name": "Neha Patel",
        "age": 22,
        "occupation": "student",
        "occupation_detail": "Design Student",
        "city": "Mumbai",
        "preferred_area": "Andheri",
        "budget_min": 18000,
        "budget_max": 25000,
        "move_in_date": "2026-09-01",
        "bio": "Creative, minimal, clean. Love plants. Looking for a respectful flatmate.",
        "answers": {
            "cleanliness": 5,
            "sleep_time": "10 PM – 11 PM",
            "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 2,
            "quiet_after": "Quiet after 11 PM",
            "smoking": "Never",
            "drinking": "Never",
            "food_pref": "Vegetarian",
            "guests": 2,
            "work_routine": 4,
            "social_pref": 2,
            "pets": "Love pets / have pets",
        },
    },
    {
        "email": "rahul@example.com",
        "full_name": "Rahul Nair",
        "age": 27,
        "occupation": "professional",
        "occupation_detail": "Data Analyst",
        "city": "Chennai",
        "preferred_area": "T. Nagar",
        "budget_min": 12000,
        "budget_max": 16000,
        "move_in_date": "2026-10-01",
        "bio": "Quiet professional, gym in the morning, cook on weekends.",
        "answers": {
            "cleanliness": 4,
            "sleep_time": "10 PM – 11 PM",
            "wake_time": "Before 6 AM",
            "noise_tolerance": 2,
            "quiet_after": "Quiet after 10 PM",
            "smoking": "Never",
            "drinking": "Occasionally",
            "food_pref": "Non-vegetarian",
            "guests": 2,
            "work_routine": 5,
            "social_pref": 2,
            "pets": "No pets please",
        },
    },
    {
        "email": "aman@example.com",
        "full_name": "Aman Reddy",
        "age": 26,
        "occupation": "professional",
        "occupation_detail": "Product Manager",
        "city": "Pune",
        "preferred_area": "Kothrud",
        "budget_min": 14000,
        "budget_max": 20000,
        "move_in_date": "2026-09-15",
        "bio": "Organized, loveboard games, host friends occasionally.",
        "answers": {
            "cleanliness": 3,
            "sleep_time": "11 PM – 12 AM",
            "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 4,
            "quiet_after": "Quiet after 11 PM",
            "smoking": "Never",
            "drinking": "Occasionally",
            "food_pref": "Non-vegetarian",
            "guests": 4,
            "work_routine": 3,
            "social_pref": 4,
            "pets": "Open to pets",
        },
    },
    {
        "email": "kriti@example.com",
        "full_name": "Kriti Menon",
        "age": 23,
        "occupation": "professional",
        "occupation_detail": "UX Researcher",
        "city": "Bangalore",
        "preferred_area": "Koramangala",
        "budget_min": 15000,
        "budget_max": 20000,
        "move_in_date": "2026-09-01",
        "bio": "Minimalist, yoga mornings, vegan. Looking for like-minded flatmate.",
        "answers": {
            "cleanliness": 5,
            "sleep_time": "Before 10 PM",
            "wake_time": "Before 6 AM",
            "noise_tolerance": 1,
            "quiet_after": "Quiet after 10 PM",
            "smoking": "Never",
            "drinking": "Never",
            "food_pref": "Vegetarian",
            "guests": 1,
            "work_routine": 5,
            "social_pref": 1,
            "pets": "No pets please",
        },
    },
    {
        "email": "vikram@example.com",
        "full_name": "Vikram Reddy",
        "age": 28,
        "occupation": "professional",
        "occupation_detail": "DevOps Engineer",
        "city": "Hyderabad",
        "preferred_area": "Gachibowli",
        "budget_min": 16000,
        "budget_max": 22000,
        "move_in_date": "2026-08-01",
        "bio": "Late-night coder, own multiple monitors. Easy going, clean.",
        "answers": {
            "cleanliness": 3,
            "sleep_time": "12 AM – 2 AM",
            "wake_time": "8 AM – 10 AM",
            "noise_tolerance": 4,
            "quiet_after": "No preference",
            "smoking": "Never",
            "drinking": "Regular",
            "food_pref": "Non-vegetarian",
            "guests": 3,
            "work_routine": 3,
            "social_pref": 3,
            "pets": "Open to pets",
        },
    },
    {
        "email": "sonal@example.com",
        "full_name": "Sonal Gupta",
        "age": 25,
        "occupation": "professional",
        "occupation_detail": "Marketing Manager",
        "city": "Delhi",
        "preferred_area": "Lajpat Nagar",
        "budget_min": 14000,
        "budget_max": 18000,
        "move_in_date": "2026-09-15",
        "bio": "Social but respectful, love movies and music. Tidy but not obsessive.",
        "answers": {
            "cleanliness": 3,
            "sleep_time": "10 PM – 11 PM",
            "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 3,
            "quiet_after": "Quiet after 11 PM",
            "smoking": "Never",
            "drinking": "Occasionally",
            "food_pref": "No preference",
            "guests": 3,
            "work_routine": 3,
            "social_pref": 3,
            "pets": "Open to pets",
        },
    },
    {
        "email": "karthik@example.com",
        "full_name": "Karthik Kulkarni",
        "age": 22,
        "occupation": "student",
        "occupation_detail": "Engineering Student",
        "city": "Vijayawada",
        "preferred_area": "Benz Circle",
        "budget_min": 5000,
        "budget_max": 8000,
        "move_in_date": "2026-09-01",
        "bio": "Simple student life, budget-friendly, morning person, library regular.",
        "answers": {
            "cleanliness": 4,
            "sleep_time": "Before 10 PM",
            "wake_time": "Before 6 AM",
            "noise_tolerance": 2,
            "quiet_after": "Quiet after 10 PM",
            "smoking": "Never",
            "drinking": "Never",
            "food_pref": "Vegetarian",
            "guests": 1,
            "work_routine": 5,
            "social_pref": 2,
            "pets": "No pets please",
        },
    },
    {
        "email": "siddharth@example.com",
        "full_name": "Siddharth Nair",
        "age": 26,
        "occupation": "professional",
        "occupation_detail": "Backend Developer",
        "city": "Kochi",
        "preferred_area": "Kakkanad",
        "budget_min": 10000,
        "budget_max": 14000,
        "move_in_date": "2026-09-01",
        "bio": "Tech nerd, anime fan, cook Kerala-style fish curry every Sunday.",
        "answers": {
            "cleanliness": 3,
            "sleep_time": "11 PM – 12 AM",
            "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 3,
            "quiet_after": "Quiet after 11 PM",
            "smoking": "Never",
            "drinking": "Occasionally",
            "food_pref": "Non-vegetarian",
            "guests": 2,
            "work_routine": 3,
            "social_pref": 3,
            "pets": "No pets please",
        },
    },
    {
        "email": "divya@example.com",
        "full_name": "Divya Iyer",
        "age": 24,
        "occupation": "professional",
        "occupation_detail": "Content Writer",
        "city": "Chennai",
        "preferred_area": "Adyar",
        "budget_min": 11000,
        "budget_max": 15000,
        "move_in_date": "2026-10-01",
        "bio": "Book lover, herbal tea, zero drama. Looking for a peaceful home.",
        "answers": {
            "cleanliness": 4,
            "sleep_time": "10 PM – 11 PM",
            "wake_time": "6 AM – 8 AM",
            "noise_tolerance": 2,
            "quiet_after": "Quiet after 10 PM",
            "smoking": "Never",
            "drinking": "Never",
            "food_pref": "Vegetarian",
            "guests": 1,
            "work_routine": 4,
            "social_pref": 2,
            "pets": "No pets please",
        },
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == settings.admin_email).first()
        if not existing_admin:
            admin = User(email=settings.admin_email,
                         hashed_password=hash_password(settings.admin_password), role="admin")
            db.add(admin)
            db.commit()
            print("Seeded admin account.")

        existing_count = db.query(User).filter(User.email != settings.admin_email).count()
        if existing_count >= len(DEMO_USERS):
            print(f"Demo users already exist ({existing_count}). Skipping seed.")
            return

        default_pw = hash_password("demo1234")
        for data in DEMO_USERS:
            if db.query(User).filter(User.email == data["email"]).first():
                continue
            user = User(email=data["email"], hashed_password=default_pw)
            db.add(user)
            db.flush()
            profile = Profile(
                user_id=user.id,
                full_name=data["full_name"],
                age=data["age"],
                occupation=data["occupation"],
                occupation_detail=data["occupation_detail"],
                city=data["city"],
                preferred_area=data["preferred_area"],
                budget_min=data["budget_min"],
                budget_max=data["budget_max"],
                move_in_date=data["move_in_date"],
                bio=data["bio"],
                is_verified=True,
            )
            db.add(profile)
            from datetime import datetime, timezone
            q = Questionnaire(
                user_id=user.id,
                answers=data["answers"],
                completed_at=datetime.now(timezone.utc),
            )
            db.add(q)
        db.commit()
        print(f"Seeded {len(DEMO_USERS)} demo users with profiles and questionnaires.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
