import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base_class import Base
from .enums import Difficulty, QuestionSource, RoundType, db_enum

if TYPE_CHECKING:
    from .interview import Interview
    from .answer import Answer

class Question(Base):
    __tablename__ = "questions"

    __table_args__ = (
        UniqueConstraint(
            "interview_id", "sequence_number",
            name="uq_questions_interview_sequence",
        ),

        UniqueConstraint(
            "parent_question_id", "follow_up_number",
            name="uq_questions_parent_follow_up_slot",
        ),

        CheckConstraint(
            "parent_question_id <> id",
            name="ck_questions_not_own_parent",
        ),

        CheckConstraint(
            "follow_up_number BETWEEN 1 AND 3",
            name="ck_questions_follow_up_number_range",
        ),

        CheckConstraint(
            "(parent_question_id IS NULL) = (follow_up_number IS NULL)",
            name="ck_questions_parent_and_slot_consistent",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    interview_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("interviews.id"),
        nullable=False,
        index=True,
    )
    parent_question_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    follow_up_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    round_type: Mapped[RoundType] = mapped_column(
        db_enum(RoundType, "round_type"),
        nullable=False,
    )

    source: Mapped[QuestionSource] = mapped_column(
        db_enum(QuestionSource, "question_source"),
        nullable=False,
    )

    difficulty: Mapped[Difficulty] = mapped_column(
        db_enum(Difficulty, "question_difficulty"),
        nullable=False,
    )

    topic: Mapped[str | None] = mapped_column(
        String(100), 
        nullable=True,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    time_limit_seconds: Mapped[int | None] = mapped_column(
        Integer,nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    interview: Mapped["Interview"] = relationship(
        back_populates="questions",
    )

    parent: Mapped["Question | None"] = relationship(
        back_populates="follow_ups",
        remote_side="Question.id",
    )

    follow_ups: Mapped[list["Question"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="Question.follow_up_number",
    )

    answer: Mapped["Answer | None"] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        uselist=False,
    )