# GatorSync — Syllabus-to-Schedule Planner

A university tool that converts syllabus documents into personalized schedules with reminders, workload intelligence, drag-and-drop calendar planning, study session tracking, and user-configurable preferences.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + React Router 6 |
| Backend | Python 3.12 + FastAPI 0.111 |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic |
| Auth | JWT (python-jose) + bcrypt + RBAC (student / ta / admin) |
| Parsing | PyPDF2 + python-docx + python-dateutil |
| CI/CD | GitHub Actions (lint → test → build) |

## Features

- **Syllabus parsing** — Upload PDF, DOCX, or TXT; multi-pass heuristics extract assignment titles, due dates, and types (exam, project, quiz, reading, homework)
- **Review-and-import workflow** — Row-by-row preview before anything is saved to the database
- **Course & assignment management** — Full CRUD scoped per user, with inline editing
- **Auto-generated tasks** — Assignments over 4 hours are split into 3-hour subtasks with staggered due dates
- **Weekly calendar** — Drag-and-drop task rescheduling, workload heatmap (light / medium / heavy), overload warnings
- **Study sessions** — Create, edit, and delete personal study blocks with title, location, and time range
- **User preferences** — Dark mode, timezone selection, and notification flags persisted per-user
- **iCal export** — Download your upcoming tasks as a `.ics` file for Google Calendar, Apple Calendar, etc.
- **Course templates** — Published by TAs/admins, one-click import for students; 9 pre-seeded templates with 100+ assignments
- **Admin panel** — User list, role management, platform statistics
- **Search & filter** — Full-text search on courses, assignments, tasks, and templates
- **Pagination** — All list endpoints support `skip`/`limit` query params
- **Accessibility** — ARIA labels, `role` attributes, `aria-required`, `htmlFor`/`id` associations, `focus-visible` ring, and screen-reader-only helpers

## Project Structure

```
GatorSync/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── auth.py            # register, login, me
│   │   │   ├── courses.py         # CRUD + search + pagination
│   │   │   ├── assignments.py     # CRUD + search + type filter + pagination
│   │   │   ├── tasks.py           # list + toggle + reschedule + search
│   │   │   ├── schedule.py        # week, day, heatmap, overload, iCal export
│   │   │   ├── syllabus.py        # parse + bulk import
│   │   │   ├── templates.py       # list + publish + import
│   │   │   ├── reminders.py       # sync + list + dismiss
│   │   │   ├── preferences.py     # GET/PATCH user preferences  [new]
│   │   │   ├── study_sessions.py  # full CRUD for study sessions [new]
│   │   │   └── admin.py
│   │   ├── models/                # SQLAlchemy ORM (10 tables)
│   │   ├── services/
│   │   │   └── syllabus_parser.py # multi-pass date + type extraction
│   │   ├── auth.py                # JWT + bcrypt
│   │   ├── rbac.py                # require_role / require_any_role
│   │   └── seed.py                # seeds roles + 9 template courses
│   ├── alembic/versions/          # 2 migration files
│   └── tests/                     # pytest — auth, rbac, courses, assignments,
│                                  # preferences, study_sessions, parser, health
├── frontend/src/
│   ├── pages/
│   │   ├── Dashboard.js           # stats, tasks, reminders, course list + edit modal
│   │   ├── Calendar.js            # weekly view + heatmap + iCal export button
│   │   ├── SyllabusUpload.js      # upload + preview + import
│   │   ├── Templates.js           # searchable template library
│   │   ├── StudySessions.js       # study session CRUD UI          [new]
│   │   ├── Settings.js            # dark mode + timezone + notifications [new]
│   │   ├── Profile.js             # account info + role display
│   │   └── AdminPanel.js          # user/role management
│   ├── context/AuthContext.js     # JWT state + login/register/logout
│   ├── components/                # ProtectedRoute, RoleGuard, ErrorBoundary
│   └── App.js                     # router + sidebar + dark mode init
├── docker-compose.yml             # PostgreSQL 16
├── .github/workflows/ci.yml       # lint → test → build
└── README.md
```

## Local Setup

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL 16 (native or Docker)

### 1. Start PostgreSQL

```bash
# Option A: Docker (recommended)
docker compose up db -d

# Option B: native Homebrew
brew install postgresql@16 && brew services start postgresql@16
createuser -s gatorsync && createdb -O gatorsync gatorsync
```

### 2. Backend

