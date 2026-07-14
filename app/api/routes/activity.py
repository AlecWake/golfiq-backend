from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.activity import ActivityFeedResponse, ActivityType
from app.services.activity_service import get_activity_feed


router = APIRouter()


@router.get(
    "",
    response_model=ActivityFeedResponse,
    status_code=status.HTTP_200_OK,
    summary="List recent activity",
    description="Return a paginated, filterable timeline of rounds and practice sessions.",
)
def get_activity_feed_endpoint(
    activity_type: ActivityType = ActivityType.ALL,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_from must not be after date_to.",
        )

    return get_activity_feed(
        db=db,
        current_user=current_user,
        activity_type=activity_type,
        limit=limit,
        offset=offset,
        date_from=date_from,
        date_to=date_to,
    )
