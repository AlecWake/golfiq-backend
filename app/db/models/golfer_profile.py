from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GolferProfile(Base):
    __tablename__ = "golfer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    current_handicap_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    scoring_goal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dominant_miss: Mapped[str | None] = mapped_column(String(100), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="golfer_profile",
    )