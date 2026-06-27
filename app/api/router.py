from fastapi import APIRouter

from app.api.routes import auth, clubs, health

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