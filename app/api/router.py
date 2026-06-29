from fastapi import APIRouter

from app.api.routes import auth, clubs, health, practice_sessions, swing_thoughts

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    clubs.router,
    prefix="/clubs",
    tags=["clubs"],
)

api_router.include_router(
    swing_thoughts.router,
    prefix="/swing-thoughts",
    tags=["swing-thoughts"],
)

api_router.include_router(
    practice_sessions.router,
    prefix="/practice-sessions",
    tags=["practice-sessions"],
)