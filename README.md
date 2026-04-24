# GatorSync — Syllabus-to-Schedule Planner

A university tool that converts syllabus documents into personalized schedules with reminders, workload intelligence, and drag-and-drop calendar planning.

## Tech Stack

- **Frontend:** React 18 + React Router
- **Backend:** Python 3.12 + FastAPI
- **Database:** PostgreSQL 16
- **Auth:** JWT + bcrypt + role-based access control (student / ta / admin)

## Features

- Syllabus upload with automatic date + assignment extraction (PDF / DOCX / TXT)
- Review-and-import UI so students can correct the parser before anything is saved
- Course + assignment CRUD, scoped per user
- Auto-generated tasks with subtask breakdown for assignments over 4 hours
- Weekly and daily calendar views with drag-and-drop rescheduling
- Workload heatmap (green / yellow / red buckets) + overload warnings
- Reminder system with 24-hour lead time for upcoming tasks
- Course templates published by TAs / admins, one-click import for students
- Admin panel: user list, role list, platform stats

## Project Structure

```
GatorSync/
├── backend/                         # FastAPI application
│   ├── app/
│   │   ├── api/routes/              # auth, admin, courses, assignments, tasks,
│   │   │                            # templates, syllabus, schedule, reminders
│   │   ├── models/                  # SQLAlchemy models
│   │   ├── services/
│   │   │   └── syllabus_parser.py   # PDF/DOCX text extraction + date heuristics
│   │   ├── auth.py                  # JWT + password hashing
│   │   ├── rbac.py                  # require_role / require_any_role deps
│   │   ├── seed.py                  # roles + 100+ template assignments
│   │   └── main.py
│   ├── alembic/versions/            # migrations
│   └── tests/                       # pytest (auth, rbac, courses, assignments, parser)
├── frontend/                        # React SPA
│   └── src/
│       ├── api.js                   # shared fetch helpers
│       ├── context/AuthContext.js
│       ├── components/              # ProtectedRoute, RoleGuard, ErrorBoundary
│       └── pages/                   # Login, Signup, Dashboard, Calendar,
│                                    # SyllabusUpload, Templates, Profile,
│                                    # AdminPanel, Forbidden
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

## Local Setup

### 1. PostgreSQL

```bash
# Option A: native
brew install postgresql@16 && brew services start postgresql@16
createuser -s gatorsync && createdb -O gatorsync gatorsync

# Option B: Docker
docker compose up db -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed          # seeds roles + 9 template courses / 106 assignments
uvicorn app.main:app --reload
```

API at http://localhost:8000 — interactive docs at http://localhost:8000/docs.

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

App at http://localhost:3000.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/db-check | DB connectivity + seeded roles |
| POST | /api/auth/register | Create account + JWT |
| POST | /api/auth/login | Issue JWT |
| GET | /api/auth/me | Current user |
| GET | /api/admin/users | Admin-only |
| GET | /api/admin/roles | Admin-only |
| GET | /api/admin/dashboard-stats | TA / admin |
| GET/POST | /api/courses | List / create courses |
| GET/PATCH/DELETE | /api/courses/{id} | Owner-scoped |
| GET/POST | /api/assignments | Auto-generates tasks |
| GET/PATCH/DELETE | /api/assignments/{id} | |
| GET | /api/tasks | All tasks for user |
| PATCH | /api/tasks/{id} | Toggle complete / reschedule (drag-drop target) |
| GET/POST | /api/templates | List / publish (staff) |
| POST | /api/templates/{id}/import | Clone into user workspace |
| POST | /api/syllabus/parse | Parse PDF/DOCX/TXT → JSON preview |
| POST | /api/syllabus/import | Bulk insert parsed rows |
| GET | /api/schedule/week?start= | 7-day schedule |
| GET | /api/schedule/day?date= | One-day schedule |
| GET | /api/schedule/heatmap?start=&days= | Workload buckets |
| GET | /api/schedule/overload?date= | Overload flag |
| GET/POST | /api/reminders | Sync + list |
| POST | /api/reminders/{id}/dismiss | Dismiss reminder |

## Testing

```bash
cd backend && pytest tests/ -v                      # 24 tests
cd frontend && CI=true npm test -- --watchAll=false # 1 smoke test
```

## Linting

```bash
cd backend && ruff check app/ tests/
cd frontend && npm run lint
```

## End-to-End Demo

1. Sign up at `/signup` → auto-assigned `student` role.
2. Either:
   - Upload a syllabus at `/upload` → review parsed rows → import into a new or existing course, OR
   - Visit `/templates` → one-click import a pre-seeded course.
3. Dashboard and Calendar now show your real assignments and auto-generated tasks.
4. On the weekly Calendar, drag any task to a new day → state persists.
5. Heatmap shows workload per day; overload banner fires when today exceeds 6 hours.
6. Reminders appear on the Dashboard for any task due within 24 hours.
