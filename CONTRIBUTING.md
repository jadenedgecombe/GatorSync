# Contributing to GatorSync

Thanks for your interest in contributing! GatorSync is a syllabus-to-schedule planner built for university students, and every improvement — big or small — helps make it more useful.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Good First Contributions](#good-first-contributions)

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL 16 (Docker recommended)
- Git

### Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/GatorSync.git
cd GatorSync
```

### Local Setup

**1. Start the database**

```bash
docker compose up db -d
```

**2. Set up the backend**

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

API will be running at `http://localhost:8000`. Interactive Swagger docs at `http://localhost:8000/docs`.

**3. Set up the frontend**

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

App will be running at `http://localhost:3000`.

---

## Project Structure

```
GatorSync/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI route handlers (one file per resource)
│   │   ├── models/           # SQLAlchemy ORM models (10 tables)
│   │   ├── services/         # Business logic (e.g. syllabus_parser.py)
│   │   ├── auth.py           # JWT + bcrypt
│   │   ├── rbac.py           # Role-based access control helpers
│   │   └── seed.py           # DB seed data (roles + template courses)
│   ├── alembic/versions/     # Database migrations
│   └── tests/                # pytest test suite
├── frontend/src/
│   ├── pages/                # Top-level React page components
│   ├── components/           # Shared components (ProtectedRoute, etc.)
│   ├── context/              # React context (AuthContext)
│   └── App.js                # Router + sidebar + dark mode
├── database/
├── .github/workflows/        # CI: lint → test → build
└── docker-compose.yml
```

---

## Development Workflow

1. **Create a branch** off `main` for your change:

   ```bash
   git checkout -b feature/my-feature-name
   # or
   git checkout -b fix/short-description
   ```

2. **Make your changes.** Keep commits focused — one logical change per commit.

3. **Lint your code** before pushing (CI will catch failures):

   ```bash
   # Backend
   cd backend && ruff check app/ tests/

   # Frontend
   cd frontend && npm run lint
   ```

4. **Run the tests:**

   ```bash
   # Backend
   cd backend && pytest tests/ -v

   # Frontend
   cd frontend && CI=true npm test -- --watchAll=false
   ```

5. **Push and open a PR** against `main`.

---

## Coding Standards

### Backend (Python / FastAPI)

- Follow the existing route file pattern in `backend/app/api/routes/` — one file per resource, `router = APIRouter()` at the top.
- Use `require_role` / `require_any_role` from `rbac.py` to protect endpoints. Don't reinvent auth checks inline.
- Add a SQLAlchemy model in `backend/app/models/` for any new table. Generate a migration with:
  ```bash
  alembic revision --autogenerate -m "describe your change"
  ```
- Linting is enforced via **Ruff**. Fix all warnings before submitting.
- Type hints are expected on all new functions.

### Frontend (React / JavaScript)

- Pages go in `frontend/src/pages/`, shared components in `frontend/src/components/`.
- Use `AuthContext` (from `context/AuthContext.js`) for auth state — don't manage JWT tokens manually.
- Wrap protected pages in `<ProtectedRoute>` and role-restricted pages in `<RoleGuard>`.
- Dark mode is handled at the app level via CSS class — don't hardcode light-mode colors.
- Accessibility: include `aria-label`, `role`, and `htmlFor`/`id` pairs on all interactive elements.
- Linting is enforced via ESLint (`npm run lint`).

---

## Testing

- **Backend:** Tests live in `backend/tests/`. Cover new routes and services with `pytest`. The existing tests for `auth`, `courses`, `assignments`, `preferences`, and `study_sessions` are good references.
- **Frontend:** Jest + Testing Library. Add component tests for any new pages or significantly changed components.
- CI runs the full test suite on every PR — all checks must pass before merge.

---

## Submitting a Pull Request

- Keep PRs focused. If your change touches multiple unrelated things, split them into separate PRs.
- Write a clear PR description: **what** you changed, **why**, and **how to test it**.
- Reference any related issue with `Closes #123` or `Related to #123`.
- Don't bump version numbers or modify unrelated config files.

---

## Good First Contributions

Not sure where to start? Here are some ideas:

- **Improve syllabus parsing** — the multi-pass heuristics in `services/syllabus_parser.py` can miss edge cases. Add support for more date formats or assignment type keywords.
- **Expand test coverage** — look for routes or services with thin test coverage and add cases.
- **Add more course templates** — templates are seeded in `app/seed.py`. UF-specific courses (MAC, COP, CHM, etc.) are especially welcome.
- **Accessibility improvements** — audit pages for missing ARIA attributes or keyboard navigation gaps.
- **UI polish** — improve responsiveness on mobile viewports, especially the Calendar and Dashboard pages.
- **Open issues** — check the [Issues tab](https://github.com/jadenedgecombe/GatorSync/issues) for reported bugs or requested features.

---

Questions? Open a [GitHub Discussion](https://github.com/jadenedgecombe/GatorSync/discussions) or leave a comment on the relevant issue.