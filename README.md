# Me-API Playground

Full-stack portfolio API and dashboard built with FastAPI, SQLAlchemy, and a static frontend. Supports profile, skills, projects, work history, search, and admin-only edits.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=YOUR_REPO_URL)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=YOUR_REPO_URL)

Replace `YOUR_REPO_URL` with your GitHub repo URL after pushing.

## Working URLs
- Frontend: YOUR_NETLIFY_URL
- Backend: YOUR_RENDER_URL
- Repo: YOUR_REPO_URL
- Resume: YOUR_RESUME_URL

## Architecture
- FastAPI + SQLAlchemy API in `backend/`
- Static HTML/CSS/JS frontend in `frontend/`
- Postgres in production (Render), SQLite supported locally

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

## Schema
See `backend/schema.md`.

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

## Known Limitations
- Single-profile assumption (demo scope).
- Admin key is stored in client code (demo-only).

The `render.yaml` and `netlify.toml` files are included to speed up provisioning.
