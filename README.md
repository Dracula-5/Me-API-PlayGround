# Me-API Playground

This is my full-stack portfolio API + dashboard built with FastAPI, SQLAlchemy, and a static frontend. It covers profile, skills, projects, work history, search, and admin-only edits.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Dracula-5/Me-API-PlayGround)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Dracula-5/Me-API-PlayGround)

## Working URLs
- Frontend: https://dapper-douhua-9deab0.netlify.app/
- Backend: https://me-api-playground-aw2m.onrender.com
- Repo: https://github.com/Dracula-5/Me-API-PlayGround
- Resume: https://drive.google.com/file/d/1AmJA3RaZsyTF0EVXF7z9mj1n_hOcMF-K/view?usp=sharing

## Architecture
- FastAPI + SQLAlchemy API in `backend/`
- Static HTML/CSS/JS frontend in `frontend/`
- Postgres in production (Render), SQLite supported locally

## Access Rules
Only admins can edit. The demo admin key is `admin 123`. This is intentionally simple for assessment and should be replaced in real deployments.

## Setup (Local)
1. Create and activate a virtual environment in `backend`.
2. Install dependencies: `pip install -r backend/requirements.txt`
3. If you previously ran SQLite, delete `backend/meapi.db` to refresh schema.
4. (Optional) Seed the database: `python backend/seed.py`
5. Start the API: `uvicorn main:app --reload` from `backend`
6. Open `frontend/index.html` in a browser.

## Setup (Production)
1. Create a Render Web Service from this repo.
2. Render settings:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Create a Render Postgres database and set `DATABASE_URL`.
4. Add env vars in Render:
   - `ADMIN_API_KEY`
   - `CORS_ORIGINS` (set to your Netlify site URL)
5. In `frontend/index.html`, update the `api-base` meta tag to your Render URL.
6. Create a Netlify site from this repo and set publish directory to `frontend`.

## Build-Time Metadata (Netlify)
Netlify runs a build step that injects live profile/skills/projects into HTML metadata.
If you ever need to run it locally:
```
python frontend/generate_meta.py
```

## Data Persistence (Render Postgres)
To make data permanent (no resets), use Render Postgres and set:
```
DATABASE_URL=<your_render_postgres_internal_url>
```

## One-time Migration (SQLite -> Postgres)
If you already added data locally in `backend/meapi.db` and want it in Postgres:
```
set TARGET_DATABASE_URL=<your_render_postgres_internal_url>
python backend/migrate_sqlite_to_postgres.py --reset
```

## Schema
See `backend/schema.md`. Quick summary:
- `Profile`: `id`, `name`, `email`, `education`, `github`, `linkedin`
- `Skill`: `id`, `name`, `proficiency`, `profile_id`
- `Project`: `id`, `title`, `description`, `links`, `profile_id`
- `Work`: `id`, `company`, `role`, `start_date`, `end_date`, `description`, `profile_id`

## Sample cURL
```bash
curl -s YOUR_RENDER_URL/health

curl -s YOUR_RENDER_URL/profile

curl -s -X PATCH YOUR_RENDER_URL/profile \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_ADMIN_KEY" \
  -d '{"name":"Your Name"}'

curl -s YOUR_RENDER_URL/projects?skill=python

curl -s YOUR_RENDER_URL/projects?limit=10&offset=0

curl -s YOUR_RENDER_URL/skills?limit=10&offset=0

curl -s YOUR_RENDER_URL/work?limit=10&offset=0

curl -s YOUR_RENDER_URL/search?q=api
```

## Postman
Import `postman_collection.json` and set variables:
- `baseUrl`
- `adminKey`

## Rate Limiting
Set env vars to control simple in-memory rate limit:
- `RATE_LIMIT` (default 60 requests)
- `RATE_WINDOW` (default 60 seconds)

## Notes
- Limits: single-profile by design for the demo, and the admin key lives in the client (demo-only).
- Trade-offs: simple admin auth keeps things easy to review, but isn’t production-grade.
- Hosting reality: Render free tiers can cold start; the UI retries and caches to feel consistent.
- Next steps: move auth to server-side sessions or OAuth, add a real user model, and add tests + CI.

The `render.yaml` and `netlify.toml` files are included to speed up provisioning.
