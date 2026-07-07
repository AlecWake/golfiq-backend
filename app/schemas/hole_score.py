from datetime import datetime

from pydantic import BaseModel, Field


class HoleScoreCreateRequest(BaseModel):
    hole_number: int = Field(ge=1, le=18)
    strokes: int = Field(gt=0)
    putts: int = Field(ge=0)
    fairway_hit: bool
    green_in_regulation: bool
    penalty_strokes: int = Field(ge=0)
    notes: str | None = None


class HoleScoreUpdateRequest(BaseModel):
    hole_number: int | None = Field(default=None, ge=1, le=18)
    strokes: int | None = Field(default=None, gt=0)
    putts: int | None = Field(default=None, ge=0)
    fairway_hit: bool | None = None
    green_in_regulation: bool | None = None
    penalty_strokes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class HoleScoreResponse(BaseModel):
    id: int
    round_id: int
    hole_number: int
    strokes: int
    putts: int
    fairway_hit: bool
    green_in_regulation: bool
    penalty_strokes: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
