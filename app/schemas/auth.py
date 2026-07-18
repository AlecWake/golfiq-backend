from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(
        description="Email address used to sign in.",
        examples=["alex.golfer@example.com"],
    )
    password: str = Field(
        min_length=8,
        description="Account password; must contain at least eight characters.",
        examples=["practice-more-2026"],
    )
    first_name: str | None = Field(
        default=None,
        description="Golfer's preferred first name.",
        examples=["Alex"],
    )
    last_name: str | None = Field(
        default=None,
        description="Golfer's last name.",
        examples=["Morgan"],
    )

    model_config = ConfigDict(title="User Registration Request")


class UserRegisterResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(
        description="Registered account email address.",
        examples=["alex.golfer@example.com"],
    )
    password: str = Field(
        description="Registered account password.",
        examples=["practice-more-2026"],
    )

    model_config = ConfigDict(title="User Login Request")


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="JWT to send in the Authorization header.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        description="Authentication scheme used by the token.",
        examples=["bearer"],
    )
    user: UserRegisterResponse

    model_config = ConfigDict(title="Authentication Token Response")
