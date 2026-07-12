from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models.golfer_profile import GolferProfile
from app.db.models.user import User


MISS_FOCUS = {
    "slice": ("Accuracy", "Tee Shot Accuracy", "face control and path awareness"),
    "hook": ("Accuracy", "Tee Shot Accuracy", "face control and start direction"),
    "push": ("Accuracy", "Tee Shot Accuracy", "alignment and face control"),
    "pull": ("Accuracy", "Tee Shot Accuracy", "alignment and path control"),
    "top": ("Ball Striking", "Contact", "contact and low-point control"),
    "fat": ("Ball Striking", "Contact", "contact and low-point control"),
    "inconsistent": ("Ball Striking", "Contact", "fundamentals and strike consistency"),
}


@dataclass(frozen=True)
class ProfileContext:
    experience_level: str | None = None
    dominant_miss: str | None = None
    scoring_goal: str | None = None
    current_handicap_estimate: float | None = None

    @property
    def miss_focus(self) -> tuple[str, str, str] | None:
        if self.dominant_miss is None:
            return None
        return MISS_FOCUS.get(self.dominant_miss)

    @property
    def fallback_focus(self) -> tuple[str, str, str] | None:
        if self.miss_focus is not None:
            return self.miss_focus
        if self.experience_level == "beginner":
            return ("Ball Striking", "Contact", "fundamentals and consistent contact")
        if self.experience_level == "intermediate":
            return ("Accuracy", "Target Practice", "targeted accuracy and keeping the ball in play")
        if self.experience_level == "advanced":
            return ("Consistency", "Consistency", "a narrow, measurable performance focus")
        if self.current_handicap_estimate is None:
            return None
        if self.current_handicap_estimate >= 30:
            return ("Ball Striking", "Contact", "fundamentals and consistent contact")
        if self.current_handicap_estimate >= 20:
            return ("Penalties", "Course Management", "consistency and penalty reduction")
        if self.current_handicap_estimate >= 10:
            return ("Iron Play", "Approach Play", "GIR and scoring refinement")
        return ("Consistency", "Consistency", "a narrow, measurable performance focus")

    def category_tie_breaker(self, category: str) -> int:
        """Analytics severity stays primary; profile context only resolves ties."""
        score = 0
        if self.miss_focus is not None and category == self.miss_focus[0]:
            score += 3
        if self.experience_level == "beginner" and category in {
            "Ball Striking", "Practice Frequency", "Swing Thoughts", "Putting"
        }:
            score += 2
        elif self.experience_level == "intermediate" and category in {
            "Iron Play", "Accuracy", "Penalties", "Putting"
        }:
            score += 2
        elif self.experience_level == "advanced" and category in {
            "Consistency", "Iron Play", "Putting", "Accuracy"
        }:
            score += 2
        if self.current_handicap_estimate is not None:
            if self.current_handicap_estimate >= 30 and category in {
                "Ball Striking", "Practice Frequency"
            }:
                score += 1
            elif self.current_handicap_estimate >= 20 and category in {
                "Consistency", "Penalties", "Accuracy"
            }:
                score += 1
            elif self.current_handicap_estimate >= 10 and category in {
                "Iron Play", "Putting"
            }:
                score += 1
            elif self.current_handicap_estimate < 10 and category == "Consistency":
                score += 1
        return score

    def goal_suffix(self) -> str:
        if self.scoring_goal is None:
            return ""
        return f" This focus supports your goal: {self.scoring_goal}."


def get_profile_context(db: Session, current_user: User) -> ProfileContext:
    golfer_profile = (
        db.query(GolferProfile)
        .filter(GolferProfile.user_id == current_user.id)
        .first()
    )
    if golfer_profile is None:
        return ProfileContext()

    return ProfileContext(
        experience_level=_normalized(golfer_profile.experience_level),
        dominant_miss=_normalized(golfer_profile.dominant_miss),
        scoring_goal=_trimmed(golfer_profile.scoring_goal),
        current_handicap_estimate=golfer_profile.current_handicap_estimate,
    )


def _normalized(value: str | None) -> str | None:
    trimmed_value = _trimmed(value)
    return trimmed_value.lower() if trimmed_value is not None else None


def _trimmed(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed_value = value.strip()
    return trimmed_value or None
