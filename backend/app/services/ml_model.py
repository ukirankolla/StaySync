"""ML compatibility model (scikit-learn).

The transparent weighted score is the primary signal for MVP (PRD §8). This model
adds a learned signal: given how real users interact, it predicts the probability
that two users will be a good match. It is trained offline via scripts/train_model.py
(or auto-trained on first boot from synthetic data) and persisted as a joblib file.
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import numpy as np

from ..questionnaire import CHOICE_KEYS, QUESTIONNAIRE, SCALE_KEYS

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "ml_model.joblib"

_option_index = {q["key"]: {o: i for i, o in enumerate(q["options"])} for q in QUESTIONNAIRE if q.get("options")}


def _pair_features(qa: dict, qb: dict, profile_a: dict | None, profile_b: dict | None) -> np.ndarray:
    """Order-invariant pairwise feature vector between two users."""
    feats: list[float] = []

    for q in QUESTIONNAIRE:
        key = q["key"]
        a, b = qa.get(key), qb.get(key)
        if a in (None, ""):
            a = 0
        if b in (None, ""):
            b = 0
        if key in SCALE_KEYS:
            a_i = float(a)
            b_i = float(b)
            feats.append(min(abs(a_i - b_i), 4) / 4.0)
            feats.append(1.0 if a_i == b_i else 0.0)
        else:
            idx = _option_index.get(key, {})
            a_i = float(idx.get(a, -1) if a != 0 else -1)
            b_i = float(idx.get(b, -1) if b != 0 else -1)
            feats.append(1.0 if (a_i >= 0 and a_i == b_i) else 0.0)
            feats.append(0.5 if (a_i >= 0 and b_i >= 0 and a_i != b_i) else 0.0)

    pa = profile_a or {}
    pb = profile_b or {}
    a_min, a_max = pa.get("budget_min"), pa.get("budget_max")
    b_min, b_max = pb.get("budget_min"), pb.get("budget_max")
    if a_min is not None and b_min is not None:
        a_max = a_max if a_max is not None else a_min
        b_max = b_max if b_max is not None else b_min
        lo, hi = max(a_min, b_min), min(a_max, b_max)
        feats.append(1.0 if lo <= hi else 0.0)
        feats.append(max(0.0, 1.0 - (max(0, lo - hi) / 20000.0)))
    else:
        feats.extend([0.5, 0.5])

    feats.append(1.0 if pa.get("city") and pa.get("city") == pb.get("city") else 0.0)
    a_area = str(pa.get("preferred_area") or "").lower()
    b_area = str(pb.get("preferred_area") or "").lower()
    feats.append(1.0 if a_area and a_area == b_area else 0.0)
    feats.append(1.0 if a_area and b_area and (a_area in b_area or b_area in a_area) else 0.0)

    return np.array(feats, dtype=np.float64)


def _load_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    return None


_model = None


def _ensure_model():
    global _model
    if _model is None:
        _model = _load_model()
    return _model


def model_available() -> bool:
    return _ensure_model() is not None


def predict(qa: dict, qb: dict, profile_a: dict | None = None, profile_b: dict | None = None) -> float | None:
    """Returns predicted probability (0-1) that users are a good match, or None if no model."""
    model = _ensure_model()
    if model is None:
        return None
    try:
        X = _pair_features(qa, qb, profile_a, profile_b).reshape(1, -1)
        return float(model.predict_proba(X)[0][1])
    except Exception:
        return None


def predict_with_model(model, qa: dict, qb: dict, profile_a=None, profile_b=None) -> float:
    X = _pair_features(qa, qb, profile_a, profile_b).reshape(1, -1)
    return float(model.predict_proba(X)[0][1])


def reload():
    global _model
    _model = _load_model()


# -------------------------------------------------------------------- training
def build_synthetic_dataset(n: int = 5000, seed: int = 42):
    """Generate synthetic pairwise examples labeled from the transparent score."""
    import random

    from .matching import compute_compatibility

    rng = random.Random(seed)
    profiles = []
    for _ in range(n):
        q = {}
        for qdef in QUESTIONNAIRE:
            if qdef["type"] == "scale":
                q[qdef["key"]] = rng.randint(qdef["min"], qdef["max"])
            else:
                q[qdef["key"]] = rng.choice(qdef["options"])
        prof = {
            "city": rng.choice(["Bengaluru", "Mumbai", "Delhi", "Pune"]),
            "preferred_area": rng.choice([None, "Koramangala", "Indiranagar", "HSR", "Andheri", "Pune East"]),
            "budget_min": rng.randint(5000, 15000),
        }
        prof["budget_max"] = prof["budget_min"] + rng.randint(3000, 15000)
        profiles.append((q, prof))

    X_list, y_list = [], []
    for _ in range(n):
        a = rng.randrange(len(profiles))
        b = rng.randrange(len(profiles))
        if a == b:
            continue
        qa, pa = profiles[a]
        qb, pb = profiles[b]
        X_list.append(_pair_features(qa, qb, pa, pb))
        result = compute_compatibility(qa, qb, pa, pb)
        label = 1 if result["score"] >= 70 else 0
        if rng.random() < 0.1:
            label = 1 - label
        y_list.append(label)

    return np.array(X_list), np.array(y_list)


def train(n: int = 5000) -> str:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import train_test_split

    X, y = build_synthetic_dataset(n=n)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42)
    model.fit(Xtr, ytr)
    y_pred = model.predict(Xte)
    acc = accuracy_score(yte, y_pred)
    report = classification_report(yte, y_pred, target_names=["not_compatible", "compatible"])

    joblib.dump(model, MODEL_PATH)
    global _model
    _model = model

    return f"Trained model saved to {MODEL_PATH}\nAccuracy: {acc:.3f}\n{report}"


def train_from_real_interactions(pairs: list[tuple[dict, dict, dict, dict, bool]]):
    """Retrain from real labelled pairs: (qa, qb, pa, pb, good_match)."""
    from sklearn.ensemble import RandomForestClassifier

    X = np.array([_pair_features(qa, qb, pa, pb) for qa, qb, pa, pb, _ in pairs])
    y = np.array([1 if good else 0 for *_, good in pairs])
    model = RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    global _model
    _model = model
    return len(pairs)
