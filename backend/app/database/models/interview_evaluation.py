import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base_class import Base

if TYPE_CHECKING:
    from .interview import Interview


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    __table_args__ = (
        CheckConstraint("overall_score BETWEEN 0 AND 100", name="ck_interview_evaluations_overall_score_range"),

        CheckConstraint(
            "communication_score IS NULL OR communication_score BETWEEN 0 AND 100",
            name="ck_interview_evaluations_communication_score_range",
        ),

        CheckConstraint(
            "video_score IS NULL OR video_score BETWEEN 0 AND 100",
            name="ck_interview_evaluations_video_score_range",
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

    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    topic_wise_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    communication_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    video_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    improvement_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    interview: Mapped["Interview"] = relationship(back_populates="evaluation")