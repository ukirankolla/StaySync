<div align="center">

# 🏠 StaySync

**Don't just find a place to stay. Find the right person to stay with.**

StaySync is a roommate compatibility platform: people find compatible roommates *before* they move in,
and colleges and hostels create better-matched shared rooms.
One codebase for the **website**, an installable **PWA**, and **Android / iOS apps**.

![React](https://img.shields.io/badge/React_18-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.12-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![Capacitor](https://img.shields.io/badge/Capacitor-119EFF?logo=capacitor&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-5A0FC8?logo=pwa&logoColor=white)

</div>

---

## Screenshots

<table>
  <tr>
    <td align="center"><img src="docs/screenshots/discover-mobile.png" width="230" alt="Discover roommates"><br><sub><b>Discover</b>: ranked matches</sub></td>
    <td align="center"><img src="docs/screenshots/flats-mobile.png" width="230" alt="Flat listing with residents"><br><sub><b>Flats</b>: price, amenities, residents</sub></td>
    <td align="center"><img src="docs/screenshots/chat-mobile.png" width="230" alt="Real-time chat"><br><sub><b>Chat</b>: full-screen, real-time</sub></td>
  </tr>
</table>

<p align="center"><img src="docs/screenshots/flats-desktop.png" width="720" alt="Desktop flats page"></p>

## Why StaySync (our motive)

**A room is more than four walls.** When people move to a new city for college or work, they often share a room
with someone they have never met. The room may be affordable and well located, but the people sharing it may
have very different routines, expectations and habits: sleep schedules, cleanliness, noise, guests, food.
That friction is avoidable. People don't only need a place to stay; they need a living arrangement that fits
how they live.

StaySync puts **lifestyle compatibility before room allocation**:

> Better roommates. Better routines. More room to grow.
> A compatible living environment won't build anyone's career for them, but it can make learning, work and
> personal goals easier to pursue.

### Who it is for

| Audience | What they do on StaySync |
|----------|--------------------------|
| **Individuals**: students moving cities, young professionals, people relocating, PG and shared-flat seekers | Build a profile, find compatible people, chat, then look for a place together |
| **Colleges, hostels, PG operators** | Collect student preferences at registration, get suggested pairings, review and make the final room allocation |

### How a person uses the app

1. **Create a profile**: budget, city and area, move-in date, and a 12-question lifestyle questionnaire (sleep, cleanliness, noise, guests, food, smoking, pets).
2. **Find compatible people**: Discover ranks real members by compatibility, each with plain-language reasons ("Both sleep around 10 PM", "Similar noise expectations", "Budgets overlap").
3. **Connect before committing**: send a request; chat opens only when both accept. Discuss boundaries and expectations, and decide for yourselves.
4. **Choose a place together**: form a group, browse listings with price, deposit, amenities and photos, and see who already lives there, with a score for *you*. Message the owner and the residents.
5. **Tell us how it went**: a short feedback form after connecting helps measure whether matches actually lead to people living together.

### Principles

- **Explainable, not mysterious.** A rules-based score with the reasons shown. Scores are recommendations, never guarantees.
- **You control your data.** Hide your profile, edit your answers, delete your account. Chat is opt-in on both sides.
- **Trust is part of the product.** Report and block tools, listing approval before going live, and honest wording that never claims to guarantee safety.
- **Humans decide.** For colleges, staff review and make the final allocation, and students have a documented way to request a change.
- **Real data only.** StaySync shows real members and real listings, never fabricated ones.

## Features

| Area | What you get |
|------|--------------|
| **Accounts** | Email/phone registration, password and OTP login, password reset, in-app account deletion |
| **Profiles** | Age, occupation, city/area, budget, move-in date, bio, photos, privacy controls |
| **Matching** | 12-question lifestyle questionnaire; weighted, explainable compatibility score with reasons; nearby-city fallback when a city has no members yet |
| **Connections** | Request, then accept or decline; chat opens only after both agree |
| **Chat** | One-to-one real-time messaging over WebSockets, online presence, unread counts, toasts |
| **Groups** | Roommate groups to house-hunt together |
| **Listings** | Search by city, area and rent; rooms or whole flats; amenities and photos; admin approval before going live; CSV bulk import for owners and operators |
| **Residents** | Posters add the flatmates already living there (they confirm). Seekers see each resident with a match score and can chat |
| **College & hostel allocation** | Join-code intake with student consent, suggested rooms by lifestyle compatibility within room capacity and hostel block, staff edit and finalise, student change requests, aggregate campus insights |
| **Lifestyle profile** | Two-step questionnaire (wake/sleep, cleanliness, personality, fitness, study/work hours, habits) that drives the match score and shows as lifestyle badges (hideable in privacy settings) |
| **Welcome carousel & Home** | First launch of the phone app (or a first visit on a small screen) shows a 3-slide welcome; after login, Home shows profile strength, quick actions, unread chats and top matches |
| **Demo chats** | Demo profiles accept connections automatically and answer with clearly labelled sample replies so the chat flow can be shown; they can't be reviewed |
| **Profile strength** | Progress meter showing what to add for better matches |
| **Save / skip** | Shortlist profiles to revisit, or hide ones you don't want to see again |
| **Roommate reviews** | After you have both chatted, rate each other and say whether you'd live together again |
| **Group house rules** | Groups agree on rules and a total budget, then jump to flats for that city and budget; flats show a match score with current residents |
| **Feedback & outcomes** | Post-connection feedback (fit, viewing, living together); admin dashboard tracks match quality, trust, real-world conversion and institution value |
| **Safety** | Report and block users, rule-based moderation that scores report severity, rate limiting, hardened production defaults |
| **Admin** | Users, reports, listings and analytics dashboard |
| **Mobile** | App-style UI (bottom tabs, full-screen chat, safe areas), PWA install, Android & iOS apps |

## How matching works

Matching is **rules-based and explainable**. Each pair gets a weighted score across the questionnaire, and the
app shows the reasons behind it:

| Category | Weight | What is compared |
|----------|-------:|------------------|
| Lifestyle | 30% | Smoking, drinking, food, pets |
| Sleep & noise | 20% | Sleep and wake times, noise tolerance, quiet hours |
| Budget & location | 20% | Budget overlap, city, preferred area |
| Cleanliness | 15% | Shared-space standards |
| Routine | 10% | How fixed the study/work routine is |
| Social | 5% | Guests and social activity at home |

Recommendations are ranked by this score only. Members who haven't completed the questionnaire show no score
rather than a misleading one. If a city has no members yet, the app says so and shows real members from nearby
cities in the same state.

For hostels, the same habit-based comparison (without budget or location) groups students into rooms, respecting
room capacity and each student's hostel block; staff review, edit and finalise.

An experimental scikit-learn model (`backend/app/services/ml_model.py`, `POST /api/ml/retrain`, admin only) is
kept for future research. It is **not used for ranking or shown to users**.

Three small rule-based **agents** (onboarding guidance, match-reason summaries, report moderation) are designed
to be swapped for an LLM later.

## Architecture

```
 Website / PWA / Android / iOS            ← one React codebase (Capacitor wraps it for the stores)
        │  REST + WebSocket
        ▼
 FastAPI  (Python 3.12)
   ├─ JWT + bcrypt auth, OTP login
   ├─ SQLAlchemy  →  SQLite (dev)  /  PostgreSQL on Supabase (prod)
   ├─ Explainable compatibility scoring (rules-based)
   ├─ Rule-based agents (onboarding, match reasons, moderation)
   └─ WebSocket chat manager
```

| Layer | Tech |
|-------|------|
| Frontend | React 18, Vite 6, React Router, `vite-plugin-pwa` |
| Mobile | Capacitor 7 (Android + iOS), see [docs/MOBILE.md](docs/MOBILE.md) |
| Backend | FastAPI, SQLAlchemy, Pydantic, scikit-learn |
| Data | SQLite (development), PostgreSQL via Supabase (production), Supabase Storage for photos |
| Email | Brevo HTTPS API (preferred), SMTP, or console output in development |
| Hosting | Vercel (frontend), Render (backend), Supabase (database + storage) |

## Getting started

**Requirements:** Python 3.12, Node 20+.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # keep ENV=development locally (ENV defaults to production when unset)
python scripts/seed.py               # optional: demo users, listings, admin
python -m uvicorn app.main:app --reload --port 8000
```

Interactive API docs: <http://localhost:8000/docs>

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The dev server proxies `/api` (including WebSockets) to the backend.
Use your browser's device toolbar to see the phone layout.

> Demo accounts created by the seed script are for **local development only**. Never seed demo data into a production database.

## Configuration

All backend settings are environment variables (see `backend/.env.example`).

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENV` | `development` or `production`. Production is the default when unset | `production` |
| `DATABASE_URL` | SQLAlchemy URL (`postgresql://…` in production) | local SQLite file |
| `JWT_SECRET` | Signs access tokens. **Must be a long random string in production**; a weak one is replaced by a random key at boot (sessions reset on restart) | placeholder |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | 10080 (7 days) |
| `CORS_ORIGINS` | Comma-separated allowed web origins (native app origins are always allowed) | localhost + Vercel |
| `CORS_ORIGIN_REGEX` | Extra origins allowed by pattern (Vercel previews) | `^https://stay-?sync[a-z0-9-]*\.vercel\.app$` |
| `ALLOW_SEED_RESET` | Required in production for `SEED_RESET` to take effect | `false` |
| `PUBLIC_BASE_URL` | Public URL of the API so uploaded photos resolve everywhere | empty |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Admin account created on first boot. **Set a strong password in production** | placeholder |
| `SEED_ON_START` / `SEED_RESET` | Bootstrap an empty database / drop and recreate it. Development and staging only | `false` |
| `BREVO_API_KEY` | Send OTP and welcome emails via Brevo | empty (prints to console) |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `MAIL_FROM` | SMTP fallback for email | empty |
| `STORAGE_BACKEND` | `local` or `supabase` | `local` |
| `SUPABASE_URL` `SUPABASE_SERVICE_KEY` `SUPABASE_STORAGE_BUCKET` | Photo storage when using Supabase | empty / `staysync` |

Frontend (`frontend/.env`): `VITE_API_URL` is the backend's URL in production and is left empty in development.

## Deployment

Three pieces: **Supabase** (Postgres + storage), **Render** (API, needs a long-running server for WebSockets) and **Vercel** (website). Railway also works.

<details>
<summary><b>1. Supabase: database and photo storage</b></summary>

1. Create a project at [supabase.com](https://supabase.com).
2. *Project Settings → Database → Connection string*: copy the pooler URI (`postgresql://…`).
3. *Storage*: create a **public** bucket named `staysync`.
</details>

### Backend on Render (what production uses)

`render.yaml` is a Blueprint for the backend. In Render choose **New → Blueprint**, select this repo, then fill in
`DATABASE_URL` (Supabase *Session pooler* string), `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `SUPABASE_SERVICE_KEY`,
`PUBLIC_BASE_URL` (the service's own URL) and `CORS_ORIGINS` (your Vercel domain). `JWT_SECRET` is generated for you.
Free services sleep after 15 minutes idle (about a minute to wake); point an uptime monitor at `/api/health` to reduce that.
Then set `VITE_API_URL` on Vercel to the Render URL and redeploy the frontend.

<details>
<summary><b>Alternative: Railway backend</b></summary>

1. Create a Railway project → **Deploy from GitHub**. It picks up `backend/railway.json` and `backend/Dockerfile`.
2. Set the variables: `ENV=production`, `DATABASE_URL`, `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`,
   `PUBLIC_BASE_URL`, `CORS_ORIGINS` (your Vercel domain), `STORAGE_BACKEND=supabase`, the three `SUPABASE_*`
   values and `BREVO_API_KEY`.
3. The ML model trains automatically on first boot. New tables (including hostel, feedback, review, saved/skipped and group-rule tables) are created at startup.
</details>

<details>
<summary><b>Vercel: website</b></summary>

1. Import the repo, set the **root directory** to `frontend` (framework: Vite, config in `frontend/vercel.json`).
2. Add the environment variable `VITE_API_URL=https://<your-backend-host>`.
3. Add a custom domain and submit the sitemap in Google Search Console.
</details>

## Mobile apps (Android & iOS)

The store apps are the same frontend, wrapped with Capacitor:

```bash
cd frontend
echo "VITE_API_URL=https://<your-backend-host>" > .env.production
npm run mobile:android      # build, sync, open Android Studio
npm run mobile:ios          # macOS: build, sync, open Xcode
```

The Android project compiles; the **full publishing guide** (signing, Play Console, App Store Connect, privacy
policy, Data safety answers, review requirements) is in **[docs/MOBILE.md](docs/MOBILE.md)**.

## API overview

Everything is under `/api` (full, interactive reference at `/docs`).

| Router | Highlights |
|--------|------------|
| `auth` | `POST /register` · `/login` · `/otp/request` · `/otp/verify` · `/forgot` · `/reset` · `GET /me` · `DELETE /me` |
| `profile` | `GET/PUT /me` · `GET/PUT /questionnaire` · `GET /{user_id}` |
| `matching` | `GET /recommendations` · `/score/{peer_id}` · `/presence` · `POST /connect` · `GET /connections` · `POST /connections/{id}/respond` |
| `chat` | `GET/POST /connections/{id}/messages` · `WS /ws` |
| `listings` | `GET /` (search) · `POST /` · `POST /import` (CSV bulk import) · `GET /mine` · `PUT/DELETE /{id}` · `POST /{id}/contact` |
| `listings` (residents) | `POST /{id}/residents` · `DELETE /{id}/residents/{user_id}` · `POST /{id}/residents/{user_id}/contact` · `GET /residents/invitations` · `POST /residents/{id}/respond` |
| `groups` | `POST /` · `GET /` · `GET /{id}` · `PUT /{id}` · `POST /{id}/invite` · `DELETE /{id}/members/{user_id}` |
| `reviews` | `POST /` · `GET /mine` · `GET /user/{id}` (roommate reviews) |
| `matching` (extra) | `POST /marks` · `DELETE /marks/{id}` · `GET /saved` (save/skip) |
| `profile` (extra) | `GET /me/strength` |
| `groups` (extra) | `POST /{id}/rules` · `DELETE /{id}/rules/{rule_id}` |
| `feedback` | `POST /` (fit and outcome after a connection) · `GET /mine` |
| `hostels` | `POST /` · `GET /` · `POST /join` · `GET /{id}` · `POST /{id}/suggest` · `PATCH /{id}/members/{user_id}` · `POST /{id}/finalize` · `POST /{id}/reopen` · `POST /{id}/change-requests` · `PATCH /{id}/change-requests/{rid}` · `GET /{id}/insights` · `DELETE /{id}/membership` |
| `moderation` | `POST /report` · `POST /block` · `GET /blocked` |
| `admin` | `GET /analytics` · `/users` (suspend / unsuspend) · `/reports` (review) · `/listings` (approve / reject) |
| `ml` | `GET /status` · `POST /predict` · `POST /retrain` |
| `upload` | `POST /image` (local disk or Supabase Storage) |

## Project structure

```
backend/
  app/
    main.py  config.py  database.py  models.py  schemas.py  security.py  deps.py
    questionnaire.py            # questions, weights, reason templates
    routers/                    # auth, profile, matching, chat, groups, listings, hostels, feedback, moderation, admin, ml, uploads
    services/                   # matching, ml_model, agents, chat_manager, notify (email), events, locations
  scripts/                      # seed.py, train_model.py
frontend/
  src/
    pages/                      # Landing, Login, Register, OTP, Profile, Questionnaire, Discover,
                                # Connections, Chat, Groups, Listings, Hostels, Admin
    components/                 # Navbar, BottomNav, MatchCard, ProfileModal, AiAssistant, …
    lib/native.js               # Capacitor startup (status bar, splash, back button)
    styles.css                  # design system + responsive / app-shell rules
  capacitor.config.json
  android/  ios/                # native projects (Capacitor)
  scripts/                      # generate_icons.py, require-api-url.mjs
docs/
  MOBILE.md                     # store release guide
  screenshots/
```

## Production checklist

- [ ] `ENV=production` and a long random `JWT_SECRET`
- [ ] Strong `ADMIN_PASSWORD` (and a real `ADMIN_EMAIL`), with `SEED_ON_START` / `SEED_RESET` turned off once bootstrapped
- [ ] `CORS_ORIGINS` limited to your real domains
- [ ] PostgreSQL `DATABASE_URL` and Supabase storage for uploads
- [ ] `BREVO_API_KEY` (or SMTP) set, so OTPs are delivered by email
- [ ] HTTPS everywhere (required by the mobile apps)
- [ ] One backend worker, **or** replace the in-memory `ChatManager` with Redis pub/sub before scaling out

### Security defaults

- Production never returns OTP codes in API responses; if no email/SMS provider is configured the request fails with a clear error.
- Login, registration, OTP and chat/upload endpoints are rate limited, and repeated wrong codes lock out the code.
- On boot in production, any admin still using the old default password is rotated to `ADMIN_PASSWORD` (or locked if none is set), and seeded demo accounts are locked.
- Passwords need at least 8 characters. Uploaded images are checked by content, not just file extension.

## Testing

```bash
cd backend && pip install -r requirements-dev.txt && python -m pytest -q tests
```

CI (`.github/workflows/ci.yml`) runs the backend tests and a frontend build on every pull request.

## Roadmap

- Push notifications (chat messages, connection requests)
- Fixed amenity checklist on listings, with filtering by amenity
- Hostel gender and policy rules beyond the block setting
- Redis-backed chat and rate limiting for multi-instance deployments
- Replace the rule-based agents with an LLM
- Pilot: one city, a few colleges or PGs, measuring whether matches lead to people living together

## Contributing

1. Branch from `main`: `feature/<short-name>` or `fix/<short-name>`.
2. Keep changes focused; run the backend and `npm run build` in `frontend/` before opening a pull request.
3. Describe what changed and how you tested it. Add screenshots for UI changes.
