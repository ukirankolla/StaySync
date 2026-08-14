"""Lightweight rule-based agents for onboarding, match reasoning, and moderation.

Each agent exposes a simple interface so it can later be backed by an LLM without
changing the API surface.
"""

from __future__ import annotations

from ..questionnaire import QUESTIONNAIRE

REPORT_REASONS = [
    "Fake profile", "Harassment", "Inappropriate content", "Scam / fraud",
    "Spam", "Fake listing", "Offensive language", "Other",
]


class BaseAgent:
    name: str = "base"

    def run(self, *args, **kwargs):
        raise NotImplementedError


class OnboardingAgent(BaseAgent):
    """Guides users through profile + questionnaire completion."""

    name = "onboarding"

    def run(self, profile: dict, answers: dict) -> dict:
        steps = [
            ("profile", bool(profile.get("full_name")) and bool(profile.get("city"))),
            ("budget", profile.get("budget_min") is not None),
            ("move_in_date", bool(profile.get("move_in_date"))),
        ]
        for q in QUESTIONNAIRE:
            steps.append((f"questionnaire.{q['key']}", q["key"] in answers and answers[q["key"]] not in (None, "")))

        done = [label for label, ok in steps if ok]
        todo = [label for label, ok in steps if not ok]
        pct = round(len(done) / len(steps) * 100)

        if pct == 100:
            tip = "You're all set! Browse recommendations to find compatible roommates."
        elif pct >= 60:
            tip = "Almost there — finish the lifestyle questions to unlock better matches."
        elif pct >= 25:
            tip = "Keep going! Answering lifestyle questions improves your match quality."
        else:
            tip = "Start with your city, budget and move-in date."

        return {"progress": pct, "next_steps": todo, "tip": tip}


class MatchReasonAgent(BaseAgent):
    """Turns raw score breakdowns into a short human explanation."""

    name = "match_reason"

    def run(self, reasons: list[str], category_scores: dict, score: float) -> dict:
        if not reasons:
            reasons = [
                f"Strong overall lifestyle alignment ({category_scores.get('lifestyle', 0):.0f}%)"
            ]
        strength = "high" if score >= 80 else ("medium" if score >= 60 else "low")
        top = reasons[:3]
        return {
            "summary": f"Compatibility {score:.0f}% — {strength} match.",
            "top_reasons": top,
            "category_breakdown": {k: round(v, 1) for k, v in category_scores.items()},
        }


class ModerationAgent(BaseAgent):
    """Scores a report for severity and suggests an action."""

    name = "moderation"

    SEVERE = ["scam", "fraud", "harass", "threat", "abuse", "sexual", "violence", "stalking"]
    MEDIUM = ["fake", "offensive", "inappropriate", "spam", "slur", "discriminat"]

    def run(self, reason: str, details: str | None = None) -> dict:
        text = f"{reason} {details or ''}".lower()
        if any(k in text for k in self.SEVERE):
            severity, action = "high", "suspend_user"
        elif any(k in text for k in self.MEDIUM):
            severity, action = "medium", "resolve"
        else:
            severity, action = "low", "dismiss"
        return {"severity": severity, "suggested_action": action}


agents = {
    OnboardingAgent.name: OnboardingAgent(),
    MatchReasonAgent.name: MatchReasonAgent(),
    ModerationAgent.name: ModerationAgent(),
}


def get_agent(name: str) -> BaseAgent:
    return agents[name]
