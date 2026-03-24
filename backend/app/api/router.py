from fastapi import APIRouter

from app.api.routes import auth, health, db_check

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(db_check.router, tags=["database"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus"])
# api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
# api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
# api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
