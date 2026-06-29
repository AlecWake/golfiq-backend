from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.practice_session import (
    PracticeSessionCreateRequest,
    PracticeSessionUpdateRequest,
)


def create_practice_session(
    db: Session,
    current_user: User,
    practice_session_data: PracticeSessionCreateRequest,
) -> PracticeSession:
    practice_session = PracticeSession(
        user_id=current_user.id,
        session_date=practice_session_data.session_date,
        practice_type=practice_session_data.practice_type,
        duration_minutes=practice_session_data.duration_minutes,
        notes=practice_session_data.notes,
        overall_rating=practice_session_data.overall_rating,
    )

    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)

    return practice_session


def get_user_practice_sessions(
    db: Session,
    current_user: User,
) -> list[PracticeSession]:
    return (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .all()
    )


def get_user_practice_session(
    db: Session,
    current_user: User,
    practice_session_id: int,
) -> PracticeSession:
    practice_session = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.id == practice_session_id,
            PracticeSession.user_id == current_user.id,
        )
        .first()
    )

    if practice_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found.",
        )

    return practice_session


def update_practice_session(
    db: Session,
    current_user: User,
    practice_session_id: int,
    practice_session_data: PracticeSessionUpdateRequest,
) -> PracticeSession:
    practice_session = get_user_practice_session(
        db,
        current_user,
        practice_session_id,
    )

    update_data = practice_session_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(practice_session, field, value)

    db.commit()
    db.refresh(practice_session)

    return practice_session


def delete_practice_session(
    db: Session,
    current_user: User,
    practice_session_id: int,
) -> None:
    practice_session = get_user_practice_session(
        db,
        current_user,
        practice_session_id,
    )

    db.delete(practice_session)
    db.commit()


def link_swing_thought_to_practice_session(
    db: Session,
    current_user: User,
    practice_session_id: int,
    swing_thought_id: int,
) -> SwingThought:
    practice_session = get_user_practice_session(
        db,
        current_user,
        practice_session_id,
    )

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

    if swing_thought in practice_session.swing_thoughts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Swing thought is already linked to this practice session.",
        )

    practice_session.swing_thoughts.append(swing_thought)
    db.commit()
    db.refresh(swing_thought)

    return swing_thought


def unlink_swing_thought_from_practice_session(
    db: Session,
    current_user: User,
    practice_session_id: int,
    swing_thought_id: int,
) -> None:
    practice_session = get_user_practice_session(
        db,
        current_user,
        practice_session_id,
    )

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

    if swing_thought not in practice_session.swing_thoughts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session swing thought link not found.",
        )

    practice_session.swing_thoughts.remove(swing_thought)
    db.commit()


def get_practice_session_swing_thoughts(
    db: Session,
    current_user: User,
    practice_session_id: int,
) -> list[SwingThought]:
    practice_session = get_user_practice_session(
        db,
        current_user,
        practice_session_id,
    )

    return list(practice_session.swing_thoughts)
