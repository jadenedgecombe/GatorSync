from fastapi import APIRouter

from app.api.routes import (
    admin,
    assignments,
    auth,
    courses,
    db_check,
    health,
    preferences,
    reminders,
    schedule,
    study_sessions,
    syllabus,
    tasks,
    templates,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(db_check.router, tags=["database"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(study_sessions.router, prefix="/study-sessions", tags=["study-sessions"])
