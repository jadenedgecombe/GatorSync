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
│   │   │   └── routes/     # Route handlers (health, db_check, etc.)
│   │   ├── models/         # SQLAlchemy models (User, Role, Course, etc.)
│   │   ├── config.py       # Settings via pydantic-settings
│   │   ├── database.py     # DB engine, session, Base class
│   │   ├── seed.py         # Seed script for initial roles
│   │   └── main.py         # App entrypoint
│   ├── alembic/            # Database migrations
│   │   └── versions/       # Migration files
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

### 2. Configure DATABASE_URL

Edit `backend/.env` and set your PostgreSQL connection string:

```
DATABASE_URL=postgresql://gatorsync:gatorsync@localhost:5432/gatorsync
```

If you used the Docker option above, the default value already works.

### 3. Run the backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at http://localhost:8000 — interactive docs at http://localhost:8000/docs.

### 4. Run database migrations

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

This creates all tables: roles, users, courses, assignments, tasks, reminders, study_sessions, user_preferences.

### 5. Seed initial roles

```bash
cd backend
source .venv/bin/activate
python -m app.seed
```

This inserts three roles: **student**, **ta**, **admin**.

### 6. Verify the database is working

Open http://localhost:8000/api/db-check in your browser. You should see:

```json
{"status": "connected", "database": "PostgreSQL", "roles": ["student", "ta", "admin"]}
```

### 7. Run the frontend

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

| Method | Path           | Description                          |
|--------|----------------|--------------------------------------|
| GET    | /api/health    | Health check                         |
| GET    | /api/db-check  | Verify DB connection and list roles  |

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
| `backend/app/models/` | SQLAlchemy models — one file per entity |
| `backend/app/database.py` | DB engine, session factory, `get_db` dependency |
| `backend/app/seed.py` | Seeds roles (student, ta, admin) into the database |
| `backend/app/api/routes/` | Add new endpoint files here (e.g., `auth.py`, `syllabus.py`) |
| `backend/app/api/router.py` | Central router — register new route modules here |
| `backend/alembic/` | Alembic migrations — run `alembic upgrade head` to apply |
| `backend/tests/` | Backend tests go here — `conftest.py` provides a shared test client |
| `frontend/src/App.js` | App shell — nav bar and route definitions |
| `frontend/src/pages/` | Add or edit page components here |
| `database/init.sql` | PostgreSQL init script — add tables here |
| `.github/workflows/ci.yml` | CI pipeline — runs lint and tests on push/PR |

### What Is Not Built Yet

The database schema is defined and ready, but no business logic has been implemented:

- No authentication or login logic
- No role-based access control
- No syllabus upload or parsing
- No reminders, study groups, or calendar export
- No real UI — all pages are placeholder text
- PostgreSQL is not required to start the app yet (the server runs without it)
