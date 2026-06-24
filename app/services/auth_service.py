from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.golfer_profile import GolferProfile
from app.db.models.user import User
from app.schemas.auth import UserRegisterRequest
from app.core.security import hash_password, verify_password


def register_user(db: Session, user_data: UserRegisterRequest) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="golfer",
    )

    db.add(user)
    db.flush()

    profile = GolferProfile(user_id=user.id)
    db.add(profile)

    db.commit()
    db.refresh(user)

    return user

def login_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return user