from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.swing_thought import (
    SwingThoughtCreateRequest,
    SwingThoughtUpdateRequest,
)


def create_swing_thought(
    db: Session,
    current_user: User,
    swing_thought_data: SwingThoughtCreateRequest,
) -> SwingThought:
    swing_thought = SwingThought(
        user_id=current_user.id,
        title=swing_thought_data.title,
        description=swing_thought_data.description,
        category=swing_thought_data.category,
    )

    db.add(swing_thought)
    db.commit()
    db.refresh(swing_thought)

    return swing_thought


def get_user_swing_thoughts(
    db: Session,
    current_user: User,
) -> list[SwingThought]:
    return (
        db.query(SwingThought)
        .filter(SwingThought.user_id == current_user.id)
        .all()
    )


def get_user_swing_thought(
    db: Session,
    current_user: User,
    swing_thought_id: int,
) -> SwingThought:
    swing_thought = (
        db.query(SwingThought)
        .filter(
            SwingThought.id == swing_thought_id,
            SwingThought.user_id == current_user.id,
        )
        .first()
    )

    if swing_thought is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swing thought not found.",
        )

    return swing_thought


def update_swing_thought(
    db: Session,
    current_user: User,
    swing_thought_id: int,
    swing_thought_data: SwingThoughtUpdateRequest,
) -> SwingThought:
    swing_thought = get_user_swing_thought(db, current_user, swing_thought_id)

    update_data = swing_thought_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(swing_thought, field, value)

    db.commit()
    db.refresh(swing_thought)

    return swing_thought


def delete_swing_thought(
    db: Session,
    current_user: User,
    swing_thought_id: int,
) -> None:
    swing_thought = get_user_swing_thought(db, current_user, swing_thought_id)

    db.delete(swing_thought)
    db.commit()