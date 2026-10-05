import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base_class import Base

from .enums import Difficulty, InterviewMode, InterviewStatus, InterviewType, db_enum

if TYPE_CHECKING:
    from .user import User
    from .resume import Resume
    from .question import Question
    from .interview_evaluation import InterviewEvaluation
    from .communication_analysis import CommunicationAnalysis
    from .video_analysis import VideoAnalysis


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    interview_type: Mapped[InterviewType] = mapped_column(
        db_enum(InterviewType, "interview_type"),
        nullable=False,
    )

    target_role: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    mode: Mapped[InterviewMode] = mapped_column(
        db_enum(InterviewMode, "interview_mode"),
        nullable=False,
    )

    difficulty: Mapped[Difficulty] = mapped_column(
        db_enum(Difficulty, "difficulty"),
        nullable=False,
    )

    status: Mapped[InterviewStatus] = mapped_column(
        db_enum(InterviewStatus, "interview_status"),
        nullable=False,
        default=InterviewStatus.IN_PROGRESS,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="interviews",
    )

    resume: Mapped["Resume | None"] = relationship()

    questions: Mapped[list["Question"]] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="Question.sequence_number",
    )

    evaluation:Mapped["InterviewEvaluation | None"]=relationship(
        back_populates="interview",
        cascade="all,delete-orphan",
        uselist=False,
    )

    communication_analysis: Mapped["CommunicationAnalysis | None"] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        uselist=False,
    )

    video_analysis: Mapped["VideoAnalysis | None"] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        uselist=False,
    )