from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.schemas.error import ErrorResponse
from app.services.auth_service import login_user, register_user


router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    description="Create a GolfIQ account and return the new user record.",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "An account already exists for the supplied email.",
        }
    },
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
    summary="Sign in",
    description="Validate account credentials and issue a JWT bearer token.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "The supplied email or password is invalid.",
        }
    },
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
    summary="Get the current user",
    description="Return the user represented by the supplied bearer token.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Missing, invalid, or expired bearer token.",
        }
    },
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user
