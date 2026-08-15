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

## Deploy

The app is built to run as three pieces: **Vercel** (website), **Railway** (FastAPI backend — needs a persistent server for WebSockets), and **Supabase** (Postgres + Storage).

### 1. Supabase (database + image storage)

1. Create a project at [supabase.com](https://supabase.com).
2. In **Project Settings → Database → Connection string**, copy the pooler/URI (format `postgresql://…`). Keep the password handy.
3. In **Storage**, create a public bucket named `staysync`.

### 2. Railway (backend)

1. Push this repo to GitHub, then create a new project on [railway.app](https://railway.app) → **Deploy from GitHub**.
2. Railway auto-detects `backend/railway.json` + `backend/Dockerfile`.
3. Add environment variables (Project → Variables):
   - `ENV=production`
   - `PUBLIC_BASE_URL=https://<your-backend>.up.railway.app`
   - `DATABASE_URL=<your Supabase postgres connection string>`
   - `JWT_SECRET=<long random string>`
   - `CORS_ORIGINS=https://<your-frontend>.vercel.app`
   - `STORAGE_BACKEND=supabase`
   - `SUPABASE_URL=https://<project>.supabase.co`
   - `SUPABASE_SERVICE_KEY=<service role key>`
   - `SUPABASE_STORAGE_BUCKET=staysync`
   - (Optional) `SMTP_HOST`/`SMTP_USER`/`SMTP_PASSWORD` to email OTPs; otherwise codes print to logs.
4. Railway runs `uvicorn app.main:app` on `$PORT`; the ML model auto-trains on first boot.
5. Seed the production database once (via Railway's CLI shell, from `/app`):
   `python scripts/seed.py`

### 3. Vercel (frontend)

1. On [vercel.com](https://vercel.com), import the repo → framework **Vite** (uses `frontend/vercel.json`).
2. Set build env var (Project → Settings → Environment Variables):
   - `VITE_API_URL=https://<your-backend>.up.railway.app`
3. Deploy. `frontend/vercel.json` rewrites all routes to the SPA.

### 4. Domain + Google

- Add a custom domain in Vercel (e.g. `staysync.app`) and HTTPS is automatic.
- Register the domain in [Google Search Console](https://search.google.com/search-console) and submit the sitemap/URL so it appears in search (takes days–weeks).

## Admin account

The app contains only real user registrations — no demo/fake data. On a fresh
database the admin (owner) login is created automatically when `SEED_ON_START`
is enabled:

| Role  | Email              | Password |
|-------|--------------------|----------|
| Admin | admin@staysync.dev | admin123 |

Both values are overridable via the `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars.

## Feature map (MVP per PRD)

| Module | Status |
|--------|--------|
| Account — email/phone register, password + OTP login | ✅ |
| Profile — age, occupation, city, area, budget, move-in date | ✅ |
| Trust — government ID upload + admin review, verified badge | ✅ |
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
    database.py        # engine / session / lightweight auto-migration
    models.py          # SQLAlchemy models
    security.py        # bcrypt, JWT, OTP
    deps.py            # auth dependencies
    questionnaire.py   # questions + weights + reason templates
    schemas.py         # Pydantic request/response models
    routers/           # auth, profile, matching, chat, groups, listings, moderation, admin, ml, uploads, verification
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

- Set `JWT_SECRET`, `DATABASE_URL` (PostgreSQL), `PUBLIC_BASE_URL`, and `CORS_ORIGINS` in `backend/.env` (see `backend/.env.example`).
- Uploads: `STORAGE_BACKEND=supabase` stores photos in Supabase Storage; `local` writes to `./uploads` (works on Railway only if you attach a volume).
- Replace console-printed OTPs with an SMS/email provider in `app/services/notify.py` (SMTP is supported via env vars).
- Swap the in-memory `ChatManager` for a Redis pub/sub layer before running multiple workers.
- Train the ML model on real labelled interactions once you have engagement data.
