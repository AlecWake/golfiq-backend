from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = Field(
        description="Current service health state.",
        examples=["ok"],
    )
    service: str = Field(
        description="Name of the responding service.",
        examples=["GolfIQ Backend"],
    )

    model_config = ConfigDict(title="API Health Response")
