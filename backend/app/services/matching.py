"""Transparent weighted compatibility scoring (PRD §8)."""

from __future__ import annotations

from ..questionnaire import (
    CATEGORY_KEYS,
    MATCH_REASON_TEMPLATES,
    MISMATCH_REASONS,
    PARTIAL_MATCH,
    QUESTION_WEIGHT,
    SCALE_KEYS,
    WEIGHTS,
)


def _scale_score(a: int, b: int, lo: int = 1, hi: int = 5) -> float:
    rng = hi - lo
    diff = abs(int(a) - int(b))
    return max(0.0, 100.0 - (diff / rng) * 100.0)


def _choice_score(a: str, b: str) -> float:
    if a == b:
        return 100.0
    return float(PARTIAL_MATCH.get((str(a), str(b)), 40.0))


def _budget_score(a_min, a_max, b_min, b_max) -> float | None:
    if a_min is None or b_min is None:
        return None
    a_max = a_max if a_max is not None else a_min
    b_max = b_max if b_max is not None else b_min
    lo = max(a_min, b_min)
    hi = min(a_max, b_max)
    if lo <= hi:
        return 100.0
    gap = lo - hi
    scale = max(1, min(a_max - a_min, b_max - b_min, 10000))
    return max(0.0, 100.0 - (gap / scale) * 100.0)


def _area_score(a_area, b_area, a_city, b_city) -> float | None:
    if a_city != b_city:
        return 0.0
    if not a_area or not b_area:
        return 70.0
    a = str(a_area).lower().strip()
    b = str(b_area).lower().strip()
    if a == b:
        return 100.0
    if a in b or b in a:
        return 85.0
    return 30.0


def _category_score(category: str, qa: dict, qb: dict) -> tuple[float, dict[str, float]]:
    keys = CATEGORY_KEYS.get(category, [])
    weights = QUESTION_WEIGHT.get(category, {})
    sub_scores: dict[str, float] = {}
    total_w = 0.0
    acc = 0.0
    for key in keys:
        a = qa.get(key)
        b = qb.get(key)
        if a is None or b is None or a == "" or b == "":
            continue
        if key in SCALE_KEYS:
            try:
                score = _scale_score(int(a), int(b))
            except (TypeError, ValueError):
                continue
        else:
            score = _choice_score(str(a), str(b))
        sub_scores[key] = round(score, 1)
        w = weights.get(key, 1.0)
        acc += score * w
        total_w += w
    if total_w == 0:
        return None, sub_scores
    return acc / total_w, sub_scores


def compute_compatibility(
    qa: dict,
    qb: dict,
    profile_a: dict | None = None,
    profile_b: dict | None = None,
) -> dict:
    """Returns {score, category_scores, sub_scores, reasons}."""
    profile_a = profile_a or {}
    profile_b = profile_b or {}

    category_scores: dict[str, float] = {}

    for cat in ("lifestyle", "sleep_noise", "cleanliness", "routine", "social"):
        score, _ = _category_score(cat, qa, qb)
        category_scores[cat] = round(score, 1) if score is not None else None

    budget = _budget_score(
        profile_a.get("budget_min"), profile_a.get("budget_max"),
        profile_b.get("budget_min"), profile_b.get("budget_max"),
    )
    area = _area_score(
        profile_a.get("preferred_area"), profile_b.get("preferred_area"),
        profile_a.get("city"), profile_b.get("city"),
    )

    sub = {"budget": budget, "area": area}
    if budget is not None and area is not None:
        category_scores["budget_location"] = round(budget * 0.6 + area * 0.4, 1)
    elif budget is not None:
        category_scores["budget_location"] = round(budget, 1)
    elif area is not None:
        category_scores["budget_location"] = round(area, 1)
    else:
        category_scores["budget_location"] = 50.0

    total = 0.0
    used_w = 0.0
    for cat, w in WEIGHTS.items():
        if category_scores[cat] is not None:
            total += category_scores[cat] * w
            used_w += w

    reasons = generate_reasons(qa, qb, category_scores, sub, profile_a, profile_b)

    score = round(total / used_w, 1) if used_w else None

    return {
        "score": score,
        "category_scores": category_scores,
        "sub_scores": sub,
        "reasons": reasons,
    }


def generate_reasons(qa, qb, category_scores, sub, pa, pb) -> list[str]:
    reasons: list[str] = []

    for key in ("cleanliness", "sleep_time", "wake_time", "quiet_after"):
        a, b = qa.get(key), qb.get(key)
        if a is None or b is None or a == "" or b == "":
            continue
        if str(a).lower() == str(b).lower() and a not in (None, ""):
            reasons.append(MATCH_REASON_TEMPLATES[key].format(**{key: a}))

    for key in ("smoking", "drinking", "food_pref"):
        a, b = qa.get(key), qb.get(key)
        if a is None or b is None:
            continue
        if str(a).lower() == str(b).lower():
            mapped = {"Never": "never smoke", "Sometimes": "only sometimes", "Regular": "smoke",
                      "Occasionally": "drink occasionally", "Never2": ""}
            if key == "smoking":
                text = "don't smoke" if a == "Never" else ("smoke sometimes" if a == "Sometimes" else "smoke")
            elif key == "drinking":
                text = "don't drink" if a == "Never" else ("drink occasionally" if a == "Occasionally" else "drink regularly")
            else:
                text = str(a)
            reasons.append(MATCH_REASON_TEMPLATES[key].format(**{f"{key}_s": text}) if key in (
                "smoking", "drinking") else f"Both prefer {text}")

    if qa.get("pets") == qb.get("pets") and qa.get("pets"):
        reasons.append("You agree on pets")

    if sub.get("budget") is not None and sub["budget"] >= 75:
        reasons.append(MATCH_REASON_TEMPLATES["budget"])
    if sub.get("area") is not None and sub["area"] >= 70:
        area_label = pb.get("preferred_area") or pa.get("preferred_area") or "the same area"
        reasons.append(MATCH_REASON_TEMPLATES["area"].format(area=area_label))

    for key, score in category_scores.items():
        if score is not None and score >= 80 and key in ("routine", "social", "cleanliness", "sleep_noise"):
            tmpl = MATCH_REASON_TEMPLATES.get(key)
            if tmpl:
                reasons.append(tmpl)

    return list(dict.fromkeys(reasons))
