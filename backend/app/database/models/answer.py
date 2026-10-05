import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_class import Base

if TYPE_CHECKING:
    from .question import Question
    from .answer_evaluation import AnswerEvaluation


class Answer(Base):
    __tablename__ = "answers"

    __table_args__ = (
        CheckConstraint(
            "hints_used >= 0",
            name="ck_answers_hints_non_negative"
        ),

        CheckConstraint(
            "time_taken_seconds IS NULL OR time_taken_seconds >= 0",
            name="ck_answers_time_non_negative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    answer_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_skipped: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    time_taken_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    hints_used: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    clarification_requested: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    question: Mapped["Question"] = relationship(
        back_populates="answer",
    )

    evaluation:Mapped["AnswerEvaluation | None"]=relationship(
        back_populates="answer",
        cascade="all,delete-orphan",
        uselist=False,
    )