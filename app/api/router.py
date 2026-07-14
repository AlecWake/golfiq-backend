from fastapi import APIRouter

from app.api.openapi import AUTHENTICATED_RESPONSES, VALIDATION_ERROR_RESPONSES
from app.api.routes import (
    activity,
    analytics,
    auth,
    clubs,
    dashboard,
    health,
    hole_scores,
    practice_sessions,
    recommendations,
    round_analytics,
    round_stats,
    rounds,
    swing_thoughts,
    users,
)

api_router = APIRouter()

api_router.include_router(
    activity.router,
    prefix="/activity",
    tags=["Activity"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    responses=VALIDATION_ERROR_RESPONSES,
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    clubs.router,
    prefix="/clubs",
    tags=["Clubs"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Golfer Profiles"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    swing_thoughts.router,
    prefix="/swing-thoughts",
    tags=["Swing Thoughts"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    practice_sessions.router,
    prefix="/practice-sessions",
    tags=["Practice Sessions"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["Recommendations"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    rounds.router,
    prefix="/rounds",
    tags=["Rounds"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    round_stats.router,
    prefix="/rounds",
    tags=["Round Statistics"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    round_analytics.router,
    prefix="/rounds",
    tags=["Analytics"],
    responses=AUTHENTICATED_RESPONSES,
)

api_router.include_router(
    hole_scores.router,
    prefix="/rounds",
    tags=["Hole Scores"],
    responses=AUTHENTICATED_RESPONSES,
)
