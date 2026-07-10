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
PracticePriorityCategory = Literal[
    "Putting",
    "Driving",
    "Iron Play",
    "Accuracy",
    "Ball Striking",
    "Penalties",
    "Consistency",
    "Practice Frequency",
    "Swing Thoughts",
]
PracticePriorityLevel = Literal["High", "Medium", "Low"]


class RecommendationResponse(BaseModel):
    recommendation_id: str
    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    description: str


class PracticePriorityResponse(BaseModel):
    priority_rank: int
    category: PracticePriorityCategory
    priority_level: PracticePriorityLevel
    title: str
    explanation: str
    supporting_metric: str
    suggested_focus: str
