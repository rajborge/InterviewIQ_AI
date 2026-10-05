import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base_class import Base

if TYPE_CHECKING:
    from .interview import Interview


class CommunicationAnalysis(Base):
    __tablename__ = "communication_analyses"

    __table_args__ = (
        CheckConstraint("filler_word_count >= 0", name="ck_comm_analyses_filler_non_negative"),

        CheckConstraint("long_pause_count >= 0", name="ck_comm_analyses_long_pause_non_negative"),

        CheckConstraint(
            "total_pause_duration_seconds IS NULL OR total_pause_duration_seconds >= 0",
            name="ck_comm_analyses_pause_duration_non_negative",
        ),

        CheckConstraint(
            "stt_confidence IS NULL OR stt_confidence BETWEEN 0 AND 100",
            name="ck_comm_analyses_stt_confidence_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    interview_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    speaking_pace_wpm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    filler_word_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    long_pause_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False, 
        default=0,
        server_default="0",
    )

    total_pause_duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    average_volume_db: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    stt_confidence: Mapped[int | None] = mapped_column(
        Integer, 
        nullable=True,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    interview: Mapped["Interview"] = relationship(back_populates="communication_analysis")