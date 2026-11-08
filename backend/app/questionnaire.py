"""Questionnaire definition, weights, and matching rules for StaySync MVP."""

from __future__ import annotations

# ---------------------------------------------------------------- questionnaire
QUESTIONNAIRE = [
    # ---- Step 1: daily rhythm and living standards
    {"key": "wake_time", "step": 1, "icon": "🌅", "label": "Wake-up time", "type": "choice",
     "options": ["Before 6 AM", "6 AM – 8 AM", "8 AM – 10 AM", "After 10 AM"]},
    {"key": "sleep_time", "step": 1, "icon": "🛏️", "label": "Sleep time", "type": "choice",
     "options": ["Before 10 PM", "10 PM – 11 PM", "11 PM – 12 AM", "12 AM – 2 AM", "After 2 AM"]},
    {"key": "cleanliness", "step": 1, "icon": "✨", "label": "Cleanliness level", "type": "scale", "min": 1, "max": 5,
     "hints": ["Relaxed", "Spotless"], "labels": ["Relaxed", "Casual", "Moderate", "Very tidy", "Spotless"]},
    {"key": "personality", "step": 1, "icon": "🧑‍🤝‍🧑", "label": "Personality", "type": "choice",
     "options": ["Introvert", "Ambivert", "Extrovert"]},
    {"key": "fitness", "step": 1, "icon": "🏋️", "label": "Fitness / Gym", "type": "choice",
     "options": ["Daily", "Few times a week", "Rarely", "Never"]},
    {"key": "study_hours", "step": 1, "icon": "🕘", "label": "Study / work hours", "type": "choice",
     "options": ["9–6 fixed", "Flexible", "Late shifts", "Exam-time heavy"]},
    # ---- Step 2: shared-space habits
    {"key": "noise_tolerance", "step": 2, "icon": "🔊", "label": "How do you feel about noise in the evening?",
     "type": "scale", "min": 1, "max": 5, "hints": ["Need silence", "No problem"]},
    {"key": "quiet_after", "step": 2, "icon": "🤫", "label": "Do you prefer a quiet time at night?", "type": "choice",
     "options": ["No preference", "Quiet after 10 PM", "Quiet after 11 PM"]},
    {"key": "smoking", "step": 2, "icon": "🚭", "label": "Do you smoke?", "type": "choice",
     "options": ["Never", "Sometimes", "Regular"]},
    {"key": "drinking", "step": 2, "icon": "🥂", "label": "How often do you drink?", "type": "choice",
     "options": ["Never", "Occasionally", "Regular"]},
    {"key": "food_pref", "step": 2, "icon": "🍽️", "label": "What is your food preference?", "type": "choice",
     "options": ["Vegetarian", "Eggetarian", "Non-vegetarian", "No preference"]},
    {"key": "guests", "step": 2, "icon": "🚪", "label": "How often do you host guests at home?", "type": "scale",
     "min": 1, "max": 5, "hints": ["Rarely", "Very often"]},
    {"key": "work_routine", "step": 2, "icon": "📚", "label": "How fixed is your study/work routine?", "type": "scale",
     "min": 1, "max": 5, "hints": ["Flexible", "Very strict"]},
    {"key": "social_pref", "step": 2, "icon": "💬", "label": "How social do you like to be at home?", "type": "scale",
     "min": 1, "max": 5, "hints": ["Introvert", "Very social"]},
    {"key": "pets", "step": 2, "icon": "🐾", "label": "How do you feel about pets?", "type": "choice",
     "options": ["No pets please", "Open to pets", "Love pets / have pets"]},
]

# Questions added later: older members may not have answered them yet, so they are optional.
OPTIONAL_KEYS = {"personality", "fitness", "study_hours"}

SCALE_KEYS = {"cleanliness", "noise_tolerance", "guests", "work_routine", "social_pref"}
CHOICE_KEYS = {"sleep_time", "wake_time", "quiet_after", "smoking", "drinking", "food_pref", "pets",
               "personality", "fitness", "study_hours"}

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
    "lifestyle": ["smoking", "drinking", "food_pref", "pets", "fitness"],
    "sleep_noise": ["sleep_time", "wake_time", "noise_tolerance", "quiet_after"],
    "cleanliness": ["cleanliness"],
    "routine": ["work_routine", "study_hours"],
    "social": ["social_pref", "guests", "personality"],
}

# Per-question weights inside a category (default equal)
QUESTION_WEIGHT = {
    "lifestyle": {"smoking": 0.3, "drinking": 0.3, "food_pref": 0.2, "pets": 0.1, "fitness": 0.1},
    "routine": {"work_routine": 0.5, "study_hours": 0.5},
    "sleep_noise": {"sleep_time": 0.35, "wake_time": 0.2, "noise_tolerance": 0.25, "quiet_after": 0.2},
    "social": {"social_pref": 0.4, "guests": 0.3, "personality": 0.3},
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
    # personality: ambivert fits both sides
    ("Ambivert", "Introvert"): 75, ("Introvert", "Ambivert"): 75,
    ("Ambivert", "Extrovert"): 75, ("Extrovert", "Ambivert"): 75,
    ("Introvert", "Extrovert"): 40, ("Extrovert", "Introvert"): 40,
    # fitness: neighbouring frequencies are close
    ("Daily", "Few times a week"): 75, ("Few times a week", "Daily"): 75,
    ("Few times a week", "Rarely"): 75, ("Rarely", "Few times a week"): 75,
    ("Rarely", "Never"): 80, ("Never", "Rarely"): 80,
    ("Daily", "Rarely"): 45, ("Rarely", "Daily"): 45,
    ("Daily", "Never"): 35, ("Never", "Daily"): 35,
    # study / work hours: "Flexible" works with most schedules
    ("Flexible", "9–6 fixed"): 75, ("9–6 fixed", "Flexible"): 75,
    ("Flexible", "Late shifts"): 75, ("Late shifts", "Flexible"): 75,
    ("Flexible", "Exam-time heavy"): 75, ("Exam-time heavy", "Flexible"): 75,
    ("9–6 fixed", "Exam-time heavy"): 55, ("Exam-time heavy", "9–6 fixed"): 55,
    ("9–6 fixed", "Late shifts"): 30, ("Late shifts", "9–6 fixed"): 30,
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
    "personality": "Personalities differ",
    "fitness": "Fitness routines differ",
    "study_hours": "Study/work hours differ",
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
