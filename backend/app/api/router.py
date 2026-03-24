from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])

# Future routers — uncomment as features are built:
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus"])
# api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
# api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
# api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
