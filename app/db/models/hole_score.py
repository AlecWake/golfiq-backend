from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HoleScore(Base):
    __tablename__ = "hole_scores"
    __table_args__ = (
        UniqueConstraint("round_id", "hole_number", name="uq_hole_scores_round_hole"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    round_id: Mapped[int] = mapped_column(
        ForeignKey("rounds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    hole_number: Mapped[int] = mapped_column(Integer, nullable=False)
    strokes: Mapped[int] = mapped_column(Integer, nullable=False)
    putts: Mapped[int] = mapped_column(Integer, nullable=False)
    fairway_hit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    green_in_regulation: Mapped[bool] = mapped_column(Boolean, nullable=False)
    penalty_strokes: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    round = relationship("Round", back_populates="hole_scores")
