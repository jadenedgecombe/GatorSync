# GatorSync - Syllabus-to-Schedule Planner

A university tool that converts syllabus documents into personalized schedules with reminders, study groups, and calendar sync.

## Tech Stack

- **Frontend:** React 18 + React Router
- **Backend:** Python 3.12 + FastAPI
- **Database:** PostgreSQL 16

## Project Structure

```
GatorSync/
├── backend/                # FastAPI application layer
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/     # Route handlers (health, auth, syllabus, etc.)
│   │   ├── config.py       # Settings via pydantic-settings
│   │   └── main.py         # App entrypoint
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/               # React presentation layer
│   ├── public/
│   ├── src/
│   │   └── pages/          # Login, Dashboard, SyllabusUpload, Calendar
│   ├── .env.example
│   └── package.json
├── database/               # PostgreSQL config
│   └── init.sql
├── .github/workflows/ci.yml
├── docker-compose.yml      # Optional: PostgreSQL via Docker
└── README.md
```

## Local Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (installed locally or via Docker)

### 1. Start PostgreSQL

**Option A — Local install:**

```bash
# macOS (Homebrew)
brew install postgresql@16
brew services start postgresql@16
createuser -s gatorsync
createdb -O gatorsync gatorsync
```

**Option B — Docker (optional):**

```bash
docker compose up db -d
```

Both options make PostgreSQL available at `localhost:5432`.

### 2. Run the backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at http://localhost:8000 — interactive docs at http://localhost:8000/docs.

### 3. Run the frontend

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

App opens at http://localhost:3000.

## Testing

```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && CI=true npm test -- --watchAll=false
```

## Linting

```bash
# Backend
cd backend && ruff check app/ tests/

# Frontend
cd frontend && npm run lint
```

## API Endpoints

| Method | Path        | Description  |
|--------|-------------|--------------|
| GET    | /api/health | Health check |

More endpoints will be added as features are implemented.

## What You Can See Right Now

After following the setup steps above, here is what you should be able to verify:

### Backend

- Open http://localhost:8000/docs to see the interactive Swagger API docs.
- Hit `GET http://localhost:8000/api/health` (in a browser or with `curl`) and you should see:
  ```json
  {"status": "healthy", "service": "GatorSync API"}
  ```
- Run `cd backend && pytest tests/ -v` — you should see **1 passing test** (health endpoint).

### Frontend

- Open http://localhost:3000 in your browser.
- You will see a dark nav bar with links: **Dashboard**, **Syllabus Upload**, **Calendar**, **Login**.
- Click each link — every page loads with placeholder text. No real functionality yet.
- Run `cd frontend && CI=true npm test -- --watchAll=false` — you should see **1 passing test** (app renders).

### Key Files and Folders to Know

| Path | What it does |
|------|-------------|
| `backend/app/main.py` | FastAPI app entrypoint — starts the server |
| `backend/app/config.py` | Central settings — reads from `.env` file |
| `backend/app/api/routes/` | Add new endpoint files here (e.g., `auth.py`, `syllabus.py`) |
| `backend/app/api/router.py` | Central router — register new route modules here |
| `backend/tests/` | Backend tests go here — `conftest.py` provides a shared test client |
| `frontend/src/App.js` | App shell — nav bar and route definitions |
| `frontend/src/pages/` | Add or edit page components here |
| `database/init.sql` | PostgreSQL init script — add tables here |
| `.github/workflows/ci.yml` | CI pipeline — runs lint and tests on push/PR |

### What Is Not Built Yet

This scaffold is **structure only** — no business logic has been implemented:

- No database tables (users, syllabi, schedules, etc.)
- No authentication or login logic
- No role-based access control
- No syllabus upload or parsing
- No reminders, study groups, or calendar export
- No real UI — all pages are placeholder text
- PostgreSQL is not required to start the app yet (the server runs without it)
