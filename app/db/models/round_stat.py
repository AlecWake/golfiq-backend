from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoundStat(Base):
    __tablename__ = "round_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    round_id: Mapped[int] = mapped_column(
        ForeignKey("rounds.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    fairways_hit: Mapped[int] = mapped_column(Integer, nullable=False)
    fairways_possible: Mapped[int] = mapped_column(Integer, nullable=False)
    greens_in_regulation: Mapped[int] = mapped_column(Integer, nullable=False)
    putts: Mapped[int] = mapped_column(Integer, nullable=False)
    penalties: Mapped[int] = mapped_column(Integer, nullable=False)
    up_and_downs: Mapped[int] = mapped_column(Integer, nullable=False)
    sand_saves: Mapped[int] = mapped_column(Integer, nullable=False)

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

    round = relationship("Round", back_populates="stats")
