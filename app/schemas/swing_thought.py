from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SwingThoughtCreateRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        description="Short, memorable name for the swing cue.",
        examples=["Smooth tempo"],
    )
    description: str | None = Field(
        default=None,
        description="Optional detail describing how the cue should feel.",
        examples=["Feel a balanced three-to-one backswing tempo."],
    )
    category: str | None = Field(
        default=None,
        max_length=50,
        description="Optional grouping for the swing cue.",
        examples=["Tempo"],
    )

    model_config = ConfigDict(title="Swing Thought Creation Request")


class SwingThoughtUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    category: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None

    model_config = ConfigDict(title="Swing Thought Update Request")


class SwingThoughtResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    category: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
