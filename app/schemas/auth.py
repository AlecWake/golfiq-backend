from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str | None = None
    last_name: str | None = None


class UserRegisterResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    message: str
    user: UserRegisterResponse

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRegisterResponse