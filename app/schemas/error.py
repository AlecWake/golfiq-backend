from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    code: str = Field(
        description="Stable machine-readable error code.",
        examples=["validation_error"],
    )
    message: str = Field(
        description="Human-readable explanation of the error.",
        examples=["Request validation failed."],
    )
    details: Any | None = Field(
        default=None,
        description="Optional structured context about the error.",
    )


class ErrorResponse(BaseModel):
    error: ErrorDetail = Field(description="Error classification and context.")
    request_id: str = Field(
        description="Request identifier to include in support or log searches.",
        examples=["f4b7d146-0fac-4e19-a871-b8ea00336f67"],
    )

    model_config = ConfigDict(title="Standard API Error")
