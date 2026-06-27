from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.club import Club
from app.db.models.user import User
from app.schemas.club import ClubCreateRequest, ClubUpdateRequest


def create_club(
    db: Session,
    current_user: User,
    club_data: ClubCreateRequest,
) -> Club:
    club = Club(
        user_id=current_user.id,
        club_name=club_data.club_name,
        club_type=club_data.club_type,
        manufacturer=club_data.manufacturer,
        model=club_data.model,
        loft=club_data.loft,
        carry_distance=club_data.carry_distance,
        total_distance=club_data.total_distance,
    )

    db.add(club)
    db.commit()
    db.refresh(club)

    return club


def get_user_clubs(db: Session, current_user: User) -> list[Club]:
    return db.query(Club).filter(Club.user_id == current_user.id).all()


def get_user_club(db: Session, current_user: User, club_id: int) -> Club:
    club = (
        db.query(Club)
        .filter(Club.id == club_id, Club.user_id == current_user.id)
        .first()
    )

    if club is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found.",
        )

    return club


def update_club(
    db: Session,
    current_user: User,
    club_id: int,
    club_data: ClubUpdateRequest,
) -> Club:
    club = get_user_club(db, current_user, club_id)

    update_data = club_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(club, field, value)

    db.commit()
    db.refresh(club)

    return club


def delete_club(db: Session, current_user: User, club_id: int) -> None:
    club = get_user_club(db, current_user, club_id)

    db.delete(club)
    db.commit()