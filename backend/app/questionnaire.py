"""Questionnaire definition, weights, and matching rules for StaySync MVP."""

from __future__ import annotations

# ---------------------------------------------------------------- questionnaire
QUESTIONNAIRE = [
    {
        "key": "cleanliness",
        "label": "How clean do you like shared spaces?",
        "type": "scale",
        "min": 1,
        "max": 5,
        "hints": ["Very casual", "Spotless"],
    },
    {
        "key": "sleep_time",
        "label": "What is your typical sleep time?",
        "type": "choice",
        "options": ["Before 10 PM", "10 PM – 11 PM", "11 PM – 12 AM", "12 AM – 2 AM", "After 2 AM"],
    },
    {
        "key": "wake_time",
        "label": "What is your typical wake-up time?",
        "type": "choice",
        "options": ["Before 6 AM", "6 AM – 8 AM", "8 AM – 10 AM", "After 10 AM"],
    },
    {
        "key": "noise_tolerance",
        "label": "How do you feel about noise in the evening?",
        "type": "scale",
        "min": 1,
        "max": 5,
        "hints": ["Need silence", "No problem"],
    },
    {
        "key": "quiet_after",
        "label": "Do you prefer a quiet time at night?",
        "type": "choice",
        "options": ["No preference", "Quiet after 10 PM", "Quiet after 11 PM"],
    },
    {
        "key": "smoking",
        "label": "Do you smoke?",
        "type": "choice",
        "options": ["Never", "Sometimes", "Regular"],
    },
    {
        "key": "drinking",
        "label": "How often do you drink?",
        "type": "choice",
        "options": ["Never", "Occasionally", "Regular"],
    },
    {
        "key": "food_pref",
        "label": "What is your food preference?",
        "type": "choice",
        "options": ["Vegetarian", "Eggetarian", "Non-vegetarian", "No preference"],
    },
    {
        "key": "guests",
        "label": "How often do you host guests at home?",
        "type": "scale",
        "min": 1,
        "max": 5,
        "hints": ["Rarely", "Very often"],
    },
    {
        "key": "work_routine",
        "label": "How fixed is your study/work routine?",
        "type": "scale",
        "min": 1,
        "max": 5,
        "hints": ["Flexible", "Very strict"],
    },
    {
        "key": "social_pref",
        "label": "How social do you like to be at home?",
        "type": "scale",
        "min": 1,
        "max": 5,
        "hints": ["Introvert", "Very social"],
    },
    {
        "key": "pets",
        "label": "How do you feel about pets?",
        "type": "choice",
        "options": ["No pets please", "Open to pets", "Love pets / have pets"],
    },
]

SCALE_KEYS = {"cleanliness", "noise_tolerance", "guests", "work_routine", "social_pref"}
CHOICE_KEYS = {"sleep_time", "wake_time", "quiet_after", "smoking", "drinking", "food_pref", "pets"}

# ---------------------------------------------------------------- weights (PRD §8)
WEIGHTS = {
    "lifestyle": 0.30,     # smoking, drinking, food, pets
    "sleep_noise": 0.20,   # sleep time, wake time, noise tolerance, quiet hours
    "budget_location": 0.20,  # budget overlap, city, preferred area
    "cleanliness": 0.15,
    "routine": 0.10,
    "social": 0.05,
}

CATEGORY_KEYS = {
    "lifestyle": ["smoking", "drinking", "food_pref", "pets"],
    "sleep_noise": ["sleep_time", "wake_time", "noise_tolerance", "quiet_after"],
    "cleanliness": ["cleanliness"],
    "routine": ["work_routine"],
    "social": ["social_pref", "guests"],
}

# Per-question weights inside a category (default equal)
QUESTION_WEIGHT = {
    "lifestyle": {"smoking": 0.35, "drinking": 0.35, "food_pref": 0.2, "pets": 0.1},
    "sleep_noise": {"sleep_time": 0.35, "wake_time": 0.2, "noise_tolerance": 0.25, "quiet_after": 0.2},
    "social": {"social_pref": 0.6, "guests": 0.4},
}

# Partial-credit similarity between related choices
PARTIAL_MATCH = {
    ("Never", "Sometimes"): 60,
    ("Sometimes", "Never"): 60,
    ("Never", "Regular"): 25,
    ("Regular", "Never"): 25,
    ("Sometimes", "Regular"): 60,
    ("Regular", "Sometimes"): 60,
    ("No preference", "Vegetarian"): 75,
    ("Vegetarian", "No preference"): 75,
    ("No preference", "Non-vegetarian"): 75,
    ("Non-vegetarian", "No preference"): 75,
    ("No preference", "Eggetarian"): 75,
    ("Eggetarian", "No preference"): 75,
    ("Vegetarian", "Eggetarian"): 60,
    ("Eggetarian", "Vegetarian"): 60,
    ("Quiet after 10 PM", "Quiet after 11 PM"): 90,
    ("Quiet after 11 PM", "Quiet after 10 PM"): 90,
}

MISMATCH_REASONS = {
    "smoking": "Smoking preferences differ",
    "drinking": "Drinking habits differ",
    "food_pref": "Food preferences differ",
    "pets": "Views on pets differ",
    "sleep_time": "Sleep schedules differ",
    "wake_time": "Wake-up routines differ",
    "noise_tolerance": "Noise tolerance differs",
    "quiet_after": "Quiet-hour preferences differ",
    "cleanliness": "Cleanliness standards differ",
    "work_routine": "Work/study routines differ",
    "social_pref": "Social preferences differ",
    "guests": "Guest habits differ",
}

# Reason templates for good matches
MATCH_REASON_TEMPLATES = {
    "cleanliness": "Both like a {cleanliness} shared space",
    "sleep_time": "Both sleep around {sleep_time}",
    "wake_time": "Both wake up around {wake_time}",
    "quiet_after": "Both prefer {quiet_after}",
    "smoking": "Both {smoking_s}",
    "drinking": "Both {drinking_s}",
    "food_pref": "Both prefer {food_pref}",
    "pets": "You agree on pets",
    "noise_tolerance": "Both are fine with similar noise levels",
    "work_routine": "Both have similar work/study routines",
    "social_pref": "Both prefer a similar level of socialising",
    "guests": "Both have similar guest habits",
    "budget": "Your budgets overlap well",
    "area": "Both are looking near {area}",
    "routine": "Both follow similar daily routines",
}
