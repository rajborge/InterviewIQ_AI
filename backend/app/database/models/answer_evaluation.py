import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base_class import Base

if TYPE_CHECKING:
    from .answer import Answer


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 100", name="ck_answer_evaluations_score_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    answer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    criteria_breakdown: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    feedback_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    answer: Mapped["Answer"] = relationship(
        back_populates="evaluation",
    )