```bash
cd backend

# Create environment file
cp .env.example .env          # or create manually (see Environment Variables below)

# Install dependencies
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed roles + 9 template courses / 106 assignments
python -m app.seed

# Start the API server
uvicorn app.main:app --reload
```

The API is now available at **http://localhost:8000**  
Interactive docs (Swagger UI): **http://localhost:8000/docs**

### 3. Frontend

```bash
cd frontend

cp .env.example .env          # sets REACT_APP_API_URL=http://localhost:8000/api

npm install
npm start
```

The app is now available at **http://localhost:3000**

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://gatorsync:gatorsync@localhost:5432/gatorsync` | PostgreSQL connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing secret (change in production) |
| `DEBUG` | `false` | Enable debug mode |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins (comma-separated) |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000/api` | Backend API base URL |

## API Reference

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Create account, returns JWT |
| POST | `/api/auth/login` | — | Login, returns JWT |
| GET | `/api/auth/me` | JWT | Current user info |

### Courses
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/courses?search=&skip=&limit=` | JWT | List user's courses |
| POST | `/api/courses` | JWT | Create course |
| GET | `/api/courses/{id}` | JWT | Get course |
| PATCH | `/api/courses/{id}` | JWT | Edit course name, code, instructor, dates |
| DELETE | `/api/courses/{id}` | JWT | Delete course + all assignments/tasks |

### Assignments
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/assignments?course_id=&search=&assignment_type=&skip=&limit=` | JWT | List assignments |
| POST | `/api/assignments` | JWT | Create assignment (auto-generates tasks) |
| PATCH | `/api/assignments/{id}` | JWT | Edit assignment |
| DELETE | `/api/assignments/{id}` | JWT | Delete assignment + tasks |

### Schedule
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/schedule/week?start=YYYY-MM-DD` | JWT | 7-day schedule |
| GET | `/api/schedule/day?date=YYYY-MM-DD` | JWT | Single-day schedule |
| GET | `/api/schedule/heatmap?start=&days=` | JWT | Workload buckets per day |
| GET | `/api/schedule/overload?date=` | JWT | Overload flag + minutes |
| GET | `/api/schedule/export.ics?days=30` | JWT | Download iCal file |

### Preferences *(new)*
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/preferences` | JWT | Get user preferences |
| PATCH | `/api/preferences` | JWT | Update dark_mode, timezone, notifications |

### Study Sessions *(new)*
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/study-sessions?skip=&limit=` | JWT | List study sessions |
| POST | `/api/study-sessions` | JWT | Create study session |
| GET | `/api/study-sessions/{id}` | JWT | Get study session |
| PATCH | `/api/study-sessions/{id}` | JWT | Edit study session |
| DELETE | `/api/study-sessions/{id}` | JWT | Delete study session |

### Other endpoints
- `GET /api/tasks?include_completed=&search=&skip=&limit=` — task list
- `PATCH /api/tasks/{id}` — toggle complete / reschedule
- `GET/POST /api/templates`, `POST /api/templates/{id}/import`
- `POST /api/syllabus/parse`, `POST /api/syllabus/import`
- `GET/POST /api/reminders`, `POST /api/reminders/{id}/dismiss`
- `GET /api/admin/users`, `GET /api/admin/roles`, `GET /api/admin/dashboard-stats`

## Testing

```bash
# Backend (pytest)
cd backend
pytest tests/ -v

# Frontend (Jest + Testing Library)
cd frontend
CI=true npm test -- --watchAll=false
```

## Linting

```bash
cd backend  && ruff check app/ tests/
cd frontend && npm run lint
```

## End-to-End Walkthrough

1. **Create an account** at `/signup` → auto-assigned `student` role.
2. **Add a course** — either upload a syllabus at `/upload` (review extracted assignments before importing), or visit `/templates` and one-click import a pre-seeded course.
3. **Dashboard** shows your stats, upcoming tasks (filterable), today's schedule, reminders, and a list of your courses with inline edit buttons.
4. **Calendar** shows the weekly grid with workload heatmap. Drag any task card to a new day to reschedule. Use **Export iCal** to download a `.ics` file.
5. **Study Sessions** — plan dedicated study blocks with a title, location, and time range.
6. **Settings** — toggle dark mode, set your timezone, and configure notification preferences.
7. **Admin Panel** (TA / admin only) — view users, manage roles, see platform stats.

## Roles

| Role | Capabilities |
|------|-------------|
| `student` | Dashboard, syllabus upload, calendar, tasks, templates, study sessions, preferences |
| `ta` | All student features + publish course templates + view admin stats |
| `admin` | All TA features + user list + role management |
