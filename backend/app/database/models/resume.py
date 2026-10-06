import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime,ForeignKey,String,Text,func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from ..base_class import Base

from .resume_skill import ResumeSkill
from .resume_experience import ResumeExperience
from .resume_education import ResumeEducation
from .resume_projects import ResumeProject

if TYPE_CHECKING:
    from .user import User

class Resume(Base):
    __tablename__="resumes"

    id:Mapped[uuid.UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id:Mapped[uuid.UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    file_path:Mapped[str]=mapped_column(
        String(500),
        nullable=False,
    )

    extracted_text:Mapped[str | None]=mapped_column(
        Text,
        nullable=True,
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user:Mapped["User"]=relationship(
        "User",
        back_populates="resumes",
    )

    skills:Mapped[list["ResumeSkill"]]=relationship(
        ResumeSkill,
        back_populates="resume",
        cascade="all,delete-orphan",
    )

    projects:Mapped[list["ResumeProject"]]=relationship(
        ResumeProject,
        back_populates="resume",
        cascade="all,delete-orphan",
    )

    experiences:Mapped[list["ResumeExperience"]]=relationship(
        ResumeExperience,
        back_populates="resume",
        cascade="all,delete-orphan",
    )

    education:Mapped[list["ResumeEducation"]]=relationship(
        ResumeEducation,
        back_populates="resume",
        cascade="all,delete-orphan",
    )
