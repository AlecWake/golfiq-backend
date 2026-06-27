from datetime import datetime

from pydantic import BaseModel, Field


class ClubCreateRequest(BaseModel):
    club_name: str = Field(min_length=1, max_length=100)
    club_type: str = Field(min_length=1, max_length=50)
    manufacturer: str | None = None
    model: str | None = None
    loft: float | None = None
    carry_distance: int | None = Field(default=None, ge=0)
    total_distance: int | None = Field(default=None, ge=0)


class ClubUpdateRequest(BaseModel):
    club_name: str | None = Field(default=None, min_length=1, max_length=100)
    club_type: str | None = Field(default=None, min_length=1, max_length=50)
    manufacturer: str | None = None
    model: str | None = None
    loft: float | None = None
    carry_distance: int | None = Field(default=None, ge=0)
    total_distance: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ClubResponse(BaseModel):
    id: int
    user_id: int
    club_name: str
    club_type: str
    manufacturer: str | None
    model: str | None
    loft: float | None
    carry_distance: int | None
    total_distance: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }