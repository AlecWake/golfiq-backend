from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.round import RoundCreateRequest, RoundUpdateRequest


def create_round(
    db: Session,
    current_user: User,
    round_data: RoundCreateRequest,
) -> Round:
    round = Round(
        user_id=current_user.id,
        round_date=round_data.round_date,
        course_name=round_data.course_name,
        tee_box=round_data.tee_box,
        holes_played=round_data.holes_played,
        total_score=round_data.total_score,
        notes=round_data.notes,
    )

    db.add(round)
    db.commit()
    db.refresh(round)

    return round


def get_user_rounds(db: Session, current_user: User) -> list[Round]:
    return db.query(Round).filter(Round.user_id == current_user.id).all()


def get_user_round(db: Session, current_user: User, round_id: int) -> Round:
    round = (
        db.query(Round)
        .filter(Round.id == round_id, Round.user_id == current_user.id)
        .first()
    )

    if round is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found.",
        )

    return round


def update_round(
    db: Session,
    current_user: User,
    round_id: int,
    round_data: RoundUpdateRequest,
) -> Round:
    round = get_user_round(db, current_user, round_id)

    update_data = round_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(round, field, value)

    db.commit()
    db.refresh(round)

    return round


def delete_round(db: Session, current_user: User, round_id: int) -> None:
    round = get_user_round(db, current_user, round_id)

    db.delete(round)
    db.commit()
