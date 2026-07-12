from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.golfer_profile import GolferProfile
from app.db.models.user import User
from app.schemas.golfer_profile import GolferProfileUpdateRequest


def get_current_user_profile(db: Session, current_user: User) -> GolferProfile:
    golfer_profile = (
        db.query(GolferProfile)
        .filter(GolferProfile.user_id == current_user.id)
        .first()
    )

    if golfer_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Golfer profile not found.",
        )

    return golfer_profile


def update_current_user_profile(
    db: Session,
    current_user: User,
    profile_data: GolferProfileUpdateRequest,
) -> GolferProfile:
    golfer_profile = get_current_user_profile(db, current_user)
    update_data = profile_data.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(golfer_profile, field_name, value)

    db.commit()
    db.refresh(golfer_profile)

    return golfer_profile
