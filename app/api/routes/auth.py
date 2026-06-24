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
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    user = login_user(db, login_data.email, login_data.password)

    return {
        "message": "Login successful.",
        "user": user,
    }