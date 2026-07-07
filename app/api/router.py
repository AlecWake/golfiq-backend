from fastapi import APIRouter

from app.api.routes import (
    analytics,
    auth,
    clubs,
    health,
    hole_scores,
    practice_sessions,
    round_analytics,
    round_stats,
    rounds,
    swing_thoughts,
)

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
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
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

api_router.include_router(
    rounds.router,
    prefix="/rounds",
    tags=["rounds"],
)

api_router.include_router(
    round_stats.router,
    prefix="/rounds",
    tags=["round-stats"],
)

api_router.include_router(
    round_analytics.router,
    prefix="/rounds",
    tags=["round-analytics"],
)

api_router.include_router(
    hole_scores.router,
    prefix="/rounds",
    tags=["hole-scores"],
)
