import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime,String,func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column,Mapped,relationship
from ..base_class import Base

if TYPE_CHECKING:
    from .resume import Resume

class User(Base):
    __tablename__="users"

    id:Mapped[uuid.UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email:Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash:Mapped[str | None]=mapped_column(
        String(255),
        nullable=True,
    )

    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    resumes:Mapped[list["Resume"]]=relationship(
        back_populates="users"
    )