from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoundStatCreateRequest(BaseModel):
    fairways_hit: int = Field(ge=0, description="Fairways hit.", examples=[8])
    fairways_possible: int = Field(
        ge=0,
        description="Holes where a fairway could be hit.",
        examples=[14],
    )
    greens_in_regulation: int = Field(
        ge=0,
        description="Greens reached in regulation.",
        examples=[7],
    )
    putts: int = Field(ge=0, description="Total putts.", examples=[34])
    penalties: int = Field(
        ge=0,
        description="Total penalty strokes.",
        examples=[2],
    )
    up_and_downs: int = Field(
        ge=0,
        description="Successful up-and-downs.",
        examples=[3],
    )
    sand_saves: int = Field(
        ge=0,
        description="Successful sand saves.",
        examples=[1],
    )

    model_config = ConfigDict(title="Round Statistics Creation Request")


class RoundStatUpdateRequest(BaseModel):
    fairways_hit: int | None = Field(default=None, ge=0)
    fairways_possible: int | None = Field(default=None, ge=0)
    greens_in_regulation: int | None = Field(default=None, ge=0)
    putts: int | None = Field(default=None, ge=0)
    penalties: int | None = Field(default=None, ge=0)
    up_and_downs: int | None = Field(default=None, ge=0)
    sand_saves: int | None = Field(default=None, ge=0)

    model_config = ConfigDict(title="Round Statistics Update Request")


class RoundStatResponse(BaseModel):
    id: int
    round_id: int
    fairways_hit: int
    fairways_possible: int
    greens_in_regulation: int
    putts: int
    penalties: int
    up_and_downs: int
    sand_saves: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
