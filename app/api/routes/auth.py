from app.db.models.user import User
from app.dependencies.auth import get_current_user

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.auth import UserRegisterRequest, UserRegisterResponse
from app.services.auth_service import register_user

from app.schemas.auth import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.auth_service import login_user, register_user

from app.core.security import create_access_token
from app.schemas.auth import TokenResponse


router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    return register_user(db, user_data)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    user = login_user(db, login_data.email, login_data.password)

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }

@router.get(
    "/me",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_200_OK,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user