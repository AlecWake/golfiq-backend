from datetime import datetime

from pydantic import BaseModel, Field


class SwingThoughtCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    category: str | None = Field(default=None, max_length=50)


class SwingThoughtUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    category: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class SwingThoughtResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    category: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }