from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.hole_score import HoleScore
from app.db.models.user import User
from app.schemas.hole_score import HoleScoreCreateRequest, HoleScoreUpdateRequest
from app.services.round_service import get_user_round


def create_hole_score(
    db: Session,
    current_user: User,
    round_id: int,
    hole_score_data: HoleScoreCreateRequest,
) -> HoleScore:
    round = get_user_round(db, current_user, round_id)

    existing_hole_score = (
        db.query(HoleScore)
        .filter(
            HoleScore.round_id == round.id,
            HoleScore.hole_number == hole_score_data.hole_number,
        )
        .first()
    )

    if existing_hole_score is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hole score already exists for this round.",
        )

    hole_score = HoleScore(
        round_id=round.id,
        hole_number=hole_score_data.hole_number,
        strokes=hole_score_data.strokes,
        putts=hole_score_data.putts,
        fairway_hit=hole_score_data.fairway_hit,
        green_in_regulation=hole_score_data.green_in_regulation,
        penalty_strokes=hole_score_data.penalty_strokes,
        notes=hole_score_data.notes,
    )

    db.add(hole_score)
    db.commit()
    db.refresh(hole_score)

    return hole_score


def get_round_hole_scores(
    db: Session,
    current_user: User,
    round_id: int,
) -> list[HoleScore]:
    round = get_user_round(db, current_user, round_id)

    return (
        db.query(HoleScore)
        .filter(HoleScore.round_id == round.id)
        .order_by(HoleScore.hole_number)
        .all()
    )


def get_round_hole_score(
    db: Session,
    current_user: User,
    round_id: int,
    hole_score_id: int,
) -> HoleScore:
    round = get_user_round(db, current_user, round_id)

    hole_score = (
        db.query(HoleScore)
        .filter(
            HoleScore.id == hole_score_id,
            HoleScore.round_id == round.id,
        )
        .first()
    )

    if hole_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hole score not found.",
        )

    return hole_score


def update_hole_score(
    db: Session,
    current_user: User,
    round_id: int,
    hole_score_id: int,
    hole_score_data: HoleScoreUpdateRequest,
) -> HoleScore:
    hole_score = get_round_hole_score(db, current_user, round_id, hole_score_id)

    update_data = hole_score_data.model_dump(exclude_unset=True)

    new_hole_number = update_data.get("hole_number")
    if new_hole_number is not None and new_hole_number != hole_score.hole_number:
        existing_hole_score = (
            db.query(HoleScore)
            .filter(
                HoleScore.round_id == hole_score.round_id,
                HoleScore.hole_number == new_hole_number,
            )
            .first()
        )

        if existing_hole_score is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hole score already exists for this round.",
            )

    for field, value in update_data.items():
        setattr(hole_score, field, value)

    db.commit()
    db.refresh(hole_score)

    return hole_score


def delete_hole_score(
    db: Session,
    current_user: User,
    round_id: int,
    hole_score_id: int,
) -> None:
    hole_score = get_round_hole_score(db, current_user, round_id, hole_score_id)

    db.delete(hole_score)
    db.commit()
