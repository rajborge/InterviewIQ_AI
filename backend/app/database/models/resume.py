import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime,ForeignKey,String,Text,func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from ..base_class import Base

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
        back_populates="resumes",
    )
