import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey,String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship

from ..base_class import Base

if TYPE_CHECKING:
    from .resume import Resume

class ResumeSkill(Base):
    __tablename__="resume_skills"

    id:Mapped[uuid.UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    resume_id:Mapped[uuid.UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("resumes.id"),
        index=True,
        nullable=False,
    )

    skill_name:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )

    resume:Mapped["Resume"]=relationship(
        back_populates="skills",
    )
