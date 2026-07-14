from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClubCreateRequest(BaseModel):
    club_name: str = Field(
        min_length=1,
        max_length=100,
        description="Display name used to identify the club.",
        examples=["7 Iron"],
    )
    club_type: str = Field(
        min_length=1,
        max_length=50,
        description="Club category.",
        examples=["Iron"],
    )
    manufacturer: str | None = Field(default=None, examples=["Titleist"])
    model: str | None = Field(default=None, examples=["T150"])
    loft: float | None = Field(
        default=None,
        description="Club loft in degrees.",
        examples=[32.0],
    )
    carry_distance: int | None = Field(
        default=None,
        ge=0,
        description="Typical carry distance in yards.",
        examples=[155],
    )
    total_distance: int | None = Field(
        default=None,
        ge=0,
        description="Typical total distance in yards.",
        examples=[162],
    )

    model_config = ConfigDict(title="Club Creation Request")


class ClubUpdateRequest(BaseModel):
    club_name: str | None = Field(default=None, min_length=1, max_length=100)
    club_type: str | None = Field(default=None, min_length=1, max_length=50)
    manufacturer: str | None = None
    model: str | None = None
    loft: float | None = None
    carry_distance: int | None = Field(default=None, ge=0)
    total_distance: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    model_config = ConfigDict(title="Club Update Request")


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
