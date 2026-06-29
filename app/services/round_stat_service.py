from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.round_stat import RoundStat
from app.db.models.user import User
from app.schemas.round_stat import RoundStatCreateRequest, RoundStatUpdateRequest
from app.services.round_service import get_user_round


def create_round_stat(
    db: Session,
    current_user: User,
    round_id: int,
    stat_data: RoundStatCreateRequest,
) -> RoundStat:
    round = get_user_round(db, current_user, round_id)

    existing_stat = db.query(RoundStat).filter(RoundStat.round_id == round.id).first()

    if existing_stat is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Round statistics already exist.",
        )

    round_stat = RoundStat(
        round_id=round.id,
        fairways_hit=stat_data.fairways_hit,
        fairways_possible=stat_data.fairways_possible,
        greens_in_regulation=stat_data.greens_in_regulation,
        putts=stat_data.putts,
        penalties=stat_data.penalties,
        up_and_downs=stat_data.up_and_downs,
        sand_saves=stat_data.sand_saves,
    )

    db.add(round_stat)
    db.commit()
    db.refresh(round_stat)

    return round_stat


def get_round_stat(db: Session, current_user: User, round_id: int) -> RoundStat:
    round = get_user_round(db, current_user, round_id)

    round_stat = db.query(RoundStat).filter(RoundStat.round_id == round.id).first()

    if round_stat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round statistics not found.",
        )

    return round_stat


def update_round_stat(
    db: Session,
    current_user: User,
    round_id: int,
    stat_data: RoundStatUpdateRequest,
) -> RoundStat:
    round_stat = get_round_stat(db, current_user, round_id)

    update_data = stat_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(round_stat, field, value)

    db.commit()
    db.refresh(round_stat)

    return round_stat


def delete_round_stat(db: Session, current_user: User, round_id: int) -> None:
    round_stat = get_round_stat(db, current_user, round_id)

    db.delete(round_stat)
    db.commit()
