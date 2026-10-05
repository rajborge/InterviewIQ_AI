import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base_class import Base
from .enums import LightingQuality, db_enum

if TYPE_CHECKING:
    from interview import Interview


class VideoAnalysis(Base):
    __tablename__ = "video_analyses"

    __table_args__ = (
        CheckConstraint(
            "face_visible_percentage IS NULL OR face_visible_percentage BETWEEN 0 AND 100",
            name="ck_video_analyses_face_visible_pct_range",
        ),

        CheckConstraint("gaze_away_count >= 0", name="ck_video_analyses_gaze_away_non_negative"),

        CheckConstraint("posture_issue_count >= 0", name="ck_video_analyses_posture_non_negative"),

        CheckConstraint(
            "excessive_movement_count >= 0", name="ck_video_analyses_movement_non_negative"
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

    face_visible_percentage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    gaze_away_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    posture_issue_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    excessive_movement_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    lighting_quality: Mapped[LightingQuality | None] = mapped_column(
        db_enum(LightingQuality, "lighting_quality"),
        nullable=True,
    )

    camera_positioning_issue: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    interview: Mapped["Interview"] = relationship(back_populates="video_analysis")