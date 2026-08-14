# StaySync

Roommate compatibility & flat-finding platform. Students and professionals find compatible roommates before they move, based on lifestyle, routine, budget, and housing preferences.

## Architecture

```
React SPA (Vite, port 5173)
        │  /api proxied (REST + WebSocket)
FastAPI (Python 3.12, port 8000)
   ├─ JWT + bcrypt auth, OTP login
   ├─ SQLAlchemy models  →  SQLite (dev) / PostgreSQL (prod)
   ├─ Weighted compatibility scoring + scikit-learn ML model
   ├─ Rule-based agents (onboarding, match-reason, moderation)
   └─ WebSocket chat manager (real-time messaging)
```

- **Backend**: `backend/` — FastAPI, SQLAlchemy, scikit-learn
- **Frontend**: `frontend/` — React 18 + Vite + React Router
- One backend serves the website now and a future Android app via the same REST/WebSocket API.

## Quick start

### 1. Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# Seed demo data (admin + 5 users, listings, group, report)
.\.venv\Scripts\python scripts\seed.py

# Train the ML compatibility model (scikit-learn, ~1-2s)
.\.venv\Scripts\python scripts\train_model.py

# Start the API
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the dev server proxies `/api` (including WebSockets) to the backend.

## Demo accounts

| Role  | Email              | Password |
|-------|--------------------|----------|
| Admin | admin@staysync.dev | admin123 |
| User  | arya@example.com   | demo123  |
| User  | bharat@example.com | demo123  |
| User  | chetan@example.com | demo123  |
| User  | divya@example.com  | demo123  |
| User  | esha@example.com   | demo123  |

## Feature map (MVP per PRD)

| Module | Status |
|--------|--------|
| Account — email/phone register, password + OTP login | ✅ |
| Profile — age, occupation, city, area, budget, move-in date | ✅ |
| Lifestyle questionnaire (12 questions) | ✅ |
| Compatibility — transparent weighted score + reasons | ✅ |
| ML predictions — scikit-learn model blended into ranking | ✅ |
| Discovery — recommended roommates feed | ✅ |
| Chat — one-to-one real-time via WebSockets | ✅ |
| Connect/request flow (pending → accept/decline) | ✅ |
| Groups — create roommate group, invite matched users | ✅ |
| Flat listings — search + post (approval flow) | ✅ |
| Report/block + moderation agent severity scoring | ✅ |
| Admin dashboard — users, reports, listings, analytics | ✅ |

## Matching logic

- Weighted transparent score (PRD §8): lifestyle 30%, sleep/noise 20%, budget/location 20%, cleanliness 15%, routine 10%, social 5%.
- The UI always shows *reasons* ("Both prefer quiet after 10 PM"), never just a mystery percentage.
- A RandomForestClassifier (`backend/ml_model.joblib`, trained in `scripts/train_model.py`) predicts match probability from pairwise features; the discovery feed is ranked by the blended signal. Retrain with real interaction data later via `POST /api/ml/retrain` or `train_from_real_interactions`.

## Agents (rule-based, LLM-swappable)

- **OnboardingAgent** — profile/questionnaire progress + next-step guidance (`/api/matching/agents/onboarding`)
- **MatchReasonAgent** — turns score breakdowns into plain-language summaries
- **ModerationAgent** — scores report severity and suggests action (dismiss / resolve / suspend_user)

## Project layout

```
backend/
  app/
    main.py            # FastAPI app + lifespan + CORS
    config.py          # settings (env-driven)
    database.py        # engine / session
    models.py          # SQLAlchemy models
    security.py        # bcrypt, JWT, OTP
    deps.py            # auth dependencies
    questionnaire.py   # questions + weights + reason templates
    schemas.py         # Pydantic request/response models
    routers/           # auth, profile, matching, chat, groups, listings, moderation, admin, ml
    services/          # matching, ml_model, agents, chat_manager, events
  scripts/
    seed.py            # demo data
    train_model.py     # train ML model
frontend/
  src/
    api/client.js      # fetch wrapper + token storage
    context/AuthContext.jsx
    pages/             # Landing, Login, Register, OTP, Profile, Questionnaire, Discover, Connections, Chat, Groups, Listings, Admin
    components/        # Navbar, MatchCard
```

## Production notes

- Set `JWT_SECRET`, `DATABASE_URL` (PostgreSQL) and `CORS_ORIGINS` in `backend/.env`.
- Replace console-printed OTPs with an SMS/email provider in `app/routers/auth.py`.
- Swap the in-memory `ChatManager` for a Redis pub/sub layer before running multiple workers.
- Train the ML model on real labelled interactions once you have engagement data.
