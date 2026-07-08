from typing import Literal

from pydantic import BaseModel


RecommendationCategory = Literal[
    "Practice",
    "Putting",
    "Accuracy",
    "Ball Striking",
    "Penalties",
    "Consistency",
    "General",
]
RecommendationPriority = Literal["low", "medium", "high"]


class RecommendationResponse(BaseModel):
    recommendation_id: str
    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    description: str
