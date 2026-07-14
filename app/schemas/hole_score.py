from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HoleScoreCreateRequest(BaseModel):
    hole_number: int = Field(
        ge=1,
        le=18,
        description="Course hole number.",
        examples=[7],
    )
    strokes: int = Field(
        gt=0,
        description="Strokes taken on the hole.",
        examples=[5],
    )
    putts: int = Field(
        ge=0,
        description="Putts taken on the hole.",
        examples=[2],
    )
    fairway_hit: bool = Field(
        description="Whether the tee shot finished in the fairway.",
        examples=[True],
    )
    green_in_regulation: bool = Field(
        description="Whether the green was reached in regulation.",
        examples=[False],
    )
    penalty_strokes: int = Field(
        ge=0,
        description="Penalty strokes taken on the hole.",
        examples=[0],
    )
    notes: str | None = Field(
        default=None,
        description="Optional free-form notes for the hole.",
        examples=["Missed approach short; two-putted from 25 feet."],
    )

    model_config = ConfigDict(title="Hole Score Creation Request")


class HoleScoreUpdateRequest(BaseModel):
    hole_number: int | None = Field(default=None, ge=1, le=18)
    strokes: int | None = Field(default=None, gt=0)
    putts: int | None = Field(default=None, ge=0)
    fairway_hit: bool | None = None
    green_in_regulation: bool | None = None
    penalty_strokes: int | None = Field(default=None, ge=0)
    notes: str | None = None

    model_config = ConfigDict(title="Hole Score Update Request")


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
