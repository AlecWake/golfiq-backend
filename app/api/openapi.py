from app.schemas.error import ErrorResponse


API_VERSION = "1.0.0"

API_DESCRIPTION = """
GolfIQ connects practice habits with on-course performance so golfers can make
evidence-based training decisions.

## Authentication

Most endpoints require a JWT access token. Register or sign in through the
**Authentication** endpoints, then send the token as
`Authorization: Bearer <access_token>`. In Swagger UI, use **Authorize** and
paste the access token.

## Errors and request tracing

Errors use a consistent envelope containing an error code, message, optional
details, and a request ID. Keep the request ID when reporting an API problem.
"""

CONTACT = {"name": "GolfIQ API Support"}

OPENAPI_TAGS = [
    {
        "name": "Authentication",
        "description": "Account registration, sign-in, and current-user identity.",
    },
    {
        "name": "Golfer Profiles",
        "description": "Personal golf attributes used to tailor GolfIQ insights.",
    },
    {"name": "Clubs", "description": "The authenticated golfer's club inventory."},
    {
        "name": "Practice Sessions",
        "description": "Practice history and links between sessions and swing thoughts.",
    },
    {
        "name": "Swing Thoughts",
        "description": "Reusable swing cues tracked by the authenticated golfer.",
    },
    {"name": "Rounds", "description": "On-course round history."},
    {
        "name": "Round Statistics",
        "description": "Aggregate statistics recorded for individual rounds.",
    },
    {
        "name": "Hole Scores",
        "description": "Hole-by-hole scoring and performance details.",
    },
    {
        "name": "Analytics",
        "description": "Cross-round and practice-to-course performance analysis.",
    },
    {
        "name": "Recommendations",
        "description": "Personalized practice priorities, plans, and schedules.",
    },
    {
        "name": "Dashboard",
        "description": "A compact overview of the golfer's GolfIQ data.",
    },
    {
        "name": "Activity",
        "description": "A filterable timeline of rounds and practice sessions.",
    },
    {
        "name": "Health",
        "description": "Unauthenticated service availability checks.",
    },
]

VALIDATION_ERROR_RESPONSES = {
    422: {
        "model": ErrorResponse,
        "description": "Request validation failed.",
    },
}

AUTHENTICATED_RESPONSES = {
    401: {
        "model": ErrorResponse,
        "description": "Missing, invalid, or expired bearer token.",
    },
    **VALIDATION_ERROR_RESPONSES,
}
