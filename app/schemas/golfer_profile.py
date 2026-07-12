from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GolferProfileUpdateRequest(BaseModel):
    current_handicap_estimate: float | None = Field(default=None, ge=-10.0, le=54.0)
    scoring_goal: str | None = Field(default=None, max_length=100)
    dominant_miss: str | None = Field(default=None, max_length=100)
    experience_level: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("scoring_goal", "dominant_miss")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        if not value:
            raise ValueError("Value must not be empty.")
        return value

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()
        allowed_levels = {"beginner", "intermediate", "advanced"}
        if value not in allowed_levels:
            raise ValueError(
                "Experience level must be beginner, intermediate, or advanced."
            )
        return value


class GolferProfileResponse(BaseModel):
    id: int
    user_id: int
    current_handicap_estimate: float | None
    scoring_goal: str | None
    dominant_miss: str | None
    experience_level: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
