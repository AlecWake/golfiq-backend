from datetime import datetime
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


PracticePlanConfidence = Literal["Low", "Moderate", "High"]


class PracticePlanItemResponse(BaseModel):
    order: int
    category: PracticePriorityCategory
    title: str
    reason: str
    recommended_minutes: int
    supporting_metric: str
    priority: PracticePriorityLevel


class PracticePlanResponse(BaseModel):
    generated_at: datetime
    overall_focus: str
    confidence: PracticePlanConfidence
    estimated_session_length_minutes: int
    practice_items: list[PracticePlanItemResponse]


class WeeklyScheduleFocusItemResponse(BaseModel):
    order: int
    category: PracticePriorityCategory
    title: str
    recommended_minutes: int
    reason: str
    priority: PracticePriorityLevel


class WeeklyScheduleEntryResponse(BaseModel):
    day_number: int
    session_title: str
    total_minutes: int
    focus_items: list[WeeklyScheduleFocusItemResponse]


class WeeklyPracticeScheduleResponse(BaseModel):
    generated_at: datetime
    available_days: int
    minutes_per_day: int
    total_weekly_minutes: int
    overall_focus: str
    confidence: PracticePlanConfidence
    schedule: list[WeeklyScheduleEntryResponse]
