from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base


practice_session_swing_thoughts = Table(
    "practice_session_swing_thoughts",
    Base.metadata,
    Column(
        "practice_session_id",
        ForeignKey("practice_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "swing_thought_id",
        ForeignKey("swing_thoughts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
